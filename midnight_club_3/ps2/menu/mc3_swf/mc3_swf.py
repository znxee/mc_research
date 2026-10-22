"""
mc3_swf.py - the flash .pck of Midnight Club 3, read completely and written
back out as a real .swf

    python mc3_swf.py info   FILE.pck
    python mc3_swf.py dump   FILE.pck [--obj N] [--frames]
    python mc3_swf.py cover  FILE.pck|DIR [--show N]
    python mc3_swf.py swf    FILE.pck|DIR --out DIR [--png] [--no-meta]
    python mc3_swf.py check  FILE.swf|DIR
    python mc3_swf.py verify FILE.pck|DIR     JPEXS FFDec decodes our SWF; every
                                               field is compared with the .pck

The way back, SWF -> .pck, is mc3_swf2pck.py. Each SWF written here carries a
DefineBinaryData exported as `mc3_pck_meta` with what SWF cannot hold (the CLUT
before premultiplication, the fans and float matrices of the shapes, the font
sheets), so an untouched object compiles back exactly.

WHAT A FLASH .PCK IS

The image of a movie the engine has already parsed: the C++ objects of the
`c:/soft/age/src/flash` library (Angel's player, `flash.lib`) dumped to disk
with their pointers made relative to a base address, so that loading is one
read plus one pass of "add the delta to every pointer". There is no SWF inside
and nothing to decompress; what was a tag is now an object.

WHERE EVERY OFFSET HERE COMES FROM

The alpha build of 24/10/2004 ships MC.MAP, and with it the names of every
function of that library. Each `X::X(datResource&)` constructor relocates
exactly the pointers of its object and walks exactly its arrays, so the
constructors ARE the layout; the `Draw`/`Update` methods say what the fields
mean. Addresses below are alpha (SLUS_123.45):

    swfFILE::swfFILE            0x202CE0   swfSHAPE::swfSHAPE        0x206C00
    swfOBJECT::Fixup (type sw.) 0x205FF8   swfSHAPE::FILLSTYLE       0x206BA0
    swfSPRITE::swfSPRITE        0x206E78   swfGRADIENT::swfGRADIENT  0x206B68
    swfFRAME::swfFRAME          0x208AD0   swfSHAPE::Draw            0x2065D0
    swfCMD::Fixup (type sw.)    0x20A740   swfBUTTON::swfBUTTON      0x207480
    swfCMD_PlaceObject2::Update 0x20A140   swfBUTTON::ChangeState    0x2070C0
    ...ClipEvent::Update        0x20A330   swfFONT::swfFONT          0x208820
    swfTEXT::Draw               0x207C38   swfFONT::SHEET::SHEET     0x208730
    swfEDITTEXT::Draw           0x2081B0   swfFONT::SHEET::DrawGlyph 0x207670
    swfACTIONLIST::Execute      0x208B40   swfCXFORMWITHALPHA::Transf 0x2058D8
    gfxTexture(datResource&)    0x4E3D18   gfxMipChain(datResource&) 0x4DE330

THE PARTS OF THE FORMAT THAT ARE NOT SWF ANY MORE

    SHAPE   no edges. A u16 display list: 1 = polyline of wide lines, 2 = a
            TRIANGLE FAN (vglBegin passes its mode straight to the GS PRIM
            field, and 5 is TRIFAN there), 4/5 = pick fill/line style. The
            curves were flattened and the fills cut into fans when the movie
            was baked; this tool stitches the fans of one fill back into
            outlines, which is what makes the result a normal SWF shape.
    TEXT    a u16 stream: 1 font+height, 2 colour, 3 y, 4 x, 5 glyph run. The
            TEXTRECORD of SWF, field for field, positions in 1/1024 em.
    FONT    no outlines. The glyph table the file still points at (+0x0C) is
            stale host memory, and the constructor zeroes it anyway; glyphs are
            drawn from bitmap SHEETS, one per point size.
    CXFORM  8 signed bytes, multipliers in 1/64 and adds in units of 4.
    MATRIX  in PlaceObject2: s16 in 8.8 for scale/rotate, twips for translate;
            everywhere else six floats, row-vector convention (swfMATRIX::Dot).
    AVM1    untouched: the interpreter reads the original bytecode from +2 of
            each action list (the u16 before it is a refcount). It goes back
            into DoAction tags byte for byte.
"""

import argparse
import collections
import hashlib
import importlib.util
import os
import struct
import sys
import zlib

_AQUI = os.path.dirname(os.path.abspath(__file__))

HEADER = 0x80
PAD = 0xCD

OBJ_NAMES = {0: 'FILE', 1: 'SHAPE', 2: 'SPRITE', 3: 'BUTTON', 4: 'BITMAP',
             5: 'FONT', 6: 'TEXT', 7: 'EDITTEXT', 8: 'SOUND'}
CMD_NAMES = {0: 'PlaceObject2', 1: 'PlaceObject2ClipEvent', 2: 'RemoveObject2',
             3: 'DoAction', 4: 'DoInitAction'}


class FormatError(Exception):
    pass


def _mod(nome):
    s = importlib.util.spec_from_file_location(nome, os.path.join(_AQUI, nome + '.py'))
    m = importlib.util.module_from_spec(s)
    sys.modules[nome] = m
    s.loader.exec_module(m)
    return m


# ---------------------------------------------------------------------------
# the file and the ledger of what has been read
# ---------------------------------------------------------------------------
class Image(object):
    """The .pck bytes, the pointer arithmetic, and a ledger of claimed ranges.

    The ledger is the point: a reader that explains every byte of every file
    (or shows the bytes it cannot explain are the 0xCD fill the allocator
    leaves) is a reader that has not missed a structure. That is measured by
    `cover`, not asserted here.
    """

    def __init__(self, data, name='?'):
        self.d = bytes(data)
        self.name = name
        if len(self.d) < HEADER + 0x40:
            raise FormatError('%s: too short for a flash .pck' % name)
        self.base, self.version, self.flag, self.size = struct.unpack_from('<4I', self.d, 0)
        if self.size + HEADER != len(self.d):
            raise FormatError('%s: header size %d + 0x80 != file size %d'
                              % (name, self.size, len(self.d)))
        self.claims = {}

    # -- addressing ------------------------------------------------------
    def off(self, va):
        """VA -> file offset, None for a null pointer."""
        if va == 0:
            return None
        o = va - self.base + HEADER
        if not HEADER <= o < len(self.d):
            raise FormatError('%s: pointer %08X lands outside the file' % (self.name, va))
        return o

    def ptr(self, o):
        return self.off(self.u32(o))

    def va(self, o):
        return o - HEADER + self.base

    # -- reads -----------------------------------------------------------
    def u8(self, o):
        return self.d[o]

    def s8(self, o):
        return struct.unpack_from('<b', self.d, o)[0]

    def u16(self, o):
        return struct.unpack_from('<H', self.d, o)[0]

    def s16(self, o):
        return struct.unpack_from('<h', self.d, o)[0]

    def u32(self, o):
        return struct.unpack_from('<I', self.d, o)[0]

    def s32(self, o):
        return struct.unpack_from('<i', self.d, o)[0]

    def f32(self, o):
        return struct.unpack_from('<f', self.d, o)[0]

    def floats(self, o, n):
        return struct.unpack_from('<%df' % n, self.d, o)

    def cstr(self, o, limit=4096):
        e = self.d.find(b'\0', o, o + limit)
        if e < 0:
            raise FormatError('%s: unterminated string at %#x' % (self.name, o))
        self.claim(o, e + 1 - o, 'string')
        return self.d[o:e]

    # -- ledger ----------------------------------------------------------
    def claim(self, o, n, kind):
        if o is None or n <= 0:
            return
        if o < HEADER or o + n > len(self.d):
            raise FormatError('%s: %s at %#x+%d runs outside the file' % (self.name, kind, o, n))
        self.claims.setdefault((o, n), kind)

    def array(self, o, n, size, kind):
        """Claim an array and, when present, the cookie `new T[n]` put 16 bytes
        in front of it (the element count as a u32, then 12 bytes of fill) -
        only classes with a destructor get one, so its absence is normal."""
        if o is None or n < 0:
            return
        # n == 0 still has its cookie: `new CLIPEVENT[0]` allocates the 16
        # bytes, and the empty array "starts" where the next object then goes
        self.claim(o, n * size, kind)
        if o - 0x10 >= HEADER and self.u32(o - 0x10) == n:
            self.claim(o - 0x10, 4, 'vec cookie')

    def coverage(self):
        """(claimed, padding, unexplained ranges) over the payload."""
        mapa = bytearray(len(self.d))
        for (o, n), _k in self.claims.items():
            mapa[o:o + n] = b'\1' * n
        claimed = padding = 0
        buracos = []
        i = HEADER
        while i < len(self.d):
            if mapa[i]:
                claimed += 1
                i += 1
                continue
            j = i
            while j < len(self.d) and not mapa[j]:
                j += 1
            trecho = self.d[i:j]
            pad = trecho.count(PAD)
            padding += pad
            if pad != len(trecho):
                buracos.append((i, j - i, len(trecho) - pad))
            i = j
        return claimed, padding, buracos


# ---------------------------------------------------------------------------
# small value types
# ---------------------------------------------------------------------------
class Matrix(object):
    """a b c d tx ty, row vector: x' = a*x + c*y + tx, y' = b*x + d*y + ty.

    That is SWF's own convention (a = ScaleX, b = RotateSkew0, c = RotateSkew1,
    d = ScaleY). Translation in PIXELS for the float matrices of the file; the
    PlaceObject2 form carries twips and is converted when read.
    """
    __slots__ = ('a', 'b', 'c', 'd', 'tx', 'ty')

    def __init__(self, a=1.0, b=0.0, c=0.0, d=1.0, tx=0.0, ty=0.0):
        self.a, self.b, self.c, self.d, self.tx, self.ty = a, b, c, d, tx, ty

    def tuple(self):
        return (self.a, self.b, self.c, self.d, self.tx, self.ty)

    def apply(self, x, y):
        return (self.a * x + self.c * y + self.tx, self.b * x + self.d * y + self.ty)

    def inverse(self):
        det = self.a * self.d - self.b * self.c
        if abs(det) < 1e-12:
            return None
        ia, ib, ic, id_ = self.d / det, -self.b / det, -self.c / det, self.a / det
        itx = -(ia * self.tx + ic * self.ty)
        ity = -(ib * self.tx + id_ * self.ty)
        return Matrix(ia, ib, ic, id_, itx, ity)

    def dot(self, other):
        """self then other (swfMATRIX::Dot(out, self, other))."""
        return Matrix(self.a * other.a + self.b * other.c,
                      self.a * other.b + self.b * other.d,
                      self.c * other.a + self.d * other.c,
                      self.c * other.b + self.d * other.d,
                      self.tx * other.a + self.ty * other.c + other.tx,
                      self.tx * other.b + self.ty * other.d + other.ty)

    def __repr__(self):
        return 'M(%.4g %.4g %.4g %.4g | %.4g %.4g)' % self.tuple()


class Cxform(object):
    """swfCXFORMWITHALPHA: 4 signed multipliers (64 = 1.0), 4 signed adds (x4).

    swfCXFORMWITHALPHA::Transform: out = clamp(4 * ((c * mul >> 8) + add)),
    i.e. c * mul / 64 + add * 4. In SWF terms mul * 4 (of 256) and add * 4.
    """
    __slots__ = ('mul', 'add')

    def __init__(self, mul=(64, 64, 64, 64), add=(0, 0, 0, 0)):
        self.mul, self.add = tuple(mul), tuple(add)

    def identity(self):
        return self.mul == (64, 64, 64, 64) and self.add == (0, 0, 0, 0)

    def __repr__(self):
        return 'CX(%s + %s)' % (self.mul, self.add)


def read_cxform(img, o):
    img.claim(o, 8, 'cxform')
    return Cxform(struct.unpack_from('<4b', img.d, o), struct.unpack_from('<4b', img.d, o + 4))


def rgba(u):
    """The engine's colours are u32 with R in the low byte (GS order)."""
    return (u & 0xFF, (u >> 8) & 0xFF, (u >> 16) & 0xFF, (u >> 24) & 0xFF)


# ---------------------------------------------------------------------------
# action lists
# ---------------------------------------------------------------------------
class ActionList(object):
    """swfACTIONLIST: u16 refcount, then the AVM1 stream as the SWF had it.

    swfACTIONLIST::Execute starts at +2 and decodes the standard way
    (op >= 0x80 carries a u16 length), stopping at op 0. Nothing in it is
    rewritten by the baker - the constant pool is the ordinary 0x88 action.
    """

    def __init__(self, img, o):
        self.offset = o
        self.refcount = img.u16(o)
        p = o + 2
        while True:
            if p >= len(img.d):
                raise FormatError('%s: action list at %#x runs off the file' % (img.name, o))
            op = img.d[p]
            if op == 0:
                p += 1
                break
            p += 3 + img.u16(p + 1) if op >= 0x80 else 1
        self.code = img.d[o + 2:p]
        img.claim(o, p - o, 'actions')


def action_list(img, o, cache):
    if o is None:
        return None
    a = cache.get(o)
    if a is None:
        a = cache[o] = ActionList(img, o)
    return a


# ---------------------------------------------------------------------------
# the timeline: frames and commands
# ---------------------------------------------------------------------------
class Place(object):
    """swfCMD_PlaceObject2 (type 0) and swfCMD_PlaceObject2ClipEvent (type 1).

        +00 u8  type          +01 u8 flags: 1 = scale present, 2 = rotate
        +04 ptr next          +08 vtable (overwritten on load)
        +0C u16 depth         +0E u16 character, 1-based object index,
                                     0xFFFF = move what is already there
        +10 ptr matrix data   s16: [sx sy] [r0 r1] tx ty, 8.8 and twips
        +14 ptr cxform        8 bytes
      type 1 only:
        +18 u32 union of the event flags     +1C s32 event count
        +20 ptr CLIPEVENT[]   12 bytes: u32 flags, ptr actions, u32 key
        +24 ptr name          the instance name; ClipEvent::Update binds it
                              as a property of the parent (vtable slot 11)

    No ratio and no clip depth: the player has neither, so a baked movie can
    hold no mask and no morph.
    """
    move = False

    def __init__(self, img, o, cache):
        self.kind = img.u8(o)
        self.flags = img.u8(o + 1)
        self.depth = img.u16(o + 0x0C)
        ch = img.u16(o + 0x0E)
        self.char = None if ch == 0xFFFF else ch
        img.claim(o, 0x18 if self.kind == 0 else 0x28, 'place%d' % self.kind)
        self.matrix = None
        m = img.ptr(o + 0x10)
        if m is not None:
            vals = []
            n = 2 * (bool(self.flags & 1) + bool(self.flags & 2) + 1)
            img.claim(m, 2 * n, 'place matrix')
            vals = [img.s16(m + 2 * k) for k in range(n)]
            k = 0
            a = d = 1.0
            b = c = 0.0
            if self.flags & 1:
                a, d = vals[0] / 256.0, vals[1] / 256.0
                k = 2
            if self.flags & 2:
                b, c = vals[k] / 256.0, vals[k + 1] / 256.0
                k += 2
            self.matrix = Matrix(a, b, c, d, vals[k] / 20.0, vals[k + 1] / 20.0)
            self.matrix_raw = vals
        cx = img.ptr(o + 0x14)
        self.cxform = read_cxform(img, cx) if cx is not None else None
        self.name = None
        self.events = []
        self.events_present = False
        self.event_flags = 0
        if self.kind == 1:
            self.event_flags = img.u32(o + 0x18)
            n = img.s32(o + 0x1C)
            ev = img.ptr(o + 0x20)
            self.events_present = ev is not None
            if ev is not None and n >= 0:
                img.array(ev, n, 12, 'clip events')
                for k in range(n):
                    e = ev + 12 * k
                    self.events.append((img.u32(e), action_list(img, img.ptr(e + 4), cache),
                                        img.u32(e + 8)))
            nm = img.ptr(o + 0x24)
            if nm is not None:
                self.name = img.cstr(nm).decode('latin-1')


class Remove(object):
    """swfCMD_RemoveObject2: +02 u16 depth."""

    def __init__(self, img, o):
        self.kind = 2
        self.depth = img.u16(o + 2)
        img.claim(o, 0x0C, 'remove')


class Actions(object):
    """swfCMD_DoAction (3) / swfCMD_DoInitAction (4): +0C ptr action list.

    DoInitAction runs once per instance (flag 0x10 of the instance) - the
    baker moved SWF's DoInitAction(sprite) into the sprite's own frame.
    """

    def __init__(self, img, o, cache):
        self.kind = img.u8(o)
        self.actions = action_list(img, img.ptr(o + 0x0C), cache)
        img.claim(o, 0x10, 'doaction')


def read_commands(img, o, cache):
    out = []
    seen = set()
    while o is not None:
        if o in seen:
            raise FormatError('%s: command list loops at %#x' % (img.name, o))
        seen.add(o)
        k = img.u8(o)
        if k in (0, 1):
            out.append(Place(img, o, cache))
        elif k == 2:
            out.append(Remove(img, o))
        elif k in (3, 4):
            out.append(Actions(img, o, cache))
        else:
            raise FormatError('%s: command type %d at %#x' % (img.name, k, o))
        o = img.ptr(o + 4)
    return out


class Frame(object):
    """swfFRAME, 8 bytes: +00 u32 (root: background RGBA), +04 first command."""

    def __init__(self, img, o, cache):
        self.word = img.u32(o)
        self.commands = read_commands(img, img.ptr(o + 4), cache)


def read_frames(img, o, n, cache):
    if o is None or n == 0:
        return []
    img.array(o, n, 8, 'frames')
    return [Frame(img, o + 8 * k, cache) for k in range(n)]


# ---------------------------------------------------------------------------
# objects
# ---------------------------------------------------------------------------
class Sprite(object):
    """swfSPRITE: +08 u16 frame count, +0C ptr frames, +10 u32 frame count again."""
    kind = 2

    def __init__(self, img, o, cache):
        self.nframes = img.u16(o + 8)
        self.count2 = img.u32(o + 0x10)
        img.claim(o, 0x14, 'sprite')
        self.frames = read_frames(img, img.ptr(o + 0x0C), self.nframes, cache)


class Gradient(object):
    """swfGRADIENT: +00 6 floats (shape TWIPS -> gradient square), +18 u8
    count, +19 u8 radial, +1C ptr u8 ratios, +20 ptr u32 colours.

    swfSHAPE::Draw evaluates it per vertex, on the raw s16 coordinates: linear
    t = (x' + 16384) * 255/32768, radial t = |(x', y')| * 255/16384 - the SWF
    gradient square, so the matrix here is the INVERSE of the one SWF stores.
    """

    def __init__(self, img, o):
        img.claim(o, 0x24, 'gradient')
        self.matrix = Matrix(*img.floats(o, 6))
        self.mat_raw = bytes(img.d[o:o + 24])
        self.count = img.u8(o + 0x18)
        self.radial = img.u8(o + 0x19)
        self.pad = img.d[o + 0x1A:o + 0x1C]
        r = img.ptr(o + 0x1C)
        c = img.ptr(o + 0x20)
        self.ratios = list(img.d[r:r + self.count]) if r is not None else []
        self.colours = [img.u32(c + 4 * k) for k in range(self.count)] if c is not None else []
        img.array(r, self.count, 1, 'gradient ratios')
        img.array(c, self.count, 4, 'gradient colours')


class FillStyle(object):
    """swfSHAPE::FILLSTYLE, 40 bytes.

        +00 u32 SWF fill type (0 solid, 0x10/0x12 gradient, 0x40..0x43 bitmap)
        +04 u32 colour        +08 6 floats: shape px -> texture S,T
        +20 ptr swfBITMAP     +24 ptr swfGRADIENT
    """

    def __init__(self, img, o, objmap):
        self.type = img.u32(o)
        self.colour = img.u32(o + 4)
        self.matrix = Matrix(*img.floats(o + 8, 6))
        self.mat_raw = bytes(img.d[o + 8:o + 32])
        b = img.u32(o + 0x20)
        self.bitmap = objmap.get(b) if b else None
        if b and self.bitmap is None:
            raise FormatError('%s: fill points at %08X, not a table object' % (img.name, b))
        g = img.ptr(o + 0x24)
        self.gradient = Gradient(img, g) if g is not None else None


class Shape(object):
    """swfSHAPE: +08 fills, +0C lines, +10 display list, +14 u16 nfills,
    +16 u16 nlines. Line style = 8 bytes, u16 width (twips) and u32 colour."""
    kind = 1

    def __init__(self, img, o, objmap):
        img.claim(o, 0x18, 'shape')
        nf, nl = img.u16(o + 0x14), img.u16(o + 0x16)
        fo, lo, do = img.ptr(o + 8), img.ptr(o + 0x0C), img.ptr(o + 0x10)
        self.fills_present, self.lines_present = fo is not None, lo is not None
        self.fills = []
        if fo is not None:
            img.array(fo, nf, 40, 'fill styles')
            self.fills = [FillStyle(img, fo + 40 * k, objmap) for k in range(nf)]
        self.lines = []
        if lo is not None:
            img.array(lo, nl, 8, 'line styles')
            self.lines = [(img.u16(lo + 8 * k), img.u16(lo + 8 * k + 2), img.u32(lo + 8 * k + 4))
                          for k in range(nl)]
        self.ops, n = self._display_list(img, do) if do is not None else ([], 0)
        self.dlist = bytes(img.d[do:do + n]) if do is not None else b''

    @staticmethod
    def _display_list(img, o):
        """swfSHAPE::Draw's interpreter, as data.

            0 end   1 n pts: wide-line polyline   2 n pts: triangle fan
            3 x y: skipped (a moveTo the player ignores)
            4 i: fill style i (1-based, 0 none)   5 i: line style i
        """
        ops = []
        p = o
        while True:
            op = img.u16(p)
            p += 2
            if op == 0:
                break
            if op in (1, 2):
                n = img.u16(p)
                p += 2
                pts = [(img.s16(p + 4 * k), img.s16(p + 4 * k + 2)) for k in range(n)]
                p += 4 * n
                ops.append((op, pts))
            elif op == 3:
                ops.append((3, (img.s16(p), img.s16(p + 2))))
                p += 4
            elif op in (4, 5):
                ops.append((op, img.u16(p)))
                p += 2
            else:
                # the player's switch has a default that just keeps reading;
                # a file that needs it is a file this reader does not know
                raise FormatError('%s: shape op %d at %#x' % (img.name, op, p - 2))
        img.claim(o, p - o, 'display list')
        return ops, p - o


class Texture(object):
    """gfxTexture as baked: +88 u16 w, +8A u16 h, +8C u32 flags, +90 ptr
    gfxTexturePalette, +94 ptr gfxMipChain, +98 load marker. +84 is a pointer
    the constructor relocates (a name when set).

    gfxMipChain: +08 one pointer per level, +28 u8 format (5 = 8 bit, 6 = 4
    bit), +29 u8 last level, +2C/+2E u16 w/h, +30 u8 = 1 when swizzled (else a
    copy of the format). gfxTexturePalette: +02 u16 colours, +04 u8 32-bit
    entries, +10 the entries.
    """

    def __init__(self, img, o):
        self.offset = o
        img.claim(o, 0x9C, 'gfxTexture')
        self.w, self.h = img.u16(o + 0x88), img.u16(o + 0x8A)
        self.flags = img.u32(o + 0x8C)
        nm = img.ptr(o + 0x84)
        self.name = img.cstr(nm).decode('latin-1') if nm is not None else None
        pal = img.ptr(o + 0x90)
        mip = img.ptr(o + 0x94)
        if mip is None:
            raise FormatError('%s: texture at %#x has no mip chain' % (img.name, o))
        self.mip = mip
        self.pal = pal
        img.claim(mip, 0x60, 'gfxMipChain')
        self.format = img.u8(mip + 0x28)
        self.levels = img.u8(mip + 0x29) + 1
        self.tw, self.th = img.u16(mip + 0x2C), img.u16(mip + 0x2E)
        self.swizzle = img.u8(mip + 0x30)
        bpp = {5: 8, 6: 4}.get(self.format)
        if bpp is None:
            raise FormatError('%s: texture format %d at %#x' % (img.name, self.format, mip))
        self.bpp = bpp
        self.pixels = []
        for lv in range(self.levels):
            px = img.ptr(mip + 8 + 4 * lv)
            n = (self.tw >> lv) * (self.th >> lv) * bpp // 8
            img.claim(px, n, 'pixels')
            self.pixels.append(px)
        self.ncolours = 0
        self.pal32 = 0
        if pal is not None:
            self.ncolours = img.u16(pal + 2)
            self.pal32 = img.u8(pal + 4)
            img.claim(pal, 0x10 + self.ncolours * (4 if self.pal32 else 2), 'palette')

    def indices(self, img):
        """Level 0 as one palette index per texel, row-major."""
        w, h = self.tw, self.th
        raw = img.d[self.pixels[0]:self.pixels[0] + w * h * self.bpp // 8]
        if self.swizzle == 1:
            perm = gs_unswizzle_map(w, h, self.bpp)
            if self.bpp == 8:
                return bytearray(raw[q] for q in perm)
            return bytearray((raw[q >> 1] >> (4 * (q & 1))) & 15 for q in perm)
        if self.bpp == 8:
            return bytearray(raw)
        return bytearray((raw[i >> 1] >> (4 * (i & 1))) & 15 for i in range(w * h))

    def palette(self, img):
        """[(r, g, b, a)] in index order, alpha scaled from the GS 0..0x80.

        A 256-entry CLUT is stored in the GS's CSM1 order (entries 8..15 and
        16..23 of every 32 swapped) - gfxTexturePalette::GetEntry undoes the
        same permutation. 16 entries are linear.
        """
        n = self.ncolours
        out = []
        for k in range(n):
            q = k if n == 16 else (k & ~0x18) | ((k >> 1) & 8) | ((k << 1) & 0x10)
            if self.pal32:
                r, g, b, a = img.d[self.pal + 0x10 + 4 * q:self.pal + 0x14 + 4 * q]
            else:
                v = img.u16(self.pal + 0x10 + 2 * q)
                r, g, b = (v & 31) << 3, ((v >> 5) & 31) << 3, ((v >> 10) & 31) << 3
                a = 0x80 if v & 0x8000 else 0
            out.append((r, g, b, min(255, (a * 255 + 64) // 128)))
        return out


_GS_MAPS = {}


def gs_unswizzle_map(w, h, bpp):
    """For each texel, where it sits in a swizzled stream (byte or nibble).

    What the game does when it swizzles (gfxMipChain::Load ->
    convert8to32/convert4to32, alpha 0x4D9D10/0x4D9E58): write the texture
    into emulated GS memory as PSMT8/PSMT4 with buffer width (w+63)>>6, then
    read it back as a PSMCT32 rectangle - w/2 x h/2 words for 8 bit, h/2 x h/4
    for a square 4-bit texture and w/4 x h/2 for a 2:1 one. The stream on disk
    is that rectangle. Undoing it is the same model run backwards; the tables
    are mc2_tex_gs's, which has proved them against MC2's textures.
    """
    key = (w, h, bpp)
    m = _GS_MAPS.get(key)
    if m is not None:
        return m
    gs = sys.modules.get('mc2_tex_gs') or _mod('mc2_tex_gs')
    if bpp == 8:
        rw, rh = w // 2, h // 2
    elif w == h:
        rw, rh = h // 2, h // 4
    else:
        rw, rh = w // 4, h // 2
    dbw32 = (rw + 63) >> 6
    where = {}
    for wy in range(rh):
        for wx in range(rw):
            where[gs.addr32(wx, wy, dbw32)] = wy * rw + wx
    pagesx = max(1, ((w + 63) >> 6) >> 1)
    m = []
    for y in range(h):
        for x in range(w):
            if bpp == 8:
                page = (y >> 6) * pagesx + (x >> 7)
                blk = gs.blockTable32[(y >> 4) & 3][(x >> 4) & 7]
                byte = page * 8192 + blk * 256 + gs.columnTable8[y & 15][x & 15]
                m.append(where[byte >> 2] * 4 + (byte & 3))
            else:
                page = (y >> 7) * pagesx + (x >> 7)
                blk = gs.blockTable4[(y >> 4) & 7][(x >> 5) & 3]
                nib = page * 16384 + blk * 512 + gs.columnTable4[y & 15][x & 31]
                m.append(where[nib >> 3] * 8 + (nib & 7))
    _GS_MAPS[key] = m
    return m


class Bitmap(object):
    """swfBITMAP: +08 ptr gfxTexture (swfFILE::FixupTexture), then +0C u16/u16
    the texture size and +10/+14 floats 1/width and 1/height of the ORIGINAL
    bitmap - the texture is the bitmap padded to powers of two."""
    kind = 4

    def __init__(self, img, o):
        img.claim(o, 0x18, 'bitmap')
        self.tex = Texture(img, img.ptr(o + 8))
        self.tw, self.th = img.u16(o + 0x0C), img.u16(o + 0x0E)
        self.inv_w, self.inv_h = img.f32(o + 0x10), img.f32(o + 0x14)
        self.w = int(round(1.0 / self.inv_w)) if self.inv_w else self.tex.tw
        self.h = int(round(1.0 / self.inv_h)) if self.inv_h else self.tex.th


class Sheet(object):
    """swfFONT::SHEET: +00 ptr textures[], +04 ptr rects (12 bytes per glyph),
    +08 s16 point size (twips), +0A u16 glyphs, +0C ptr u8 texture per glyph
    (or null: all on texture 0), +10 s32 textures.

    rect: u8 u v w h (texels; the player divides by 128) then s16 x0 y0 x1 y1
    in 1/1024 em - swfFONT::SHEET::DrawGlyph.
    """

    def __init__(self, img, o):
        img.claim(o, 0x14, 'font sheet')
        self.size = img.s16(o + 8)
        self.count = img.u16(o + 0x0A)
        ntex = img.s32(o + 0x10)
        to = img.ptr(o)
        self.textures = []
        if to is not None:
            img.array(to, ntex, 4, 'sheet textures')
            self.textures = [Texture(img, img.ptr(to + 4 * k)) for k in range(ntex)]
        ro = img.ptr(o + 4)
        self.rects = []
        if ro is not None:
            img.array(ro, self.count, 12, 'glyph rects')
            for k in range(self.count):
                r = ro + 12 * k
                self.rects.append(tuple(img.d[r:r + 4]) + struct.unpack_from('<4h', img.d, r + 4))
        io_ = img.ptr(o + 0x0C)
        self.texindex = list(img.d[io_:io_ + self.count]) if io_ is not None else None
        img.array(io_, self.count, 1, 'glyph texture index')


class Font(object):
    """swfFONT.

        +08 s16 glyphs            +0C stale glyph-outline table (zeroed)
        +10 ptr u16 code per glyph   +14 ptr u16 advance per glyph (1/1024 em)
        +18 u8[128] ASCII -> glyph   +98 s16 sheets  +9A ascent  +9C descent
        +9E leading               +A0 ptr sheet[]
    """
    kind = 5

    def __init__(self, img, o):
        self.count = img.s16(o + 8)
        nsheets = img.s16(o + 0x98)
        img.claim(o, 0xA0 + 4 * nsheets, 'font')
        self.glyph_table = img.u32(o + 0x0C)
        co, ao = img.ptr(o + 0x10), img.ptr(o + 0x14)
        self.codes = [img.u16(co + 2 * k) for k in range(self.count)] if co is not None else []
        self.advances = [img.u16(ao + 2 * k) for k in range(self.count)] if ao is not None else []
        img.array(co, self.count, 2, 'font codes')
        img.array(ao, self.count, 2, 'font advances')
        self.ascii = list(img.d[o + 0x18:o + 0x98])
        self.ascent, self.descent, self.leading = img.s16(o + 0x9A), img.s16(o + 0x9C), img.s16(o + 0x9E)
        self.sheets = []
        for k in range(nsheets):
            so = img.ptr(o + 0xA0 + 4 * k)
            if so is not None:
                self.sheets.append(Sheet(img, so))
        # the outline table is host memory of the baking tool: its entries do
        # not land in the file. Only the vec_new cookie and the array itself
        # are here, and they are read to account for the bytes, not used.
        go = None
        try:
            go = img.off(self.glyph_table)
        except FormatError:
            go = None
        if go is not None:
            img.claim(go - 0x10, 0x10 + 8 * self.count, 'stale glyph table')


class Text(object):
    """swfTEXT: +08 matrix (6 floats), +20 ptr record stream (u16):

        1 font height   2 lo hi (RGBA)   3 y   4 x   5 n (glyph advance)*n

    x/y/advance in twips; the player divides by the height into 1/1024 em.
    """
    kind = 6

    def __init__(self, img, o):
        img.claim(o, 0x24, 'text')
        self.matrix = Matrix(*img.floats(o + 8, 6))
        self.records = []
        p0 = p = img.ptr(o + 0x20)
        if p is None:
            return
        while True:
            op = img.u16(p)
            p += 2
            if op == 0:
                break
            if op == 1:
                self.records.append(('font', img.u16(p), img.u16(p + 2)))
                p += 4
            elif op == 2:
                self.records.append(('colour', img.u16(p) | (img.u16(p + 2) << 16)))
                p += 4
            elif op == 3:
                self.records.append(('y', img.s16(p)))
                p += 2
            elif op == 4:
                self.records.append(('x', img.s16(p)))
                p += 2
            elif op == 5:
                n = img.u16(p)
                p += 2
                self.records.append(('glyphs', [(img.u16(p + 4 * k), img.s16(p + 4 * k + 2))
                                                for k in range(n)]))
                p += 4 * n
            else:
                raise FormatError('%s: text op %d at %#x' % (img.name, op, p - 2))
        img.claim(p0, p - p0, 'text records')


class EditText(object):
    """swfEDITTEXT.

        +08 ptr initial text (UTF-8)   +0C ptr variable name
        +10 u16 has text               +12 s16 leading (1/1024 em)
        +14 u32 colour                 +18 u16 font (object index)
        +1A u16 height (twips)
        v5: +1C/+1E/+20/+22 s16 width, height, xmin, ymin; +24 u8 align
        v6: +1C/+20/+24/+28 s32 width, height, xmin, ymin; +2C u8 align
        Bounds are in 1/1024 of the height. Align: 0 left, 1 right,
        2 center, 3 justify. Leading stays s16 in both versions.
    """
    kind = 7

    def __init__(self, img, o):
        self.units_bits = 32 if img.version == 6 else 16
        img.claim(o, 0x2D if self.units_bits == 32 else 0x25, 'edittext')
        self.has_text = img.u16(o + 0x10)
        # the constructor relocates +08 only when +10 is set and otherwise
        # points it at a "" of its own: the stored word is then garbage
        to = img.ptr(o + 8) if self.has_text else None
        vo = img.ptr(o + 0x0C)
        self.text = img.cstr(to) if to is not None else b''
        self.var = img.cstr(vo) if vo is not None else b''
        self.leading = img.s16(o + 0x12)
        self.colour = img.u32(o + 0x14)
        self.font = img.u16(o + 0x18)
        self.height = img.u16(o + 0x1A)
        fmt = '<4i' if self.units_bits == 32 else '<4h'
        self.bw, self.bh, self.xmin, self.ymin = struct.unpack_from(fmt, img.d, o + 0x1C)
        self.align = img.u8(o + (0x2C if self.units_bits == 32 else 0x24))


class Button(object):
    """swfBUTTON: +08 u8 ?, +09 u8 records, +0A u8 conditions, +0C ptr
    BUTTONRECORD[] (40 bytes), +10 ptr BUTTONCONDACTION[] (8 bytes).

    record: +00 u8 states (1 up 2 over 4 down 8 hit), +02 u16 depth, +04 six
    floats, +1C cxform, +24 ptr object. condition: +00 u16 the two bytes of
    SWF's CondActionData (bit 0 IdleToOverUp ... key code in bits 9..15),
    +04 ptr actions.
    """
    kind = 3

    def __init__(self, img, o, objmap, cache):
        img.claim(o, 0x14, 'button')
        self.byte8 = img.u8(o + 8)
        nr, nc = img.u8(o + 9), img.u8(o + 0x0A)
        ro, co = img.ptr(o + 0x0C), img.ptr(o + 0x10)
        self.records = []
        if ro is not None:
            img.array(ro, nr, 40, 'button records')
            for k in range(nr):
                r = ro + 40 * k
                tgt = img.u32(r + 0x24)
                if tgt not in objmap:
                    raise FormatError('%s: button record points at %08X' % (img.name, tgt))
                self.records.append((img.u8(r), img.u16(r + 2), Matrix(*img.floats(r + 4, 6)),
                                     read_cxform(img, r + 0x1C), objmap[tgt]))
        self.conds = []
        if co is not None:
            img.array(co, nc, 8, 'button conditions')
            for k in range(nc):
                c = co + 8 * k
                self.conds.append((img.u16(c), action_list(img, img.ptr(c + 4), cache)))


class Sound(object):
    """swfSOUND: nothing past the vtable; sounds are played by name."""
    kind = 8

    def __init__(self, img, o):
        img.claim(o, 8, 'sound')


class Movie(object):
    """swfFILE at +0x80, 0x40 bytes:

        +00 u8 0   +04 vtable   +08 u16 frames   +0C ptr frames
        +10 ptr object table (index 0 unused)    +14 u8 SWF version
        +18 f32 xmin xmax ymin ymax (pixels)     +28 u16 frame rate (8.8)
        +2A u16 object count + 1                 +30 u32 frames again
    """

    def __init__(self, data, name='?'):
        img = self.img = Image(data, name)
        o = HEADER
        if img.u8(o) != 0:
            raise FormatError('%s: payload does not start with swfFILE' % name)
        img.claim(o, 0x34, 'swfFILE')
        self.swf_version = img.u8(o + 0x14)
        self.rect = img.floats(o + 0x18, 4)
        self.rate = img.u16(o + 0x28)
        self.nframes = img.u16(o + 8)
        self.count2 = img.u32(o + 0x30)
        n = img.u16(o + 0x2A)
        to = img.ptr(o + 0x10)
        img.array(to, n, 4, 'object table')
        self.table_zero = img.u32(to)
        vas = [img.u32(to + 4 * k) for k in range(n)]
        offs = [None] + [img.off(v) if v else None for v in vas[1:]]
        objmap = {}
        for k in range(1, n):
            if vas[k]:
                objmap[vas[k]] = k
        self.cache = {}
        self.objects = [None] * n
        for k in range(1, n):
            oo = offs[k]
            if oo is None:
                continue
            t = img.u8(oo)
            if t == 1:
                ob = Shape(img, oo, objmap)
            elif t == 2:
                ob = Sprite(img, oo, self.cache)
            elif t == 3:
                ob = Button(img, oo, objmap, self.cache)
            elif t == 4:
                ob = Bitmap(img, oo)
            elif t == 5:
                ob = Font(img, oo)
            elif t == 6:
                ob = Text(img, oo)
            elif t == 7:
                ob = EditText(img, oo)
            elif t == 8:
                ob = Sound(img, oo)
            else:
                raise FormatError('%s: object %d has type %d' % (name, k, t))
            ob.index = k
            ob.offset = oo
            self.objects[k] = ob
        self.frames = read_frames(img, img.ptr(o + 0x0C), self.nframes, self.cache)


def load(path):
    return Movie(open(path, 'rb').read(), os.path.basename(path))


# ---------------------------------------------------------------------------
# SWF: bits and the small records
# ---------------------------------------------------------------------------
class Bits(object):
    """MSB-first bit packer - every SWF bit field is stored this way, and a
    byte field after bit fields starts on the next byte."""
    __slots__ = ('buf', 'acc', 'n')

    def __init__(self):
        self.buf = bytearray()
        self.acc = 0
        self.n = 0

    def ub(self, nbits, v):
        if nbits <= 0:
            return
        self.acc = (self.acc << nbits) | (int(v) & ((1 << nbits) - 1))
        self.n += nbits
        while self.n >= 8:
            self.n -= 8
            self.buf.append((self.acc >> self.n) & 0xFF)
        self.acc &= (1 << self.n) - 1

    sb = ub     # two's complement, masked to the width

    def align(self):
        if self.n:
            self.buf.append((self.acc << (8 - self.n)) & 0xFF)
            self.acc = self.n = 0

    def raw(self, b):
        self.align()
        self.buf += b

    def u8(self, v):
        self.raw(struct.pack('<B', v))

    def u16(self, v):
        self.raw(struct.pack('<H', v))

    def s16(self, v):
        self.raw(struct.pack('<h', v))

    def u32(self, v):
        self.raw(struct.pack('<I', v))

    def done(self):
        self.align()
        return bytes(self.buf)


def sbits(*vals):
    """Width of a signed field that holds every value (at least 1)."""
    n = 1
    for v in vals:
        b = (v if v >= 0 else ~v).bit_length() + 1
        if b > n:
            n = b
    return n


def put_rect(b, xmin, xmax, ymin, ymax):
    n = sbits(xmin, xmax, ymin, ymax)
    b.ub(5, n)
    for v in (xmin, xmax, ymin, ymax):
        b.sb(n, v)
    b.align()


def fixed(f):
    return int(round(f * 65536.0))


def put_matrix(b, m, twips_scale=20.0, scale=None, rotate=None):
    """A Matrix as SWF's MATRIX. `twips_scale` converts the translation: 20 for
    the pixel matrices of the file, 1 for those already in twips. `scale` and
    `rotate` force HasScale/HasRotate (a PlaceObject2 of the .pck says in its
    flags whether it carries them, identity values or not)."""
    sx, sy, r0, r1 = fixed(m.a), fixed(m.d), fixed(m.b), fixed(m.c)
    tx, ty = int(round(m.tx * twips_scale)), int(round(m.ty * twips_scale))
    if scale is None:
        scale = (sx, sy) != (65536, 65536)
    if rotate is None:
        rotate = (r0, r1) != (0, 0)
    if scale:
        b.ub(1, 1)
        n = sbits(sx, sy)
        b.ub(5, n)
        b.sb(n, sx)
        b.sb(n, sy)
    else:
        b.ub(1, 0)
    if rotate:
        b.ub(1, 1)
        n = sbits(r0, r1)
        b.ub(5, n)
        b.sb(n, r0)
        b.sb(n, r1)
    else:
        b.ub(1, 0)
    n = sbits(tx, ty) if (tx or ty) else 0
    b.ub(5, n)
    b.sb(n, tx)
    b.sb(n, ty)
    b.align()


def put_cxform(b, cx):
    """CXFORMWITHALPHA: multipliers in 1/256 and adds - the file's x4 both."""
    mul = [4 * v for v in cx.mul]
    add = [4 * v for v in cx.add]
    hm, ha = mul != [256] * 4, add != [0] * 4
    n = sbits(*((mul if hm else []) + (add if ha else []) + [0]))
    b.ub(1, ha)
    b.ub(1, hm)
    b.ub(4, n)
    for v in (mul if hm else []) + (add if ha else []):
        b.sb(n, v)
    b.align()


def rgba_bytes(u):
    return bytes(rgba(u))


def edit_units(t, h, bits=16):
    """What the baker stored for t twips in an EditText of height h (twips):
    trunc(t * 1024 / h), toward zero, kept in an s16 - measured on the 6618
    EditTexts of the alpha, bounds, origin and leading alike. The s16 does
    overflow: 70 fields 540 px wide hold -28713 (36823 - 65536)."""
    if not h:
        return t
    q = abs(t) * 1024 // h
    q = -q if t < 0 else q
    sign = 1 << (bits - 1)
    return ((q + sign) & ((1 << bits) - 1)) - sign


def edit_twips(v, h, length=False, bits=16):
    """The twips edit_units turns back into v - the nearest such value, so
    that a .pck -> .swf -> .pck trip gives the same numbers again. A negative
    width or height (`length`) is read as the overflow it is."""
    if not h:
        return v
    bases = (v + 0x10000, v) if (bits == 16 and length and v < 0) else (v,)
    for base in bases:
        t0 = int(round(base * h / 1024.0))
        for d in (0, -1, 1, -2, 2, -3, 3):
            if edit_units(t0 + d, h, bits) == v:
                return t0 + d
    return int(round(v * h / 1024.0))


def swf_tag(code, body):
    n = len(body)
    if n < 0x3F:
        return struct.pack('<H', (code << 6) | n) + body
    return struct.pack('<HI', (code << 6) | 0x3F, n) + body


T_END, T_SHOWFRAME, T_SETBG, T_DOACTION = 0, 1, 9, 12
T_PLACE2, T_REMOVE2, T_SHAPE3, T_TEXT2, T_BUTTON2 = 26, 28, 32, 33, 34
T_LOSSLESS2, T_EDITTEXT, T_SPRITE, T_EXPORT, T_FONT2, T_INITACTION = 36, 37, 39, 56, 48, 59
T_BINARY = 87


# ---------------------------------------------------------------------------
# the meta block: what a SWF cannot say about the .pck it came from
# ---------------------------------------------------------------------------
META_NAME = 'mc3_pck_meta'
META_MAGIC = b'MC3M'
META_VERSION = 1
M_MOVIE, M_BITMAP, M_SHAPE, M_FONT = 0, 1, 2, 3
M_CLIP_KEYS = 4
M_FILL_TYPES = 5
M_BUTTON = 6


def tag_hash(body):
    """What ties a meta record to the tag it was written with: if the tag is
    edited, the hash no longer matches and the record is ignored."""
    return hashlib.sha1(body).digest()[:8]


def meta_record(kind, cid, payload):
    return struct.pack('<BHI', kind, cid, len(payload)) + payload


def read_meta(data):
    """{(kind, cid): payload} of a meta block, {} if it is not one."""
    if data[:4] != META_MAGIC:
        return {}
    ver, n = struct.unpack_from('<HH', data, 4)
    if ver != META_VERSION:
        raise FormatError('meta block version %d, this tool reads %d' % (ver, META_VERSION))
    out = {}
    p = 8
    for _ in range(n):
        kind, cid, ln = struct.unpack_from('<BHI', data, p)
        p += 7
        out[(kind, cid)] = data[p:p + ln]
        p += ln
    return out


# ---------------------------------------------------------------------------
# SHAPE: from triangle fans back to outlines
# ---------------------------------------------------------------------------
def _area2(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])


def _separated(t1, t2):
    """No overlap of positive area between two triangles wound with area2 > 0
    (touching along an edge or at a corner is not overlap)."""
    for tri, other in ((t1, t2), (t2, t1)):
        for k in range(3):
            ax, ay = tri[k]
            bx, by = tri[(k + 1) % 3]
            ex, ey = bx - ax, by - ay
            if all(ex * (py - ay) - ey * (px - ax) <= 0 for px, py in other):
                return True
    return False


class _Layer(object):
    __slots__ = ('tris', 'lines', 'boxes')

    def __init__(self):
        self.tris = []      # (tri, fill)
        self.lines = []     # (line style, [points])
        self.boxes = []

    def collides(self, tri, fill):
        x0 = min(p[0] for p in tri)
        x1 = max(p[0] for p in tri)
        y0 = min(p[1] for p in tri)
        y1 = max(p[1] for p in tri)
        for (bx0, by0, bx1, by1), (t, f) in zip(self.boxes, self.tris):
            if bx1 <= x0 or x1 <= bx0 or by1 <= y0 or y1 <= by0:
                continue
            if not _separated(tri, t):
                return True
        return False

    def add(self, tri, fill):
        self.tris.append((tri, fill))
        self.boxes.append((min(p[0] for p in tri), min(p[1] for p in tri),
                           max(p[0] for p in tri), max(p[1] for p in tri)))


def shape_layers(sh):
    """The display list as SWF style layers.

    swfSHAPE::Draw paints in list order, so a later fan covers an earlier one.
    A SWF shape has no order inside a layer - the fills of one layer must not
    overlap - so a fan that would overlap what the layer already holds, or one
    that comes after a line, opens a new layer (StateNewStyles). In practice
    the baker tessellated each fill region on its own and that never happens
    inside one original layer; the test is what proves it file by file.
    Style index 0 keeps the previous style, exactly like the player's switch.
    """
    layers = [_Layer()]
    fill = line = 0
    extra = {}
    for op in sh.ops:
        k = op[0]
        if k == 4:
            if op[1]:
                fill = op[1]
        elif k == 5:
            if op[1]:
                line = op[1]
        elif k == 2:
            pts = op[1]
            f = fill or extra.setdefault('fill', len(sh.fills) + 1)
            cur = layers[-1]
            tris = []
            for i in range(1, len(pts) - 1):
                tri = (pts[0], pts[i], pts[i + 1])
                a = _area2(*tri)
                if a == 0:
                    continue
                if a < 0:
                    tri = (tri[0], tri[2], tri[1])
                tris.append(tri)
            if cur.lines or any(cur.collides(t, f) for t in tris):
                cur = _Layer()
                layers.append(cur)
            for t in tris:
                cur.add(t, f)
        elif k == 1:
            layers[-1].lines.append((line or extra.setdefault('line', len(sh.lines) + 1), op[1]))
    return layers, extra


def layer_edges(layer):
    """[(a, b, fill0, fill1, line)] for one layer, with the shared edges gone.

    Every triangle is wound with area2 > 0, which with y pointing down puts
    its inside on the RIGHT of each edge - SWF's FillStyle1. An edge used by
    two triangles in opposite directions is interior: dropped when both sides
    are the same fill, merged into one edge with a fill on each side when not.
    """
    groups = collections.OrderedDict()
    for tri, f in layer.tris:
        for k in range(3):
            a, b = tri[k], tri[(k + 1) % 3]
            groups.setdefault((a, b) if a < b else (b, a), []).append((a, b, f))
    out = []
    for lst in groups.values():
        if len(lst) == 2 and lst[0][0] == lst[1][1] and lst[0][1] == lst[1][0]:
            (a, b, f1), (_a, _b, f2) = lst
            if f1 != f2:
                out.append((a, b, f2, f1, 0))
            continue
        for a, b, f in lst:
            out.append((a, b, 0, f, 0))
    for ln, pts in layer.lines:
        for k in range(len(pts) - 1):
            if pts[k] != pts[k + 1]:
                out.append((pts[k], pts[k + 1], 0, 0, ln))
    return out


def chain(edges):
    """Join (a, b) edges into as few connected paths as possible."""
    by_start = collections.defaultdict(list)
    indeg = collections.Counter()
    for i, (a, b) in enumerate(edges):
        by_start[a].append(i)
        indeg[b] += 1
    used = [False] * len(edges)
    starts = [p for p in by_start if len(by_start[p]) > indeg[p]] + list(by_start)
    paths = []
    for s in starts:
        while by_start[s]:
            i = by_start[s].pop()
            if used[i]:
                continue
            used[i] = True
            path = [edges[i][0], edges[i][1]]
            cur = edges[i][1]
            while by_start[cur]:
                j = by_start[cur].pop()
                if used[j]:
                    continue
                used[j] = True
                path.append(edges[j][1])
                cur = edges[j][1]
            paths.append(path)
    return paths


def put_edges(b, path):
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        dx, dy = x1 - x0, y1 - y0
        n = max(sbits(dx, dy), 2)
        b.ub(1, 1)
        b.ub(1, 1)
        b.ub(4, n - 2)
        if dx and dy:
            b.ub(1, 1)
            b.sb(n, dx)
            b.sb(n, dy)
        else:
            b.ub(1, 0)
            b.ub(1, 1 if dx == 0 else 0)
            b.sb(n, dy if dx == 0 else dx)


def put_style_change(b, pos, styles, cur, nfb, nlb, move):
    f0, f1, ln = styles
    c0, c1, cl = cur
    b.ub(1, 0)
    b.ub(1, 0)                       # StateNewStyles
    b.ub(1, ln != cl)
    b.ub(1, f1 != c1)
    b.ub(1, f0 != c0)
    b.ub(1, 1 if move else 0)
    if move:
        n = sbits(pos[0], pos[1])
        b.ub(5, n)
        b.sb(n, pos[0])
        b.sb(n, pos[1])
    if f0 != c0:
        b.ub(nfb, f0)
    if f1 != c1:
        b.ub(nfb, f1)
    if ln != cl:
        b.ub(nlb, ln)


def _ubits(v):
    return max(1, v.bit_length()) if v else 0


# ---------------------------------------------------------------------------
# FONT: the sheets traced back into outlines
# ---------------------------------------------------------------------------
_MS_SEGS = {1: (('L', 'B'),), 2: (('B', 'R'),), 3: (('L', 'R'),), 4: (('T', 'R'),),
            6: (('T', 'B'),), 7: (('L', 'T'),), 8: (('L', 'T'),), 9: (('T', 'B'),),
            11: (('T', 'R'),), 12: (('L', 'R'),), 13: (('B', 'R'),), 14: (('L', 'B'),)}


def trace(alpha, w, h, level=0.5):
    """Marching squares over a w x h coverage grid (0..1), zero-padded.

    Returns closed loops in texel coordinates (texel i spans [i, i+1], its
    sample sits at i + 0.5), oriented for SWF fill style 0: outer contours
    with area2 < 0 and holes with area2 > 0 (y down), i.e. ink on the LEFT.
    """
    W, H = w + 2, h + 2

    def g(i, j):
        if 1 <= i <= w and 1 <= j <= h:
            return alpha[(j - 1) * w + (i - 1)]
        return 0.0

    def pos(key):
        kind, i, j = key
        if kind == 'h':                               # between (i,j) and (i+1,j)
            a, c = g(i, j), g(i + 1, j)
            t = 0.5 if a == c else (level - a) / (c - a)
            return (i - 0.5 + t, j - 0.5)
        a, c = g(i, j), g(i, j + 1)                   # between (i,j) and (i,j+1)
        t = 0.5 if a == c else (level - a) / (c - a)
        return (i - 0.5, j - 0.5 + t)

    adj = collections.defaultdict(list)
    for j in range(H - 1):
        for i in range(W - 1):
            tl, tr, br, bl = g(i, j), g(i + 1, j), g(i + 1, j + 1), g(i, j + 1)
            case = ((tl >= level) << 3) | ((tr >= level) << 2) | ((br >= level) << 1) | (bl >= level)
            if case in (0, 15):
                continue
            T, B = ('h', i, j), ('h', i, j + 1)
            L, R = ('v', i, j), ('v', i + 1, j)
            ed = {'T': T, 'B': B, 'L': L, 'R': R}
            if case in (5, 10):
                centre = (tl + tr + br + bl) / 4.0 >= level
                if case == 5:
                    segs = (('L', 'T'), ('B', 'R')) if centre else (('T', 'R'), ('L', 'B'))
                else:
                    segs = (('T', 'R'), ('L', 'B')) if centre else (('L', 'T'), ('B', 'R'))
            else:
                segs = _MS_SEGS[case]
            for p, q in segs:
                adj[ed[p]].append(ed[q])
                adj[ed[q]].append(ed[p])
    loops = []
    seen = set()
    for start in list(adj):
        if start in seen:
            continue
        loop = [start]
        seen.add(start)
        prev, cur = None, start
        while True:
            nxt = [k for k in adj[cur] if k != prev]
            if not nxt:
                break
            n = nxt[0]
            if n == start:
                break
            if n in seen:
                break
            seen.add(n)
            loop.append(n)
            prev, cur = cur, n
        if len(loop) >= 3:
            loops.append([pos(k) for k in loop])
    # orientation by nesting depth: even = ink outline, odd = hole
    def area2(pts):
        return sum(pts[k][0] * pts[(k + 1) % len(pts)][1] - pts[(k + 1) % len(pts)][0] * pts[k][1]
                   for k in range(len(pts)))

    def inside(pt, pts):
        x, y = pt
        c = False
        for k in range(len(pts)):
            (x0, y0), (x1, y1) = pts[k], pts[(k + 1) % len(pts)]
            if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
                c = not c
        return c
    out = []
    for k, lp in enumerate(loops):
        depth = sum(1 for j, other in enumerate(loops) if j != k and inside(lp[0], other))
        a = area2(lp)
        if (depth % 2 == 0) != (a < 0):
            lp = lp[::-1]
        out.append(lp)
    return out


def _simplify(pts):
    """Drop repeated and collinear points of a closed loop of int points."""
    q = []
    for p in pts:
        if not q or q[-1] != p:
            q.append(p)
    if len(q) > 1 and q[0] == q[-1]:
        q.pop()
    changed = True
    while changed and len(q) > 3:
        changed = False
        r = []
        n = len(q)
        for k in range(n):
            a, b, c = q[k - 1], q[k], q[(k + 1) % n]
            if _area2(a, b, c) == 0:
                changed = True
                continue
            r.append(b)
        q = r
    return q


def glyph_loops(img, font):
    """{glyph: [loop in 1/1024 em]} from the largest sheet of the font."""
    if not font.sheets:
        return {}
    sheet = max(font.sheets, key=lambda s: s.size)
    pix = {}
    out = {}
    for g, (u, v, w, h, x0, y0, x1, y1) in enumerate(sheet.rects):
        if not w or not h or x1 == x0 or y1 == y0:
            out[g] = []
            continue
        ti = sheet.texindex[g] if sheet.texindex is not None else 0
        if ti not in pix:
            t = sheet.textures[ti]
            pal = t.palette(img)
            idx = t.indices(img)
            pix[ti] = (t.tw, [pal[c][3] / 255.0 for c in idx])
        tw, cov = pix[ti]
        grid = [cov[(v + j) * tw + (u + i)] if (u + i) < tw and (v + j) * tw < len(cov) else 0.0
                for j in range(h) for i in range(w)]
        sx, sy = (x1 - x0) / float(w), (y1 - y0) / float(h)
        loops = []
        for lp in trace(grid, w, h):
            q = _simplify([(int(round(x0 + px * sx)), int(round(y0 + py * sy))) for px, py in lp])
            if len(q) >= 3:
                loops.append(q)
        out[g] = loops
    return out


def font_metrics(ft):
    """Ascent, descent, leading - with the allocator's 0xCDCD read as unset.

    The two fonts that have no advance table (garage_x.pck #5 and #8, used
    only by static TEXT, which carries its own advances) were never given
    metrics either: the three words are the 0xCD fill. They go out as 0.
    """
    return tuple(0 if v == -0x3233 else v for v in (ft.ascent, ft.descent, ft.leading))


def glyph_shape(loops):
    """A DefineFont2 glyph SHAPE: 1 fill bit, no line bits, fill style 0."""
    b = Bits()
    b.ub(4, 1)
    b.ub(4, 0)
    first = True
    for lp in loops:
        b.ub(1, 0)
        b.ub(1, 0)
        b.ub(1, 0)
        b.ub(1, 0)
        b.ub(1, 1 if first else 0)
        b.ub(1, 1)
        n = sbits(lp[0][0], lp[0][1])
        b.ub(5, n)
        b.sb(n, lp[0][0])
        b.sb(n, lp[0][1])
        if first:
            b.ub(1, 1)
            first = False
        put_edges(b, lp + [lp[0]])
    b.ub(1, 0)
    b.ub(5, 0)
    return b.done()


# ---------------------------------------------------------------------------
# the writer
# ---------------------------------------------------------------------------
class SwfWriter(object):
    """One .pck in, one .swf out. Character ids ARE the object-table indices,
    so `#123` in a dump of the .pck is character 123 in any SWF tool."""

    def __init__(self, movie, sheets=True, meta=True):
        self.m = movie
        self.img = movie.img
        self.sheets = sheets
        self.meta = [] if meta else None
        self.out = []
        self.defined = set()
        self.next_id = len(movie.objects)
        self.exports = []
        self.stats = collections.Counter()
        self.font_glyphs = {}

    # -- helpers ---------------------------------------------------------
    def need(self, cid):
        if cid not in self.defined:
            raise FormatError('%s: character %d used before it is defined' % (self.img.name, cid))

    def deps(self, ob):
        if isinstance(ob, Shape):
            return [f.bitmap for f in ob.fills if f.bitmap is not None]
        if isinstance(ob, Sprite):
            return [c.char for fr in ob.frames for c in fr.commands
                    if isinstance(c, Place) and c.char is not None]
        if isinstance(ob, Button):
            return [r[4] for r in ob.records]
        if isinstance(ob, Text):
            return [r[1] for r in ob.records if r[0] == 'font']
        if isinstance(ob, EditText):
            return [ob.font]
        return []

    def define(self, k, stack=()):
        if k in self.defined:
            return
        if k in stack:
            raise FormatError('%s: object %d contains itself' % (self.img.name, k))
        ob = self.m.objects[k]
        if ob is None:
            raise FormatError('%s: reference to empty object slot %d' % (self.img.name, k))
        for d in self.deps(ob):
            self.define(d, stack + (k,))
        fn = {1: self.w_shape, 2: self.w_sprite, 3: self.w_button, 4: self.w_bitmap,
              5: self.w_font, 6: self.w_text, 7: self.w_edittext, 8: self.w_sound}[ob.kind]
        fn(ob)
        self.defined.add(k)
        self.stats[OBJ_NAMES[ob.kind]] += 1

    # -- bitmaps ---------------------------------------------------------
    def lossless(self, cid, tex, inv=None):
        """DefineBitsLossless2, colour-mapped: the texture's own indices and
        palette, nothing resampled. SWF wants the palette premultiplied - which
        loses the colour of every entry that is not opaque, so the CLUT as
        stored goes into the meta block too (with 1/w, 1/h of the bitmap the
        baker resampled: the texture is that bitmap scaled to powers of two)."""
        w, h = tex.tw, tex.th
        pal = tex.palette(self.img)
        idx = tex.indices(self.img)
        table = bytearray()
        for r, g, bl, a in pal:
            table += bytes((r * a // 255, g * a // 255, bl * a // 255, a))
        stride = (w + 3) & ~3
        rows = bytearray()
        for y in range(h):
            rows += idx[y * w:(y + 1) * w] + bytes(stride - w)
        body = struct.pack('<HBHHB', cid, 3, w, h, len(pal) - 1) + zlib.compress(bytes(table + rows), 9)
        self.out.append(swf_tag(T_LOSSLESS2, body))
        if self.meta is not None:
            esz = 4 if tex.pal32 else 2
            raw = self.img.d[tex.pal + 0x10:tex.pal + 0x10 + esz * tex.ncolours]
            pay = tag_hash(body) + struct.pack('<BH', tex.pal32, tex.ncolours) + raw
            pay += struct.pack('<B', inv is not None) + (inv or b'')
            self.meta.append(meta_record(M_BITMAP, cid, pay))

    def w_bitmap(self, ob):
        self.lossless(ob.index, ob.tex, bytes(self.img.d[ob.offset + 0x10:ob.offset + 0x18]))

    def w_sound(self, ob):
        # swfSOUND carries nothing; there is no sound to write
        self.stats['sound skipped'] += 1

    # -- shapes ----------------------------------------------------------
    def put_fill_array(self, b, sh, extra):
        fills = list(sh.fills)
        n = len(fills) + (1 if 'fill' in extra else 0)
        if n < 255:
            b.u8(n)
        else:
            b.u8(255)
            b.u16(n)
        for f in fills:
            t = f.type & 0xFF
            b.u8(t)
            if t == 0x00:
                b.raw(rgba_bytes(f.colour))
            elif t in (0x10, 0x12, 0x13):
                g = f.gradient
                if g is None:
                    raise FormatError('%s: gradient fill without a gradient' % self.img.name)
                inv = g.matrix.inverse() or Matrix()
                put_matrix(b, inv, 1.0)
                b.ub(2, 0)
                b.ub(2, 0)
                b.ub(4, g.count)
                b.align()
                for r, c in zip(g.ratios, g.colours):
                    b.u8(r)
                    b.raw(rgba_bytes(c))
                if t == 0x13:
                    b.s16(0)
            elif 0x40 <= t <= 0x43:
                if f.bitmap is None:
                    # the "no bitmap" fill Flash MX leaves in every shape:
                    # never selected by the display list, kept so that the
                    # indices of the others do not move
                    b.u16(0xFFFF)
                    inv = Matrix(0.05, 0, 0, 0.05, 0, 0).dot(f.matrix).inverse()
                    put_matrix(b, inv or Matrix(), 1.0)
                else:
                    self.need(f.bitmap)
                    tex = self.m.objects[f.bitmap].tex
                    # twips -> pixels -> S,T (the file's matrix) -> texels
                    a = Matrix(0.05, 0, 0, 0.05, 0, 0).dot(f.matrix).dot(Matrix(tex.tw, 0, 0, tex.th, 0, 0))
                    inv = a.inverse()
                    if inv is None:
                        self.stats['singular bitmap matrix'] += 1
                        inv = Matrix(20, 0, 0, 20, 0, 0)
                    b.u16(f.bitmap)
                    put_matrix(b, inv, 1.0)
            else:
                raise FormatError('%s: fill type %#x' % (self.img.name, t))
        if 'fill' in extra:
            b.u8(0)
            b.raw(b'\xff\xff\xff\xff')

    def put_line_array(self, b, sh, extra):
        n = len(sh.lines) + (1 if 'line' in extra else 0)
        if n < 255:
            b.u8(n)
        else:
            b.u8(255)
            b.u16(n)
        for wdt, _pad, col in sh.lines:
            b.u16(wdt)
            b.raw(rgba_bytes(col))
        if 'line' in extra:
            b.u16(20)
            b.raw(b'\xff\xff\xff\xff')

    def w_shape(self, sh):
        layers, extra = shape_layers(sh)
        nfill = len(sh.fills) + (1 if 'fill' in extra else 0)
        nline = len(sh.lines) + (1 if 'line' in extra else 0)
        nfb, nlb = _ubits(nfill), _ubits(nline)
        xs, ys = [], []
        wmax = max([l[0] for l in sh.lines] + [20 if 'line' in extra else 0])
        for op in sh.ops:
            if op[0] in (1, 2):
                for x, y in op[1]:
                    xs.append(x)
                    ys.append(y)
        has_line = any(op[0] == 1 for op in sh.ops)
        pad = (wmax + 1) // 2 if has_line else 0
        if xs:
            bounds = (min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad)
        else:
            bounds = (0, 0, 0, 0)
        b = Bits()
        b.u16(sh.index)
        put_rect(b, *bounds)
        self.put_fill_array(b, sh, extra)
        self.put_line_array(b, sh, extra)
        b.ub(4, nfb)
        b.ub(4, nlb)
        cur = (0, 0, 0)
        for li, layer in enumerate(layers):
            if li:
                b.ub(1, 0)
                b.ub(1, 1)
                b.ub(4, 0)
                self.put_fill_array(b, sh, extra)
                self.put_line_array(b, sh, extra)
                b.ub(4, nfb)
                b.ub(4, nlb)
                cur = (0, 0, 0)
                self.stats['extra shape layers'] += 1
            groups = collections.OrderedDict()
            for a, c, f0, f1, ln in layer_edges(layer):
                groups.setdefault((f0, f1, ln), []).append((a, c))
            for style, edges in groups.items():
                for path in chain(edges):
                    # always an absolute move: one record per path either way
                    put_style_change(b, path[0], style, cur, nfb, nlb, True)
                    cur = style
                    put_edges(b, path)
        b.ub(1, 0)
        b.ub(5, 0)
        body = b.done()
        self.out.append(swf_tag(T_SHAPE3, body))
        if self.meta is not None:
            # the fans as baked, and the float matrices the SWF can only round
            pay = tag_hash(body) + struct.pack('<BHHI', sh.fills_present | (sh.lines_present << 1),
                                               len(sh.fills), len(sh.lines), len(sh.dlist)) + sh.dlist
            for f in sh.fills:
                pay += f.mat_raw + struct.pack('<B', f.gradient is not None)
                if f.gradient is not None:
                    pay += f.gradient.mat_raw
            self.meta.append(meta_record(M_SHAPE, sh.index, pay))
            if any(f.type != (f.type & 0xFF) for f in sh.fills):
                self.meta.append(meta_record(M_FILL_TYPES, sh.index, tag_hash(body) +
                                 struct.pack('<%dI' % len(sh.fills), *(f.type for f in sh.fills))))

    # -- timelines -------------------------------------------------------
    def control_tags(self, frames, owner):
        """PlaceObject2/RemoveObject2/DoAction + ShowFrame, frame by frame.

        swfINSTANCE::AddChild replaces what sits at a depth; SWF wants that
        said with PlaceFlagMove, so the depths in use are tracked."""
        tags = []
        live = set()
        key_records = []
        for fk, fr in enumerate(frames):
            if owner is None and fk and fr.word != frames[fk - 1].word:
                tags.append(swf_tag(T_SETBG, rgba_bytes(fr.word)[:3]))
            for ci, c in enumerate(fr.commands):
                if isinstance(c, Place):
                    tag = self.place(c, c.depth in live)
                    tags.append(tag)
                    keys = [key for flags, _acts, key in c.events]
                    if self.meta is not None and any(key != (key & 255 if flags & (1 << 17) else 0)
                            for flags, _acts, key in c.events):
                        body = _walk(tag, 0)[0][1]
                        key_records.append(struct.pack('<HHH', fk, ci, len(keys)) + tag_hash(body) +
                                           struct.pack('<%dI' % len(keys), *keys))
                    live.add(c.depth)
                elif isinstance(c, Remove):
                    tags.append(swf_tag(T_REMOVE2, struct.pack('<H', c.depth)))
                    live.discard(c.depth)
                elif c.kind == 3:
                    tags.append(swf_tag(T_DOACTION, c.actions.code))
                else:
                    # DoInitAction: SWF keeps it outside the sprite, keyed by it
                    self.init_actions.append((owner or 0, c.actions.code))
            tags.append(swf_tag(T_SHOWFRAME, b''))
        if key_records:
            self.meta.append(meta_record(M_CLIP_KEYS, owner or 0,
                                         struct.pack('<H', len(key_records)) + b''.join(key_records)))
        return tags

    def place(self, c, occupied):
        has_char = c.char is not None
        if has_char:
            self.need(c.char)
        # a CLIPEVENT array - even an empty one - is a clip action block, so
        # the way back makes a PlaceObject2ClipEvent with an array again
        clip = bool(c.events or c.events_present or (c.kind == 1 and c.event_flags))
        b = Bits()
        b.ub(1, 1 if clip else 0)
        b.ub(1, 0)                                  # clip depth: the player has none
        b.ub(1, c.name is not None)
        b.ub(1, 0)                                  # ratio: likewise
        b.ub(1, c.cxform is not None)
        b.ub(1, c.matrix is not None)
        b.ub(1, has_char)
        b.ub(1, (not has_char) or occupied)
        b.u16(c.depth)
        if has_char:
            b.u16(c.char)
        if c.matrix is not None:
            put_matrix(b, c.matrix, scale=bool(c.flags & 1), rotate=bool(c.flags & 2))
        if c.cxform is not None:
            put_cxform(b, c.cxform)
        if c.name is not None:
            b.raw(c.name.encode('latin-1') + b'\0')
        if clip:
            b.u16(0)
            b.u32(c.event_flags)
            for flags, acts, key in c.events:
                code = acts.code if acts is not None else b'\0'
                extra = b''
                if flags & (1 << 17):               # ClipEventKeyPress carries a key
                    extra = struct.pack('<B', key & 0xFF)
                b.u32(flags)
                b.u32(len(extra) + len(code))
                b.raw(extra + code)
            b.u32(0)
        return swf_tag(T_PLACE2, b.done())

    def w_sprite(self, sp):
        tags = self.control_tags(sp.frames, sp.index)
        body = struct.pack('<HH', sp.index, sp.nframes) + b''.join(tags) + swf_tag(T_END, b'')
        self.out.append(swf_tag(T_SPRITE, body))

    # -- buttons ---------------------------------------------------------
    def w_button(self, bt):
        b = Bits()
        b.u16(bt.index)
        b.u8(1 if bt.byte8 else 0)                  # TrackAsMenu
        recs = Bits()
        for states, depth, mat, cx, target in bt.records:
            self.need(target)
            recs.u8(states & 0x0F)
            recs.u16(target)
            recs.u16(depth)
            put_matrix(recs, mat)
            put_cxform(recs, cx)
        recs.u8(0)
        recs = recs.done()
        conds = []
        for cond, acts in bt.conds:
            conds.append(struct.pack('<H', cond) + (acts.code if acts is not None else b'\0'))
        b.u16(2 + len(recs) if conds else 0)
        b.raw(recs)
        for k, cbody in enumerate(conds):
            b.u16(0 if k == len(conds) - 1 else 2 + len(cbody))
            b.raw(cbody)
        body = b.done()
        self.out.append(swf_tag(T_BUTTON2, body))
        if self.meta is not None and self.img.version == 6:
            # Some Remix button translations differ by one float ULP from
            # the alpha baker's trunc32(twips / 20) reconstruction.
            pay = tag_hash(body) + struct.pack('<H', len(bt.records))
            for states, _depth, mat, _cx, _target in bt.records:
                pay += struct.pack('<B6f', states, *mat.tuple())
            self.meta.append(meta_record(M_BUTTON, bt.index, pay))

    # -- text ------------------------------------------------------------
    def w_font(self, ft):
        loops = glyph_loops(self.img, ft)
        self.font_glyphs[ft.index] = loops
        n = ft.count
        shapes = [glyph_shape(loops.get(g, [])) for g in range(n)]
        name = ('font%d' % ft.index).encode('ascii')
        sheet = max(ft.sheets, key=lambda s: s.size) if ft.sheets else None
        offsets = []
        pos = 4 * (n + 1)                          # wide offsets, simplest to be right
        for s in shapes:
            offsets.append(pos)
            pos += len(s)
        code_off = pos
        b = Bits()
        b.u16(ft.index)
        b.u8(0x80 | 0x08 | 0x04)                  # HasLayout, WideOffsets, WideCodes
        b.u8(0)                                   # language
        b.u8(len(name))
        b.raw(name)
        b.u16(n)
        b.raw(b''.join(struct.pack('<I', o) for o in offsets) + struct.pack('<I', code_off))
        b.raw(b''.join(shapes))
        b.raw(b''.join(struct.pack('<H', c) for c in ft.codes[:n]))
        metrics = font_metrics(ft)
        if metrics != (ft.ascent, ft.descent, ft.leading):
            self.stats['font metrics unset'] += 1
        for v in metrics:
            b.s16(v)
        advances = ft.advances
        if len(advances) != n:
            # +0x14 may be null (2 fonts, both in garage_x.pck): the player
            # then advances every glyph by 800 (swfEDITTEXT::Draw, MeasureLine)
            advances = [800] * n
            self.stats['font without advances'] += 1
        b.raw(b''.join(struct.pack('<h', min(32767, a)) for a in advances))
        for g in range(n):
            if sheet is not None and g < len(sheet.rects):
                _u, _v, _w, _h, x0, y0, x1, y1 = sheet.rects[g]
            else:
                x0 = y0 = x1 = y1 = 0
            put_rect(b, x0, x1, y0, y1)
        b.u16(0)                                  # no kerning
        body = b.done()
        self.out.append(swf_tag(T_FONT2, body))
        if self.sheets:
            ids = []
            for si, s in enumerate(ft.sheets):
                ids.append([])
                for ti, t in enumerate(s.textures):
                    cid = self.next_id
                    self.next_id += 1
                    self.lossless(cid, t)
                    ids[-1].append(cid)
                    self.exports.append((cid, 'font%d_sheet%d_size%d_tex%d' % (ft.index, si, s.size, ti)))
                    self.stats['font sheet bitmaps'] += 1
            if self.meta is not None:
                # the sheets as baked: the glyph boxes of each size and which
                # of the exported bitmaps hold them
                pay = tag_hash(body) + struct.pack('<B3hB', len(ft.advances) == ft.count,
                                                   ft.ascent, ft.descent, ft.leading, len(ft.sheets))
                for s, sid in zip(ft.sheets, ids):
                    pay += struct.pack('<hHBB', s.size, s.count, s.texindex is not None, len(sid))
                    pay += b''.join(struct.pack('<4B4h', *r) for r in s.rects)
                    if s.texindex is not None:
                        pay += bytes(s.texindex)
                    pay += struct.pack('<%dH' % len(sid), *sid)
                self.meta.append(meta_record(M_FONT, ft.index, pay))

    def text_bounds(self, tx):
        font, height = None, 0
        x = y = 0
        xs, ys = [], []
        for r in tx.records:
            if r[0] == 'font':
                font, height = self.m.objects[r[1]], r[2]
            elif r[0] == 'x':
                x = r[1]
            elif r[0] == 'y':
                y = r[1]
            elif r[0] == 'glyphs' and font is not None:
                sheet = max(font.sheets, key=lambda s: s.size) if font.sheets else None
                for g, adv in r[1]:
                    if sheet is not None and g < len(sheet.rects):
                        _u, _v, _w, _h, x0, y0, x1, y1 = sheet.rects[g]
                        if x1 > x0:
                            xs += [x + x0 * height // 1024, x + x1 * height // 1024]
                            ys += [y + y0 * height // 1024, y + y1 * height // 1024]
                    x += adv
        if not xs:
            return (0, 0, 0, 0)
        return (min(xs), max(xs), min(ys), max(ys))

    def w_text(self, tx):
        glyphs = [g for r in tx.records if r[0] == 'glyphs' for g, _a in r[1]]
        advs = [a for r in tx.records if r[0] == 'glyphs' for _g, a in r[1]]
        gbits = max(1, max(glyphs).bit_length()) if glyphs else 1
        abits = sbits(*advs) if advs else 1
        b = Bits()
        b.u16(tx.index)
        put_rect(b, *self.text_bounds(tx))
        put_matrix(b, tx.matrix)
        b.u8(gbits)
        b.u8(abits)
        style = {}
        for r in tx.records:
            if r[0] != 'glyphs':
                style[r[0]] = r[1:] if r[0] == 'font' else r[1]
                continue
            run = r[1]
            for k in range(0, max(1, len(run)), 255):
                part = run[k:k + 255]
                b.ub(1, 1)
                b.ub(3, 0)
                b.ub(1, 'font' in style)
                b.ub(1, 'colour' in style)
                b.ub(1, 'y' in style)
                b.ub(1, 'x' in style)
                if 'font' in style:
                    self.need(style['font'][0])
                    b.u16(style['font'][0])
                if 'colour' in style:
                    b.raw(rgba_bytes(style['colour']))
                if 'x' in style:
                    b.s16(style['x'])
                if 'y' in style:
                    b.s16(style['y'])
                if 'font' in style:
                    b.u16(style['font'][1])
                b.u8(len(part))
                for g, a in part:
                    b.ub(gbits, g)
                    b.sb(abits, a)
                b.align()
                style = {}
        b.u8(0)
        self.out.append(swf_tag(T_TEXT2, b.done()))

    def w_edittext(self, et):
        h = et.height

        def tw(v):
            return edit_twips(v, h, bits=et.units_bits)
        b = Bits()
        b.u16(et.index)
        # width and height on their own: the baker measured them as lengths
        x0, y0 = tw(et.xmin), tw(et.ymin)
        put_rect(b, x0, x0 + edit_twips(et.bw, h, True, et.units_bits),
                 y0, y0 + edit_twips(et.bh, h, True, et.units_bits))
        has_text = bool(et.has_text)
        # swfEDITTEXT::Draw always word-wraps (MeasureLine) and breaks on \r,
        # and nothing in the player edits or selects: say so to Flash
        b.ub(1, has_text)       # HasText
        b.ub(1, 1)              # WordWrap
        b.ub(1, 1)              # Multiline
        b.ub(1, 0)              # Password
        b.ub(1, 1)              # ReadOnly
        b.ub(1, 1)              # HasTextColor
        b.ub(1, 0)              # HasMaxLength
        b.ub(1, 1)              # HasFont
        b.ub(1, 0)              # HasFontClass
        b.ub(1, 0)              # AutoSize
        b.ub(1, 1)              # HasLayout
        b.ub(1, 1)              # NoSelect
        b.ub(1, 0)              # Border
        b.ub(1, 0)              # WasStatic
        b.ub(1, 0)              # HTML
        b.ub(1, 1)              # UseOutlines: the traced font
        self.need(et.font)
        b.u16(et.font)
        b.u16(h)
        b.raw(rgba_bytes(et.colour))
        b.u8(et.align if et.align <= 3 else 0)
        b.u16(0)
        b.u16(0)
        b.u16(0)
        b.s16(edit_twips(et.leading, h))
        b.raw(et.var + b'\0')
        if has_text:
            b.raw(et.text + b'\0')
        self.out.append(swf_tag(T_EDITTEXT, b.done()))

    # -- the file --------------------------------------------------------
    def build(self, compress=True):
        m = self.m
        self.init_actions = []
        tags = []
        if m.frames:
            tags.append(swf_tag(T_SETBG, rgba_bytes(m.frames[0].word)[:3]))
        for k in range(1, len(m.objects)):
            if m.objects[k] is not None:
                self.define(k)
        tags += self.out
        self.out = []
        main = self.control_tags(m.frames, None)
        for sid, code in self.init_actions:
            tags.append(swf_tag(T_INITACTION, struct.pack('<H', sid) + code))
        if self.meta is not None:
            cid = self.next_id
            self.next_id += 1
            data = META_MAGIC + struct.pack('<HH', META_VERSION, len(self.meta) + 1)
            # Keep the original six bytes readable by older tools. The optional
            # suffix identifies the PCK baker; SWF's version is independent.
            data += meta_record(M_MOVIE, 0, struct.pack('<HI3I', len(m.objects), m.table_zero,
                                                      m.img.version, m.img.base, m.img.flag))
            data += b''.join(self.meta)
            tags.append(swf_tag(T_BINARY, struct.pack('<HI', cid, 0) + data))
            self.exports.append((cid, META_NAME))
        if self.exports:
            body = struct.pack('<H', len(self.exports))
            for cid, name in self.exports:
                body += struct.pack('<H', cid) + name.encode('ascii') + b'\0'
            tags.append(swf_tag(T_EXPORT, body))
        tags += main
        tags.append(swf_tag(T_END, b''))
        head = Bits()
        x0, x1, y0, y1 = m.rect
        put_rect(head, int(round(x0 * 20)), int(round(x1 * 20)), int(round(y0 * 20)), int(round(y1 * 20)))
        head.u16(m.rate)
        head.u16(m.nframes)
        payload = head.done() + b''.join(tags)
        version = m.swf_version or 6
        total = 8 + len(payload)
        if compress:
            return b'CWS' + struct.pack('<BI', version, total) + zlib.compress(payload, 9)
        return b'FWS' + struct.pack('<BI', version, total) + payload


# ---------------------------------------------------------------------------
# reading a SWF back: enough to prove what was written is well formed
# ---------------------------------------------------------------------------
def swf_tags(data):
    """(version, frame size, rate, frames, [(code, body)]) of a FWS/CWS file."""
    sig = data[:3]
    ver, total = struct.unpack_from('<BI', data, 3)
    if sig == b'CWS':
        body = zlib.decompress(data[8:])
    elif sig == b'FWS':
        body = data[8:]
    else:
        raise FormatError('not a SWF: %r' % sig)
    if len(body) + 8 != total:
        raise FormatError('header length %d, real %d' % (total, len(body) + 8))
    nb = body[0] >> 3
    rb = (5 + 4 * nb + 7) // 8
    rate, frames = struct.unpack_from('<HH', body, rb)
    tags = _walk(body, rb + 4)
    return ver, rate, frames, tags


def _walk(body, p):
    tags = []
    while p < len(body):
        h = struct.unpack_from('<H', body, p)[0]
        p += 2
        code, n = h >> 6, h & 0x3F
        if n == 0x3F:
            n = struct.unpack_from('<I', body, p)[0]
            p += 4
        if p + n > len(body):
            raise FormatError('tag %d runs %d byte(s) past the end' % (code, p + n - len(body)))
        tags.append((code, body[p:p + n]))
        p += n
        if code == T_END:
            break
    return tags


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------
def _inputs(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            out += sorted(os.path.join(p, f) for f in os.listdir(p) if f.lower().endswith('.pck'))
        else:
            out.append(p)
    return out


def cmd_info(a):
    for path in _inputs(a.files):
        m = load(path)
        hist = collections.Counter(OBJ_NAMES[o.kind] for o in m.objects if o is not None)
        print('%s  v%d  %d bytes' % (os.path.basename(path), m.img.version, len(m.img.d)))
        print('   SWF %d  %gx%g px  %g fps  %d frame(s)  %d object(s)  %d action list(s)'
              % (m.swf_version, m.rect[1] - m.rect[0], m.rect[3] - m.rect[2], m.rate / 256.0,
                 m.nframes, sum(hist.values()), len(m.cache)))
        print('   ' + '  '.join('%s %d' % kv for kv in sorted(hist.items())))


def cmd_cover(a):
    tot = dict(payload=0, claimed=0, padding=0, unexplained=0)
    falhas = 0
    for path in _inputs(a.files):
        try:
            m = load(path)
        except FormatError as e:
            falhas += 1
            print('   FAIL %s' % e)
            continue
        claimed, padding, buracos = m.img.coverage()
        payload = len(m.img.d) - HEADER
        unexplained = sum(b[2] for b in buracos)
        tot['payload'] += payload
        tot['claimed'] += claimed
        tot['padding'] += padding
        tot['unexplained'] += unexplained
        if unexplained or a.verbose:
            print('   %-34s %9d  claimed %6.2f%%  pad %6.2f%%  unexplained %d in %d run(s)'
                  % (os.path.basename(path), payload, 100.0 * claimed / payload,
                     100.0 * padding / payload, unexplained, len(buracos)))
            for o, n, ruins in sorted(buracos, key=lambda b: -b[2])[:a.show]:
                print('        %#08x +%-6d %d non-pad  %s' % (o, n, ruins,
                      m.img.d[o:o + min(n, 24)].hex(' ')))
    p = tot['payload'] or 1
    print('-- %d byte(s) of payload: %.4f%% claimed, %.4f%% 0xCD fill, %d byte(s) unexplained%s'
          % (tot['payload'], 100.0 * tot['claimed'] / p, 100.0 * tot['padding'] / p,
             tot['unexplained'], ', %d file(s) failed' % falhas if falhas else ''))
    return 1 if (falhas or tot['unexplained']) else 0


def cmd_dump(a):
    m = load(a.file)

    def fmt_cmd(c):
        if isinstance(c, Place):
            s = '%s depth %d char %s' % (CMD_NAMES[c.kind], c.depth, c.char)
            if c.matrix is not None:
                s += ' %r' % c.matrix
            if c.cxform is not None:
                s += ' %r' % c.cxform
            if c.name:
                s += ' name %r' % c.name
            if c.events:
                s += ' events %s' % ['%x' % e[0] for e in c.events]
            return s
        if isinstance(c, Remove):
            return 'RemoveObject2 depth %d' % c.depth
        return '%s %d bytes' % (CMD_NAMES[c.kind], len(c.actions.code) if c.actions else 0)

    if a.frames or a.obj is None:
        for k, f in enumerate(m.frames):
            print('frame %d  word %08X' % (k, f.word))
            for c in f.commands:
                print('   ' + fmt_cmd(c))
    for k, ob in enumerate(m.objects):
        if ob is None or (a.obj is not None and k != a.obj):
            continue
        print('#%d %s @%#x' % (k, OBJ_NAMES[ob.kind], ob.offset))
        if isinstance(ob, Shape):
            for f in ob.fills:
                print('   fill type %#x colour %08X %r bitmap %s grad %s'
                      % (f.type, f.colour, f.matrix, f.bitmap,
                         None if f.gradient is None else (f.gradient.radial, f.gradient.ratios,
                                                          ['%08X' % c for c in f.gradient.colours],
                                                          f.gradient.matrix)))
            for l in ob.lines:
                print('   line width %d (+2 %04X) colour %08X' % l)
            for op in ob.ops:
                if op[0] in (1, 2):
                    print('   op %d %d pts %s' % (op[0], len(op[1]), op[1][:6]))
                else:
                    print('   op %d %s' % op)
        elif isinstance(ob, Sprite):
            for fk, f in enumerate(ob.frames):
                print('   frame %d word %08X' % (fk, f.word))
                for c in f.commands:
                    print('      ' + fmt_cmd(c))
        elif isinstance(ob, Button):
            print('   byte8 %d' % ob.byte8)
            for r in ob.records:
                print('   rec states %x depth %d %r %r -> #%d' % r)
            for c in ob.conds:
                print('   cond %04X %d bytes' % (c[0], len(c[1].code) if c[1] else 0))
        elif isinstance(ob, Bitmap):
            t = ob.tex
            print('   %dx%d (tex %dx%d, fmt %d, swz %d, %d level(s), %d colours, pal32 %s) name %r'
                  % (ob.w, ob.h, t.tw, t.th, t.format, t.swizzle, t.levels, t.ncolours,
                     getattr(t, 'pal32', None), t.name))
        elif isinstance(ob, Font):
            print('   %d glyphs, ascent %d descent %d leading %d, codes %s...'
                  % (ob.count, ob.ascent, ob.descent, ob.leading,
                     ''.join(chr(c) if 32 <= c < 127 else '?' for c in ob.codes[:40])))
            for s in ob.sheets:
                print('   sheet size %d, %d glyphs, %d texture(s) %s, texindex %s'
                      % (s.size, s.count, len(s.textures),
                         ['%dx%d' % (t.tw, t.th) for t in s.textures],
                         None if s.texindex is None else sorted(set(s.texindex))))
        elif isinstance(ob, Text):
            print('   %r' % ob.matrix)
            for r in ob.records:
                print('   %s' % (r,))
        elif isinstance(ob, EditText):
            print('   var %r text %r font #%d h %d colour %08X bounds (%d %d %d %d) align %d leading %d'
                  % (ob.var, ob.text, ob.font, ob.height, ob.colour, ob.xmin, ob.ymin,
                     ob.bw, ob.bh, ob.align, ob.leading))


def cmd_swf(a):
    os.makedirs(a.out, exist_ok=True)
    tot = collections.Counter()
    falhas = 0
    for path in _inputs(a.files):
        nome = os.path.splitext(os.path.basename(path))[0]
        try:
            m = load(path)
            w = SwfWriter(m, sheets=not a.no_sheets, meta=not a.no_meta)
            data = w.build(compress=not a.uncompressed)
        except FormatError as e:
            falhas += 1
            print('   FAIL %s' % e)
            continue
        dst = os.path.join(a.out, nome + '.swf')
        with open(dst, 'wb') as f:
            f.write(data)
        tot['files'] += 1
        tot['bytes'] += len(data)
        tot.update(w.stats)
        if a.png:
            tex = sys.modules.get('mc3_tex') or _mod('mc3_tex')
            pasta = os.path.join(a.out, nome + '_bitmaps')
            os.makedirs(pasta, exist_ok=True)
            for ob in m.objects:
                if isinstance(ob, Bitmap):
                    t = ob.tex
                    pal = t.palette(m.img)
                    px = bytearray()
                    for c in t.indices(m.img):
                        px += bytes(pal[c])
                    tex.write_png(os.path.join(pasta, '%04d_%dx%d.png' % (ob.index, t.tw, t.th)),
                                  t.tw, t.th, px)
        if not a.quiet:
            print('   %-34s -> %s  %d bytes  %s' % (os.path.basename(path), os.path.basename(dst), len(data),
                  ' '.join('%s %d' % kv for kv in sorted(w.stats.items()))))
    print('-- %d SWF written (%d bytes)%s' % (tot['files'], tot['bytes'],
          ', %d FAILED' % falhas if falhas else ''))
    extra = {k: v for k, v in tot.items() if k not in ('files', 'bytes')}
    if extra:
        print('   ' + '  '.join('%s %d' % kv for kv in sorted(extra.items())))
    return 1 if falhas else 0


DEFINES = {2, 6, 10, 14, 20, 21, 22, 32, 33, 34, 35, 36, 37, 39, 46, 48, 60, 75, 83, 84, 87, 90, 91}


def check_swf(data):
    """Problems of one SWF as a list of strings - empty when it is sound.

    Walks every tag (and every tag inside every DefineSprite), checks that
    lengths add up, that each character id is defined once and before any
    PlaceObject2 that names it, and that the frame counts match ShowFrames.
    """
    probs = []
    ver, rate, frames, tags = swf_tags(data)
    defined = set()

    def run(tags, where, nframes):
        shows = 0
        for code, body in tags:
            if code in DEFINES:
                cid = struct.unpack_from('<H', body, 0)[0]
                if cid in defined:
                    probs.append('%s: id %d defined twice' % (where, cid))
                defined.add(cid)
                if code == T_SPRITE:
                    sid, nf = struct.unpack_from('<HH', body, 0)
                    run(_walk(body, 4), 'sprite %d' % sid, nf)
            elif code == T_PLACE2:
                if body[0] & 2:
                    cid = struct.unpack_from('<H', body, 3)[0]
                    if cid not in defined:
                        probs.append('%s: PlaceObject2 of undefined id %d' % (where, cid))
            elif code == T_SHOWFRAME:
                shows += 1
        if shows != nframes:
            probs.append('%s: %d ShowFrame for %d frame(s)' % (where, shows, nframes))
        if not tags or tags[-1][0] != T_END:
            probs.append('%s: no End tag' % where)
    run(tags, 'root', frames)
    return probs


def cmd_check(a):
    ruins = 0
    n = 0
    for p in a.files:
        lista = ([os.path.join(p, f) for f in sorted(os.listdir(p)) if f.lower().endswith('.swf')]
                 if os.path.isdir(p) else [p])
        for path in lista:
            n += 1
            try:
                probs = check_swf(open(path, 'rb').read())
            except Exception as e:                      # a crash is a finding
                probs = ['unreadable: %r' % e]
            if probs:
                ruins += 1
                print('   %s' % os.path.basename(path))
                for pr in probs[:a.show]:
                    print('      %s' % pr)
    print('-- %d SWF checked, %d with problems' % (n, ruins))
    return 1 if ruins else 0


# ---------------------------------------------------------------------------
# verify: an independent decoder against the source
# ---------------------------------------------------------------------------
FFDEC = os.environ.get('FFDEC', os.path.join(os.environ.get('FFDEC_DIR', ''), 'ffdec-cli.exe'))


class Verify(object):
    """What JPEXS FFDec decodes from our SWF, field by field, against the .pck.

    FFDec's -swf2xml decodes every field of every tag with its own parser. If
    the bit packing of a MATRIX, a CXFORM, a TEXTRECORD or a DefineEditText
    were off, the values it reads back would not be the ones in the file.
    """

    def __init__(self, movie, xml_root):
        self.m = movie
        self.root = xml_root
        self.count = collections.Counter()
        self.bad = collections.Counter()
        self.example = {}

    def chk(self, kind, ok, detail=''):
        self.count[kind] += 1
        if not ok:
            self.bad[kind] += 1
            self.example.setdefault(kind, detail)

    @staticmethod
    def children(el):
        st = el.find('subTags')
        if st is None:
            st = el.find('tags')
        return list(st) if st is not None else []

    @staticmethod
    def rgba_of(e):
        return tuple(int(e.get(k)) for k in ('red', 'green', 'blue', 'alpha'))

    def matrix(self, me, mat, twips=None):
        hs, hr = me.get('hasScale') == 'true', me.get('hasRotate') == 'true'
        sx = float(me.get('scaleX')) if hs else 1.0
        sy = float(me.get('scaleY')) if hs else 1.0
        r0 = float(me.get('rotateSkew0')) if hr else 0.0
        r1 = float(me.get('rotateSkew1')) if hr else 0.0
        tx, ty = int(me.get('translateX')), int(me.get('translateY'))
        ok = all(abs(u - v) < 2e-5 for u, v in ((sx, mat.a), (sy, mat.d), (r0, mat.b), (r1, mat.c)))
        if twips is not None:
            return ok and (tx, ty) == tuple(twips)
        return ok and abs(tx - mat.tx * 20) <= 0.5 and abs(ty - mat.ty * 20) <= 0.5

    @staticmethod
    def cxform(ce, cx):
        if ce is None:
            return cx is None
        names = ('red', 'green', 'blue', 'alpha')
        return (tuple(int(ce.get(n + 'MultTerm')) for n in names) == tuple(4 * v for v in cx.mul) and
                tuple(int(ce.get(n + 'AddTerm')) for n in names) == tuple(4 * v for v in cx.add))

    def timeline(self, tags, frames, where):
        seq = [t for t in tags if t.get('type') in ('PlaceObject2Tag', 'RemoveObject2Tag',
                                                      'DoActionTag', 'ShowFrameTag')]
        cmds = []
        for fr in frames:
            cmds += [c for c in fr.commands if not (isinstance(c, Actions) and c.kind == 4)]
            cmds.append(None)
        self.chk('timeline length', len(seq) == len(cmds), where)
        for t, c in zip(seq, cmds):
            ty = t.get('type')
            if c is None:
                self.chk('show frame', ty == 'ShowFrameTag', where)
            elif isinstance(c, Place):
                if ty != 'PlaceObject2Tag':
                    self.chk('place', False, where)
                    continue
                hc = t.get('placeFlagHasCharacter') == 'true'
                self.chk('place depth/char', int(t.get('depth')) == c.depth and
                         (int(t.get('characterId')) if hc else None) == c.char, where)
                me = t.find('matrix')
                if c.matrix is not None:
                    self.chk('place matrix', me is not None and self.matrix(me, c.matrix, c.matrix_raw[-2:]), where)
                else:
                    self.chk('place matrix', me is None, where)
                self.chk('place cxform', self.cxform(t.find('colorTransform'), c.cxform), where)
                self.chk('place name', t.get('name') == c.name, where)
                recs = t.findall('clipActions/clipActionRecords/item')
                self.chk('clip events', len(recs) == len(c.events), where)
                for r, (flags, acts, _k) in zip(recs, c.events):
                    ef = r.find('eventFlags')
                    got = (ef.get('clipEventLoad') == 'true') | ((ef.get('clipEventEnterFrame') == 'true') << 1)
                    self.chk('clip event', got == flags and r.get('actionBytes') == acts.code.hex(), where)
            elif isinstance(c, Remove):
                self.chk('remove', ty == 'RemoveObject2Tag' and int(t.get('depth')) == c.depth, where)
            else:
                self.chk('do action', ty == 'DoActionTag' and t.get('actionBytes') == c.actions.code.hex(), where)

    def run(self):
        top = self.children(self.root)
        by_id = {}
        for t in top:
            for k in ('shapeId', 'spriteId', 'buttonId', 'characterID', 'fontID'):
                if t.get(k) is not None:
                    by_id.setdefault(int(t.get(k)), t)
                    break
        self.timeline(top, self.m.frames, 'root')
        for ob in self.m.objects:
            if ob is None:
                continue
            t = by_id.get(ob.index)
            where = '#%d' % ob.index
            self.chk('defined', t is not None, where)
            if t is None:
                continue
            if isinstance(ob, Sprite):
                self.chk('sprite frames', int(t.get('frameCount')) == ob.nframes, where)
                self.timeline(self.children(t), ob.frames, 'sprite %d' % ob.index)
            elif isinstance(ob, Shape):
                fs = t.findall('shapes/fillStyles/fillStyles/item')
                self.chk('shape fills', len(fs) >= len(ob.fills), where)
                for e, f in zip(fs, ob.fills):
                    ok = int(e.get('fillStyleType')) == (f.type & 0xFF)
                    if (f.type & 0xFF) == 0:
                        ok = ok and self.rgba_of(e.find('color')) == rgba(f.colour)
                    elif (f.type & 0xFF) >= 0x40:
                        ok = ok and int(e.get('bitmapId')) == (0xFFFF if f.bitmap is None else f.bitmap)
                    self.chk('fill style', ok, where)
                ls = t.findall('shapes/lineStyles/lineStyles/item')
                for e, l in zip(ls, ob.lines):
                    self.chk('line style', int(e.get('width')) == l[0] and
                             self.rgba_of(e.find('color')) == rgba(l[2]), where)
            elif isinstance(ob, Button):
                recs = t.findall('characters/item')
                self.chk('button records', len(recs) == len(ob.records), where)
                for e, (states, depth, mat, cx, target) in zip(recs, ob.records):
                    got = ((e.get('buttonStateUp') == 'true') | ((e.get('buttonStateOver') == 'true') << 1) |
                           ((e.get('buttonStateDown') == 'true') << 2) | ((e.get('buttonStateHitTest') == 'true') << 3))
                    self.chk('button record', got == states & 15 and int(e.get('characterId')) == target and
                             int(e.get('placeDepth')) == depth and self.matrix(e.find('placeMatrix'), mat) and
                             self.cxform(e.find('colorTransform'), cx), where)
                acts = t.findall('actions/item')
                names = ('condIdleToOverUp', 'condOverUpToIdle', 'condOverUpToOverDown', 'condOverDownToOverUp',
                         'condOverDownToOutDown', 'condOutDownToOverDown', 'condOutDownToIdle',
                         'condIdleToOverDown', 'condOverDownToIdle')
                self.chk('button conditions', len(acts) == len(ob.conds), where)
                for e, (cond, al) in zip(acts, ob.conds):
                    got = sum((e.get(n) == 'true') << k for k, n in enumerate(names)) | (int(e.get('condKeyPress')) << 9)
                    self.chk('button condition', got == cond and e.get('actionBytes') == al.code.hex(), where)
            elif isinstance(ob, Text):
                mine, style = [], {}
                for r in ob.records:
                    if r[0] == 'glyphs':
                        mine.append((style, r[1]))
                        style = {}
                    else:
                        style[r[0]] = r[1:]
                recs = t.findall('textRecords/item')
                self.chk('text records', len(recs) == len(mine), where)
                for e, (st, glyphs) in zip(recs, mine):
                    ok = [(int(g.get('glyphIndex')), int(g.get('glyphAdvance')))
                          for g in e.findall('glyphEntries/item')] == list(glyphs)
                    if 'font' in st:
                        ok = ok and (int(e.get('fontId')), int(e.get('textHeight'))) == st['font']
                    if 'x' in st:
                        ok = ok and int(e.get('xOffset')) == st['x'][0]
                    if 'y' in st:
                        ok = ok and int(e.get('yOffset')) == st['y'][0]
                    if 'colour' in st:
                        ok = ok and self.rgba_of(e.find('textColorA')) == rgba(st['colour'][0])
                    self.chk('text record', ok, where)
            elif isinstance(ob, EditText):
                h = ob.height
                tw = lambda v: edit_twips(v, h, bits=ob.units_bits)
                b = t.find('bounds')
                txt = (t.get('initialText') or '').replace('\\u0020', ' ').replace('\\r', '\r').replace('\\n', '\n')
                self.chk('edit text', int(t.get('fontId')) == ob.font and int(t.get('fontHeight')) == h and
                         int(t.get('align')) == ob.align and int(t.get('leading')) == edit_twips(ob.leading, h) and
                         self.rgba_of(t.find('textColor')) == rgba(ob.colour) and
                         (int(b.get('Xmin')), int(b.get('Xmax')), int(b.get('Ymin')), int(b.get('Ymax'))) ==
                         (tw(ob.xmin), tw(ob.xmin) + edit_twips(ob.bw, h, True, ob.units_bits), tw(ob.ymin),
                          tw(ob.ymin) + edit_twips(ob.bh, h, True, ob.units_bits)) and
                         (t.get('hasText') == 'true') == bool(ob.has_text) and
                         (not ob.has_text or txt == ob.text.decode('utf-8', 'replace')), where)
            elif isinstance(ob, Font):
                codes = [int(e.text) for e in t.findall('codeTable/item')]
                adv = [int(e.text) for e in t.findall('fontAdvanceTable/item')]
                self.chk('font', (int(t.get('fontAscent')), int(t.get('fontDescent')), int(t.get('fontLeading')))
                         == font_metrics(ob) and codes == ob.codes and adv == (ob.advances if len(ob.advances) == ob.count else [800] * ob.count) and
                         len(t.findall('glyphShapeTable/item')) == ob.count, where)
            elif isinstance(ob, Bitmap):
                self.chk('bitmap', (int(t.get('bitmapWidth')), int(t.get('bitmapHeight'))) == (ob.tex.tw, ob.tex.th)
                         and int(t.get('bitmapColorTableSize')) == ob.tex.ncolours - 1, where)
        return self


def cmd_verify(a):
    import subprocess
    import tempfile
    import xml.etree.ElementTree as ET
    if not os.path.isfile(FFDEC):
        raise SystemExit('ffdec-cli not found at %s (set FFDEC)' % FFDEC)
    total = mism = 0
    for path in _inputs(a.files):
        m = load(path)
        if a.swf:
            # the delivered file itself, not a fresh build of it
            data = open(os.path.join(a.swf, os.path.splitext(os.path.basename(path))[0] + '.swf'), 'rb').read()
        else:
            data = SwfWriter(m).build(compress=False)
        with tempfile.TemporaryDirectory() as tmp:
            swf, xml = os.path.join(tmp, 'x.swf'), os.path.join(tmp, 'x.xml')
            open(swf, 'wb').write(data)
            p = subprocess.run([FFDEC, '-swf2xml', swf, xml], capture_output=True, text=True)
            log = (p.stdout or '') + (p.stderr or '')
            if p.returncode or 'Exception' in log or not os.path.exists(xml):
                print('   %-34s FFDec could not read it:\n%s' % (os.path.basename(path), log[-800:]))
                mism += 1
                continue
            v = Verify(m, ET.parse(xml).getroot()).run()
        n, b = sum(v.count.values()), sum(v.bad.values())
        total += n
        mism += b
        print('   %-34s %7d field checks, %d mismatch(es)' % (os.path.basename(path), n, b))
        for k in sorted(v.bad):
            print('      %-20s %d  e.g. %s' % (k, v.bad[k], v.example[k]))
    print('-- %d field checks, %d mismatch(es)' % (total, mism))
    return 1 if mism else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='acao')
    s = sub.add_parser('verify', help='FFDec reads our SWF; compare every field with the .pck')
    s.add_argument('files', nargs='+')
    s.add_argument('--swf', help='check the .swf already written in this folder instead of a fresh build')
    s = sub.add_parser('info')
    s.add_argument('files', nargs='+')
    s = sub.add_parser('cover')
    s.add_argument('files', nargs='+')
    s.add_argument('--show', type=int, default=6)
    s.add_argument('-v', '--verbose', action='store_true')
    s = sub.add_parser('dump')
    s.add_argument('file')
    s.add_argument('--obj', type=int)
    s.add_argument('--frames', action='store_true')
    s = sub.add_parser('swf', help='write .swf files')
    s.add_argument('files', nargs='+')
    s.add_argument('--out', required=True)
    s.add_argument('--png', action='store_true', help='also every bitmap as PNG')
    s.add_argument('--no-sheets', action='store_true',
                   help='leave the font sheet textures out of the SWF')
    s.add_argument('--uncompressed', action='store_true', help='FWS instead of CWS')
    s.add_argument('--no-meta', action='store_true',
                   help='leave out the mc3_pck_meta block (the exact palettes, fans and '
                        'font sheets mc3_swf2pck uses to rebuild untouched objects)')
    s.add_argument('-q', '--quiet', action='store_true')
    s = sub.add_parser('check', help='re-read written .swf files')
    s.add_argument('files', nargs='+')
    s.add_argument('--show', type=int, default=8)
    a = ap.parse_args()
    fn = {'info': cmd_info, 'cover': cmd_cover, 'dump': cmd_dump,
          'swf': cmd_swf, 'check': cmd_check, 'verify': cmd_verify}.get(a.acao)
    if not fn:
        ap.print_help()
        return 2
    return fn(a) or 0


if __name__ == '__main__':
    sys.exit(main())
