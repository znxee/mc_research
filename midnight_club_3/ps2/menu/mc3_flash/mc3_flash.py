"""mc3_flash.py - reads the .pck files in ASSETS/flash.

    python mc3_flash.py info     FILE.pck
    python mc3_flash.py objects  FILE.pck [--type SPRITE]
    python mc3_flash.py sprites  FILE.pck [--clips]
    python mc3_flash.py strings  FILE.pck [--min 4]
    python mc3_flash.py actions  FILE.pck [--limit 20]
    python mc3_flash.py diff     A.pck B.pck
    python mc3_flash.py vars     GAME.ELF [--list] [--grep RE]

The last one reads the ELF, not a .pck: the movies hold no data, so half of any
"where does this list come from" lives on the engine side. See cmd_vars.

WHAT THESE FILES ARE

Not SWF. There is no FWS/CWS/ZWS anywhere in them, so no Flash tool will open
one. A flash .pck is a memory image of an ALREADY PARSED movie: live C++ objects
dumped to disk with their pointers intact, to be loaded in one read and used
where they land. That is the same load-in-place idea as the mesh and city .pck,
and it is why editing means rebuilding pointers rather than recompiling a movie.

    PckFileHeader   0x10   base VA (0x06800000), type 6, version, body size
    swfFILE       +0x84    +04 frame_count=1  +08 framesPtr  +0C objPtrList
                           +10 fps=6          +26 objectCount (u16)

    file offset = va - base + 0x80

Layouts come from AlgumCorrupto's RAGE-SWF-research (flashpck.h), with one
correction measured here: swfFILE sits at +0x84, not +0x80. Everything else in
that header checked out against the PS2 files.

VALIDATION

By structure, never by address range. A candidate is good when its pointers land
inside the image and the counts agree with objectCount - not when a value falls
in some window that happened to hold true for retail files. That distinction has
already cost this project two readers that went blind on their own output.
"""
import argparse
import collections
import io
import os
import re
import struct
import sys

HDR = 0x80                      # PckFileHeader plus padding, before swfFILE-1
FILE_AT = 0x84                  # where swfFILE actually starts

OBJ_TYPES = {0: 'FILE', 1: 'SHAPE', 2: 'SPRITE', 3: 'BUTTON', 4: 'BITMAP',
             5: 'FONT', 6: 'TEXT', 7: 'EDITTEXT'}
CMD_TYPES = {0: 'PLACEOBJECT2', 1: 'CLIPEVENT', 2: 'REMOVEOBJECT', 3: 'DOACTION'}

# AVM1. Only the opcodes that actually turn up are named; the rest print as
# their number, which is more honest than guessing.
AVM1 = {
    0x04: 'NEXTFRAME', 0x05: 'PREVFRAME', 0x06: 'PLAY', 0x07: 'STOP',
    0x08: 'TOGGLEQUALITY', 0x09: 'STOPSOUNDS',
    0x0A: 'ADD', 0x0B: 'SUBTRACT', 0x0C: 'MULTIPLY', 0x0D: 'DIVIDE',
    0x0E: 'EQUALS', 0x0F: 'LESS', 0x10: 'AND', 0x11: 'OR', 0x12: 'NOT',
    0x13: 'STRINGEQUALS', 0x17: 'POP', 0x18: 'TOINTEGER',
    0x1C: 'GETVARIABLE', 0x1D: 'SETVARIABLE',
    0x20: 'SETTARGET2', 0x21: 'STRINGADD', 0x22: 'GETPROPERTY',
    0x23: 'SETPROPERTY', 0x24: 'CLONESPRITE', 0x25: 'REMOVESPRITE',
    0x26: 'TRACE', 0x28: 'ENDDRAG', 0x2A: 'THROW', 0x2B: 'CASTOP',
    0x30: 'RANDOMNUMBER', 0x34: 'GETTIME',
    0x3A: 'DELETE', 0x3B: 'DELETE2', 0x3C: 'DEFINELOCAL',
    0x3D: 'CALLFUNCTION', 0x3E: 'RETURN', 0x3F: 'MODULO',
    0x40: 'NEWOBJECT', 0x41: 'DEFINELOCAL2', 0x42: 'INITARRAY',
    0x43: 'INITOBJECT', 0x44: 'TYPEOF', 0x46: 'ENUMERATE',
    0x47: 'ADD2', 0x48: 'LESS2', 0x49: 'EQUALS2', 0x4C: 'PUSHDUPLICATE',
    0x4E: 'GETMEMBER', 0x4F: 'SETMEMBER', 0x50: 'INCREMENT',
    0x51: 'DECREMENT', 0x52: 'CALLMETHOD', 0x53: 'NEWMETHOD',
    0x55: 'ENUMERATE2', 0x60: 'BITAND', 0x61: 'BITOR', 0x62: 'BITXOR',
    0x63: 'BITLSHIFT', 0x64: 'BITRSHIFT', 0x67: 'GREATER',
    0x81: 'GOTOFRAME', 0x83: 'GETURL', 0x87: 'STOREREGISTER',
    0x88: 'CONSTANTPOOL', 0x8A: 'WAITFORFRAME', 0x8B: 'SETTARGET',
    0x8C: 'GOTOLABEL', 0x8E: 'DEFINEFUNCTION2', 0x94: 'WITH',
    0x96: 'PUSH', 0x99: 'JUMP', 0x9A: 'GETURL2', 0x9B: 'DEFINEFUNCTION',
    0x9D: 'IF', 0x9E: 'CALL', 0x9F: 'GOTOFRAME2',
}


class Pck(object):
    def __init__(self, path):
        self.path = path
        self.d = open(path, 'rb').read()
        self.base, self.kind, self.ver, self.body = struct.unpack_from('<IIII', self.d, 0)
        self.frame_count = self.u16(FILE_AT + 0x04)
        self.frames_ptr = self.u32(FILE_AT + 0x08)
        self.obj_list = self.u32(FILE_AT + 0x0C)
        self.fps = self.d[FILE_AT + 0x10]
        self.object_count = self.u16(FILE_AT + 0x26)

    # --- raw access -------------------------------------------------------
    def u8(self, o):  return self.d[o]
    def u16(self, o): return struct.unpack_from('<H', self.d, o)[0]
    def u32(self, o): return struct.unpack_from('<I', self.d, o)[0]

    def off(self, va):
        """VA -> file offset. Returns None when it does not land in the file."""
        o = va - self.base + HDR
        return o if 0 <= o < len(self.d) else None

    def inside(self, va):
        return self.off(va) is not None

    def cstr(self, va, limit=128):
        o = self.off(va)
        if o is None:
            return None
        e = self.d.find(b'\0', o, min(o + limit, len(self.d)))
        if e < 0:
            return None
        try:
            return self.d[o:e].decode('latin1')
        except Exception:
            return None

    # --- structure --------------------------------------------------------
    def objects(self):
        """[(index, va, type)] from the object pointer list."""
        out = []
        o = self.off(self.obj_list)
        if o is None:
            return out
        for i in range(self.object_count):
            if o + 4 > len(self.d):
                break
            va = self.u32(o)
            o += 4
            oo = self.off(va)
            out.append((i, va, self.u8(oo) if oo is not None else None))
        return out

    def sane(self):
        """Structural check. Deliberately not an address-range test."""
        objs = self.objects()
        good = sum(1 for _i, va, _t in objs if self.inside(va))
        typed = sum(1 for _i, _va, t in objs if t in OBJ_TYPES)
        return dict(
            header_kind=self.kind,
            body_matches=(self.body + HDR == len(self.d)),
            frame_count=self.frame_count,
            fps=self.fps,
            frames_ok=self.inside(self.frames_ptr),
            objlist_ok=self.inside(self.obj_list),
            objects=len(objs), pointers_inside=good, known_types=typed)

    def root_frames(self):
        """The movie's OWN frames, from swfFILE.framesPtr.

        Easy to miss, and missing them hides the most interesting code: the
        menu's names live in the root frame's constant pool, not in any sprite.
        """
        out = []
        fo = self.off(self.frames_ptr)
        if fo is None:
            return out
        for i in range(self.frame_count):
            if fo + 8 > len(self.d):
                break
            out.append((i, self.u32(fo + 4)))
            fo += 8
        return out

    def action_blocks(self):
        """Every AVM1 stream in the file, wherever it hides.

        Three places, and a walk that only knows the first finds almost nothing:
          - DOACTION commands in sprite frames
          - DOACTION commands in the movie's own frames
          - code hung off CLIPEVENT commands (+0x20)
        """
        out = []
        laco = [(-1, self.root_frames())]
        for i, va, t in self.objects():
            if OBJ_TYPES.get(t) == 'SPRITE':
                laco.append((i, self.sprite_frames(va)))
        for owner, frames in laco:
            for _fi, cva in frames:
                for c, k in self.commands(cva):
                    kind = CMD_TYPES.get(k)
                    if kind == 'DOACTION':
                        out.append((owner, c, 'doAction', self.u32(self.off(c) + 0x0C)))
                    elif kind == 'CLIPEVENT':
                        w = self.u32(self.off(c) + 0x20)
                        if w and self.inside(w):
                            out.append((owner, c, 'clipEvent', w))
        return out

    def sprite_frames(self, va):
        """[(frame index, commands va)] for a SPRITE object."""
        o = self.off(va)
        if o is None:
            return []
        n = self.u32(o + 0x10)
        fp = self.u32(o + 0x0C)
        if n > 4096 or not self.inside(fp):
            return []
        out = []
        fo = self.off(fp)
        for i in range(n):
            if fo + 8 > len(self.d):
                break
            out.append((i, self.u32(fo + 4)))
            fo += 8
        return out

    def commands(self, va, cap=4096):
        """Walk the command linked list. `cap` stops a corrupt next pointer
        from spinning forever, which is the failure mode that matters."""
        out, seen = [], set()
        while va and self.inside(va) and len(out) < cap and va not in seen:
            seen.add(va)
            o = self.off(va)
            out.append((va, self.u8(o)))
            va = self.u32(o + 4)
        return out


# --------------------------------------------------------------------------
def prologue(p, va):
    """RAGE puts a 0xC5 block in front of the bytecode: `C5 <len16> <blob>`.

    The blob is the constant pool, already expanded into strings at build time
    rather than left as an AVM1 CONSTANTPOOL tag - consistent with everything
    else here being pre-parsed. 453 of the 501 doAction streams in toplevel.pck
    start with it, and in every one the byte just past the declared length is a
    valid opcode, which is what makes this framing rather than coincidence.

    Returns (code offset, pool).
    There are TWO framings in one file, which is why a reader that knows only
    the first finds almost nothing:

      C5 <len16> <blob>   sprite blocks: the pool already expanded to strings
      01 00 88 <len16>..  root blocks: an ordinary AVM1 CONSTANTPOOL tag

    Both are handled, and the pool is read either way - without it every operand
    prints as `const7` and the disassembly says nothing.
    """
    o = p.off(va)
    if o is None:
        return o, []
    if p.d[o] == 0xC5:
        ln = struct.unpack_from('<H', p.d, o + 1)[0]
        blob = p.d[o + 3:o + 3 + ln]
        pool = [m.group()[:-1].decode('latin1')
                for m in re.finditer(rb'[ -~]{2,64}\x00', blob)]
        return o + 3 + ln, pool
    # a 2-byte count sits in front of the root streams
    if p.d[o] == 0x01 and p.d[o + 1] == 0x00:
        o += 2
    if p.d[o] == 0x88:
        ln = struct.unpack_from('<H', p.d, o + 1)[0]
        body = p.d[o + 3:o + 3 + ln]
        pool = [s.decode('latin1') for s in body[2:].split(b'\0')[:-1]]
        return o + 3 + ln, pool
    return o, []


def avm1(p, va, limit=4096):
    """Disassemble an AVM1 stream. Returns [(offset, name, detail)]."""
    o, pool = prologue(p, va)
    if o is None:
        return []
    out, start = [], o
    while o - start < limit and o < len(p.d):
        op = p.d[o]
        here = o - start
        o += 1
        if op == 0:
            out.append((here, 'END', ''))
            break
        if op < 0x80:
            out.append((here, AVM1.get(op, 'op_%02X' % op), ''))
            continue
        if o + 2 > len(p.d):
            break
        ln = struct.unpack_from('<H', p.d, o)[0]
        o += 2
        body = p.d[o:o + ln]
        o += ln
        name = AVM1.get(op, 'op_%02X' % op)
        det = ''
        if op == 0x88:                       # CONSTANTPOOL
            pool = [s.decode('latin1') for s in body[2:].split(b'\0')[:-1]]
            det = '%d strings' % len(pool)
        elif op == 0x96:                     # PUSH
            det = ' '.join(_push(body, pool))
        elif op == 0x8B or op == 0x8C:       # SETTARGET / GOTOLABEL
            det = repr(body.split(b'\0')[0].decode('latin1'))
        elif ln:
            det = '%d bytes' % ln
        out.append((here, name, det))
    return out


def _push(body, pool):
    """PUSH carries a typed list; the string cases are the ones worth reading."""
    out, i = [], 0
    while i < len(body):
        t = body[i]
        i += 1
        if t == 0:                                    # literal string
            e = body.find(b'\0', i)
            if e < 0:
                break
            out.append(repr(body[i:e].decode('latin1')))
            i = e + 1
        elif t == 1:
            i += 4
            out.append('float')
        elif t in (2, 3):
            out.append('null' if t == 2 else 'undef')
        elif t == 4:
            out.append('reg%d' % body[i]); i += 1
        elif t == 5:
            out.append('bool%d' % body[i]); i += 1
        elif t == 6:
            i += 8; out.append('double')
        elif t == 7:
            out.append('%d' % struct.unpack_from('<i', body, i)[0]); i += 4
        elif t == 8:
            k = body[i]; i += 1
            out.append(repr(pool[k]) if k < len(pool) else 'const%d' % k)
        elif t == 9:
            k = struct.unpack_from('<H', body, i)[0]; i += 2
            out.append(repr(pool[k]) if k < len(pool) else 'const%d' % k)
        else:
            break
    return out


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
#  The other half of the frontend: what the ENGINE feeds the movie.
#
#  A flash .pck holds the movie. It does not hold the data. Every list the
#  frontend shows - car names, upgrade names, the garage's ShowRoomNames - is
#  pushed in from C++ at run time through mcFlash::SetContextVariable, and read
#  back with GetContextVariable. So "where does this menu's list come from?" is
#  never answered by reading the .pck alone: half the answer is in the ELF.
#
#  This command enumerates that channel: every hook point between the game and
#  the movies, with the variable name each site writes.
# --------------------------------------------------------------------------
class Elf(object):
    """Just enough ELF to read the one PT_LOAD an EE executable has."""

    def __init__(self, path):
        self.path = path
        self.d = open(path, 'rb').read()
        po = struct.unpack_from('<I', self.d, 0x1C)[0]
        pn = struct.unpack_from('<H', self.d, 0x2C)[0]
        ps = struct.unpack_from('<H', self.d, 0x2A)[0]
        carga = []
        for i in range(pn):
            t, off, va, _pa, fsz, _msz, _fl, _al = struct.unpack_from(
                '<IIIIIIII', self.d, po + i * ps)
            if t == 1:
                carga.append((off, va, fsz))
        if len(carga) != 1:
            raise SystemExit('%s: expected one PT_LOAD, found %d'
                             % (os.path.basename(path), len(carga)))
        self.off, self.va, self.size = carga[0]

    def word(self, va):
        return struct.unpack_from('<I', self.d, va - self.va + self.off)[0]

    def words(self):
        for o in range(self.off, self.off + self.size - 3, 4):
            yield o - self.off + self.va, struct.unpack_from('<I', self.d, o)[0]

    def cstr(self, va, limit=96):
        o = va - self.va + self.off
        if not (self.off <= o < self.off + self.size):
            return None
        e = self.d.find(b'\0', o, o + limit)
        if e < 0:
            return None
        s = self.d[o:e]
        if not s or not all(32 <= c < 127 for c in s):
            return None
        return s.decode('latin1')

    def func_start(self, va, limite=4000):
        """Walk back to the `addiu $sp, $sp, -N` that opens the frame."""
        for k in range(limite):
            a = va - 4 * k
            if a < self.va:
                return None
            w = self.word(a)
            if ((w >> 26) == 0x09 and ((w >> 21) & 0x1F) == 29
                    and ((w >> 16) & 0x1F) == 29 and (w & 0x8000)):
                return a
        return None


def _escreve(w):
    """Which register this instruction writes, or -1."""
    op = w >> 26
    if op in (0x0F, 0x09, 0x0D, 0x23, 0x24, 0x25, 0x21):
        return (w >> 16) & 0x1F
    if op == 0:                                   # SPECIAL: rd
        return (w >> 11) & 0x1F
    return -1


def arg_string(elf, jal_va, reg=5, alcance=24):
    """Resolve the static string in `reg` at a call site, or None.

    Deliberately conservative. The value is accepted only when the instruction
    that last wrote the register is an `addiu` off a `lui` in the same
    straight-line run, with no branch in between. Anything else reports None
    rather than a guess: a wrong variable name here sends someone patching the
    wrong screen, which costs more than an honest blank.

    The delay slot is read first, because on MIPS it runs BEFORE the call and is
    where the compiler usually parks the last argument.
    """
    ordem = [jal_va + 4] + [jal_va - 4 * k for k in range(1, alcance)]
    for a in ordem:
        if a < elf.va or a >= elf.va + elf.size:
            continue
        w = elf.word(a)
        op = w >> 26
        # a branch or another call ends the straight-line run we can trust
        if a != jal_va + 4 and (op == 0x01 or 0x02 <= op <= 0x07):
            return None
        if _escreve(w) != reg:
            continue
        if op != 0x09:                    # written, but not by addiu -> unknown
            return None
        base = (w >> 21) & 0x1F
        imm = w & 0xFFFF
        if imm >= 0x8000:
            imm -= 0x10000
        if base == 0:
            return None
        for k in range(1, 10):            # find the lui that fed it
            b = a - 4 * k
            if b < elf.va:
                return None
            w2 = elf.word(b)
            if (w2 >> 26) == 0x0F and ((w2 >> 16) & 0x1F) == base:
                return elf.cstr((((w2 & 0xFFFF) << 16) + imm) & 0xFFFFFFFF)
            if _escreve(w2) == base:
                return None
        return None
    return None


def _simbolos():
    """The name tables from simbolos/, most trusted layer first."""
    aqui = os.path.dirname(os.path.abspath(__file__))
    tab = {}
    for nome in ('nomes_manuais.tsv', 'nomes.tsv', 'nomes_grafo.tsv',
                 'nomes_vizinhos.tsv', 'nomes_token.tsv'):
        p = os.path.join(aqui, 'simbolos', nome)
        if not os.path.exists(p):
            continue
        for ln in io.open(p, encoding='utf-8', errors='ignore'):
            campo = ln.rstrip('\n').split('\t')
            if len(campo) >= 2:
                try:
                    tab.setdefault(int(campo[0], 16), campo[1])
                except ValueError:
                    pass
    return tab


def flash_api(sym):
    """Addresses of the mcFlash context API, taken from the symbol tables.

    Read from simbolos/ rather than pasted here, so a better name table
    improves this command instead of silently disagreeing with it.
    """
    curto = (('GetContextVariableString', 'getstr'),
             ('SetContextVariable', 'set'),
             ('GetContextVariable', 'get'),
             ('GetArrayLength', 'arraylen'))
    # the demangled argument list, shortened to what a reader needs: whether
    # this site writes a scalar or one slot of an array, and of what type
    tipo = [('char_const__ptr__int_char_const__ptr', 'name,i,str'),
            ('char_const__ptr__int_int', 'name,i,int'),
            ('char_const__ptr__int_swfVARIANT__ref', 'name,i,&var'),
            ('char_const__ptr__char__ptr__int', 'name,buf,n'),
            ('char_const__ptr__char_const__ptr', 'name,str'),
            ('char_const__ptr__float', 'name,float'),
            ('char_const__ptr__int', 'name,int'),
            ('char_const__ptr', 'name')]
    api = {}
    for va, nome in sym.items():
        if not nome.startswith('mcFlash__'):
            continue
        corpo = nome[len('mcFlash__'):]
        for k, v in curto:
            if not corpo.startswith(k):
                continue
            resto = corpo[len(k):].strip('_')
            args = next((c for m, c in tipo if resto == m), resto or 'name')
            api[va] = '%s(%s)' % (v, args)
            break
    return api


def cmd_vars(a):
    sym = _simbolos()
    api = flash_api(sym)
    if not api:
        print('   no mcFlash symbols in simbolos/ - nothing to scan for')
        return 1
    elf = Elf(a.elf)
    achados = []
    for va, w in elf.words():
        if (w >> 26) != 0x03:                          # jal
            continue
        alvo = (va & 0xF0000000) | ((w & 0x3FFFFFF) << 2)
        if alvo in api:
            achados.append((va, api[alvo], arg_string(elf, va)))

    total = len(achados)
    if a.grep:
        rx = re.compile(a.grep, re.I)
        achados = [x for x in achados if x[2] and rx.search(x[2])]
    elif not a.all:
        achados = [x for x in achados if x[2]]

    por_nome = collections.Counter(x[2] for x in achados if x[2])
    if a.list:
        for nome, n in sorted(por_nome.items()):
            print('   %-38s %d' % (nome, n))
    else:
        for va, kind, nome in achados:
            f = elf.func_start(va)
            print('   %08X  %-26s %-34s %s'
                  % (va, kind, repr(nome) if nome else '<not a static string>',
                     sym.get(f, '%08X' % f if f else '?')))
    print('   -- %d shown, %d distinct names, %d call sites in the ELF'
          % (len(achados), len(por_nome), total))
    return 0


def cmd_info(a):
    p = Pck(a.file)
    s = p.sane()
    print('%s  %d bytes' % (os.path.basename(p.path), len(p.d)))
    print('   base VA        %08X   type %d   version %d   body %d %s'
          % (p.base, p.kind, p.ver, p.body,
             '' if s['body_matches'] else '(!! body + 0x80 != file size)'))
    print('   swfFILE +%02X    frames %d   fps %d' % (FILE_AT, p.frame_count, p.fps))
    print('   framesPtr      %08X %s' % (p.frames_ptr, 'ok' if s['frames_ok'] else 'OUTSIDE'))
    print('   objPtrList     %08X %s' % (p.obj_list, 'ok' if s['objlist_ok'] else 'OUTSIDE'))
    print('   objectCount    %d' % p.object_count)
    print('   pointers inside image  %d / %d' % (s['pointers_inside'], s['objects']))
    print('   recognised types       %d / %d' % (s['known_types'], s['objects']))
    hist = collections.Counter(OBJ_TYPES.get(t, '?%s' % t)
                               for _i, _va, t in p.objects())
    print('   objects by type:')
    for k, n in hist.most_common():
        print('      %-10s %d' % (k, n))


def cmd_objects(a):
    p = Pck(a.file)
    want = a.type.upper() if a.type else None
    for i, va, t in p.objects():
        nome = OBJ_TYPES.get(t, '?%s' % t)
        if want and nome != want:
            continue
        extra = ''
        if nome == 'SPRITE':
            fr = p.sprite_frames(va)
            extra = '%d frames' % len(fr)
        print('   %4d  %08X  %-9s %s' % (i, va, nome, extra))


def cmd_sprites(a):
    p = Pck(a.file)
    total_cmds = 0
    for i, va, t in p.objects():
        if OBJ_TYPES.get(t) != 'SPRITE':
            continue
        frames = p.sprite_frames(va)
        cmds = []
        for _fi, cva in frames:
            cmds += p.commands(cva)
        total_cmds += len(cmds)
        kinds = collections.Counter(CMD_TYPES.get(k, '?%d' % k) for _v, k in cmds)
        if not a.clips:
            print('   %4d  %08X  %2d frames  %s'
                  % (i, va, len(frames),
                     ' '.join('%s=%d' % kv for kv in sorted(kinds.items()))))
            continue
        # the names are what make a sprite identifiable from outside
        nomes = []
        for cva, k in cmds:
            if CMD_TYPES.get(k) == 'CLIPEVENT':
                s = p.cstr(p.u32(p.off(cva) + 0x24))
                if s:
                    nomes.append(s)
        if nomes:
            print('   %4d  %08X  %s' % (i, va, ', '.join(sorted(set(nomes)))))
    print('   -- %d commands walked' % total_cmds)


def cmd_strings(a):
    p = Pck(a.file)
    pat = re.compile(rb'[ -~]{%d,}' % a.min)
    seen = []
    for m in pat.finditer(p.d, HDR):
        seen.append((p.base + m.start() - HDR, m.group().decode('latin1')))
    if a.grep:
        rx = re.compile(a.grep, re.I)
        seen = [x for x in seen if rx.search(x[1])]
    for va, s in seen[:a.limit]:
        print('   %08X  %s' % (va, s))
    print('   -- %d strings' % len(seen))


def cmd_actions(a):
    p = Pck(a.file)
    blocos = p.action_blocks()
    if a.grep:
        rx = re.compile(a.grep, re.I)
        blocos = [b for b in blocos if any(rx.search(s) for s in prologue(p, b[3])[1])]
    print('   %d action blocks%s' % (len(blocos), ' matching' if a.grep else ''))
    for n, (owner, c, kind, code) in enumerate(blocos):
        if n >= a.limit:
            print('   ... stopping at --limit %d' % a.limit)
            break
        ins = avm1(p, code)
        _o, pool = prologue(p, code)
        dono = 'root' if owner < 0 else 'object %d' % owner
        print('   %s, %s at %08X -> code %08X, %d ops, %d pooled strings'
              % (dono, kind, c, code, len(ins), len(pool)))
        for off, nome, det in ins[:a.ops]:
            print('      %4d  %-14s %s' % (off, nome, det))
        if len(ins) > a.ops:
            print('      ... %d more' % (len(ins) - a.ops))
        print()


def cmd_diff(a):
    x, y = Pck(a.a), Pck(a.b)
    print('%-28s %-28s' % (os.path.basename(x.path), os.path.basename(y.path)))
    for nome, va, vb in (('objectCount', x.object_count, y.object_count),
                         ('body size', x.body, y.body),
                         ('frames', x.frame_count, y.frame_count)):
        print('   %-14s %-14s %-14s %s'
              % (nome, va, vb, '' if va == vb else '<-- differ'))
    hx = collections.Counter(OBJ_TYPES.get(t, '?') for _i, _v, t in x.objects())
    hy = collections.Counter(OBJ_TYPES.get(t, '?') for _i, _v, t in y.objects())
    print('   objects by type:')
    for k in sorted(set(hx) | set(hy)):
        print('      %-10s %-6d %-6d %s'
              % (k, hx.get(k, 0), hy.get(k, 0),
                 '' if hx.get(k) == hy.get(k) else '<-- differ'))
    sx = set(m.group() for m in re.finditer(rb'[ -~]{5,}', x.d))
    sy = set(m.group() for m in re.finditer(rb'[ -~]{5,}', y.d))
    print('   strings only in A: %d, only in B: %d, shared: %d'
          % (len(sx - sy), len(sy - sx), len(sx & sy)))


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='acao')
    for nome in ('info', 'objects', 'sprites', 'strings', 'actions'):
        s = sub.add_parser(nome)
        s.add_argument('file')
        if nome == 'objects':
            s.add_argument('--type')
        if nome == 'sprites':
            s.add_argument('--clips', action='store_true')
        if nome == 'strings':
            s.add_argument('--min', type=int, default=4)
            s.add_argument('--grep')
            s.add_argument('--limit', type=int, default=60)
        if nome == 'actions':
            s.add_argument('--limit', type=int, default=20)
            s.add_argument('--ops', type=int, default=40)
            s.add_argument('--grep')
    d = sub.add_parser('diff')
    d.add_argument('a')
    d.add_argument('b')

    v = sub.add_parser('vars')
    v.add_argument('elf', help='the game ELF, e.g. slus_213.55.ELF')
    v.add_argument('--list', action='store_true',
                   help='names and counts only, no call sites')
    v.add_argument('--grep', help='regex over the variable name')
    v.add_argument('--all', action='store_true',
                   help='include sites whose name is not a static string')

    a = ap.parse_args()
    if not a.acao:
        ap.print_help()
        return 1
    return {'info': cmd_info, 'objects': cmd_objects, 'sprites': cmd_sprites,
            'strings': cmd_strings, 'actions': cmd_actions,
            'diff': cmd_diff, 'vars': cmd_vars}[a.acao](a) or 0


if __name__ == '__main__':
    sys.exit(main())
