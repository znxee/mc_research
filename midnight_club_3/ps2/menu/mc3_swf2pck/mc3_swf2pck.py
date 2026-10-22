"""
mc3_swf2pck.py - the way back: a .swf compiled into the alpha's flash .pck

    python mc3_swf2pck.py pck       FILE.swf|DIR --out DIR
    python mc3_swf2pck.py roundtrip FILE.pck|DIR [--layout source|packed]
    python mc3_swf2pck.py viaswf    FILE.pck|DIR [--no-meta]
    python mc3_swf2pck.py ingame    FILE.pck|DIR|orig --name N [--at 40] [--compare DIR]

`mc3_swf.py` reads a flash .pck completely and writes it out as a SWF. This
tool is the other half: it writes the .pck - the memory image of Angel's flash
player objects (c:/soft/age/src/flash) - from a model of the movie, and builds
that model from a SWF.

THE IMAGE IS AN ALLOCATOR'S HEAP

The baker parsed the SWF on a PS2 (its pointers into its own heap are still in
the files: 0x00238F60, the stale glyph tables), allocating every object in a
resource heap based at 0x06800000, filled with 0xCD, and dumped the heap. So
writing a .pck means: allocate the same objects, fill them field by field,
point them at each other and dump. Everything below was taken from the code
that builds or reads each object, in the alpha (SLUS_123.45, names from MC.MAP):

    gfxMipChain(int,int,fmt,int,bool)  0x4DE078   the mip chain: +04 links the
        previous chain (gfxMipChain::sm_First), per level blocks and TBW from
        AdjustSize (0x4DDFD8) - the GS page the format wants
    gfxMipChain::CanSwizzle 0x4DE500 / Load 0x4DE5B0   swizzled only when w==h or
        w==2h (and >= 16x16 for 8 bit, 32x16 for 4 bit)
    gfxTexture::InitDma 0x4E2AF0 / UpdateRegs 0x4E32B0  the A+D packet: TEX1,
        CLAMP, TEX0, MIPTBP1/2, 0xCAFEBABE; TEX0 from TBW/PSM/TW/TH/CLD
    gfxTexturePalette::Create 0x4E7248 / SetEntry 0x4E72D8   CLUT, CSM1 order
    swfEDITTEXT(datResource&) 0x208910   +10 = strlen(text)+1 (0 = no text)
    swfFONT(datResource&) 0x208820       +0C zeroed: the glyph table is dead

The vtable words the objects carry are the BAKER's build (0x20Axxx; the alpha's
own are at 0x5DCxxx); every constructor overwrites them, so they are copied
as they are. The two the alpha files never show follow from the spacing:
swfSOUND 0x20A6D8 (one PlaceObject2 in the 305 files carries it - a stale
word), swfCMD_DoInitAction 0x20A7F8.

TWO LAYOUTS

    source   every block at the offset it has in the .pck the model came from.
             With that, `roundtrip` proves each FIELD: the rebuilt file must be
             the original byte for byte - 305 of 305 files of the alpha are.
    packed   a plain bump allocator (the alignments the baker used). What a SWF
             is compiled with; checked by reading the result back.

FROM A SWF

A SWF written by mc3_swf.py carries an `mc3_pck_meta` block: for every bitmap,
shape and font, what SWF cannot hold (the CLUT before premultiplication, the
fans and float matrices, the glyph sheets) and a hash of the tag it was written
with. Untouched tags come back exactly from it; an edited one - or any other
SWF - is compiled from what the SWF says: shapes cut into trapezoids by an
even-odd sweep per fill style, bitmaps scaled to the nearest power of two (at
most 512) and quantized, font sheets drawn for every size a text uses. Matrix
floats are made the way the baker's EE FPU made them, rounding toward zero.

`viaswf` checks both ways on the alpha's own files (with the block: the same
movie, field by field; without it: the same coverage per fill, the same
strokes, the same texels and alpha), and `ingame` puts a compiled set in the
alpha's HostFS folder (modloader/boot/alpha), boots it and screenshots it.
"""

import argparse
import collections
import importlib.util
import math
import os
import re
import struct
import sys
import zlib

_AQUI = os.path.dirname(os.path.abspath(__file__))

BASE = 0x06800000
HEADER = 0x80
CD = 0xCD

VT = {'FILE': 0x20A510, 'EDITTEXT': 0x20A540, 'TEXT': 0x20A570, 'FONT': 0x20A5A0,
      'SHAPE': 0x20A6A8, 'SOUND': 0x20A6D8, 'SPRITE': 0x20A708, 'BITMAP': 0x20A738,
      'BUTTON': 0x20A768, 'REMOVE': 0x20A798, 'PLACE1': 0x20A7B8, 'PLACE0': 0x20A7D8,
      'DOINIT': 0x20A7F8, 'DOACTION': 0x20A818}
OBJ_VT = {1: 'SHAPE', 2: 'SPRITE', 3: 'BUTTON', 4: 'BITMAP', 5: 'FONT', 6: 'TEXT',
          7: 'EDITTEXT', 8: 'SOUND'}

# the first gfxMipChain of every file links to this one: a chain the baker had
# made before its resource heap opened (gfxMipChain::sm_First)
MIP_LINK_FIRST = 0x00238F60
# swfEDITTEXT +08 when there is no text: an address in the baker's image; the
# constructor replaces it with a "" of its own
EDITTEXT_NO_TEXT = 0x0020CB26

# Serialized baker addresses, not the runtime vtables installed by Place.
# v6 object/command values are measured across the untouched Remix corpus,
# except SOUND/DOINIT: absent from the corpus, inferred from adjacent slots.
BAKERS = {
    5: (VT, MIP_LINK_FIRST, EDITTEXT_NO_TEXT),
    6: ({'FILE': 0x211A50, 'EDITTEXT': 0x211A80, 'TEXT': 0x211AB0,
         'FONT': 0x211AE0, 'SHAPE': 0x211C00, 'SOUND': 0x211C30,
         'SPRITE': 0x211C60, 'BITMAP': 0x211C90, 'BUTTON': 0x211CC0,
         'REMOVE': 0x211CF0, 'PLACE1': 0x211D10, 'PLACE0': 0x211D30,
         'DOINIT': 0x211D50, 'DOACTION': 0x211D70}, 0x00245040, 0x00214116),
}


def baker(version):
    if version not in BAKERS:
        raise BakeError('unsupported PCK version %d (expected 5 or 6)' % version)
    return BAKERS[version]

# gfxImage formats -> GS (gfxImage::sm_FmtToPsm), bits per texel in VRAM
# (vramBppTable) and the page AdjustSize pads small textures to
PSM = {5: 0x13, 6: 0x14}
VRAM_BPP = {5: 8, 6: 4}
PAGE = {5: (128, 64), 6: (128, 128)}


def _mod(nome):
    m = sys.modules.get(nome)
    if m is not None:
        return m
    s = importlib.util.spec_from_file_location(nome, os.path.join(_AQUI, nome + '.py'))
    m = importlib.util.module_from_spec(s)
    sys.modules[nome] = m
    s.loader.exec_module(m)
    return m


class BakeError(Exception):
    pass


# ---------------------------------------------------------------------------
# the heap
# ---------------------------------------------------------------------------
class Block(object):
    """One allocation: its bytes (0xCD where nothing is written), the pointers
    in it, and - for `new T[n]` of a class with a destructor - the element
    count the 16-byte cookie in front of it holds."""
    __slots__ = ('kind', 'data', 'align', 'cookie', 'relocs', 'addr', 'src', 'extra')

    def __init__(self, kind, size, align, cookie, src, extra):
        self.kind = kind
        self.data = bytearray([CD]) * size
        self.align = align
        self.cookie = cookie
        self.relocs = []
        self.addr = None
        self.src = src
        self.extra = extra

    def put(self, fmt, off, *v):
        struct.pack_into('<' + fmt, self.data, off, *v)

    def raw(self, off, b):
        self.data[off:off + len(b)] = b

    def ptr(self, off, target, delta=0):
        """A pointer to `target` (a Block), or 0 for None."""
        if target is None:
            self.put('I', off, 0)
        else:
            self.relocs.append((off, target, delta))


class Heap(object):
    def __init__(self, base=BASE):
        self.base = base
        self.blocks = []

    def new(self, kind, size, align=16, cookie=None, src=None, extra=0):
        b = Block(kind, size, align, cookie, src, extra)
        self.blocks.append(b)
        return b

    def layout_packed(self):
        p = self.base
        for b in self.blocks:
            a = b.align
            p = (p + a - 1) & -a
            if b.cookie is not None:
                p += 16
            b.addr = p
            p += len(b.data) + b.extra
        return p - self.base

    def layout_source(self):
        end = 0
        for b in self.blocks:
            if b.src is None:
                raise BakeError('%s has no source offset' % b.kind)
            b.addr = self.base + b.src - HEADER
            end = max(end, b.addr + len(b.data) - self.base)
        return end

    def image(self, size, version=5, flag=1):
        out = bytearray([CD]) * size
        for b in self.blocks:
            o = b.addr - self.base
            if b.cookie is not None:
                struct.pack_into('<I', out, o - 16, b.cookie)
            d = b.data
            if b.relocs:
                d = bytearray(d)
                for off, t, delta in b.relocs:
                    struct.pack_into('<I', d, off, t.addr + delta)
            out[o:o + len(d)] = d
        head = struct.pack('<4I', self.base, version, flag, size) + bytes(HEADER - 16)
        return head + bytes(out)


# ---------------------------------------------------------------------------
# the model: what a .pck holds, in plain values
# ---------------------------------------------------------------------------
class Obj(object):
    """An attribute bag; `src` maps a part name to its offset in a source .pck."""

    def __init__(self, **kw):
        self.src = {}
        self.__dict__.update(kw)


def u16s(vals):
    return struct.pack('<%dH' % len(vals), *vals)


def gs_log2(v):
    """ceil(log2(v)) the way UpdateRegs counts it."""
    n = 0
    x = (2 * v - 1) >> 1
    while x:
        x >>= 1
        n += 1
    return n


def adjust_size(fmt, w, h):
    """AdjustSize (0x4DDFD8): a texture that is neither square nor 2:1 and is
    smaller than a GS page is padded - to the page, or to a square, whichever
    is smaller."""
    if w == h or w == 2 * h:
        return w, h
    pw, ph = PAGE[fmt]
    if w >= pw and h >= ph:
        return w, h
    aw, ah = max(w, pw), max(h, ph)
    m = max(w, h)
    if aw * ah < m * m:
        return aw, ah
    return m, m


def can_swizzle(fmt, w, h):
    """gfxMipChain::CanSwizzle for one level."""
    if not (w == h or w == 2 * h):
        return False
    if fmt == 5:
        return w >= 16 and h >= 16
    return w >= 32 and h >= 16


class Texture(Obj):
    """gfxTexture + gfxMipChain + gfxTexturePalette, one level (every texture
    of the alpha's flash files has one).

        fmt      5 (8 bit) or 6 (4 bit)
        w, h     the texture size
        pixels   level 0 as stored: swizzled when `swizzled`
        palette  the CLUT entries as stored (32-bit, CSM1 order for 256)
        link     gfxMipChain +04 (None: the previous chain, as the baker had it)
    """

    def derive(self):
        fmt, w, h = self.fmt, self.w, self.h
        aw, ah = adjust_size(fmt, w, h)
        self.blocks = (VRAM_BPP[fmt] * aw * ah + 2047) >> 11
        self.tbw = (aw + 63) >> 6
        n = len(self.palette) // 4
        self.pal_blocks = 1 if n == 16 else 4
        tex0 = (self.tbw << 14) | (PSM[fmt] << 20) | (gs_log2(w) << 26) | (gs_log2(h) << 30)
        tex0 |= 0x400000000          # TCC: the alpha of the texture is used
        tex0 |= 0x2000000000000000   # CLD = 1: load the CLUT
        self.tex0 = tex0


# ---------------------------------------------------------------------------
# model -> blocks
# ---------------------------------------------------------------------------
class Builder(object):
    """Allocates the model's objects in the order the baker did and fills
    them. `order` (optional) interleaves definitions with root commands the
    way the SWF did: [('obj', k) | ('root', frame)]."""

    def __init__(self, model):
        self.m = model
        self.vt, self.mip_link_first, self.edittext_no_text = baker(model.version)
        self.h = Heap(getattr(model, 'base', BASE))
        self.objs = {}
        self.actions = {}
        self.last_mip = None
        self.font_block = {}

    def new(self, kind, size, align=16, cookie=None, src=None, extra=0):
        return self.h.new(kind, size, align, cookie, src, extra)

    # -- action lists ----------------------------------------------------
    def action(self, a):
        if a is None:
            return None
        b = self.actions.get(id(a))
        if b is None:
            code = a.code
            b = self.new('actions', 2 + len(code), 4, src=a.src.get('self'), extra=1)
            b.put('H', 0, a.refcount)
            b.raw(2, code)
            self.actions[id(a)] = b
        return b

    # -- timelines -------------------------------------------------------
    def frames_array(self, frames, src):
        if not frames:
            return None
        return self.new('frames', 8 * len(frames), 4, cookie=len(frames), src=src)

    def commands(self, fa, k, fr):
        """The commands of frame k of a timeline whose frame array is `fa`."""
        fa.put('I', 8 * k, fr.word)
        prev, prev_off = fa, 8 * k + 4
        for c in fr.commands:
            b = self.command(c)
            prev.ptr(prev_off, b)
            prev, prev_off = b, 4
        prev.put('I', prev_off, 0)

    def command(self, c):
        if c.kind in (0, 1):
            size = 0x18 if c.kind == 0 else 0x28
            b = self.new('place%d' % c.kind, size, 4, src=c.src.get('self'))
            b.put('B', 0, c.kind)
            b.put('B', 1, c.flags)
            b.raw(2, c.pad)
            b.put('I', 8, c.vt)
            b.put('HH', 0x0C, c.depth, c.char)
            mb = None
            if c.mat is not None:
                mb = self.new('place matrix', 2 * len(c.mat), 4, src=c.src.get('mat'))
                mb.raw(0, struct.pack('<%dh' % len(c.mat), *c.mat))
            b.ptr(0x10, mb)
            cb = None
            if c.cx is not None:
                cb = self.new('cxform', 8, 4, src=c.src.get('cx'))
                cb.raw(0, c.cx)
            b.ptr(0x14, cb)
            if c.kind == 1:
                b.put('I', 0x18, c.event_flags)
                b.put('i', 0x1C, c.nevents)
                nb = None
                if c.name is not None:
                    nb = self.new('string', len(c.name) + 1, 4, src=c.src.get('name'))
                    nb.raw(0, c.name + b'\0')
                b.ptr(0x24, nb)
                eb = None
                if c.events is not None:
                    acts = [self.action(a) for _f, a, _k in c.events]
                    eb = self.new('clip events', 12 * len(c.events), 4, cookie=len(c.events),
                                  src=c.src.get('events'))
                    for i, ((flags, _a, key), ab) in enumerate(zip(c.events, acts)):
                        eb.put('I', 12 * i, flags)
                        eb.ptr(12 * i + 4, ab)
                        eb.put('I', 12 * i + 8, key)
                b.ptr(0x20, eb)
            return b
        if c.kind == 2:
            b = self.new('remove', 0x0C, 4, src=c.src.get('self'))
            b.put('B', 0, 2)
            b.raw(1, c.pad)
            b.put('H', 2, c.depth)
            b.put('I', 8, c.vt)
            return b
        b = self.new('doaction', 0x10, 16, src=c.src.get('self'))
        b.put('B', 0, c.kind)
        b.put('I', 8, c.vt)
        b.ptr(0x0C, self.action(c.action))
        return b

    def timeline(self, frames, src):
        fa = self.frames_array(frames, src)
        for k, fr in enumerate(frames):
            self.commands(fa, k, fr)
        return fa

    # -- textures --------------------------------------------------------
    def texture(self, t):
        t.derive()
        mip = self.new('gfxMipChain', 0x60, 16, src=t.src.get('mip'))
        pix = self.new('pixels', len(t.pixels), 16, src=t.src.get('pix'))
        pix.raw(0, t.pixels)
        tex = self.new('gfxTexture', 0xA0, 64, src=t.src.get('tex'))
        pal = self.new('palette', 16 + len(t.palette), 16, src=t.src.get('pal'))

        mip.put('I', 0, 1)
        if t.link is not None:
            mip.put('I', 4, t.link)
        elif self.last_mip is None:
            mip.put('I', 4, self.mip_link_first)
        else:
            mip.ptr(4, self.last_mip)
        self.last_mip = mip
        mip.ptr(8, pix)
        mip.put('BBHHH', 0x28, t.fmt, 0, t.blocks, t.w, t.h)
        if t.swizzled:
            mode = 1 if (t.fmt == 5 or t.w == t.h) else 2
            up_h = t.h >> 2 if (t.fmt == 6 and t.w == t.h) else t.h >> 1
            mip.put('BBH', 0x30, 1, mode, up_h)
        else:
            mip.put('BBH', 0x30, t.fmt, 0, t.h)
        mip.put('QQ', 0x38, 0, 0)
        mip.put('H', 0x48, t.blocks)
        mip.put('B', 0x58, t.tbw)

        # gfxTexture::InitDma, then UpdateRegs
        tex.put('Q', 0x00, 0x60000006)
        tex.put('Q', 0x08, 0x5000000611000000)
        tex.put('Q', 0x10, 0x1000000000008005)
        tex.put('Q', 0x18, 14)
        tex.put('Q', 0x20, 0x00000FC800000120)     # TEX1: bias K -3.5, MMAG/MMIN linear
        tex.put('II', 0x28, 0x14, 0)
        tex.put('Q', 0x30, 0)
        tex.put('II', 0x38, 0x08, 0)
        tex.put('Q', 0x40, t.tex0)
        tex.put('Ii', 0x48, 0x06, -1)
        tex.put('I', 0x58, 0x34)
        tex.put('II', 0x68, 0x36, 0xCAFEBABE)
        tex.put('HHI', 0x70, t.blocks + t.pal_blocks, 0, 0)
        tex.put('Q', 0x78, t.tex0)
        tex.put('II', 0x80, 0, 0)
        tex.put('HHI', 0x88, t.w, t.h, t.flags)
        tex.ptr(0x90, pal)
        tex.ptr(0x94, mip)
        tex.put('I', 0x98, 1)

        n = len(t.palette) // 4
        pal.put('HHB', 0, 1, n, 1)
        pal.put('I', 8, t.pal_blocks)
        pal.raw(16, t.palette)
        return tex

    # -- objects ---------------------------------------------------------
    def object(self, k):
        ob = self.m.objects[k]
        fn = {1: self.shape, 2: self.sprite, 3: self.button, 4: self.bitmap, 5: self.font,
              6: self.text, 7: self.edittext, 8: self.sound}[ob.kind]
        fn(k, ob)

    def head(self, k, ob, kind, size):
        b = self.new(kind, size, 16, src=ob.src.get('self'))
        b.put('B', 0, ob.kind)
        b.put('I', 4, ob.vt)
        self.objs[k] = b
        return b

    def shape(self, k, sh):
        b = self.head(k, sh, 'shape', 0x18)
        grads = []
        for f in sh.fills:
            g = f.gradient
            if g is None:
                grads.append(None)
                continue
            rb = self.new('gradient ratios', len(g.ratios), 4, src=g.src.get('ratios'))
            rb.raw(0, g.ratios)
            cb = self.new('gradient colours', 4 * len(g.colours), 8, src=g.src.get('colours'))
            cb.raw(0, struct.pack('<%dI' % len(g.colours), *g.colours))
            gb = self.new('gradient', 0x24, 16, src=g.src.get('self'))
            gb.raw(0, g.mat)
            gb.put('BB', 0x18, g.count, g.radial)
            gb.raw(0x1A, g.pad)
            gb.ptr(0x1C, rb)
            gb.ptr(0x20, cb)
            grads.append(gb)
        db = self.new('display list', len(sh.dlist), 16, src=sh.src.get('dlist'))
        db.raw(0, sh.dlist)
        fb = None
        if sh.fills_present:
            fb = self.new('fill styles', 40 * len(sh.fills), 16, src=sh.src.get('fills'))
            for i, f in enumerate(sh.fills):
                o = 40 * i
                fb.put('II', o, f.type, f.colour)
                fb.raw(o + 8, f.mat)
                if f.bitmap is not None:
                    fb.ptr(o + 0x20, self.objs[f.bitmap])
                else:
                    fb.put('I', o + 0x20, 0)
                fb.ptr(o + 0x24, grads[i])
        lb = None
        if sh.lines_present:
            lb = self.new('line styles', 8 * len(sh.lines), 8, src=sh.src.get('lines'))
            for i, (w, pad, col) in enumerate(sh.lines):
                lb.put('HHI', 8 * i, w, pad, col)
        b.ptr(8, fb)
        b.ptr(0x0C, lb)
        b.ptr(0x10, db)
        b.put('HH', 0x14, len(sh.fills), len(sh.lines))

    def sprite(self, k, sp):
        b = self.head(k, sp, 'sprite', 0x10)
        b.put('H', 8, len(sp.frames))
        b.ptr(0x0C, self.timeline(sp.frames, sp.src.get('frames')))

    def button(self, k, bt):
        b = self.head(k, bt, 'button', 0x14)
        b.put('BBB', 8, bt.byte8, len(bt.records), len(bt.conds))
        rb = None
        if bt.records_present:
            rb = self.new('button records', 40 * len(bt.records), 16, src=bt.src.get('records'))
            for i, r in enumerate(bt.records):
                o = 40 * i
                rb.put('B', o, r.states)
                if r.pad is not None:
                    rb.raw(o + 1, r.pad)
                rb.put('H', o + 2, r.depth)
                rb.raw(o + 4, r.mat)
                rb.raw(o + 0x1C, r.cx)
                rb.ptr(o + 0x24, self.objs[r.char])
        b.ptr(0x0C, rb)
        cb = None
        if bt.conds_present:
            acts = [self.action(a) for _c, a, _p in bt.conds]
            cb = self.new('button conditions', 8 * len(bt.conds), 16, cookie=len(bt.conds),
                          src=bt.src.get('conds'))
            for i, ((cond, _a, pad), ab) in enumerate(zip(bt.conds, acts)):
                cb.put('H', 8 * i, cond)
                if pad is not None:
                    cb.raw(8 * i + 2, pad)
                cb.ptr(8 * i + 4, ab)
        b.ptr(0x10, cb)

    def bitmap(self, k, bm):
        b = self.head(k, bm, 'bitmap', 0x18)
        b.put('HH', 0x0C, bm.tw, bm.th)
        b.raw(0x10, bm.inv)
        b.ptr(8, self.texture(bm.tex))

    def font(self, k, ft):
        b = self.head(k, ft, 'font', 0xC0)
        b.put('h', 8, ft.count)
        gt = None
        if ft.glyph_table is not None:
            gt = self.new('stale glyph table', len(ft.glyph_table), 16,
                          cookie=len(ft.glyph_table) // 8, src=ft.src.get('glyphs'))
            gt.raw(0, ft.glyph_table)
        b.ptr(0x0C, gt)
        cb = None
        if ft.codes is not None:
            cb = self.new('font codes', 2 * len(ft.codes), 16, src=ft.src.get('codes'))
            cb.raw(0, u16s(ft.codes))
        b.ptr(0x10, cb)
        ab = None
        if ft.advances is not None:
            ab = self.new('font advances', 2 * len(ft.advances), 16, src=ft.src.get('advances'))
            ab.raw(0, u16s(ft.advances))
        b.ptr(0x14, ab)
        b.raw(0x18, ft.ascii)
        b.put('hhhh', 0x98, len(ft.sheets), ft.ascent, ft.descent, ft.leading)
        self.font_block[k] = b
        # sheets are made when a text first needs them (see sheets_for)
        for i, s in enumerate(ft.sheets):
            if not s.lazy:
                b.ptr(0xA0 + 4 * i, self.sheet(s))

    def sheet(self, s):
        b = self.new('font sheet', 0x14, 16, src=s.src.get('self'))
        rb = self.new('glyph rects', len(s.rects), 4, src=s.src.get('rects'))
        rb.raw(0, s.rects)
        tb = self.new('sheet textures', 4 * len(s.textures), 4, src=s.src.get('textures'))
        texs = [self.texture(t) for t in s.textures]
        for i, t in enumerate(texs):
            tb.ptr(4 * i, t)
        ib = None
        if s.texindex is not None:
            ib = self.new('glyph texture index', len(s.texindex), 1, src=s.src.get('texindex'))
            ib.raw(0, s.texindex)
        b.ptr(0, tb)
        b.ptr(4, rb)
        b.put('hH', 8, s.size, s.count)
        b.ptr(0x0C, ib)
        b.put('i', 0x10, len(s.textures))
        return b

    def sheets_for(self, font_index, height):
        """The sheets a text object created when it was baked."""
        ft = self.m.objects[font_index]
        fb = self.font_block[font_index]
        for i, s in enumerate(ft.sheets):
            if s.lazy and s.size == height and not getattr(s, 'made', False):
                s.made = True
                fb.ptr(0xA0 + 4 * i, self.sheet(s))

    def text(self, k, tx):
        b = self.head(k, tx, 'text', 0x24)
        b.raw(8, tx.mat)
        for f, hgt in tx.sheet_needs:
            self.sheets_for(f, hgt)
        rb = None
        if tx.records is not None:
            rb = self.new('text records', len(tx.records), 16, src=tx.src.get('records'))
            rb.raw(0, tx.records)
        b.ptr(0x20, rb)

    def edittext(self, k, et):
        wide = self.m.version == 6
        b = self.head(k, et, 'edittext', 0x30 if wide else 0x28)
        self.sheets_for(et.font, et.height)
        vb = None
        if et.var is not None:
            vb = self.new('string', len(et.var) + 1, 4, src=et.src.get('var'))
            vb.raw(0, et.var + b'\0')
        tb = None
        if et.text is not None:
            tb = self.new('string', len(et.text) + 1, 4, src=et.src.get('text'))
            tb.raw(0, et.text + b'\0')
            b.ptr(8, tb)
        else:
            b.put('I', 8, et.text_word)
        b.ptr(0x0C, vb)
        b.put('Hh', 0x10, et.textlen, et.leading)
        b.put('IHH', 0x14, et.colour, et.font, et.height)
        b.put('iiii' if wide else 'hhhh', 0x1C, et.bw, et.bh, et.xmin, et.ymin)
        b.put('B', 0x2C if wide else 0x24, et.align)

    def sound(self, k, sd):
        self.head(k, sd, 'sound', 8)

    # -- the file --------------------------------------------------------
    def build(self):
        m = self.m
        f = self.new('swfFILE', 0x30, 16, src=m.src.get('file'))
        f.put('B', 0, 0)
        f.put('I', 4, m.vt)
        f.put('H', 8, len(m.frames))
        f.put('B', 0x14, m.swf_version)
        f.raw(0x18, m.rect)
        f.put('HH', 0x28, m.rate, len(m.objects))
        fa = self.frames_array(m.frames, m.src.get('frames'))
        f.ptr(0x0C, fa)
        order = m.order or ([('obj', k) for k in range(1, len(m.objects)) if m.objects[k] is not None]
                            + [('root', k) for k in range(len(m.frames))])
        tails = {}
        for item in order:
            what, k = item[0], item[1]
            if what == 'obj':
                self.object(k)
            elif what == 'root':
                self.commands(fa, k, m.frames[k])
                tails[k] = None
            else:
                # one root command where its tag stood in the SWF
                if k not in tails:
                    fa.put('I', 8 * k, m.frames[k].word)
                    tails[k] = (fa, 8 * k + 4)
                b = self.command(m.frames[k].commands[item[2]])
                blk, off = tails[k]
                blk.ptr(off, b)
                tails[k] = (b, 4)
        for k, fr in enumerate(m.frames):
            if k not in tails:
                self.commands(fa, k, fr)
            elif tails[k] is not None:
                tails[k][0].put('I', tails[k][1], 0)
        tb = self.new('object table', 4 * len(m.objects), 16, src=m.src.get('table'))
        tb.put('I', 0, m.table_zero)
        for k in range(1, len(m.objects)):
            if m.objects[k] is None:
                tb.put('I', 4 * k, 0)
            else:
                tb.ptr(4 * k, self.objs[k])
        f.ptr(0x10, tb)
        return self.h

    def image(self, layout='packed', size=None):
        h = self.build()
        if layout == 'source':
            end = h.layout_source()
            size = size if size is not None else end
        else:
            size = h.layout_packed()
        return h.image(size, self.m.version, self.m.flag)


# ---------------------------------------------------------------------------
# .pck -> model, with every offset kept (the `source` layout)
# ---------------------------------------------------------------------------
class FromPck(object):
    """Reads a flash .pck into the model, keeping the offset of every part."""

    def __init__(self, data, name='?'):
        R = _mod('mc3_swf')
        self.R = R
        self.mv = R.Movie(data, name)     # the reader proves the file is sound first
        self.img = self.mv.img
        self.actions = {}

    def u8(self, o):
        return self.img.d[o]

    def u16(self, o):
        return self.img.u16(o)

    def u32(self, o):
        return self.img.u32(o)

    def off(self, va):
        return self.img.off(va)

    def raw(self, o, n):
        return bytes(self.img.d[o:o + n])

    def action(self, o):
        if o is None:
            return None
        a = self.actions.get(o)
        if a is None:
            al = self.R.ActionList(self.img, o)
            a = self.actions[o] = Obj(refcount=al.refcount, code=bytes(al.code))
            a.src['self'] = o
        return a

    def model(self):
        img = self.img
        o = HEADER
        m = Obj(base=img.base, version=img.version, flag=img.flag, size=len(img.d) - HEADER,
                vt=self.u32(o + 4), swf_version=self.u8(o + 0x14), rect=self.raw(o + 0x18, 16),
                rate=self.u16(o + 0x28), order=None)
        nframes = self.u16(o + 8)
        fo = self.off(self.u32(o + 0x0C))
        to = self.off(self.u32(o + 0x10))
        n = self.u16(o + 0x2A)
        m.src.update(file=o, frames=fo, table=to)
        m.table_zero = self.u32(to)
        self.byva = {}
        for k in range(1, n):
            va = self.u32(to + 4 * k)
            if va:
                self.byva[va] = k
        m.objects = [None] * n
        for k in range(1, n):
            va = self.u32(to + 4 * k)
            if va:
                m.objects[k] = self.object(self.off(va))
        m.frames = self.frames(fo, nframes)
        # sheets: created lazily by the first text/edittext of their size
        self.sheet_owners(m)
        return m

    def frames(self, o, n):
        out = []
        for k in range(n):
            fr = Obj(word=self.u32(o + 8 * k), commands=[])
            c = self.off(self.u32(o + 8 * k + 4)) if self.u32(o + 8 * k + 4) else None
            while c is not None:
                fr.commands.append(self.command(c))
                nxt = self.u32(c + 4)
                c = self.off(nxt) if nxt else None
            out.append(fr)
        return out

    def command(self, o):
        k = self.u8(o)
        if k in (0, 1):
            c = Obj(kind=k, flags=self.u8(o + 1), pad=self.raw(o + 2, 2), vt=self.u32(o + 8),
                    depth=self.u16(o + 0x0C), char=self.u16(o + 0x0E), mat=None, cx=None)
            c.src['self'] = o
            mo = self.u32(o + 0x10)
            if mo:
                mo = self.off(mo)
                nv = 2 * (bool(c.flags & 1) + bool(c.flags & 2) + 1)
                c.mat = list(struct.unpack_from('<%dh' % nv, self.img.d, mo))
                c.src['mat'] = mo
            co = self.u32(o + 0x14)
            if co:
                co = self.off(co)
                c.cx = self.raw(co, 8)
                c.src['cx'] = co
            if k == 1:
                c.event_flags = self.u32(o + 0x18)
                c.nevents = struct.unpack_from('<i', self.img.d, o + 0x1C)[0]
                c.events = None
                eo = self.u32(o + 0x20)
                if eo:
                    eo = self.off(eo)
                    c.src['events'] = eo
                    c.events = []
                    for i in range(max(0, c.nevents)):
                        e = eo + 12 * i
                        ao = self.u32(e + 4)
                        c.events.append((self.u32(e), self.action(self.off(ao) if ao else None),
                                         self.u32(e + 8)))
                c.name = None
                no = self.u32(o + 0x24)
                if no:
                    no = self.off(no)
                    c.name = bytes(self.img.cstr(no))
                    c.src['name'] = no
            return c
        if k == 2:
            c = Obj(kind=2, pad=self.raw(o + 1, 1), depth=self.u16(o + 2), vt=self.u32(o + 8))
            c.src['self'] = o
            return c
        ao = self.u32(o + 0x0C)
        c = Obj(kind=k, vt=self.u32(o + 8), action=self.action(self.off(ao) if ao else None))
        c.src['self'] = o
        return c

    def texture(self, o):
        img = self.img
        t = Texture(fmt=None)
        mip = self.off(self.u32(o + 0x94))
        pal = self.off(self.u32(o + 0x90))
        t.fmt = self.u8(mip + 0x28)
        t.w, t.h = self.u16(mip + 0x2C), self.u16(mip + 0x2E)
        t.swizzled = self.u8(mip + 0x30) == 1
        bpp = {5: 8, 6: 4}[t.fmt]
        po = self.off(self.u32(mip + 8))
        t.pixels = self.raw(po, t.w * t.h * bpp // 8)
        ncol = self.u16(pal + 2)
        t.palette = self.raw(pal + 16, 4 * ncol)
        t.flags = self.u32(o + 0x8C)
        t.link = self.u32(mip + 4)
        t.src.update(tex=o, mip=mip, pix=po, pal=pal)
        if img.u32(o + 0x84):
            raise BakeError('%s: texture at %#x has a name' % (img.name, o))
        return t

    def object(self, o):
        k = self.u8(o)
        ob = Obj(kind=k, vt=self.u32(o + 4))
        ob.src['self'] = o
        if k == 1:
            nf, nl = self.u16(o + 0x14), self.u16(o + 0x16)
            fo, lo, do = self.u32(o + 8), self.u32(o + 0x0C), self.u32(o + 0x10)
            ob.fills_present, ob.lines_present = bool(fo), bool(lo)
            ob.fills, ob.lines = [], []
            if fo:
                fo = self.off(fo)
                ob.src['fills'] = fo
                for i in range(nf):
                    f = fo + 40 * i
                    fl = Obj(type=self.u32(f), colour=self.u32(f + 4), mat=self.raw(f + 8, 24),
                             bitmap=None, gradient=None)
                    bva = self.u32(f + 0x20)
                    if bva:
                        fl.bitmap = self.byva[bva]
                    go = self.u32(f + 0x24)
                    if go:
                        go = self.off(go)
                        cnt = self.u8(go + 0x18)
                        ro, cvo = self.off(self.u32(go + 0x1C)), self.off(self.u32(go + 0x20))
                        g = Obj(mat=self.raw(go, 24), count=cnt, radial=self.u8(go + 0x19),
                                pad=self.raw(go + 0x1A, 2), ratios=self.raw(ro, cnt),
                                colours=list(struct.unpack_from('<%dI' % cnt, self.img.d, cvo)))
                        g.src.update(self=go, ratios=ro, colours=cvo)
                        fl.gradient = g
                    ob.fills.append(fl)
            if lo:
                lo = self.off(lo)
                ob.src['lines'] = lo
                ob.lines = [struct.unpack_from('<HHI', self.img.d, lo + 8 * i) for i in range(nl)]
            do = self.off(do)
            ob.src['dlist'] = do
            n = self._dlist_len(do)
            ob.dlist = self.raw(do, n)
        elif k == 2:
            fo = self.u32(o + 0x0C)
            fo = self.off(fo) if fo else None
            ob.src['frames'] = fo
            ob.frames = self.frames(fo, self.u16(o + 8)) if fo is not None else []
        elif k == 3:
            ob.byte8 = self.u8(o + 8)
            nr, nc = self.u8(o + 9), self.u8(o + 0x0A)
            ro, co = self.u32(o + 0x0C), self.u32(o + 0x10)
            ob.records_present, ob.conds_present = bool(ro), bool(co)
            ob.records, ob.conds = [], []
            if ro:
                ro = self.off(ro)
                ob.src['records'] = ro
                for i in range(nr):
                    r = ro + 40 * i
                    # +01 is stack garbage the baker copied with the record
                    ob.records.append(Obj(states=self.u8(r), pad=self.raw(r + 1, 1), depth=self.u16(r + 2),
                                          mat=self.raw(r + 4, 24), cx=self.raw(r + 0x1C, 8),
                                          char=self.byva[self.u32(r + 0x24)]))
            if co:
                co = self.off(co)
                ob.src['conds'] = co
                for i in range(nc):
                    c = co + 8 * i
                    ao = self.u32(c + 4)
                    # +02 likewise: the player reads the u16 at +00 only
                    ob.conds.append((self.u16(c), self.action(self.off(ao) if ao else None),
                                     self.raw(c + 2, 2)))
        elif k == 4:
            ob.tw, ob.th = self.u16(o + 0x0C), self.u16(o + 0x0E)
            ob.inv = self.raw(o + 0x10, 8)
            ob.tex = self.texture(self.off(self.u32(o + 8)))
        elif k == 5:
            ob.count = struct.unpack_from('<h', self.img.d, o + 8)[0]
            gva, co, ao = self.u32(o + 0x0C), self.u32(o + 0x10), self.u32(o + 0x14)
            ob.glyph_table = None
            if gva:
                go = self.off(gva)
                ng = self.u32(go - 16)
                ob.glyph_table = self.raw(go, 8 * ng)
                ob.src['glyphs'] = go
            ob.codes = ob.advances = None
            if co:
                co = self.off(co)
                ob.codes = list(struct.unpack_from('<%dH' % ob.count, self.img.d, co))
                ob.src['codes'] = co
            if ao:
                ao = self.off(ao)
                ob.advances = list(struct.unpack_from('<%dH' % ob.count, self.img.d, ao))
                ob.src['advances'] = ao
            ob.ascii = self.raw(o + 0x18, 128)
            ns, ob.ascent, ob.descent, ob.leading = struct.unpack_from('<4h', self.img.d, o + 0x98)
            ob.sheets = []
            for i in range(ns):
                so = self.off(self.u32(o + 0xA0 + 4 * i))
                ob.sheets.append(self.sheet(so))
        elif k == 6:
            ob.mat = self.raw(o + 8, 24)
            ro = self.u32(o + 0x20)
            ob.records = None
            ob.sheet_needs = []
            if ro:
                ro = self.off(ro)
                ob.src['records'] = ro
                p = ro
                while True:
                    op = self.u16(p)
                    p += 2
                    if op == 0:
                        break
                    if op == 1:
                        ob.sheet_needs.append((self.u16(p), self.u16(p + 2)))
                    p += {1: 4, 2: 4, 3: 2, 4: 2}.get(op, 0)
                    if op == 5:
                        p += 2 + 4 * self.u16(p)
                ob.records = self.raw(ro, p - ro)
        elif k == 7:
            ob.textlen = self.u16(o + 0x10)
            ob.text = None
            ob.text_word = self.u32(o + 8)
            if ob.textlen and ob.text_word:
                to = self.off(ob.text_word)
                ob.text = bytes(self.img.cstr(to))
                ob.src['text'] = to
            vo = self.u32(o + 0x0C)
            ob.var = None
            if vo:
                vo = self.off(vo)
                ob.var = bytes(self.img.cstr(vo))
                ob.src['var'] = vo
            ob.leading = struct.unpack_from('<h', self.img.d, o + 0x12)[0]
            ob.colour, ob.font, ob.height = struct.unpack_from('<IHH', self.img.d, o + 0x14)
            wide = self.img.version == 6
            ob.bw, ob.bh, ob.xmin, ob.ymin = struct.unpack_from('<4i' if wide else '<4h', self.img.d, o + 0x1C)
            ob.align = self.u8(o + (0x2C if wide else 0x24))
        elif k != 8:
            raise BakeError('%s: object type %d at %#x' % (self.img.name, k, o))
        return ob

    def _dlist_len(self, o):
        p = o
        while True:
            op = self.u16(p)
            p += 2
            if op == 0:
                return p - o
            if op in (1, 2):
                p += 2 + 4 * self.u16(p)
            elif op == 3:
                p += 4
            elif op in (4, 5):
                p += 2
            else:
                raise BakeError('%s: shape op %d at %#x' % (self.img.name, op, p - 2))

    def sheet(self, o):
        s = Obj(lazy=True)
        s.src['self'] = o
        s.size = struct.unpack_from('<h', self.img.d, o + 8)[0]
        s.count = self.u16(o + 0x0A)
        ntex = struct.unpack_from('<i', self.img.d, o + 0x10)[0]
        to = self.off(self.u32(o))
        ro = self.off(self.u32(o + 4))
        io_ = self.u32(o + 0x0C)
        s.src.update(textures=to, rects=ro)
        s.rects = self.raw(ro, 12 * s.count)
        s.textures = [self.texture(self.off(self.u32(to + 4 * i))) for i in range(ntex)]
        s.texindex = None
        if io_:
            io_ = self.off(io_)
            s.texindex = self.raw(io_, s.count)
            s.src['texindex'] = io_
        return s

    def sheet_owners(self, m):
        """Each sheet was made by the first text that needed it: the object
        right before it in the file. Sheets nobody claims are built with
        their font."""
        for ob in m.objects:
            if ob is not None and ob.kind == 7:
                ob.sheet_needs = [(ob.font, ob.height)]
        for k, ob in enumerate(m.objects):
            if ob is None or ob.kind != 5:
                continue
            for s in ob.sheets:
                s.lazy = any(o2 is not None and o2.kind in (6, 7) and (k, s.size) in o2.sheet_needs
                             for o2 in m.objects)


# ---------------------------------------------------------------------------
# SWF -> model
# ---------------------------------------------------------------------------
def f32(x):
    return struct.unpack('<f', struct.pack('<f', x))[0]


def trunc32(x):
    """x as a float32 rounded toward zero - the EE FPU's rounding, which is
    what the baker's floats show: every translation in the alpha's TEXT and
    button records is trunc32(twips / 20), 27608 of 27608."""
    f = f32(x)
    if abs(f) > abs(x):
        bits = struct.unpack('<I', struct.pack('<f', f))[0] - 1
        f = struct.unpack('<f', struct.pack('<I', bits))[0]
    return f


class BitReader(object):
    """MSB-first reader of SWF bit fields; a byte field after bit fields
    starts on the next byte."""
    __slots__ = ('d', 'bp')

    def __init__(self, data, pos=0):
        self.d = data
        self.bp = pos * 8

    def ub(self, n):
        if n <= 0:
            return 0
        bp = self.bp
        b0 = bp >> 3
        end = bp + n
        nb = ((end + 7) >> 3) - b0
        if b0 + nb > len(self.d):
            raise BakeError('bit field runs past the end of the tag')
        chunk = int.from_bytes(self.d[b0:b0 + nb], 'big')
        self.bp = end
        return (chunk >> (nb * 8 - (end - b0 * 8))) & ((1 << n) - 1)

    def sb(self, n):
        v = self.ub(n)
        if n and v >> (n - 1):
            v -= 1 << n
        return v

    def align(self):
        self.bp = (self.bp + 7) & ~7

    @property
    def pos(self):
        return (self.bp + 7) >> 3

    def _get(self, fmt, n):
        self.align()
        p = self.bp >> 3
        if p + n > len(self.d):
            raise BakeError('field runs past the end of the tag')
        self.bp += 8 * n
        return struct.unpack_from(fmt, self.d, p)[0]

    def u8(self):
        return self._get('<B', 1)

    def u16(self):
        return self._get('<H', 2)

    def s16(self):
        return self._get('<h', 2)

    def u32(self):
        return self._get('<I', 4)

    def raw(self, n):
        self.align()
        p = self.bp >> 3
        self.bp += 8 * n
        return bytes(self.d[p:p + n])

    def string(self):
        self.align()
        p = self.bp >> 3
        e = self.d.find(b'\0', p)
        if e < 0:
            raise BakeError('unterminated string')
        self.bp = (e + 1) * 8
        return bytes(self.d[p:e])

    def rest(self):
        self.align()
        return bytes(self.d[self.bp >> 3:])


def read_rect(br):
    n = br.ub(5)
    v = [br.sb(n) for _ in range(4)]
    br.align()
    return v


class SMatrix(object):
    """A SWF MATRIX as stored: 16.16 scale/rotate, twips translation."""
    __slots__ = ('has_scale', 'sx', 'sy', 'has_rot', 'r0', 'r1', 'tx', 'ty')

    def __repr__(self):
        return 'SM(%d %d %d %d %d %d %d %d)' % (self.has_scale, self.sx, self.sy, self.has_rot,
                                                self.r0, self.r1, self.tx, self.ty)

    def floats(self, tdiv=20.0):
        """(a b c d tx ty), translation divided by `tdiv` (pixels by default)."""
        return (self.sx / 65536.0, self.r0 / 65536.0, self.r1 / 65536.0, self.sy / 65536.0,
                self.tx / tdiv, self.ty / tdiv)

    def pck_floats(self):
        """The six floats the baker stored for a TEXT or a button record."""
        return struct.pack('<6f', trunc32(self.sx / 65536.0), trunc32(self.r0 / 65536.0),
                           trunc32(self.r1 / 65536.0), trunc32(self.sy / 65536.0),
                           trunc32(self.tx / 20.0), trunc32(self.ty / 20.0))


def read_matrix(br):
    m = SMatrix()
    m.has_scale = br.ub(1)
    if m.has_scale:
        n = br.ub(5)
        m.sx, m.sy = br.sb(n), br.sb(n)
    else:
        m.sx = m.sy = 65536
    m.has_rot = br.ub(1)
    if m.has_rot:
        n = br.ub(5)
        m.r0, m.r1 = br.sb(n), br.sb(n)
    else:
        m.r0 = m.r1 = 0
    n = br.ub(5)
    m.tx, m.ty = br.sb(n), br.sb(n)
    br.align()
    return m


def read_cxform(br, alpha):
    has_add, has_mul, n = br.ub(1), br.ub(1), br.ub(4)
    k = 4 if alpha else 3
    mul = [br.sb(n) for _ in range(k)] if has_mul else [256] * k
    add = [br.sb(n) for _ in range(k)] if has_add else [0] * k
    br.align()
    if not alpha:
        mul.append(256)
        add.append(0)
    return mul, add


def cxform_bytes(cx):
    """swfCXFORMWITHALPHA: multipliers in 1/64, adds in units of 4."""
    mul, add = cx

    def s8(v):
        return max(-128, min(127, int(math.floor(v / 4.0 + 0.5))))
    return struct.pack('<8b', *([s8(v) for v in mul] + [s8(v) for v in add]))


def read_colour(br, alpha):
    r, g, b = br.u8(), br.u8(), br.u8()
    a = br.u8() if alpha else 255
    return r | (g << 8) | (b << 16) | (a << 24)


def s16c(v):
    return max(-32768, min(32767, v))


def fx88(v):
    """16.16 -> the 8.8 of a PlaceObject2's matrix."""
    return s16c(int(math.floor(v / 256.0 + 0.5)))


IDENTITY = struct.pack('<6f', 1, 0, 0, 1, 0, 0)


# -- shapes ----------------------------------------------------------------
def read_fill_styles(br, ver):
    n = br.u8()
    if n == 0xFF and ver >= 2:
        n = br.u16()
    out = []
    for _ in range(n):
        t = br.u8()
        st = {'type': t}
        if t == 0x00:
            st['colour'] = read_colour(br, ver >= 3)
        elif t in (0x10, 0x12, 0x13):
            st['matrix'] = read_matrix(br)
            br.align()
            st['spread'] = br.ub(2)
            st['interp'] = br.ub(2)
            k = br.ub(4)
            recs = []
            for _ in range(k):
                ratio = br.u8()
                recs.append((ratio, read_colour(br, ver >= 3)))
            st['records'] = recs
            if t == 0x13:
                st['focal'] = br.s16()
        elif 0x40 <= t <= 0x43:
            st['bitmap'] = br.u16()
            st['matrix'] = read_matrix(br)
        else:
            raise BakeError('fill style type %#x' % t)
        out.append(st)
    return out


def read_line_styles(br, ver):
    n = br.u8()
    if n == 0xFF and ver >= 2:
        n = br.u16()
    out = []
    for _ in range(n):
        w = br.u16()
        if ver >= 4:
            br.ub(2)
            join = br.ub(2)
            has_fill = br.ub(1)
            br.ub(1)
            br.ub(1)
            br.ub(1)
            br.ub(5)
            br.ub(1)
            br.ub(2)
            if join == 2:
                br.u16()
            if has_fill:
                fs = read_fill_styles_one(br, ver)
                col = fs.get('colour', 0xFFFFFFFF)
            else:
                col = read_colour(br, True)
        else:
            col = read_colour(br, ver >= 3)
        out.append((w, col))
    return out


def read_fill_styles_one(br, ver):
    """One FILLSTYLE (a LINESTYLE2 fill)."""
    t = br.u8()
    st = {'type': t}
    if t == 0x00:
        st['colour'] = read_colour(br, True)
    elif t in (0x10, 0x12, 0x13):
        read_matrix(br)
        br.align()
        br.ub(4)
        k = br.ub(4)
        for _ in range(k):
            br.u8()
            read_colour(br, True)
        if t == 0x13:
            br.s16()
    else:
        br.u16()
        read_matrix(br)
    return st


def flatten_quad(p0, c, p1, tol=6.0, depth=0):
    """A quadratic Bezier as points after p0 (twips), at most `tol` off."""
    mx = (p0[0] + 2 * c[0] + p1[0]) / 4.0
    my = (p0[1] + 2 * c[1] + p1[1]) / 4.0
    ex, ey = (p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0
    if depth >= 10 or (mx - ex) ** 2 + (my - ey) ** 2 <= tol * tol:
        return [p1]
    a = ((p0[0] + c[0]) / 2.0, (p0[1] + c[1]) / 2.0)
    b = ((c[0] + p1[0]) / 2.0, (c[1] + p1[1]) / 2.0)
    m = (mx, my)
    return flatten_quad(p0, a, m, tol, depth + 1) + flatten_quad(m, b, p1, tol, depth + 1)


class SwfShape(object):
    """A DefineShape* as style layers of straight edges (curves flattened):
    layers = [(fill styles, line styles, [(x0, y0, x1, y1, f0, f1, line)])]."""

    def __init__(self, body, code):
        ver = {2: 1, 22: 2, 32: 3, 83: 4, 46: 3}.get(code, 3)
        br = BitReader(body)
        self.id = br.u16()
        self.bounds = read_rect(br)
        if code == 83:
            read_rect(br)
            br.u8()
        fills, lines = read_fill_styles(br, ver), read_line_styles(br, ver)
        self.layers = [(fills, lines, [])]
        self.records(br, ver)

    def records(self, br, ver):
        nfb, nlb = br.ub(4), br.ub(4)
        edges = self.layers[-1][2]
        x = y = 0
        f0 = f1 = ln = 0
        while True:
            if br.ub(1) == 0:
                flags = br.ub(5)
                if flags == 0:
                    break
                if flags & 1:
                    n = br.ub(5)
                    x, y = br.sb(n), br.sb(n)
                v0 = br.ub(nfb) if flags & 2 else None
                v1 = br.ub(nfb) if flags & 4 else None
                vl = br.ub(nlb) if flags & 8 else None
                if flags & 16:
                    # new style arrays: the styles in use start over from 0,
                    # and the ones this record sets index the new arrays
                    fills, lines = read_fill_styles(br, ver), read_line_styles(br, ver)
                    nfb, nlb = br.ub(4), br.ub(4)
                    self.layers.append((fills, lines, []))
                    edges = self.layers[-1][2]
                    f0 = f1 = ln = 0
                if v0 is not None:
                    f0 = v0
                if v1 is not None:
                    f1 = v1
                if vl is not None:
                    ln = vl
                continue
            if br.ub(1):
                n = br.ub(4) + 2
                if br.ub(1):
                    dx, dy = br.sb(n), br.sb(n)
                elif br.ub(1):
                    dx, dy = 0, br.sb(n)
                else:
                    dx, dy = br.sb(n), 0
                edges.append((x, y, x + dx, y + dy, f0, f1, ln))
                x, y = x + dx, y + dy
            else:
                n = br.ub(4) + 2
                cdx, cdy, adx, ady = br.sb(n), br.sb(n), br.sb(n), br.sb(n)
                c = (x + cdx, y + cdy)
                p1 = (c[0] + adx, c[1] + ady)
                px, py = x, y
                for qx, qy in flatten_quad((x, y), c, p1):
                    qx, qy = int(round(qx)), int(round(qy))
                    if (qx, qy) != (px, py):
                        edges.append((px, py, qx, qy, f0, f1, ln))
                    px, py = qx, qy
                x, y = p1


def tessellate(edges):
    """The fills of one style layer as trapezoids: {fill: [points]}.

    For each fill style, the edges that have it on exactly one side bound its
    regions; a horizontal sweep fills them even-odd, which does not depend on
    which way a contour runs (Flash MX's own shapes, the SWF writer's, and
    FFDec's SVG import all wind differently). Strips are cut at every end
    point and every crossing, and a region bounded by the same two edges over
    several strips becomes one trapezoid. Each trapezoid is a fan of 4 points
    (3 when a side has no width), which is what the player draws (GS TRIFAN).
    """
    by_fill = collections.defaultdict(list)
    for x0, y0, x1, y1, f0, f1, _ln in edges:
        if y0 == y1 or f0 == f1:
            continue
        seg = (x0, y0, x1, y1) if y0 < y1 else (x1, y1, x0, y0)
        for f in (f0, f1):
            if f:
                by_fill[f].append(seg)
    out = {}
    for f, segs in by_fill.items():
        traps = _even_odd(segs)
        if traps:
            out[f] = traps
    return out


def _x_at(s, y):
    xa, ya, xb, yb = s
    return xa + (y - ya) * (xb - xa) / float(yb - ya)


def _even_odd(segs):
    """Trapezoids covering the even-odd interior of a set of edges (each with
    ya < yb)."""
    ys = set()
    for s in segs:
        ys.add(s[1])
        ys.add(s[3])
    # crossings: only pairs whose y ranges overlap are tested
    order = sorted(range(len(segs)), key=lambda i: segs[i][1])
    active = []
    for i in order:
        s = segs[i]
        active = [j for j in active if segs[j][3] > s[1]]
        for j in active:
            t = segs[j]
            lo, hi = max(s[1], t[1]), min(s[3], t[3])
            if hi <= lo:
                continue
            d0 = _x_at(s, lo) - _x_at(t, lo)
            d1 = _x_at(s, hi) - _x_at(t, hi)
            if (d0 < 0 < d1) or (d1 < 0 < d0):
                ys.add(lo + (hi - lo) * d0 / (d0 - d1))
        active.append(i)
    ys = sorted(ys)
    nxt = 0
    live = []
    open_ = {}
    traps = []

    def emit(key, top, bottom):
        L, R = segs[key[0]], segs[key[1]]
        yt, yb = int(round(top)), int(round(bottom))
        if yb <= yt:
            return
        xl0, xr0 = int(round(_x_at(L, top))), int(round(_x_at(R, top)))
        xl1, xr1 = int(round(_x_at(L, bottom))), int(round(_x_at(R, bottom)))
        if xl0 == xr0 and xl1 == xr1:
            return
        if xl0 == xr0:
            pts = [(xl0, yt), (xr1, yb), (xl1, yb)]
        elif xl1 == xr1:
            pts = [(xl0, yt), (xr0, yt), (xl1, yb)]
        else:
            pts = [(xl0, yt), (xr0, yt), (xr1, yb), (xl1, yb)]
        traps.append(pts)

    for y0, y1 in zip(ys, ys[1:]):
        if y1 - y0 < 1e-9:
            continue
        while nxt < len(order) and segs[order[nxt]][1] <= y0:
            live.append(order[nxt])
            nxt += 1
        live = [i for i in live if segs[i][3] > y0]
        ym = (y0 + y1) / 2.0
        strip = sorted((i for i in live if segs[i][1] <= y0 and segs[i][3] >= y1),
                       key=lambda i: _x_at(segs[i], ym))
        cur = set(zip(strip[0::2], strip[1::2]))
        for key in list(open_):
            if key not in cur:
                emit(key, open_.pop(key), y0)
        for key in cur:
            if key not in open_:
                open_[key] = y0
    for key, top in open_.items():
        emit(key, top, ys[-1])
    return traps


def line_paths(edges):
    """[(line style, [points])]: the stroked edges joined end to end."""
    out = []
    for x0, y0, x1, y1, _f0, _f1, ln in edges:
        if not ln:
            continue
        if out and out[-1][0] == ln and out[-1][1][-1] == (x0, y0):
            out[-1][1].append((x1, y1))
        else:
            out.append((ln, [(x0, y0), (x1, y1)]))
    return out


# -- bitmaps ---------------------------------------------------------------
def pow2_near(v, cap=512):
    """The power of two the baker scaled a bitmap side to: the nearest one,
    at most 512 (606 -> 512, 95 -> 64, 105 -> 128, 992 -> 512)."""
    p = 8                                         # gfxMipChain wants 8 at least
    while p < cap and abs(p * 2 - v) <= abs(p - v):
        p *= 2
    return min(p, cap)


ALPHA_FROM_GS = [min(255, (a * 255 + 64) // 128) for a in range(129)]
ALPHA_TO_GS = {}
for _a in range(128, -1, -1):
    ALPHA_TO_GS[ALPHA_FROM_GS[_a]] = _a


def gs_alpha(a8):
    a = ALPHA_TO_GS.get(a8)
    return a if a is not None else (a8 * 128 + 127) // 255


def clut_slot(k, n):
    """Where entry k of an n-colour CLUT is stored (CSM1: 8..15 and 16..23
    of every 32 swapped; gfxTexturePalette::SetEntry)."""
    return k if n == 16 else (k & ~0x18) | ((k >> 1) & 8) | ((k << 1) & 0x10)


def make_texture(w, h, indices, palette, fmt):
    """A Texture from row-major indices and [(r, g, b, a8)]: swizzled when the
    game would (gfxMipChain::CanSwizzle), CLUT in CSM1 order, alpha in GS
    0..0x80."""
    R = _mod('mc3_swf')
    n = 256 if fmt == 5 else 16
    pal = bytearray(4 * n)
    for k, (r, g, b, a) in enumerate(palette[:n]):
        q = clut_slot(k, n)
        pal[4 * q:4 * q + 4] = bytes((r, g, b, gs_alpha(a)))
    import numpy as np
    swz = can_swizzle(fmt, w, h)
    bpp = 8 if fmt == 5 else 4
    idx = np.frombuffer(bytes(indices), dtype=np.uint8)[:w * h]
    if fmt == 5:
        px = np.zeros(w * h, dtype=np.uint8)
        if swz:
            px[np.asarray(R.gs_unswizzle_map(w, h, 8))] = idx
        else:
            px[:] = idx
    else:
        q = np.asarray(R.gs_unswizzle_map(w, h, 4)) if swz else np.arange(w * h)
        nib = np.zeros(w * h, dtype=np.uint8)
        nib[q] = idx & 15
        px = nib[0::2] | (nib[1::2] << 4)
    t = Texture(fmt=fmt, w=w, h=h, swizzled=swz, pixels=px.tobytes(), palette=bytes(pal),
                flags=0x60000, link=None)
    t.bpp = bpp
    return t


def quantize_rgba(w, h, rgba, colours):
    """Indices and palette for an RGBA image (Pillow's octree quantizer);
    the colour of transparent texels is first bled in from their opaque
    neighbours so that bilinear filtering does not darken edges."""
    from PIL import Image
    import numpy as np
    a = np.frombuffer(rgba, dtype=np.uint8).reshape(h, w, 4).astype(np.int32).copy()
    solid = a[:, :, 3] > 0
    if solid.any() and not solid.all():
        rgb = a[:, :, :3]
        for _ in range(8):
            if solid.all():
                break
            acc = np.zeros_like(rgb)
            cnt = np.zeros((h, w), dtype=np.int32)
            for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                sh = np.roll(np.roll(solid, dy, 0), dx, 1)
                shc = np.roll(np.roll(rgb, dy, 0), dx, 1)
                acc += shc * sh[:, :, None]
                cnt += sh
            grow = (~solid) & (cnt > 0)
            rgb[grow] = acc[grow] // cnt[grow][:, None]
            solid = solid | grow
    img = Image.fromarray(a.astype(np.uint8), 'RGBA')
    q = img.quantize(colors=colours, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
    pal = q.getpalette('RGBA')[:4 * colours]
    pal += [0] * (4 * colours - len(pal))
    palette = [tuple(pal[4 * k:4 * k + 4]) for k in range(colours)]
    return bytes(q.tobytes()), palette


class SwfBitmap(object):
    """A DefineBits* as (w, h) and either indices + palette (colour-mapped,
    kept as they are) or RGBA. Colours not premultiplied."""

    def __init__(self, code, body, jpeg_tables=b''):
        self.id = struct.unpack_from('<H', body, 0)[0]
        self.indices = self.palette = self.rgba = None
        if code in (20, 36):
            self.lossless(code, body)
        else:
            self.jpeg(code, body, jpeg_tables)

    def lossless(self, code, body):
        alpha = code == 36
        fmt, w, h = struct.unpack_from('<BHH', body, 2)
        self.w, self.h = w, h
        p = 7
        if fmt == 3:
            n = body[p] + 1
            p += 1
            raw = zlib.decompress(body[p:])
            esz = 4 if alpha else 3
            pal = []
            for k in range(n):
                e = raw[esz * k:esz * k + esz]
                r, g, b = e[0], e[1], e[2]
                a = e[3] if alpha else 255
                if alpha and a and a < 255:
                    r, g, b = (min(255, (c * 255 + a // 2) // a) for c in (r, g, b))
                pal.append((r, g, b, a))
            stride = (w + 3) & ~3
            off = esz * n
            idx = bytearray()
            for y in range(h):
                idx += raw[off + y * stride:off + y * stride + w]
            self.indices, self.palette = bytes(idx), pal
            self.raw_pm = raw[:esz * n]
        elif fmt in (4, 5):
            raw = zlib.decompress(body[p:])
            out = bytearray(w * h * 4)
            if fmt == 5:
                for i in range(w * h):
                    a, r, g, b = raw[4 * i:4 * i + 4]
                    if not alpha:
                        a = 255
                    elif a and a < 255:
                        r, g, b = (min(255, (c * 255 + a // 2) // a) for c in (r, g, b))
                    out[4 * i:4 * i + 4] = bytes((r, g, b, a))
            else:
                stride = (2 * w + 3) & ~3
                for y in range(h):
                    for x in range(w):
                        v = struct.unpack_from('>H', raw, y * stride + 2 * x)[0]
                        out[4 * (y * w + x):4 * (y * w + x) + 4] = bytes((
                            ((v >> 10) & 31) << 3, ((v >> 5) & 31) << 3, (v & 31) << 3, 255))
            self.rgba = bytes(out)
        else:
            raise BakeError('bitmap %d: lossless format %d' % (self.id, fmt))

    def jpeg(self, code, body, tables):
        from PIL import Image
        import io
        p = 2
        alpha = None
        if code == 35:
            n = struct.unpack_from('<I', body, 2)[0]
            data = body[6:6 + n]
            alpha = zlib.decompress(body[6 + n:])
        else:
            data = body[p:]
        if code == 6:
            data = tables + data
        # SWF JPEGs may carry an extra EOI/SOI pair in front
        data = data.replace(b'\xff\xd9\xff\xd8', b'')
        im = Image.open(io.BytesIO(data)).convert('RGBA')
        self.w, self.h = im.size
        px = bytearray(im.tobytes())
        if alpha is not None and len(alpha) >= self.w * self.h:
            px[3::4] = alpha[:self.w * self.h]
        self.rgba = bytes(px)

    def texture(self, fmt=None):
        """The texture the baker made: the bitmap scaled to the nearest
        powers of two (at most 512), 4 bit when it is 512 wide or tall, else
        8 bit. A colour-mapped bitmap already that size keeps its indices."""
        tw, th = pow2_near(self.w), pow2_near(self.h)
        if self.indices is not None and (tw, th) == (self.w, self.h):
            n = len(self.palette)
            fmt = fmt or (6 if n <= 16 else 5)
            pal = list(self.palette) + [(0, 0, 0, 0)] * (256 - n)
            return make_texture(tw, th, self.indices, pal, fmt)
        fmt = fmt or (6 if max(tw, th) >= 512 else 5)
        rgba = self.rgba
        if rgba is None:
            rgba = b''.join(bytes(self.palette[i]) for i in self.indices)
        if (tw, th) != (self.w, self.h):
            from PIL import Image
            im = Image.frombytes('RGBA', (self.w, self.h), rgba)
            rgba = im.resize((tw, th), Image.LANCZOS).tobytes()
        idx, pal = quantize_rgba(tw, th, rgba, 256 if fmt == 5 else 16)
        return make_texture(tw, th, idx, pal, fmt)


# -- fonts -----------------------------------------------------------------
class SwfFont(object):
    """DefineFont2/3: codes, advances, metrics, and the glyph outlines (in
    1/1024 em) for sheets that have to be drawn."""

    def __init__(self, code, body):
        br = BitReader(body)
        self.id = br.u16()
        flags = br.u8()
        br.u8()
        self.name = br.raw(br.u8())
        n = br.u16()
        self.count = n
        wide_off, wide_codes, layout = flags & 0x08, flags & 0x04, flags & 0x80
        base = br.pos
        offs = [br.u32() if wide_off else br.u16() for _ in range(n)]
        code_off = br.u32() if wide_off else br.u16()
        scale = 1.0 / 20.0 if code == 75 else 1.0
        self.glyphs = []
        for k in range(n):
            end = offs[k + 1] if k + 1 < n else code_off
            self.glyphs.append(self.glyph(body[base + offs[k]:base + end], scale))
        br = BitReader(body, base + code_off)
        self.codes = [br.u16() if wide_codes else br.u8() for _ in range(n)]
        self.ascent = self.descent = self.leading = 0
        self.advances = None
        if layout:
            self.ascent, self.descent, self.leading = br.s16(), br.s16(), br.s16()
            self.advances = [max(0, min(0xFFFF, br.s16())) for _ in range(n)]

    @staticmethod
    def glyph(data, scale):
        if not data:
            return []
        br = BitReader(data)
        sh = SwfShape.__new__(SwfShape)
        sh.layers = [([{'type': 0, 'colour': 0xFFFFFFFF}], [], [])]
        try:
            sh.records(br, 1)
        except BakeError:
            return []
        edges = sh.layers[0][2]
        if scale != 1.0:
            edges = [(x0 * scale, y0 * scale, x1 * scale, y1 * scale, f0, f1, ln)
                     for x0, y0, x1, y1, f0, f1, ln in edges]
        return edges

    def ascii(self):
        out = bytearray(128)
        for g, c in enumerate(self.codes):
            if c < 128 and out[c] == 0:
                out[c] = g
        return bytes(out)


class FromSwf(object):
    """A SWF into the model the Builder writes.

    Character ids are object-table indices (what mc3_swf writes); the tags
    are taken in their order, so the objects are allocated in the order the
    baker met them. Where the SWF carries a mc3_pck_meta block written with
    it (`mc3_swf.py swf`), every object whose tag is unchanged is rebuilt
    from it exactly: the CLUT before premultiplication, the fans and float
    matrices of the shapes, the glyph sheets of the fonts. An edited tag (its
    hash no longer matches) is compiled from what the SWF says."""

    def __init__(self, data, name='?', pck_version=None, base=None):
        self.name = name
        self.R = _mod('mc3_swf')
        sig = data[:3]
        if sig == b'CWS':
            body = zlib.decompress(data[8:])
        elif sig == b'FWS':
            body = data[8:]
        else:
            raise BakeError('%s: not a SWF (%r)' % (name, sig))
        self.version = data[3]
        br = BitReader(body)
        self.frame_rect = read_rect(br)
        self.rate = br.u16()
        self.nframes = br.u16()
        self.tags = self.R._walk(body, br.pos)
        # Read the optional movie suffix before parsing commands or objects.
        # Old meta blocks still default to alpha, as did all earlier releases.
        binary, exports = {}, {}
        for code, tag in self.tags:
            if code == self.R.T_BINARY:
                binary[struct.unpack_from('<H', tag)[0]] = tag[6:]
            elif code == self.R.T_EXPORT:
                r = BitReader(tag)
                for _ in range(r.u16()):
                    cid = r.u16()
                    exports[r.string().decode('ascii', 'replace')] = cid
        meta = self.R.read_meta(binary.get(exports.get(self.R.META_NAME), b''))
        self.clip_key_meta = {}
        for (kind, owner), payload in meta.items():
            if kind != self.R.M_CLIP_KEYS:
                continue
            pos = 2
            for _ in range(struct.unpack_from('<H', payload)[0]):
                frame, command, count = struct.unpack_from('<HHH', payload, pos)
                pos += 6
                digest = payload[pos:pos + 8]
                pos += 8
                keys = struct.unpack_from('<%dI' % count, payload, pos)
                pos += 4 * count
                self.clip_key_meta[(owner or 0, frame, command)] = (digest, keys)
        movie = meta.get((self.R.M_MOVIE, 0), b'')
        version, saved_base, self.flag = struct.unpack_from('<3I', movie, 6) if len(movie) >= 18 else (5, BASE, 1)
        self.pck_version = version if pck_version is None else pck_version
        self.base = saved_base if base is None else base
        self.vt, self.mip_link_first, self.edittext_no_text = baker(self.pck_version)
        self.stats = collections.Counter()
        self.warn = collections.Counter()

    # -- helpers ---------------------------------------------------------
    def action(self, code):
        a = self.actions.get(code)
        if a is None:
            a = self.actions[code] = Obj(refcount=0, code=code)
        a.refcount += 1
        return a

    def meta_for(self, kind, cid, body):
        """The meta payload after its hash, if the record is there and its
        hash is the tag's own."""
        pay = self.meta.get((kind, cid))
        if pay is None:
            return None
        if pay[:8] != self.R.tag_hash(body):
            label = {1: 'bitmap', 2: 'shape', 3: 'font', 5: 'fill types', 6: 'button'}.get(kind, str(kind))
            self.stats['edited since written (%s)' % label] += 1
            return None
        return pay[8:]

    # -- timeline --------------------------------------------------------
    def place(self, body, code):
        br = BitReader(body)
        flags = br.u8()
        if code == 70:
            flags2 = br.u8()
        depth = br.u16()
        if code == 70 and flags2 & 0x08:
            br.string()                       # class name: nothing to bind it to
            self.warn['PlaceObject3 class name ignored'] += 1
        char = br.u16() if flags & 0x02 else 0xFFFF
        m = read_matrix(br) if flags & 0x04 else None
        cx = read_cxform(br, True) if flags & 0x08 else None
        if flags & 0x10:
            br.u16()
            self.warn['ratio ignored (the player has no morph)'] += 1
        name = br.string() if flags & 0x20 else None
        if flags & 0x40:
            br.u16()
            self.warn['clip depth ignored (the player has no mask)'] += 1
        if code == 70 and flags2 & 0x07:
            self.warn['PlaceObject3 filters/blend ignored'] += 1
        events = None
        if flags & 0x80:
            br.u16()
            wide = self.version >= 6
            br.u32() if wide else br.u16()
            events = []
            while True:
                ef = br.u32() if wide else br.u16()
                if ef == 0:
                    break
                size = br.u32()
                key = 0
                if ef & (1 << 17):
                    key = br.u8()
                    size -= 1
                events.append((ef, self.action(br.raw(size)), key))
        kind = 1 if (name is not None or events is not None) else 0
        c = Obj(kind=kind, flags=0, pad=b'\xcd\xcd', vt=self.vt['PLACE1' if kind else 'PLACE0'],
                depth=depth, char=char, mat=None, cx=None)
        if m is not None:
            vals = []
            if m.has_scale:
                c.flags |= 1
                vals += [fx88(m.sx), fx88(m.sy)]
            if m.has_rot:
                c.flags |= 2
                vals += [fx88(m.r0), fx88(m.r1)]
            vals += [s16c(m.tx), s16c(m.ty)]
            c.mat = vals
        else:
            c.flags = CD          # the baker sets the flags with the matrix, else never
        if cx is not None:
            c.cx = cxform_bytes(cx)
        if kind:
            c.name = name
            c.events = events
            c.nevents = len(events) if events is not None else 0
            c.event_flags = 0
            for ef, _a, _k in events or ():
                c.event_flags |= ef
        return c

    def timeline(self, tags, owner):
        """[Frame], and for the root the (frame, command) order of the tags."""
        frames = [Obj(word=0, commands=[])]
        steps = []
        for code, body in tags:
            fr = frames[-1]
            if code in (26, 70):
                c = self.place(body, code)
                saved = self.clip_key_meta.get((owner or 0, len(frames) - 1, len(fr.commands)))
                if saved and saved[0] == self.R.tag_hash(body) and c.events is not None and len(c.events) == len(saved[1]):
                    c.events = [(f, act, key) for (f, act, _old), key in zip(c.events, saved[1])]
                    self.stats['clip key words exact (meta)'] += len(saved[1])
                fr.commands.append(c)
                steps.append((len(frames) - 1, len(fr.commands) - 1))
            elif code in (28, 5):
                depth = struct.unpack_from('<H', body, 0 if code == 28 else 2)[0]
                fr.commands.append(Obj(kind=2, pad=b'\xcd', depth=depth, vt=self.vt['REMOVE']))
                steps.append((len(frames) - 1, len(fr.commands) - 1))
            elif code == 12:
                fr.commands.append(Obj(kind=3, vt=self.vt['DOACTION'], action=self.action(bytes(body))))
                steps.append((len(frames) - 1, len(fr.commands) - 1))
            elif code == 1:
                if owner is None:
                    fr.word = self.background
                frames.append(Obj(word=0, commands=[]))
            elif code == 9 and owner is None:
                r, g, b = body[0], body[1], body[2]
                self.background = r | (g << 8) | (b << 16) | 0xFF000000
            elif code == 43:
                self.warn['frame label ignored'] += 1
            elif code == 0:
                break
            else:
                yield_def = self.define(code, body)
                if yield_def is not None:
                    steps.append(('obj', yield_def))
        if not frames[-1].commands and len(frames) > 1:
            frames.pop()
        return frames, steps

    # -- definitions -----------------------------------------------------
    def define(self, code, body):
        """Turns a definition tag into a model object; returns its id when it
        is one, None when the tag is consumed some other way or ignored."""
        cid = struct.unpack_from('<H', body, 0)[0] if len(body) >= 2 else 0
        if code in (2, 22, 32, 83):
            self.pending_shapes.append((code, body))
            self.shape_bodies[cid] = (code, body)
            return cid
        if code in (20, 36, 21, 35, 6):
            self.bitmaps[cid] = (code, body)
            return cid
        if code == 8:
            self.jpeg_tables = body
            return None
        if code in (48, 75):
            self.fonts[cid] = (code, body)
            return cid
        if code in (11, 33):
            self.texts[cid] = (code, body)
            return cid
        if code == 37:
            self.edits[cid] = body
            return cid
        if code in (34, 7):
            self.buttons[cid] = (code, body)
            return cid
        if code == 39:
            self.sprites[cid] = body
            return cid
        if code == 14:
            self.sounds.add(cid)
            return cid
        if code == 59:
            self.init_actions.append((cid, bytes(body[2:])))
            return None
        if code == 56:
            br = BitReader(body)
            for _ in range(br.u16()):
                i = br.u16()
                self.exports[br.string().decode('latin-1')] = i
            return None
        if code == 87:
            self.binary[cid] = bytes(body[6:])
            return None
        if code in (24, 64, 65, 69, 77, 88, 41, 63, 13, 62, 10, 73, 74, 78, 86):
            return None                          # protection, metadata, font info, ...
        if code in (15, 18, 19, 45, 60):
            self.warn['sound/video tag %d ignored' % code] += 1
            return None
        self.warn['tag %d ignored' % code] += 1
        return None

    def model(self):
        R = self.R
        self.actions = {}
        self.bitmaps, self.fonts, self.texts, self.edits = {}, {}, {}, {}
        self.buttons, self.sprites, self.sounds = {}, {}, set()
        self.shape_bodies, self.pending_shapes = {}, []
        self.exports, self.binary, self.init_actions = {}, {}, []
        self.jpeg_tables = b''
        self.background = 0xFFFFFFFF
        frames, steps = self.timeline(self.tags, None)
        mid = self.exports.get(R.META_NAME)
        self.meta = R.read_meta(self.binary[mid]) if mid in self.binary else {}
        if self.meta:
            self.stats['meta block'] += 1

        # what the font meta says the sheet bitmaps are
        sheet_bitmaps = set()
        font_meta = {}
        for fid, (code, body) in self.fonts.items():
            pay = self.meta_for(R.M_FONT, fid, body)
            if pay is not None:
                font_meta[fid] = self.read_font_meta(pay)
                for s in font_meta[fid][4]:
                    sheet_bitmaps.update(s['cids'])
        # the sheet bitmaps mc3_swf exports are font data, not objects, meta or not
        for nm, cid in self.exports.items():
            if re.match(r'font\d+_sheet\d+_size-?\d+_tex\d+$', nm):
                sheet_bitmaps.add(cid)
        defined = set(self.shape_bodies) | set(self.bitmaps) | set(self.fonts) | set(self.texts) | \
            set(self.edits) | set(self.buttons) | set(self.sprites) | self.sounds
        defined -= sheet_bitmaps
        mv = self.meta.get((R.M_MOVIE, 0))
        if mv is not None:
            nobj, table_zero = struct.unpack_from('<HI', mv, 0)
        else:
            nobj, table_zero = (max(defined) + 1 if defined else 1), 0
        m = Obj(base=self.base, version=self.pck_version, flag=self.flag, vt=self.vt['FILE'], swf_version=self.version, rate=self.rate,
                table_zero=table_zero)
        x0, x1, y0, y1 = self.frame_rect
        m.rect = struct.pack('<4f', x0 / 20.0, x1 / 20.0, y0 / 20.0, y1 / 20.0)
        m.objects = [None] * nobj
        self.m = m
        self.textures = {}
        # objects, in tag order
        first = {}
        for i, st in enumerate(steps):
            if st[0] == 'obj':
                first.setdefault(st[1], i)
        for cid in sorted(defined, key=lambda c: first.get(c, len(steps))):
            if cid >= nobj:
                self.warn['character %d beyond the object table' % cid] += 1
                continue
            m.objects[cid] = self.make(cid, font_meta)
        for sid, code in self.init_actions:
            sp = m.objects[sid] if sid < nobj else None
            if sp is not None and sp.kind == 2 and sp.frames:
                sp.frames[0].commands.insert(0, Obj(kind=4, vt=self.vt['DOINIT'], action=self.action(code)))
            else:
                self.warn['DoInitAction for %d dropped' % sid] += 1
        while len(frames) < self.nframes:
            frames.append(Obj(word=self.background, commands=[]))
        for fr in frames:
            fr.word = fr.word or self.background
        m.frames = frames[:max(self.nframes, 1)]
        self.sheets_by_size(m, font_meta)
        m.order = []
        for st in steps:
            if st[0] == 'obj':
                if st[1] < nobj and m.objects[st[1]] is not None:
                    m.order.append(('obj', st[1]))
            elif st[0] < len(m.frames):
                m.order.append(('cmd', st[0], st[1]))
        return m

    def make(self, cid, font_meta):
        if cid in self.shape_bodies:
            return self.shape(cid, *self.shape_bodies[cid])
        if cid in self.bitmaps:
            return self.bitmap(cid)
        if cid in self.fonts:
            return self.font(cid, font_meta.get(cid))
        if cid in self.texts:
            return self.text(cid, *self.texts[cid])
        if cid in self.edits:
            return self.edittext(cid, self.edits[cid])
        if cid in self.buttons:
            return self.button(cid, *self.buttons[cid])
        if cid in self.sprites:
            return self.sprite(cid, self.sprites[cid])
        ob = Obj(kind=8, vt=self.vt['SOUND'])
        return ob

    # -- objects ---------------------------------------------------------
    def texture_of(self, cid):
        t = self.textures.get(cid)
        if t is not None:
            return t
        code, body = self.bitmaps[cid]
        bm = SwfBitmap(code, body, self.jpeg_tables)
        pay = self.meta_for(_mod('mc3_swf').M_BITMAP, cid, body)
        t = bm.texture()
        if pay is not None and bm.indices is not None:
            pal32, n = struct.unpack_from('<BH', pay, 0)
            esz = 4 if pal32 else 2
            raw = pay[3:3 + esz * n]
            if pal32 and n == len(t.palette) // 4:
                t.palette = bytes(raw)
                self.stats['bitmaps exact (meta)'] += 1
            p = 3 + esz * n
            if pay[p]:
                t.inv = pay[p + 1:p + 9]
        else:
            self.stats['bitmaps converted'] += 1
        t.swf_size = (bm.w, bm.h)
        self.textures[cid] = t
        return t

    def bitmap(self, cid):
        t = self.texture_of(cid)
        inv = getattr(t, 'inv', None)
        if inv is None:
            w, h = t.swf_size
            inv = struct.pack('<2f', trunc32(1.0 / w), trunc32(1.0 / h))
        return Obj(kind=4, vt=self.vt['BITMAP'], tw=t.w, th=t.h, inv=inv, tex=t)

    def fill_style(self, st):
        t = st['type']
        f = Obj(type=t, colour=0xFFFFFFFF, mat=IDENTITY, bitmap=None, gradient=None)
        if t == 0:
            f.colour = st['colour']
        elif t in (0x10, 0x12, 0x13):
            M = self.R.Matrix(*st['matrix'].floats(1.0)).inverse() or self.R.Matrix()
            recs = st['records']
            f.gradient = Obj(mat=struct.pack('<6f', *(trunc32(v) for v in M.tuple())), count=len(recs),
                             radial=0 if t == 0x10 else 1, pad=b'\xcd\xcd',
                             ratios=bytes(r for r, _c in recs), colours=[c for _r, c in recs])
        else:
            # twips -> pixels, the inverse of the SWF matrix (bitmap texels ->
            # shape), then texels -> S,T. The "no bitmap" fill Flash MX leaves
            # in every shape (id 0xFFFF) went through the same sum as a 1x1
            # bitmap: (20 0 0 20 0 0) in all the alpha's files
            bid = st['bitmap']
            bw = bh = 1
            if bid != 0xFFFF and bid in self.bitmaps and self.m.objects[bid] is not None:
                f.bitmap = bid
                bw, bh = self.textures[bid].swf_size
            elif bid != 0xFFFF:
                self.warn['bitmap fill of a missing bitmap'] += 1
            Mx = self.R.Matrix
            inv = Mx(*st['matrix'].floats(1.0)).inverse() or Mx()
            F = Mx(20, 0, 0, 20, 0, 0).dot(inv).dot(Mx(1.0 / bw, 0, 0, 1.0 / bh, 0, 0))
            f.mat = struct.pack('<6f', *(trunc32(v) for v in F.tuple()))
        return f

    def shape(self, cid, code, body):
        sh = SwfShape(body, code)
        ob = Obj(kind=1, vt=self.vt['SHAPE'])
        # one fill array and one line array for the whole shape: the style
        # arrays of the layers are concatenated, identical ones shared
        fills, lines, fmaps, lmaps = [], [], [], []
        seen_f, seen_l = {}, {}
        for fs, ls, _e in sh.layers:
            key = repr(fs)
            if key not in seen_f:
                seen_f[key] = len(fills)
                fills += fs
            fmaps.append(seen_f[key])
            key = repr(ls)
            if key not in seen_l:
                seen_l[key] = len(lines)
                lines += ls
            lmaps.append(seen_l[key])
        ob.fills = [self.fill_style(st) for st in fills]
        ob.lines = [(w, 0, col) for w, col in lines]
        pay = self.meta_for(_mod('mc3_swf').M_SHAPE, cid, body)
        if pay is not None:
            flags, nf, nl, dn = struct.unpack_from('<BHHI', pay, 0)
            p = 9
            ob.dlist = pay[p:p + dn]
            p += dn
            ob.fills, ob.lines = ob.fills[:nf], ob.lines[:nl]
            for f in ob.fills:
                f.mat = pay[p:p + 24]
                has_g = pay[p + 24]
                p += 25
                if has_g:
                    if f.gradient is not None:
                        f.gradient.mat = pay[p:p + 24]
                    p += 24
            ob.fills_present, ob.lines_present = bool(flags & 1), bool(flags & 2)
            types = self.meta_for(self.R.M_FILL_TYPES, cid, body)
            if types is not None:
                for f, raw_type in zip(ob.fills, struct.unpack('<%dI' % len(ob.fills), types)):
                    f.type = raw_type
            self.stats['shapes exact (meta)'] += 1
            return ob
        dl = []
        for (fs, ls, edges), fo, lo in zip(sh.layers, fmaps, lmaps):
            regions = tessellate(edges)
            for f in sorted(regions):
                if f > len(fs):
                    continue
                dl += [4, fo + f]
                for pts in regions[f]:
                    dl += [2, len(pts)]
                    for x, y in pts:
                        dl += [x & 0xFFFF, y & 0xFFFF]
            for ln, pts in line_paths(edges):
                if ln > len(ls):
                    continue
                dl += [5, lo + ln, 1, len(pts)]
                for x, y in pts:
                    dl += [int(round(x)) & 0xFFFF, int(round(y)) & 0xFFFF]
        dl.append(0)
        ob.dlist = struct.pack('<%dH' % len(dl), *dl)
        ob.fills_present, ob.lines_present = bool(ob.fills), bool(ob.lines)
        self.stats['shapes tessellated'] += 1
        return ob

    def sprite(self, cid, body):
        nf = struct.unpack_from('<H', body, 2)[0]
        frames, _steps = self.timeline(self.R._walk(body, 4), cid)
        while len(frames) < nf:
            frames.append(Obj(word=0, commands=[]))
        return Obj(kind=2, vt=self.vt['SPRITE'], frames=frames[:nf])

    def button(self, cid, code, body):
        br = BitReader(body)
        br.u16()
        ob = Obj(kind=3, vt=self.vt['BUTTON'], records=[], conds=[])
        if code == 34:
            ob.byte8 = br.u8() & 1
            aoff = br.u16()
            start = br.pos
        else:
            ob.byte8 = 0
        while True:
            fl = br.u8()
            if fl == 0:
                break
            ch, depth = br.u16(), br.u16()
            m = read_matrix(br)
            cx = read_cxform(br, True) if code == 34 else ([256] * 4, [0] * 4)
            if fl & 0x10:
                raise BakeError('%s: button %d carries filters (SWF 8), which the player '
                                'cannot draw' % (self.name, cid))
            if fl & 0x20:
                br.u8()
                self.warn['button blend mode ignored'] += 1
            ob.records.append(Obj(states=fl & 0x0F, pad=None, depth=depth, mat=m.pck_floats(),
                                  cx=cxform_bytes(cx), char=ch))
        if code == 34:
            if aoff:
                p = start - 2 + aoff
                while True:
                    size, cond = struct.unpack_from('<HH', body, p)
                    end = p + size if size else len(body)
                    ob.conds.append((cond, self.action(bytes(body[p + 4:end])), None))
                    if not size:
                        break
                    p = end
        else:
            ob.conds.append((0x08, self.action(br.rest()), None))
        ob.records_present = True
        ob.conds_present = bool(ob.conds)
        pay = self.meta_for(self.R.M_BUTTON, cid, body)
        if pay is not None and struct.unpack_from('<H', pay)[0] == len(ob.records):
            for i, rec in enumerate(ob.records):
                rec.states = pay[2 + 25 * i]
                rec.mat = pay[3 + 25 * i:27 + 25 * i]
            self.stats['button matrices exact (meta)'] += len(ob.records)
        return ob

    def text(self, cid, code, body):
        br = BitReader(body)
        br.u16()
        read_rect(br)
        m = read_matrix(br)
        gb, ab = br.u8(), br.u8()
        ops = []
        needs = []
        while True:
            fl = br.u8()
            if fl == 0:
                break
            font = colour = x = y = height = None
            if fl & 0x08:
                font = br.u16()
            if fl & 0x04:
                colour = read_colour(br, code == 33)
            if fl & 0x01:
                x = br.s16()
            if fl & 0x02:
                y = br.s16()
            if fl & 0x08:
                height = br.u16()
            n = br.u8()
            glyphs = [(br.ub(gb), br.sb(ab)) for _ in range(n)]
            br.align()
            # the baker's order: colour, font, x, y, glyphs
            if colour is not None:
                ops += [2, colour & 0xFFFF, colour >> 16]
            if font is not None:
                ops += [1, font, height]
                if (font, height) not in needs:
                    needs.append((font, height))
            if x is not None:
                ops += [4, x & 0xFFFF]
            if y is not None:
                ops += [3, y & 0xFFFF]
            ops += [5, n]
            for g, a in glyphs:
                ops += [g, a & 0xFFFF]
        ops.append(0)
        return Obj(kind=6, vt=self.vt['TEXT'], mat=m.pck_floats(),
                   records=struct.pack('<%dH' % len(ops), *ops), sheet_needs=needs)

    def edittext(self, cid, body):
        R = self.R
        br = BitReader(body)
        br.u16()
        x0, x1, y0, y1 = read_rect(br)
        f1, f2 = br.u8(), br.u8()
        font = height = 0
        colour = 0xFF000000
        align = 0
        leading = 0
        if f1 & 0x01:
            font = br.u16()
        if f2 & 0x80:
            br.string()
            self.warn['EditText font class ignored'] += 1
        if f1 & 0x01:
            height = br.u16()
        if f1 & 0x04:
            colour = read_colour(br, True)
        if f1 & 0x02:
            br.u16()
        if f2 & 0x20:
            align = br.u8()
            br.u16()
            br.u16()
            br.u16()
            leading = br.s16()
        var = br.string()
        text = br.string() if f1 & 0x80 else None
        if f2 & 0x02:
            self.warn['EditText HTML shown as plain text'] += 1
        ob = Obj(kind=7, vt=self.vt['EDITTEXT'], text=text, var=var, font=font, height=height,
                 colour=colour, align=align, text_word=self.edittext_no_text,
                 textlen=len(text) + 1 if text is not None else 0)
        bits = 32 if self.pck_version == 6 else 16
        ob.xmin, ob.ymin = R.edit_units(x0, height, bits), R.edit_units(y0, height, bits)
        ob.bw, ob.bh = R.edit_units(x1 - x0, height, bits), R.edit_units(y1 - y0, height, bits)
        ob.leading = R.edit_units(leading, height)
        ob.sheet_needs = [(font, height)]
        return ob

    def read_font_meta(self, pay):
        adv_present, asc, desc, lead, ns = struct.unpack_from('<B3hB', pay, 0)
        p = 8
        sheets = []
        for _ in range(ns):
            size, count, has_ti, nt = struct.unpack_from('<hHBB', pay, p)
            p += 6
            rects = pay[p:p + 12 * count]
            p += 12 * count
            ti = None
            if has_ti:
                ti = pay[p:p + count]
                p += count
            cids = list(struct.unpack_from('<%dH' % nt, pay, p))
            p += 2 * nt
            sheets.append({'size': size, 'count': count, 'rects': rects, 'texindex': ti, 'cids': cids})
        return adv_present, asc, desc, lead, sheets

    def font(self, cid, meta):
        code, body = self.fonts[cid]
        sf = SwfFont(code, body)
        ob = Obj(kind=5, vt=self.vt['FONT'], count=sf.count, glyph_table=None, codes=sf.codes,
                 advances=sf.advances, ascii=sf.ascii(), ascent=sf.ascent, descent=sf.descent,
                 leading=sf.leading, sheets=[])
        ob.swf = sf
        if meta is not None:
            adv_present, ob.ascent, ob.descent, ob.leading, sheets = meta
            if not adv_present:
                ob.advances = None
            for s in sheets:
                sh = Obj(lazy=True, size=s['size'], count=s['count'], rects=s['rects'],
                         texindex=s['texindex'], textures=[self.texture_of(c) for c in s['cids']])
                ob.sheets.append(sh)
            self.stats['fonts exact (meta)'] += 1
        else:
            self.stats['fonts from outlines'] += 1
        return ob

    def sheets_by_size(self, m, font_meta):
        """Every (font, height) a text uses needs a sheet of that size."""
        need = collections.OrderedDict()
        for ob in m.objects:
            if ob is not None and ob.kind in (6, 7):
                for f, h in ob.sheet_needs:
                    need.setdefault((f, h), True)
        for (f, h) in need:
            ft = m.objects[f] if f < len(m.objects) else None
            if ft is None or ft.kind != 5:
                raise BakeError('%s: a text uses font %d, which is not a font' % (self.name, f))
            if any(s.size == h for s in ft.sheets):
                continue
            ft.sheets.append(rasterize_sheet(ft, h))
            self.stats['font sheets drawn'] += 1
        # a sheet is made by the first text that needs it, as the baker did
        for k, ob in enumerate(m.objects):
            if ob is not None and ob.kind == 5:
                for sh in ob.sheets:
                    sh.lazy = (k, sh.size) in need


def glyph_levels(edges, s, x0t, y0t, w, h, ss=4):
    """Coverage of one glyph in 16 levels over a w x h texel box: nonzero
    winding, ss x ss samples per texel. `edges` in 1/1024 em, s = texels
    per em unit, (x0t, y0t) the box corner in texels. Every sample row of
    every edge is crossed at once (numpy), the winding is a running sum per
    row, and the spans go in through a difference array."""
    import numpy as np
    W, H = w * ss, h * ss
    e = np.array([((ax * s - x0t) * ss, (ay * s - y0t) * ss, (bx * s - x0t) * ss, (by * s - y0t) * ss)
                  for ax, ay, bx, by, _f0, _f1, _ln in edges if ay != by], dtype=np.float64)
    if not len(e):
        return np.zeros((h, w), dtype=np.uint8)
    ax, ay, bx, by = e.T
    # sample row r (centre r + 0.5) crosses an edge when ylo <= r + 0.5 < yhi
    r0 = np.clip(np.ceil(np.minimum(ay, by) - 0.5), 0, H).astype(np.int64)
    r1 = np.clip(np.ceil(np.maximum(ay, by) - 0.5), 0, H).astype(np.int64)
    n = np.maximum(r1 - r0, 0)
    if not n.sum():
        return np.zeros((h, w), dtype=np.uint8)
    idx = np.repeat(np.arange(len(e)), n)
    rows = np.repeat(r0, n) + (np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n))
    yc = rows + 0.5
    x = ax[idx] + (yc - ay[idx]) * (bx[idx] - ax[idx]) / (by[idx] - ay[idx])
    d = np.where(by[idx] > ay[idx], 1, -1)
    order = np.lexsort((d, x, rows))
    rows, x, d = rows[order], x[order], d[order]
    first = np.r_[True, rows[1:] != rows[:-1]]
    start = np.maximum.accumulate(np.where(first, np.arange(len(rows)), 0))
    cum = np.cumsum(d)
    wind = cum - (cum[start] - d[start])
    span = (wind[:-1] != 0) & (rows[:-1] == rows[1:])
    c0 = np.clip(np.ceil(x[:-1][span] - 0.5), 0, W).astype(np.int64)
    c1 = np.clip(np.ceil(x[1:][span] - 0.5), 0, W).astype(np.int64)
    rr = rows[:-1][span]
    keep = c1 > c0
    diff = np.zeros((H, W + 1), dtype=np.int32)
    np.add.at(diff, (rr[keep], c0[keep]), 1)
    np.add.at(diff, (rr[keep], c1[keep]), -1)
    cov = (np.cumsum(diff, axis=1)[:, :W] > 0).astype(np.float32)
    c = cov.reshape(h, ss, w, ss).mean(axis=(1, 3))
    return np.clip(np.round(c * 15), 0, 15).astype(np.uint8)


def rasterize_sheet(ft, size):
    """A swfFONT::SHEET for `size` twips, drawn from the font's outlines: one
    texel per screen pixel, glyphs packed in rows with a texel between them
    on 128x128 4-bit textures (swfFONT::SHEET::DrawGlyph divides by 128),
    white with the coverage in the alpha - as the baker's own sheets are."""
    import numpy as np
    sf = ft.swf
    s = size / 20.0 / 1024.0
    boxes = []
    for edges in sf.glyphs:
        if not edges:
            boxes.append(None)
            continue
        xs = [e[0] for e in edges] + [e[2] for e in edges]
        ys = [e[1] for e in edges] + [e[3] for e in edges]
        boxes.append((min(xs), min(ys), max(xs), max(ys)))
    biggest = max([max(b[2] - b[0], b[3] - b[1]) for b in boxes if b] or [1])
    if biggest * s > 120:
        s = 120.0 / biggest                      # glyphs bigger than a sheet: fewer texels
    texs = [np.zeros((128, 128), dtype=np.uint8)]
    tex_of = []
    rects = bytearray()
    u = v = rowh = 0
    for g, b in enumerate(boxes):
        if b is None:
            rects += struct.pack('<4B4h', 0, 0, 0, 0, 0, 0, 0, 0)
            tex_of.append(0)
            continue
        x0t, y0t = int(math.floor(b[0] * s)) - 1, int(math.floor(b[1] * s)) - 1
        x1t, y1t = int(math.ceil(b[2] * s)) + 1, int(math.ceil(b[3] * s)) + 1
        w, h = x1t - x0t, y1t - y0t
        if u + w > 128:
            u, v, rowh = 0, v + rowh + 1, 0
        if v + h > 128:
            texs.append(np.zeros((128, 128), dtype=np.uint8))
            u = v = rowh = 0
        texs[-1][v:v + h, u:u + w] = glyph_levels(sf.glyphs[g], s, x0t, y0t, w, h)
        rects += struct.pack('<4B4h', u, v, w, h, s16c(int(round(x0t / s))), s16c(int(round(y0t / s))),
                             s16c(int(round(x1t / s))), s16c(int(round(y1t / s))))
        tex_of.append(len(texs) - 1)
        u += w + 1
        rowh = max(rowh, h)
    ramp = [(255, 255, 255, (k * 255 + 7) // 15) for k in range(16)]
    textures = [make_texture(128, 128, bytes(t.reshape(-1)), ramp, 6) for t in texs]
    return Obj(lazy=True, size=size, count=len(boxes), rects=bytes(rects), textures=textures,
               texindex=bytes(tex_of) if len(texs) > 1 else None)


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------
def _inputs(paths, ext):
    out = []
    for p in paths:
        if os.path.isdir(p):
            out += sorted(os.path.join(p, f) for f in os.listdir(p) if f.lower().endswith(ext))
        else:
            out.append(p)
    return out


def source_order(m):
    """Definitions and root commands in the order their first block sits in
    the source file - the order the baker met them in the SWF."""
    items = []
    for k, ob in enumerate(m.objects):
        if ob is not None:
            items.append((ob.src['self'], ('obj', k)))
    for k, fr in enumerate(m.frames):
        for i, c in enumerate(fr.commands):
            items.append((c.src['self'], ('cmd', k, i)))
    items.sort()
    return [it for _o, it in items]


def diff_report(a, b, blocks, limit=6):
    """Ranges where two images differ, each with the block that covers it."""
    n = min(len(a), len(b))
    runs = []
    i = 0
    while i < n:
        if a[i] == b[i]:
            i += 1
            continue
        j = i
        while j < n and a[j] != b[j]:
            j += 1
        runs.append((i, j - i))
        i = j
    out = []
    for o, ln in runs[:limit]:
        va = o - HEADER + struct.unpack_from('<I', a)[0]
        owner = '?'
        for bl in blocks:
            if bl.addr is not None and bl.addr <= va < bl.addr + len(bl.data):
                owner = '%s+%#x' % (bl.kind, va - bl.addr)
                break
        out.append('%#x+%d (%s): got %s want %s' % (o, ln, owner, b[o:o + min(ln, 8)].hex(),
                                                 a[o:o + min(ln, 8)].hex()))
    return runs, out


def cmd_roundtrip(a):
    files = _inputs(a.files, '.pck')
    same = 0
    kinds = collections.Counter()
    for path in files:
        data = open(path, 'rb').read()
        name = os.path.basename(path)
        try:
            fp = FromPck(data, name)
            m = fp.model()
            if a.layout == 'source':
                m.order = source_order(m)
                bld = Builder(m)
                out = bld.image('source', size=len(data) - HEADER)
            else:
                m.order = source_order(m)
                bld = Builder(m)
                out = bld.image('packed')
        except (BakeError, Exception) as e:
            if not isinstance(e, BakeError) and a.raise_errors:
                raise
            print('   FAIL %-30s %s: %s' % (name, type(e).__name__, e))
            continue
        if a.layout == 'source':
            if out == data:
                same += 1
                if a.verbose:
                    print('   same %s' % name)
                continue
            runs, rep = diff_report(data, out, bld.h.blocks)
            for r in rep:
                kinds[r.split('(')[1].split('+')[0]] += 1
            print('   DIFF %-30s %d run(s), %d byte(s)%s' % (name, len(runs), sum(r[1] for r in runs),
                  '' if len(out) == len(data) else ', size %d vs %d' % (len(out), len(data))))
            for r in rep:
                print('        ' + r)
        else:
            holes = check_image(out, name)
            bad, ex = compare(m, FromPck(out, name).model())
            ok = not bad and not holes
            same += ok
            if not ok or a.verbose:
                print('   %-30s %8d -> %8d bytes  %s%s' % (name, len(data), len(out),
                      'same movie' if not bad else 'DIFFERS: %s' % dict(bad),
                      ', %d unexplained byte(s)' % holes if holes else ''))
                for e in ex:
                    print('        ' + e)
    print('-- %d of %d file(s) %s' % (same, len(files),
          'rebuilt byte for byte' if a.layout == 'source' else 'rebuilt and read back the same'))
    if kinds:
        print('   differences by block: %s' % dict(kinds))
    return 0 if same == len(files) else 1


def canon(m, runtime_keys=False):
    """The model as nested tuples, without what the allocator decides (the
    offsets) and without the words nothing reads: the vtables (constructors
    overwrite them), gfxMipChain +04, the font glyph table (swfFONT zeroes
    +0C), the stack bytes of button records and conditions, an EditText's +08
    when it has no text. Two models with the same canon() are the same movie
    to the player."""
    def act(a):
        return None if a is None else (a.refcount, a.code)

    def cmd(c):
        if c.kind in (0, 1):
            t = (c.kind, c.flags, c.depth, c.char, tuple(c.mat) if c.mat else None, c.cx)
            if c.kind == 1:
                ev = None if c.events is None else tuple((f, act(a),
                    (k & 255 if f & (1 << 17) else 0) if runtime_keys else k) for f, a, k in c.events)
                t += (c.event_flags, c.nevents, ev, c.name)
            return t
        if c.kind == 2:
            return (2, c.depth)
        return (c.kind, act(c.action))

    def frames(fs):
        return tuple((f.word, tuple(cmd(c) for c in f.commands)) for f in fs)

    def tex(t):
        return (t.fmt, t.w, t.h, t.swizzled, t.pixels, t.palette, t.flags)

    def obj(o):
        if o is None:
            return None
        k = o.kind
        if k == 1:
            fills = tuple((f.type, f.colour, f.mat, f.bitmap,
                           None if f.gradient is None else
                           (f.gradient.mat, f.gradient.count, f.gradient.radial, f.gradient.ratios,
                            tuple(f.gradient.colours))) for f in o.fills)
            return (1, fills, tuple(tuple(l) for l in o.lines), o.dlist, o.fills_present, o.lines_present)
        if k == 2:
            return (2, frames(o.frames))
        if k == 3:
            return (3, o.byte8, tuple((r.states, r.depth, r.mat, r.cx, r.char) for r in o.records),
                    tuple((c, act(a)) for c, a, _p in o.conds), o.records_present, o.conds_present)
        if k == 4:
            return (4, o.tw, o.th, o.inv, tex(o.tex))
        if k == 5:
            return (5, o.count, tuple(o.codes or ()), None if o.advances is None else tuple(o.advances),
                    o.ascii, o.ascent, o.descent, o.leading,
                    tuple((sh.size, sh.count, sh.rects, sh.texindex, tuple(tex(t) for t in sh.textures))
                          for sh in o.sheets))
        if k == 6:
            return (6, o.mat, o.records)
        if k == 7:
            return (7, o.textlen, o.text, o.var, o.leading, o.colour, o.font, o.height, o.bw, o.bh,
                    o.xmin, o.ymin, o.align)
        return (k,)
    return ((m.version, m.flag, m.swf_version, m.rect, m.rate, len(m.objects), m.table_zero),
            frames(m.frames), [obj(o) for o in m.objects])


KIND = {1: 'SHAPE', 2: 'SPRITE', 3: 'BUTTON', 4: 'BITMAP', 5: 'FONT', 6: 'TEXT', 7: 'EDITTEXT', 8: 'SOUND'}


def first_difference(a, b, path=''):
    """Where two canon() trees part, as a path of indices."""
    if type(a) is not type(b) or not isinstance(a, tuple):
        return path if a != b else None
    if len(a) != len(b):
        return '%s (length %d vs %d)' % (path, len(a), len(b))
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return first_difference(x, y, '%s[%d]' % (path, i))
    return None


def compare(m0, m1):
    """(objects that differ by kind, examples) between two models."""
    c0, c1 = canon(m0), canon(m1)
    bad = collections.Counter()
    ex = []
    if c0[0] != c1[0]:
        bad['movie'] += 1
        ex.append('movie %s' % first_difference(c0[0], c1[0]))
    if c0[1] != c1[1]:
        bad['root timeline'] += 1
        ex.append('root timeline %s' % first_difference(c0[1], c1[1]))
    for k, (a, b) in enumerate(zip(c0[2], c1[2])):
        if a != b:
            kind = KIND.get((a or b)[0], '?') if (a or b) else '?'
            bad[kind] += 1
            if len(ex) < 6:
                ex.append('#%d %s %s' % (k, kind, first_difference(a, b) if a and b else 'missing'))
    if len(c0[2]) != len(c1[2]):
        bad['object count'] += 1
    return bad, ex


def dlist_geometry(dlist):
    """What a display list covers, independent of how it was cut: the area
    each fill style paints (twips^2, fans as triangles) and the multiset of
    stroked segments per line style, direction ignored."""
    v = struct.unpack('<%dH' % (len(dlist) // 2), dlist)
    area = collections.Counter()
    segs = collections.Counter()
    fill = line = 0
    p = 0
    while p < len(v):
        op = v[p]
        p += 1
        if op == 0:
            break
        if op in (1, 2):
            n = v[p]
            p += 1
            pts = [(struct.unpack('<h', struct.pack('<H', v[p + 2 * k]))[0],
                    struct.unpack('<h', struct.pack('<H', v[p + 2 * k + 1]))[0]) for k in range(n)]
            p += 2 * n
            if op == 2:
                a = 0
                for i in range(1, n - 1):
                    (x0, y0), (x1, y1), (x2, y2) = pts[0], pts[i], pts[i + 1]
                    a += abs((x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0))
                area[fill] += a / 2.0
            else:
                for q, r in zip(pts, pts[1:]):
                    if q != r:
                        segs[(line,) + (q + r if q < r else r + q)] += 1
        elif op == 3:
            p += 2
        elif op == 4:
            fill = v[p] or fill
            p += 1
        elif op == 5:
            line = v[p] or line
            p += 1
        else:
            break
    return area, segs


def same_geometry(sh0, sh1):
    """None when two shapes paint the same thing, else what differs."""
    a0, s0 = dlist_geometry(sh0.dlist)
    a1, s1 = dlist_geometry(sh1.dlist)
    if s0 != s1:
        return 'stroked segments differ (%d vs %d)' % (sum(s0.values()), sum(s1.values()))
    for f in set(a0) | set(a1):
        x, y = a0.get(f, 0.0), a1.get(f, 0.0)
        if abs(x - y) > max(0.01 * max(x, y), 400.0):
            return 'fill %d covers %.0f twips^2, was %.0f' % (f, y, x)
    return None


def styles_close(s0, s1, unused_bitmap_matrices=False, stats=None):
    """Fill and line styles equal, matrices within float noise (a SWF says
    16.16; the floats come back to about 5e-7)."""
    def close(a, b):
        va, vb = struct.unpack('<6f', a), struct.unpack('<6f', b)
        return all(abs(x - y) <= 1e-5 * max(1.0, abs(x)) for x, y in zip(va, vb))
    if len(s0.fills) != len(s1.fills) or [tuple(l) for l in s0.lines] != [tuple(l) for l in s1.lines]:
        return False
    used0 = set(dlist_geometry(s0.dlist)[0])
    used1 = set(dlist_geometry(s1.dlist)[0])
    for index, (f, g) in enumerate(zip(s0.fills, s1.fills), 1):
        if (f.type & 255, f.colour, f.bitmap) != (g.type & 255, g.colour, g.bitmap):
            return False
        if not close(f.mat, g.mat):
            # SWF bitmap matrices have integral twip translations. A null
            # bitmap style that neither display list draws has no texels to
            # transform. Keep strict equality for every drawn style; report
            # the discarded precision of these unused v6 placeholders.
            unused = (unused_bitmap_matrices and 0x40 <= (f.type & 255) <= 0x43
                      and f.bitmap is None and index not in used0 and index not in used1)
            if not unused:
                return False
            if stats is not None:
                stats['unused bitmap matrices quantized by SWF'] += 1
        if (f.gradient is None) != (g.gradient is None):
            return False
        if f.gradient is not None:
            a, b = f.gradient, g.gradient
            if (a.count, a.radial, a.ratios, list(a.colours)) != (b.count, b.radial, b.ratios, list(b.colours))                     or not close(a.mat, b.mat):
                return False
    return True


def compare_nometa(m0, m1):
    """compare() for a SWF compiled without its meta block, where some
    differences are the point: shapes must paint the same coverage
    (same_geometry), bitmaps keep their texels and the alpha of every CLUT
    entry (colours of non-opaque entries were premultiplied), fonts keep
    codes, advances and metrics (the sheets are drawn anew). Everything else
    must be equal, as with the meta block."""
    # SWF cannot carry the unused high bytes of CLIPEVENT.key. RunEvents
    # (Remix 0x212CD0) only reads flags/actions for load/enterFrame events.
    c0, c1 = canon(m0, runtime_keys=True), canon(m1, runtime_keys=True)
    bad = collections.Counter()
    st = collections.Counter()
    ex = []
    for part, i in (('movie', 0), ('root timeline', 1)):
        if c0[i] != c1[i]:
            bad[part] += 1
            ex.append('%s %s' % (part, first_difference(c0[i], c1[i])))
    if len(c0[2]) != len(c1[2]):
        bad['object count'] += 1
    for k, (a, b) in enumerate(zip(c0[2], c1[2])):
        if a == b:
            continue
        kind = KIND.get((a or b)[0], '?') if (a or b) else '?'
        why = 'missing' if not (a and b) else None
        if why is None and kind == 'SHAPE':
            o0, o1 = m0.objects[k], m1.objects[k]
            why = same_geometry(o0, o1)
            if why is None:
                st['shapes re-tessellated, same coverage'] += 1
                if not styles_close(o0, o1, unused_bitmap_matrices=m0.version == 6, stats=st):
                    why = 'fill or line styles differ'
        elif why is None and kind == 'BUTTON' and m0.version == 6:
            o0, o1 = m0.objects[k], m1.objects[k]
            if a[:2] != b[:2] or a[3:] != b[3:] or len(o0.records) != len(o1.records):
                why = 'button flags, actions or record count differ'
            else:
                for r0, r1 in zip(o0.records, o1.records):
                    if (r0.states, r0.depth, r0.cx, r0.char) != (r1.states, r1.depth, r1.cx, r1.char):
                        why = 'button record differs'
                        break
                    v0, v1 = struct.unpack('<6f', r0.mat), struct.unpack('<6f', r1.mat)
                    if any(abs(x - y) > 1e-5 * max(1.0, abs(x)) for x, y in zip(v0, v1)):
                        why = 'button matrix differs beyond SWF precision'
                        break
                if why is None:
                    st['buttons same within SWF matrix precision'] += 1
        elif why is None and kind == 'BITMAP':
            t0, t1 = m0.objects[k].tex, m1.objects[k].tex
            if (t0.fmt, t0.w, t0.h, t0.swizzled, t0.pixels) != (t1.fmt, t1.w, t1.h, t1.swizzled, t1.pixels):
                why = 'texels differ'
            elif t0.palette[3::4] != t1.palette[3::4]:
                why = 'CLUT alpha differs'
            else:
                st['bitmaps same texels and alpha'] += 1
        elif why is None and kind == 'FONT':
            if a[:8] != b[:8]:
                why = 'font %s' % first_difference(a[:8], b[:8])
            else:
                st['fonts same, sheets drawn'] += 1
        elif why is None:
            why = first_difference(a, b)
        if why is not None:
            bad[kind] += 1
            if len(ex) < 6:
                ex.append('#%d %s %s' % (k, kind, why))
    return bad, ex, st


def check_image(data, name):
    """Read a written .pck back: the reader must take it and explain every
    byte of it."""
    R = _mod('mc3_swf')
    mv = R.Movie(data, name)
    _claimed, _pad, holes = mv.img.coverage()
    return sum(h[2] for h in holes)


def cmd_viaswf(a):
    """.pck -> .swf (mc3_swf) -> .pck (this tool), then the two models compared."""
    R = _mod('mc3_swf')
    files = _inputs(a.files, '.pck')
    if a.out:
        for folder in ('swf', 'pck'):
            os.makedirs(os.path.join(a.out, folder), exist_ok=True)
    same = 0
    tot = collections.Counter()
    for path in files:
        name = os.path.basename(path)
        data = open(path, 'rb').read()
        try:
            fp = FromPck(data, name)
            m0 = fp.model()
            swf = R.SwfWriter(fp.mv, meta=not a.no_meta).build(compress=False)
            fs = FromSwf(swf, name, pck_version=m0.version, base=m0.base)
            m1 = fs.model()
            out = Builder(m1).image('packed')
            holes = check_image(out, name)
            m2 = FromPck(out, name).model()
        except Exception as e:
            if a.raise_errors:
                raise
            print('   FAIL %-30s %s: %s' % (name, type(e).__name__, e))
            continue
        if a.no_meta:
            bad, ex, st = compare_nometa(m0, m2)
            tot.update(st)
        else:
            bad, ex = compare(m0, m2)
        tot.update(fs.stats)
        ok = not bad and not holes
        same += ok
        if a.out:
            stem = os.path.splitext(name)[0]
            with open(os.path.join(a.out, 'swf', stem + '.swf'), 'wb') as f:
                f.write(swf)
            with open(os.path.join(a.out, 'pck', stem + '.pck'), 'wb') as f:
                f.write(out)
        if not ok or a.verbose:
            print('   %-30s %8d -> swf %8d -> %8d  %s%s' % (
                name, len(data), len(swf), len(out),
                'same movie' if not bad else 'DIFFERS: %s' % dict(bad),
                ', %d unexplained byte(s)' % holes if holes else ''))
            for e in ex:
                print('        ' + e)
            if fs.warn:
                print('        warnings: %s' % dict(fs.warn))
    print('-- %d of %d file(s): .pck -> .swf -> .pck gives the same movie%s' % (
        same, len(files), ' (shapes by coverage, bitmaps by texels and alpha, fonts but their sheets)'
        if a.no_meta else ''))
    if tot:
        print('   ' + '  '.join('%s %d' % kv for kv in sorted(tot.items())))
    return 0 if same == len(files) else 1


def cmd_pck(a):
    """.swf -> .pck"""
    files = _inputs(a.files, '.swf')
    os.makedirs(a.out, exist_ok=True)
    fails = 0
    for path in files:
        name = os.path.splitext(os.path.basename(path))[0]
        try:
            fs = FromSwf(open(path, 'rb').read(), name, pck_version=a.pck_version, base=a.base)
            m = fs.model()
            out = Builder(m).image('packed')
            holes = check_image(out, name)
        except Exception as e:
            if a.raise_errors:
                raise
            fails += 1
            print('   FAIL %-30s %s: %s' % (name, type(e).__name__, e))
            continue
        dst = os.path.join(a.out, name + '.pck')
        with open(dst, 'wb') as f:
            f.write(out)
        n = collections.Counter(KIND.get(o.kind) for o in m.objects if o is not None)
        print('   %-30s -> %s  %d bytes  %s%s' % (os.path.basename(path), os.path.basename(dst), len(out),
              ' '.join('%s %d' % kv for kv in sorted(n.items())),
              '  UNEXPLAINED %d' % holes if holes else ''))
        if fs.stats:
            print('        ' + '  '.join('%s %d' % kv for kv in sorted(fs.stats.items())))
        if fs.warn:
            print('        warnings: ' + '  '.join('%s %d' % kv for kv in sorted(fs.warn.items())))
    print('-- %d .pck written%s' % (len(files) - fails, ', %d FAILED' % fails if fails else ''))
    return 1 if fails else 0


HOSTFS = os.environ.get('MC3_ALPHA_HOSTFS', os.environ.get('MC3_ALPHA_HOSTFS', ''))


def pcsx2_running():
    import subprocess
    p = subprocess.run(['tasklist'], capture_output=True, text=True)
    return 'pcsx2' in p.stdout.lower()


def cmd_alpha_remix(a):
    """Compare both corpora and optionally audit the All In reader, read-only."""
    import hashlib
    import json
    import types
    import zipfile
    os.makedirs(a.out, exist_ok=True)
    alpha = {os.path.basename(p): p for p in _inputs([a.alpha], '.pck')}
    remix = {os.path.basename(p): p for p in _inputs([a.remix], '.pck')}
    common = sorted(set(alpha) & set(remix))
    report = {'common': len(common), 'alpha_only': sorted(set(alpha) - set(remix)),
              'remix_only': sorted(set(remix) - set(alpha)), 'movies': []}
    allin = None
    if a.all_in:
        with zipfile.ZipFile(a.all_in) as z:
            source = z.read('mc3pck.py')
        allin = types.ModuleType('_mc3allin_audit')
        sys.modules[allin.__name__] = allin
        exec(compile(source, a.all_in + '/mc3pck.py', 'exec'), allin.__dict__)
        report['all_in'] = {'source_sha256': hashlib.sha256(source).hexdigest(),
                            'totals': collections.Counter(), 'examples': []}

    def inventory(fp, m):
        return {'objects': dict(collections.Counter(KIND[o.kind] for o in m.objects if o)),
                'root_frames': len(m.frames),
                'sprite_frames': sum(len(o.frames) for o in m.objects if o and o.kind == 2),
                'action_lists': len(fp.actions),
                'action_bytes': sum(len(o.code) for o in fp.actions.values()),
                'action_refs': sum(o.refcount for o in fp.actions.values())}

    def scripts(fp):
        return {hashlib.sha256(o.code).hexdigest(): o.refcount for o in fp.actions.values()}

    for name, path in sorted(remix.items()):
        f1 = FromPck(open(path, 'rb').read(), name)
        m1 = f1.model()
        c1 = canon(m1)
        if name in alpha:
            f0 = FromPck(open(alpha[name], 'rb').read(), name)
            m0 = f0.model()
            c0 = canon(m0)
            changed = collections.Counter()
            for i in range(max(len(c0[2]), len(c1[2]))):
                x = c0[2][i] if i < len(c0[2]) else None
                y = c1[2][i] if i < len(c1[2]) else None
                if x != y:
                    changed[KIND[(y or x)[0]]] += 1
            row = {'name': name, 'alpha': inventory(f0, m0), 'remix': inventory(f1, m1),
                   'same_movie_except_pck_version': c0[0][1:] == c1[0][1:] and c0[1:] == c1[1:],
                   'root_timeline_changed': c0[1] != c1[1],
                   'scripts_changed': scripts(f0) != scripts(f1),
                   'changed_objects_by_index': dict(changed)}
            report['movies'].append(row)
        if allin:
            p = allin.Pck(path)
            audit = report['all_in']
            totals = audit['totals']
            totals['files'] += 1
            ours = [(i, o.offset, KIND[o.kind]) for i, o in enumerate(f1.mv.objects) if o]
            totals['object_graph_matches'] += list(p.objects()) == ours
            for text in p.text_objects():
                totals['texts'] += 1
                ob = f1.mv.objects[text.index]
                glyphs, fonts, chars = [], set(), []
                font = None
                for rec in ob.records:
                    if rec[0] == 'font':
                        font = f1.mv.objects[rec[1]]
                        fonts.add(font.offset)
                    elif rec[0] == 'glyphs':
                        glyphs.extend((g, advance & 0xFFFF) for g, advance in rec[1])
                        chars.extend(chr(font.codes[g]) for g, _advance in rec[1])
                equal = text.error is None and tuple(glyphs) == text.records
                totals['glyph_records_match'] += equal
                totals['decode_errors'] += text.error is not None
                totals['font_match'] += text.font_offset in fonts
                plain = ''.join(chars)
                totals['visible_text_match'] += text.error is None and text.text.replace('\n', '') == plain
                if not equal and len(audit['examples']) < 12:
                    audit['examples'].append({'file': name, 'object': text.index,
                        'native_records': len(glyphs), 'all_in_records': len(text.records),
                        'native_text': plain[:120], 'all_in_text': text.text[:120], 'error': text.error})
        print('   compared ' + name, flush=True)
    report['same_movies'] = sum(r['same_movie_except_pck_version'] for r in report['movies'])
    report['changed_script_movies'] = sum(r['scripts_changed'] for r in report['movies'])
    with open(os.path.join(a.out, 'alpha_remix.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    write_alpha_remix_markdown(report, os.path.join(a.out, 'alpha_remix_movies.md'))
    print('-- %d common movies; %d same movie, %d with changed scripts' %
          (len(common), report['same_movies'], report['changed_script_movies']))
    if allin:
        print('   All In: %s' % dict(report['all_in']['totals']))


def write_alpha_remix_markdown(report, path):
    """Render the measured comparison and both complete exclusive-name lists."""
    lines = ['# Alpha x Remix: per-movie measurements', '',
             'Object changes compare the same table index, including additions/removals. '
             'Script changes include reference counts. Baker addresses and pointer layout '
             'are excluded; PCK version is the only header field ignored.', '',
             '| Movie | Alpha objects | Remix objects | Changed objects by type | Scripts | Same movie |',
             '|---|---:|---:|---|---|---|']
    for r in report['movies']:
        lines.append('| %s | %d | %d | %s | %s | %s |' % (r['name'],
            sum(r['alpha']['objects'].values()), sum(r['remix']['objects'].values()),
            ', '.join('%s:%d' % kv for kv in sorted(r['changed_objects_by_index'].items())) or 'none',
            'changed' if r['scripts_changed'] else 'same',
            'yes' if r['same_movie_except_pck_version'] else 'no'))
    for key, title in [('remix_only', 'Remix-only movies'), ('alpha_only', 'Alpha-only movies')]:
        names = report[key]
        lines.extend(['', '## %s (%d)' % (title, len(names)), ''])
        groups = collections.defaultdict(list)
        for name in names:
            groups[name.split('_', 1)[0]].append(name)
        for prefix, members in sorted(groups.items()):
            lines.extend(['### %s (%d)' % (prefix, len(members)), '',
                          ', '.join('`%s`' % name for name in members), ''])
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def shot_difference(a, b, thr=24):
    """(share of pixels that differ by more than thr, largest difference) of
    two screenshots of the same moment, the PCSX2 OSD masked: the stats block
    at the top right and the settings line at the bottom."""
    import numpy as np
    from PIL import Image
    A = np.asarray(Image.open(a).convert('RGB')).astype(np.int16)
    B = np.asarray(Image.open(b).convert('RGB')).astype(np.int16)
    if A.shape != B.shape:
        return None, None
    h, w, _ = A.shape
    mask = np.ones((h, w), bool)
    mask[0:int(h * 0.38), int(w * 0.49):] = False
    mask[int(h * 0.965):, :] = False
    d = np.abs(A - B).max(axis=2)
    d[~mask] = 0
    return 100.0 * (d > thr).sum() / mask.sum(), int(d.max())


def cmd_ingame(a):
    """Boot a game with a set of .pck in ASSETS/flash, screenshot, and put
    back what was there - files and mc3boot.ini - whatever happens."""
    import shutil
    import subprocess
    import tempfile
    import hashlib
    import json
    a.hostfs = a.hostfs or (HOSTFS if a.game == 'alpha' else os.environ.get('MC3_ALPHA_HOSTFS', ''))
    flash = os.path.join(a.hostfs, 'ASSETS', 'flash')
    ini = os.path.join(a.hostfs, 'mc3boot.ini')
    elf = os.path.join(a.hostfs, 'mc3boot_alpha.elf' if a.game == 'alpha' else 'mc3boot.elf')
    for p in (flash, ini, elf):
        if not os.path.exists(p):
            raise SystemExit('%s not found' % p)
    if pcsx2_running():
        raise SystemExit('PCSX2 is running - not touching %s' % a.hostfs)
    files = []
    if a.set != 'orig':
        files = [f for f in sorted(os.listdir(a.set)) if f.lower().endswith('.pck')] \
            if os.path.isdir(a.set) else [os.path.basename(a.set)]
        src_dir = a.set if os.path.isdir(a.set) else os.path.dirname(a.set)
    out = os.path.join(a.out, a.name)
    os.makedirs(out, exist_ok=True)
    ini_before = open(ini, 'rb').read()
    keep = tempfile.mkdtemp(prefix='mc3_ingame_')
    before_hashes = {}
    backed_up = []
    try:
        for f in files:
            d = os.path.join(flash, f)
            before_hashes[f] = hashlib.sha256(open(d, 'rb').read()).hexdigest() if os.path.exists(d) else None
            if os.path.exists(d):
                shutil.copyfile(d, os.path.join(keep, f))
            # A failed/partial backup must never be restored over the source,
            # and files not backed up must never be removed by finally.
            backed_up.append(f)
        boot = a.boot if a.boot is not None else (['garage = 1'] if a.game == 'alpha' else None)
        if boot is not None:
            # [boot] is the section at the start of a line - comments name it too.
            text = ini_before.decode('latin-1').replace('\r\n', '\n')
            head = text[:text.index('\n[boot]') + 1] if '\n[boot]' in text else text + '\n'
            with open(ini, 'w', newline='\r\n') as f:
                f.write(head + '[boot]\n' + ''.join(line + '\n' for line in boot))
        for f in files:
            shutil.copyfile(os.path.join(src_dir, f), os.path.join(flash, f))
        print('   %d .pck in place, [boot] %s' % (len(files), '; '.join(boot or []) or 'preserved'))
        if a.game == 'remix':
            steps = a.steps or ['until state:41 90', 'shot title', 'push cross state:40',
                              'select ' + a.profile, 'push cross state:20',
                              'until row:go_to_garage', 'select go_to_garage',
                              'push cross state:6', 'select =Yes up',
                              'press cross', 'until game:5 90', 'menu', 'wait 3', 'shot garage']
            command = [sys.executable, os.path.join(_AQUI, 'mc3_pcsx2_drive.py'),
                       '--elf', elf, '--skip-fmv', '--out', out] + steps
            shots = [s.split()[1] + '.png' for s in steps if s.split()[0] == 'shot']
        else:
            command = [sys.executable, os.path.join(_AQUI, 'mc3_pcsx2_shots.py'), '--elf', elf,
                       '--at'] + [str(t) for t in a.at] + ['--out', out]
            shots = ['t%03d.png' % int(t) for t in a.at]
        subprocess.run(command, check=True)
        for name in shots:
            if not os.path.isfile(os.path.join(out, name)):
                raise BakeError('screenshot missing: ' + name)
    finally:
        restored = 0
        for f in backed_up:
            k = os.path.join(keep, f)
            d = os.path.join(flash, f)
            if os.path.exists(k):
                shutil.copyfile(k, d)
                restored += 1
            elif os.path.exists(d):
                os.remove(d)                 # it was not there before
        with open(ini, 'wb') as f:
            f.write(ini_before)
        after_hashes = {name: hashlib.sha256(open(os.path.join(flash, name), 'rb').read()).hexdigest()
                        if os.path.exists(os.path.join(flash, name)) else None for name in before_hashes}
        restoration = {'hostfs': a.hostfs, 'files': len(files), 'backed_up': len(backed_up), 'before': before_hashes,
                       'after': after_hashes, 'files_restored': before_hashes == after_hashes,
                       'ini_restored': open(ini, 'rb').read() == ini_before}
        with open(os.path.join(out, 'restoration.json'), 'w', encoding='utf-8') as f:
            json.dump(restoration, f, indent=2)
        shutil.rmtree(keep, ignore_errors=True)
        print('   restored %d file(s) and mc3boot.ini' % restored)
    if a.compare:
        for n in shots:
            pa, pb = os.path.join(a.compare, n), os.path.join(out, n)
            if os.path.exists(pa) and os.path.exists(pb):
                share, mx = shot_difference(pa, pb)
                print('   %s: %.3f%% of the pixels differ from %s (largest %s)' % (n, share, a.compare, mx))


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='acao')
    s = sub.add_parser('alpha-remix', help='read-only per-movie comparison and optional MC3 All In audit')
    s.add_argument('--alpha', required=True)
    s.add_argument('--remix', required=True)
    s.add_argument('--out', required=True)
    s.add_argument('--all-in', help='MC3 All In v1.2.3 ZIP (reader is loaded in isolation)')
    s = sub.add_parser('pck', help='.swf -> .pck')
    s.add_argument('files', nargs='+')
    s.add_argument('--out', required=True)
    s.add_argument('--pck-version', type=int, choices=(5, 6), default=None,
                   help='target baker (default: movie meta, or alpha v5 without meta)')
    s.add_argument('--base', type=lambda s: int(s, 0), default=None,
                   help='pointer base (default: movie meta, or 0x06800000 without meta)')
    s.add_argument('--raise', dest='raise_errors', action='store_true')
    s = sub.add_parser('roundtrip', help='.pck -> model -> .pck')
    s.add_argument('files', nargs='+')
    s.add_argument('--layout', choices=('source', 'packed'), default='source')
    s.add_argument('-v', '--verbose', action='store_true')
    s.add_argument('--raise', dest='raise_errors', action='store_true')
    s = sub.add_parser('viaswf', help='.pck -> .swf -> .pck, the two movies compared')
    s.add_argument('files', nargs='+')
    s.add_argument('--out', help='also save the intermediate SWFs and compiled PCKs in swf/ and pck/')
    s.add_argument('--no-meta', action='store_true', help='compile the SWF without its meta block')
    s.add_argument('-v', '--verbose', action='store_true')
    s.add_argument('--raise', dest='raise_errors', action='store_true')
    s = sub.add_parser('ingame', help='boot alpha or Remix with a set of .pck and screenshot it')
    s.add_argument('set', help="a .pck, a folder of .pck, or 'orig' (what ASSETS/flash already has)")
    s.add_argument('--name', required=True, help='subfolder of --out for the screenshots')
    s.add_argument('--at', nargs='+', type=float, default=[40.0], help='seconds after boot')
    s.add_argument('--boot', nargs='+', default=None,
                   help='replace [boot] for this run (default: alpha garage=1; Remix preserved)')
    s.add_argument('--game', choices=('alpha', 'remix'), default='alpha')
    s.add_argument('--profile', default='havefun', help='existing profile used by the Remix menu script')
    s.add_argument('--steps', nargs='+', help='custom mc3_pcsx2_drive steps for Remix')
    s.add_argument('--hostfs', default=None, help='HostFS (default: MC3_ALPHA_HOSTFS for alpha; Y:/mc3.2_alpha_hostfs for Remix)')
    s.add_argument('--out', default=os.path.join(_AQUI, 'output', 'flash_swf', 'ingame'))
    s.add_argument('--compare', help='a folder of screenshots of the same moments to compare with')
    a = ap.parse_args()
    fn = {'roundtrip': cmd_roundtrip, 'viaswf': cmd_viaswf, 'pck': cmd_pck,
          'ingame': cmd_ingame, 'alpha-remix': cmd_alpha_remix}.get(a.acao)
    if not fn:
        ap.print_help()
        return 2
    return fn(a) or 0


if __name__ == '__main__':
    sys.exit(main())
