"""
mc3_alpha_map.py - read the October 2004 alpha's linker map (MC.MAP)

The alpha build ships the linker map the retail executable does not have: 20275
symbols with full C++ signatures, the section each one lives in, and the .obj it
was compiled from. `mc3_symbols.py` already carries the FUNCTION names over to
retail. This reads the rest, which nothing else does - of those 20275 symbols
only 16237 are code:

    data    2751 named globals in .data/.bss/.rodata, plus 1043 in
            .gnu.linkonce.d. Every fork here chases raw global addresses
            (dword_615B40, 0x0070E56C); the alpha names them.
    spad    the complete scratchpad layout at 0x70000000, 62 symbols
    vu      19 named VU microprograms with their byte ranges in .vutext
    units   which translation unit each symbol came from - 888 of them

`units` is what makes the neighbour pass in mc3_symbols.py safe. That pass walks
outward from an anchor naming whatever sits beside it and stops at the first
size disagreement, but it has no idea where one .cpp ends and the next begins.
A run that walks off the end of a translation unit names every function after it
wrongly, and nothing in the output says so. The map draws that line.

    python mc3_alpha_map.py census
    python mc3_alpha_map.py tree
    python mc3_alpha_map.py data --grep City
    python mc3_alpha_map.py vu
    python mc3_alpha_map.py spad
    python mc3_alpha_map.py units --grep mccity
    python mc3_alpha_map.py export --out output/alpha2004
    python mc3_alpha_map.py state --boot 40        boot the alpha, say where it is
    python mc3_alpha_map.py state FILE.p2s          the same from a savestate
"""

import argparse
import collections
import io
import os
import re
import struct
import sys

ALPHA_DIR = os.path.join(os.environ.get('MC_RESEARCH_ASSETS', ''), 'MIDNIGHT CLUB 3 DUB PS2 ALPHA BUILD 102404')
MAP = os.path.join(ALPHA_DIR, 'MC.MAP')

# The map is columnar and the column a name starts in is what says whether it is
# an output section, an input section, an object file or a symbol. Everything
# here depends on these four being right; the header line is
#     Address  Size     Align Out     In      File    Symbol
COL_OUT, COL_IN, COL_FILE, COL_SYM = 24, 32, 40, 48

# A section holding executable code. `.gnu.linkonce.t.*` is one per inline or
# template function - the compiler emits it in every translation unit that uses
# it and the linker keeps one. They are real functions and there are 1949 of them.
CODE_PREFIX = ('.text', '.gnu.linkonce.t')
DATA_PREFIX = ('.data', '.bss', '.rodata', '.sdata', '.sbss', '.rdata',
               '.gnu.linkonce.d', '.gnu.linkonce.r', '.lit4', '.lit8',
               '.scommon', '.sndata', '.ctors', '.dtors', '.gcc_except_table')

Sym = collections.namedtuple('Sym', 'addr size sec obj name')


def read_map(path=MAP):
    """Every symbol the map places, in file order.

    `<default>` rows are kept: they carry no name but they do carry the size of
    an anonymous chunk, which is the only thing that gives the VU overlays their
    page layout. Callers that want names filter with `named()`.
    """
    out = []
    sec_out = sec_in = obj = None
    for raw in io.open(path, encoding='latin1'):
        line = raw.rstrip('\n')
        if len(line) <= COL_OUT:
            continue
        try:
            addr = int(line[0:8], 16)
            size = int(line[9:17], 16)
        except ValueError:
            continue
        rest = line[COL_OUT:]
        if not rest.strip():
            continue
        col = COL_OUT + len(rest) - len(rest.lstrip())
        text = rest.strip()
        if col < COL_IN:
            sec_out, sec_in, obj = text, None, None
        elif col < COL_FILE:
            # `<default>` is the linker's unnamed chunk of the output section,
            # not a section name. Taking it literally costs the whole of
            # `.vutext` and a third of `.spad`: those output sections have no
            # named input section, so every symbol under them lands under
            # `<default>` and the VU microcode disappears from the census.
            sec_in = None if text == '<default>' else text
        elif col < COL_SYM:
            obj = None if text == '<default>' else text
        else:
            out.append(Sym(addr, size, sec_in or sec_out, obj, text))
    return out


def named(syms):
    return [s for s in syms if s.name and s.name != '<default>']


def is_code(s):
    return bool(s.sec) and s.sec.startswith(CODE_PREFIX)


def is_data(s):
    return bool(s.sec) and s.sec.startswith(DATA_PREFIX)


LIB_RE = re.compile(r'([A-Za-z0-9_]+\.lib)\(([^)]+)\)')


def unit(obj):
    """('mcgame.lib', 'game.obj', 'c:/soft/mc3/src/mcgame') for one map path.

    The map writes the full build path of the library plus the object inside it,
    which is the original source tree: `c:/soft/age/src/` is the shared engine
    and `c:/soft/mc3/src/` is the game. The `psx2_final` leaf is the build
    configuration, not a source directory, so it comes off.
    """
    if not obj:
        return (None, None, None)
    p = obj.replace(chr(92), '/')
    m = LIB_RE.search(p)
    lib, name = (m.group(1), m.group(2)) if m else (None, p.rsplit('/', 1)[-1])
    head = p.rsplit('/', 1)[0] if '/' in p else ''
    head = re.sub(r'/psx2_final$', '', head)
    return (lib, name, head)


def cmd_census(a):
    syms = read_map(a.map)
    nm = named(syms)
    print('%s' % a.map)
    print('%d rows, %d named' % (len(syms), len(nm)))
    code = [s for s in nm if is_code(s)]
    data = [s for s in nm if is_data(s)]
    resto = [s for s in nm if not is_code(s) and not is_data(s)]
    print('   code   %5d   (.text %d, .gnu.linkonce.t %d)'
          % (len(code),
             sum(1 for s in code if s.sec.startswith('.text')),
             sum(1 for s in code if s.sec.startswith('.gnu.linkonce.t'))))
    print('   data   %5d' % len(data))
    print('   other  %5d   (scratchpad, VU, overlays, absolutes)' % len(resto))
    print()
    por_sec = collections.Counter()
    for s in nm:
        k = s.sec or '?'
        for p in CODE_PREFIX + DATA_PREFIX:
            if k.startswith(p):
                k = p + '*' if k != p else p
                break
        if k.startswith('.DVP'):
            k = '.DVP.overlay*'
        por_sec[k] += 1
    for k, v in por_sec.most_common():
        print('   %-24s %5d' % (k, v))
    print()
    libs = collections.defaultdict(set)
    for s in syms:
        lib, obj, _d = unit(s.obj)
        if obj:
            libs[lib or '(direct)'].add(obj)
    print('%d translation units in %d libraries'
          % (sum(len(v) for v in libs.values()), len(libs)))
    for k, v in sorted(libs.items(), key=lambda kv: -len(kv[1]))[:a.top]:
        print('   %-24s %3d obj' % (k, len(v)))


def cmd_tree(a):
    syms = read_map(a.map)
    dirs = collections.defaultdict(set)
    for s in syms:
        lib, obj, d = unit(s.obj)
        if obj:
            dirs[d].add(obj)
    print('%d source directories, %d translation units'
          % (len(dirs), sum(len(v) for v in dirs.values())))
    for d in sorted(dirs):
        print('   %-50s %3d' % (d, len(dirs[d])))


def _grep(rows, pat, key):
    if not pat:
        return rows
    r = re.compile(pat, re.I)
    return [x for x in rows if r.search(key(x))]


def cmd_data(a):
    rows = [s for s in named(read_map(a.map)) if is_data(s)]
    rows = _grep(rows, a.grep, lambda s: s.name)
    print('%d named globals%s' % (len(rows), (' matching %r' % a.grep) if a.grep else ''))
    for s in sorted(rows):
        lib, obj, _d = unit(s.obj)
        print('   %08X %6X  %-16s %-22s %s'
              % (s.addr, s.size, s.sec[:16], (obj or '')[:22], s.name))


def cmd_spad(a):
    rows = [s for s in named(read_map(a.map)) if s.sec == '.spad']
    spr = sorted(s for s in rows if 0x70000000 <= s.addr < 0x70004000)
    resto = sorted(s for s in rows if s not in spr)
    print('scratchpad, %d symbols at 0x70000000' % len(spr))
    fim = 0
    for s in spr:
        if s.addr > fim and fim:
            print('   %08X %6X   -- %d bytes unaccounted --'
                  % (fim, s.addr - fim, s.addr - fim))
        lib, obj, _d = unit(s.obj)
        print('   %08X %6X  %-22s %s' % (s.addr, s.size, (obj or '')[:22], s.name))
        fim = max(fim, s.addr + s.size)
    print()
    print('linker constants carried in the same section:')
    for s in resto:
        print('   %08X %6X  %s' % (s.addr, s.size, s.name))


VU_START = ('_DmaTag', '_start_')
VU_END = ('_DmaEnd', '_end_')


def vu_programs(syms):
    """{name: {...}} for each VU microprogram the map places.

    A program appears twice. In `.vutext` it is a DMA chain in main memory,
    bracketed by `X_DmaTag`/`X_DmaEnd` (the older gfx ones use `X_start_`/
    `X_end_`) - that is what a DMA transfer hands to the VIF, and it is why
    searching the executable for an MPG tag finds nothing: the upload is built
    by the chain, not stamped in the data. In a `.DVP.overlay` section the same
    program appears as VU-local code, bracketed by `X_CodeStart`/`X_CodeEnd`,
    paged in 0x800-byte chunks; that pair gives the size in VU instruction
    memory, and any other symbol in that section is a named entry point.
    """
    prog = {}
    for s in named(syms):
        sec = s.sec or ''
        if sec == '.vutext':
            for suf in VU_START:
                if s.name.endswith(suf):
                    p = prog.setdefault(s.name[:-len(suf)], {})
                    p['elf_start'], p['obj'] = s.addr, s.obj
            for suf in VU_END:
                if s.name.endswith(suf):
                    prog.setdefault(s.name[:-len(suf)], {})['elf_end'] = s.addr
        elif sec.startswith('.DVP'):
            if s.name.endswith('_CodeStart'):
                prog.setdefault(s.name[:-len('_CodeStart')], {})['vu_start'] = s.addr
            elif s.name.endswith('_CodeEnd'):
                prog.setdefault(s.name[:-len('_CodeEnd')], {})['vu_end'] = s.addr
            else:
                # a named address inside the microprogram: an entry point, or a
                # routine the C++ side jumps to (vu0_sincos, rv1_BindNextState)
                lib, obj, _d = unit(s.obj)
                prog.setdefault('@' + (obj or '?'), {}).setdefault(
                    'entries', []).append((s.addr, s.name))
    return prog


def cmd_vu(a):
    syms = read_map(a.map)
    prog = vu_programs(syms)
    dono = {}
    for k, v in prog.items():
        if not k.startswith('@'):
            _l, o, _d = unit(v.get('obj'))
            if o:
                dono['@' + o] = k
    print('VU microcode in the alpha ELF')
    print('%-26s %-19s %8s %8s %s'
          % ('program', 'ELF range', 'ELF sz', 'VU sz', 'object'))
    for k in sorted(prog):
        if k.startswith('@'):
            continue
        v = prog[k]
        s0, s1 = v.get('elf_start'), v.get('elf_end')
        lib, obj, _d = unit(v.get('obj'))
        print('%-26s %08X..%08X %8X %8X %s'
              % (k[:26], s0 or 0, s1 or 0, (s1 - s0) if s0 and s1 else 0,
                 v.get('vu_end', 0), obj or ''))
    print()
    print('named addresses inside the microprograms (VU-local):')
    for k in sorted(prog):
        if not k.startswith('@'):
            continue
        for addr, nome in sorted(prog[k].get('entries', [])):
            print('   %-26s +%04X  %s' % (dono.get(k, k[1:])[:26], addr, nome))


RETAIL_ELF = os.path.join(os.environ.get('MC_WORK_DIR', ''), 'slus_213.55')
ALPHA_ELF = os.path.join(ALPHA_DIR, 'SLUS_123.45')

OV_RE = re.compile(r'^[.]DVP[.]overlay[.][.]([^.]+)[.](\d+)[.](\d+)[.](\d+)$')

# The retail names, read out of retail itself. `mcTextureFactory::mcTextureFactory`
# (0x003B5750) registers the shader microcode with
# `rmcShader::AddMicrocode(char const*, unsigned int const*)`, and the two
# arguments of that call are the name string and the chain address:
#
#     li  $a0, aCarbonFiberDc      # "carbon_fiber_dc"
#     jal rmcShader__AddMicrocode
#     li  $a1, dword_602290        # the DMA chain, in the delay slot
#
# So this table owes nothing to the alpha. It is here as the answer key that the
# overlay-id route below is checked against - and the two agree 10 for 10.
VERIFICADO = {
    0x005F8ED0: 'noise_pointlight_dc',
    0x005F5DA0: 'noise_cn_pointlight_dc',
    0x005F2D10: 'noise_cn_lighttexgen_dc',
    0x00604640: 'carpaint_3pass_dc',
    0x00609860: 'cpv_distort_vtx_dc',
    0x00606B00: 'city_reflect_ci',
    0x005FBF00: 'skinned_fresnel',
    0x00600210: 'texgen_fresnel_dc',
    0x0060E9A0: 'light_texgen_dc',
    0x0060C890: 'distort_dc',
    0x00602290: 'carbon_fiber_dc',
    0x005FE010: 'specular2_dc',
}

# Who consumes the nine that AddMicrocode does not register, from IDA xrefs.
CONSUMIDOR = {
    0x005E9610: 'rmcSetCpvMode',
    0x005EC4F0: 'rmcSetCpvMode',
    0x005EF9A0: 'mcInstBucket::Draw',
    0x005EFD40: '(sem xref direto)',
    0x005F1390: 'ptxMicrocode',
    0x005F29C0: 'mcOccluderSystem::PrepOccluders_VU0',
    0x00610A60: 'lowPsxGfx::DoMicrocode',
    0x00612010: 'lowPsxGfx::DoMicrocode, MainMicrocode+0',
    0x00613FB0: 'gfxPointSpriteBegin, MainMicrocode+4',
}


def secoes(path):
    """[(name, type, addr, offset, size)] from an ELF section header table.

    Both executables keep theirs - retail is not stripped, which is what makes
    any of this possible without the map.
    """
    d = io.open(path, 'rb').read()
    shoff = struct.unpack_from('<I', d, 0x20)[0]
    shent, shnum, shstrndx = struct.unpack_from('<HHH', d, 0x2E)
    so = shoff + shstrndx * shent
    st_off, st_size = struct.unpack_from('<II', d, so + 0x10)
    strs = d[st_off:st_off + st_size]
    out = []
    for i in range(shnum):
        o = shoff + i * shent
        nm, typ, _flg, addr, off, size = struct.unpack_from('<6I', d, o)
        out.append((strs[nm:strs.find(b'\0', nm)].decode('latin1'),
                    typ, addr, off, size))
    return d, out


def overlays(secl):
    """{overlay id: total VU code size}, in section order.

    The `.DVP.overlay` sections are SHT_NOBITS - they carry no bytes, only the
    reservation of VU instruction memory, split into 0x800 pages (256
    instructions, which is one MPG packet). The number in the section name is
    stable across builds and is what identifies a program.
    """
    g = collections.OrderedDict()
    for n, _t, _a, _o, s in secl:
        m = OV_RE.match(n)
        if m:
            k = int(m.group(2))
            g[k] = g.get(k, 0) + s
    return g


def cadeia(d, vaddr, voff, vsize):
    """Walk `.vutext` as a DMA chain: [(vaddr, size)] per program.

    Each program starts with a source-chain DMA tag whose low 16 bits are the
    qword count of everything that follows it, so one tag read gives the whole
    program's length and the next tag's position. Checked against the alpha,
    where MC.MAP gives the true boundaries: 16 of 16 exact. The three `rv1_*`
    blocks at the end of the segment are not chains - they are the older
    gfx.lib VU1 code, bracketed by `_start_`/`_end_` instead - and the walk
    stops when it stops seeing tags.
    """
    blocos, p = [], 0
    while p + 4 <= vsize:
        tag = struct.unpack_from('<I', d, voff + p)[0]
        if (tag >> 16) != 0x6000:
            break
        n = ((tag & 0xFFFF) + 1) * 16
        if n <= 0 or p + n > vsize:
            break
        blocos.append((vaddr + p, n))
        p += n
    return blocos, p


def cmd_vuretail(a):
    dA, sA = secoes(a.alpha)
    dR, sR = secoes(a.retail)
    ovA, ovR = overlays(sA), overlays(sR)
    vtR = [x for x in sR if x[0] == '.vutext'][0]
    _n, _t, va, vo, vs = vtR
    blocos, parou = cadeia(dR, va, vo, vs)

    prog = vu_programs(read_map(a.map))
    ordem = [k for _s, k, _v in
             sorted((v.get('elf_start', 0), k, v)
                    for k, v in prog.items() if not k.startswith('@'))]
    nome_por_id = dict(zip(list(ovA), ordem))

    print('retail .vutext %08X..%08X (%X bytes); %d programas em cadeia, '
          '%X bytes de rv1_* no fim' % (va, va + vs, vs, len(blocos), vs - parou))
    print('overlays: alpha %d ids, retail %d ids; novos no retail: %s'
          % (len(ovA), len(ovR), ' '.join(str(k) for k in ovR if k not in ovA)))
    print()
    print('%-26s %-19s %-8s %-8s %-6s %s'
          % ('programa', 'faixa retail', 'cadeia', 'codigo', 'id ok', 'origem do nome'))
    idsR = list(ovR)
    bate = discorda = 0
    for i, (ini, n) in enumerate(blocos):
        oid = idsR[i] if i < len(idsR) else None
        porid = nome_por_id.get(oid)
        ver = VERIFICADO.get(ini)
        nome = ver or porid or '?'
        if ver and porid:
            if ver == porid:
                bate += 1
                origem = 'AddMicrocode = overlay'
            else:
                discorda += 1
                origem = 'DISCORDA: overlay diz %s' % porid
        elif ver:
            origem = 'AddMicrocode (id %s e novo)' % oid
        else:
            origem = CONSUMIDOR.get(ini, 'overlay id')
        print('%-26s %08X..%08X %-8X %-8X %-6s %s'
              % (nome[:26], ini, ini + n, n, ovR.get(oid, 0),
                 'sim' if oid in ovA else 'novo', origem))
    # Os rv1_*, que nao sao cadeia, ficam no rabo do segmento. Sem tag de DMA
    # nao ha tamanho para ler, entao ele sai do overlay do retail mais o excesso
    # que o MESMO programa tem na alpha (onde MC.MAP da os dois numeros). Se a
    # conta fechar exatamente no fim do segmento, o rabo esta certo.
    p = va + parou
    for oid in idsR[len(blocos):]:
        k = nome_por_id.get(oid, '? id %s' % oid)
        v = prog.get(k, {})
        folga = (v.get('elf_end', 0) - v.get('elf_start', 0)) - ovA.get(oid, 0)
        tam = ovR.get(oid, 0) + max(folga, 0)
        print('%-26s %08X..%08X %-8X %-8X %-6s %s'
              % (k[:26], p, p + tam, tam, ovR.get(oid, 0),
                 'sim' if oid in ovA else 'novo',
                 CONSUMIDOR.get(p, 'nao e cadeia (_start_/_end_)')))
        p += tam
    print()
    print('conferencia cruzada: %d nomes iguais pelas duas rotas, %d divergentes'
          % (bate, discorda))
    if p != va + vs:
        print('AVISO: o fim calculado %08X nao fecha com o fim do segmento %08X'
              % (p, va + vs))
    else:
        print('o segmento fecha exatamente em %08X' % p)


def cmd_units(a):
    syms = read_map(a.map)
    rows = [s for s in named(syms) if is_code(s)]
    rows = _grep(rows, a.grep, lambda s: (s.obj or '') + ' ' + s.name)
    porobj = collections.defaultdict(list)
    for s in rows:
        porobj[s.obj].append(s)
    print('%d code symbols in %d translation units' % (len(rows), len(porobj)))
    for obj in sorted(porobj, key=lambda o: min(x.addr for x in porobj[o])):
        rs = sorted(porobj[obj])
        lib, nome, d = unit(obj)
        print('   %08X..%08X  %-22s %-34s %d sym'
              % (rs[0].addr, rs[-1].addr + rs[-1].size, (nome or '')[:22],
                 (d or '')[:34], len(rs)))
        if a.verbose:
            for s in rs:
                print('        %08X %6X  %s' % (s.addr, s.size, s.name))


def cmd_export(a):
    syms = read_map(a.map)
    nm = named(syms)
    if not os.path.isdir(a.out):
        os.makedirs(a.out)

    def grava(nome, linhas, cab):
        p = os.path.join(a.out, nome)
        with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
            f.write(cab + '\n')
            f.write('\n'.join(linhas) + '\n')
        print('   %-22s %5d linhas -> %s' % (nome, len(linhas), p))

    code = [s for s in nm if is_code(s)]
    grava('alpha_units.tsv',
          ['%08X\t%d\t%s\t%s' % (s.addr, s.size, unit(s.obj)[1] or '', s.name)
           for s in sorted(code)],
          '# addr\tsize\tobj\tname   (alpha .text symbols, translation unit)')

    data = [s for s in nm if is_data(s)]
    grava('alpha_data.tsv',
          ['%08X\t%d\t%s\t%s\t%s'
           % (s.addr, s.size, s.sec, unit(s.obj)[1] or '', s.name)
           for s in sorted(data)],
          '# addr\tsize\tsection\tobj\tname   (alpha named globals)')

    spad = [s for s in nm if s.sec == '.spad']
    grava('alpha_spad.tsv',
          ['%08X\t%d\t%s\t%s' % (s.addr, s.size, unit(s.obj)[1] or '', s.name)
           for s in sorted(spad)],
          '# addr\tsize\tobj\tname   (scratchpad + linker constants)')

    prog = vu_programs(syms)
    linhas = []
    for k in sorted(prog):
        if k.startswith('@'):
            continue
        v = prog[k]
        linhas.append('%08X\t%08X\t%X\t%s\t%s'
                      % (v.get('elf_start', 0), v.get('elf_end', 0),
                         v.get('vu_end', 0), unit(v.get('obj'))[1] or '', k))
    grava('alpha_vu.tsv', linhas,
          '# elf_start\telf_end\tvu_size\tobj\tprogram   (VU microcode)')


# ---------------------------------------------------------------------------
# state: where the alpha is, from a PCSX2 savestate, in MC.MAP's names
# ---------------------------------------------------------------------------
ALPHA_LOADER = os.path.join(os.environ.get('MC3_ALPHA_HOSTFS', ''), 'mc3boot_alpha.elf')


def p2s_members(path):
    """{name: bytes} of a PCSX2 savestate. The members are zstd (zip method
    93), which zipfile will not inflate, so each is read raw and decompressed."""
    import zipfile
    import zstandard
    z = open(path, 'rb').read()
    out = {}
    for info in zipfile.ZipFile(io.BytesIO(z)).infolist():
        o = info.header_offset
        n, m = struct.unpack_from('<HH', z, o + 26)
        data = z[o + 30 + n + m:o + 30 + n + m + info.compress_size]
        if info.compress_type == 93:
            data = zstandard.ZstdDecompressor().decompress(data, max_output_size=64 << 20)
        out[info.filename] = data
    return out


def boot_and_save(seconds, slot=9, elf=ALPHA_LOADER):
    """Boot the alpha through mc3boot_alpha, wait, savestate over PINE.

    Slot 9 so the other forks' slot 1 (the F1 hotkey) and 3 (mc3_savestate)
    are left alone. Returns the .p2s path."""
    import glob
    import importlib.util
    import subprocess
    import time
    s = importlib.util.spec_from_file_location(
        'mc3_savestate', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mc3_savestate.py'))
    ss = importlib.util.module_from_spec(s)
    s.loader.exec_module(ss)
    p = subprocess.Popen([ss.PCSX2, '-batch', '-nogui', '--', elf],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    path = None
    try:
        time.sleep(seconds)
        pine = ss.Pine()
        t0 = time.time()
        while True:
            try:
                pine._call(struct.pack('<BB', ss.SAVESTATE, slot), 0)
                break
            except ss.NotReady:
                if time.time() - t0 > 30:
                    raise
                time.sleep(1)
        last = -1
        for _ in range(60):
            time.sleep(1)
            cand = [f for f in glob.glob(os.path.join(ss.SSTATES, '*.%02d.p2s' % slot))
                    if os.path.getmtime(f) > t0 - 2]
            if cand:
                path = max(cand, key=os.path.getmtime)
                size = os.path.getsize(path)
                if size == last and size > 0:
                    break
                last = size
    finally:
        p.kill()
        p.wait()
    if not path:
        raise SystemExit('no savestate appeared in slot %d' % slot)
    return path


def cmd_state(a):
    import bisect
    path = a.file or boot_and_save(a.boot, a.slot)
    st = p2s_members(path)
    ram = st['eeMemory.bin']
    dat = st['PCSX2 Internal Structures.dat']
    syms = sorted((s.addr, s.size, s.name) for s in named(read_map(a.map)))
    addrs = [s[0] for s in syms]

    def name(va):
        i = bisect.bisect_right(addrs, va) - 1
        if i < 0:
            return '?'
        ad, sz, nm = syms[i]
        return ('%s+0x%X' % (nm, va - ad)) if va < ad + max(sz, 4) else '(after %s)' % nm

    def text(va, n=72):
        if not 0x100000 <= va < 0x2000000:
            return ''
        o = va & 0x1FFFFFF
        e = ram.find(b'\0', o, o + n)
        s = ram[o:e if e >= 0 else o + n]
        return repr(s.decode('latin-1')) if s and all(32 <= c < 127 for c in s) else ''

    # cpuRegs as R5900.h lays it out: 32 GPR of 16 bytes, HI, LO, CP0, sa,
    # IsDelaySlot, pc at +680 - after a tag zero-padded to 32 bytes
    base = dat.find(b'cpuRegs\0') + 32
    gpr = [struct.unpack_from('<I', dat, base + 16 * i)[0] for i in range(32)]
    pc = struct.unpack_from('<I', dat, base + 680)[0]
    print('%s' % path)
    print('   pc %08X  %s' % (pc, name(pc)))
    print('   ra %08X  %s' % (gpr[31], name(gpr[31])))
    # a hang in a loader usually still has the name it was given in a register
    for nm, i in (('a0', 4), ('a1', 5), ('a2', 6), ('s0', 16), ('s1', 17), ('s2', 18), ('s3', 19)):
        t = text(gpr[i])
        if t:
            print('   %s %08X  %s' % (nm, gpr[i], t))
    # the kernel's thread table: 256 records of 76 bytes at 0x8001A580
    print('   threads:')
    for tid in range(256):
        o = 0x1A580 + 76 * tid
        status = struct.unpack_from('<I', ram, o + 8)[0]
        if not status or status > 16:
            continue
        resume, regctx = struct.unpack_from('<II', ram, o + 12)
        wtype, sema = struct.unpack_from('<II', ram, o + 28)
        entry = struct.unpack_from('<I', ram, o + 48)[0]
        sra = 0
        if regctx and (regctx & 0x1FFFFFF) + 16 * 32 <= len(ram):
            sra = struct.unpack_from('<I', ram, (regctx & 0x1FFFFFF) + 16 * 31)[0]
        state = {1: 'RUN', 2: 'READY', 4: 'WAIT', 8: 'SUSPEND', 12: 'WAITSUSP',
                 16: 'DORMANT'}.get(status, status)
        print('     %3d %-8s %s entry %-40s at %-44s ra %s'
              % (tid, state, ('sema %3d' % sema) if wtype == 2 else '        ',
                 name(entry)[:40], name(resume)[:44], name(sra)[:50] if sra else '-'))
    if a.shot and st.get('Screenshot.png'):
        open(a.shot, 'wb').write(st['Screenshot.png'])
        print('   screenshot -> %s' % a.shot)


def cmd_decomp(a):
    """Export a resumable research corpus, separate from reconstructed C++."""
    import hashlib
    import json
    import time
    from pathlib import Path
    import mc3_ida

    root = Path(a.project).resolve()
    root.mkdir(parents=True, exist_ok=True)
    identity = hashlib.sha256(Path(a.map).read_bytes()).hexdigest()
    binary_identity = hashlib.sha256(Path(a.binary).read_bytes()).hexdigest()
    manifest_path = root / 'inventory' / 'progress.json'
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding='utf-8'))
        if previous.get('map_sha256') != identity or \
                previous.get('elf_sha256', binary_identity) != binary_identity:
            raise SystemExit('Input identity changed: use a fresh project research directory')
    inventory = root / 'inventory'
    research = root / 'research' / 'pseudocode'
    inventory.mkdir(exist_ok=True)
    research.mkdir(parents=True, exist_ok=True)
    symbols = named(read_map(a.map))
    records = []
    paths = {}
    for s in symbols:
        lib, obj, directory = unit(s.obj)
        # Preserve source directories and library names to avoid basename collisions.
        original = (directory or 'unattributed').replace(':', '')
        safe = '/'.join(re.sub(r'[^A-Za-z0-9_.-]', '_', p)
                        for p in original.split('/') if p and p not in ('.', '..'))
        relative = safe + '/' + (lib or 'direct') + '/' + (obj or 'unknown')
        relative = re.sub(r'[^A-Za-z0-9_/.-]', '_', relative)
        paths[s.obj] = relative
        records.append(dict(address=s.addr, size=s.size, section=s.sec,
                            signature=s.name, original_object=s.obj,
                            library=lib, unit=relative, is_code=is_code(s)))
    def save(path, value):
        temp = path.with_suffix(path.suffix + '.tmp')
        temp.write_text(json.dumps(value, indent=2, ensure_ascii=True), encoding='utf-8')
        temp.replace(path)
    save(inventory / 'map_symbols.json', dict(map_sha256=identity,
                                             elf_sha256=binary_identity, symbols=records))
    binary, sections = secoes(a.binary)
    address_names = collections.defaultdict(list)
    for r in records:
        address_names[r['address']].append(r['signature'])
    tables = []
    for r in records:
        if 'virtual table' not in r['signature']:
            continue
        table = dict(r)
        table['words'] = []
        for _name, section_type, address, file_offset, size in sections:
            if section_type != 8 and address <= r['address'] and \
                    r['address'] + r['size'] <= address + size:
                offset = file_offset + r['address'] - address
                for index in range(r['size'] // 4):
                    value = struct.unpack_from('<I', binary, offset + index * 4)[0]
                    table['words'].append(dict(offset=index * 4, value=value,
                                               exact_symbols=address_names.get(value, [])))
                break
        tables.append(table)
    save(inventory / 'vtables.json', tables)
    sym_records = []
    for line in Path(a.sym).read_text(encoding='latin1').splitlines():
        match = re.match(r'^\s*([0-9A-Fa-f]+)\s+(\w)\s+(.+)$', line)
        if match:
            sym_records.append(dict(address=int(match.group(1), 16),
                                    kind=match.group(2), name=match.group(3)))
        elif line.strip():
            sym_records.append(dict(raw=line.strip()))
    save(inventory / 'nm_symbols.json', sym_records)
    classes = collections.defaultdict(list)
    for r in records:
        prefix = r['signature'].split('(', 1)[0]
        if r['is_code'] and '::' in prefix:
            classes[prefix.rsplit('::', 1)[0]].append(r['address'])
    save(inventory / 'classes.json', dict(classes))
    save(inventory / 'vu_programs.json', vu_programs(read_map(a.map)))
    # A skeleton is documentation, never a collection of fake implementations.
    for original, relative in paths.items():
        if not original:
            continue
        cpp = root / 'src' / 'original' / (relative + '.cpp')
        cpp.parent.mkdir(parents=True, exist_ok=True)
        if not cpp.exists():
            members = [r for r in records if r['original_object'] == original and r['is_code']]
            lines = ['// Original translation unit: ' + original,
                     '// Inventory only. No function is implemented by this file.']
            lines += ['// 0x%08X | %d bytes | %s' %
                      (r['address'], r['size'], r['signature']) for r in members]
            cpp.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('Inventory: %d symbols, %d object paths, %d vtables' %
          (len(records), sum(bool(x) for x in paths),
           sum('virtual table' in r['signature'] for r in records)), flush=True)
    if a.inventory_only:
        return
    index_path = inventory / 'ida_functions.json'
    if not index_path.exists():
        index = mc3_ida.run(mc3_ida.py('''
import json
emit(json.dumps([dict(address=ea, name=idc.get_func_name(ea),
                     size=ida_funcs.get_func(ea).end_ea-ea)
                 for ea in idautils.Functions()]))
'''), a.elf)
        save(index_path, dict(map_sha256=identity, functions=json.loads(index)))
    index = json.loads(index_path.read_text(encoding='utf-8'))
    if index['map_sha256'] != identity:
        raise SystemExit('MAP changed: use a fresh project research directory')
    targets = [r for r in records if r['is_code']]
    known = {r['address'] for r in targets}
    for r in index['functions']:
        if r['address'] not in known:
            targets.append(dict(address=r['address'], size=r['size'], signature=r['name'],
                                original_object=None, library=None,
                                unit='unattributed/ida_only', is_code=True))
    if a.library:
        targets = [r for r in targets if r['library'] in a.library]
    targets.sort(key=lambda r: (r['unit'], r['address']))
    manifest_path = inventory / 'progress.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}
    if manifest and manifest.get('map_sha256') != identity:
        raise SystemExit('MAP changed: refusing to reuse previous progress')
    manifest.setdefault('map_sha256', identity)
    manifest.setdefault('elf_sha256', binary_identity)
    manifest.setdefault('functions', {})
    completed = manifest['functions']
    pending = [r for r in targets if '%08X' % r['address'] not in completed or
               (a.retry_failed and completed['%08X' % r['address']]['extraction'] == 'failed')]
    if a.max_functions:
        pending = pending[:a.max_functions]
    for start in range(0, len(pending), a.batch_size):
        batch = pending[start:start + a.batch_size]
        addresses = sorted({r['address'] for r in batch})
        body = '''
import json, time
if not HEX:
    raise RuntimeError('Hex-Rays MIPS is unavailable')
results=[]
for ea in %r:
    started=time.perf_counter()
    f=ida_funcs.get_func(ea)
    result=dict(address=ea, ida_name=idc.get_func_name(ea))
    try:
        if not f or f.start_ea != ea:
            raise ValueError('MAP address is not an IDA function start')
        cfunc=ida_hexrays.decompile(ea)
        if cfunc is None:
            raise ValueError('Hex-Rays returned no pseudocode')
        result.update(status='extracted', pseudocode=str(cfunc))
    except Exception as exc:
        result.update(status='failed', error=repr(exc))
    result['seconds']=time.perf_counter()-started
    results.append(result)
emit(json.dumps(results, ensure_ascii=True))
''' % addresses
        began = time.perf_counter()
        results = json.loads(mc3_ida.run(mc3_ida.py(body), a.elf))
        elapsed = time.perf_counter() - began
        by_address = {r['address']: r for r in results}
        batch_key = hashlib.sha256(','.join(map(str, addresses)).encode()).hexdigest()[:16]
        save(research / ('batch_' + batch_key + '.json'),
             dict(map_sha256=identity, wall_seconds=elapsed, results=results, symbols=batch))
        for r in batch:
            result = by_address[r['address']]
            key = '%08X' % r['address']
            completed[key] = dict(unit=r['unit'], library=r['library'],
                                  signature=r['signature'], extraction=result['status'],
                                  reconstructed=False, compiled=False, validated=False,
                                  batch=batch_key)
            output = research / r['unit'] / (key + '.txt')
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text('// %s @ 0x%s (%d MAP/IDA bytes)\n%s\n' %
                              (r['signature'], key, r['size'],
                               result.get('pseudocode', result.get('error'))), encoding='utf-8')
        save(manifest_path, manifest)
        print('Batch %s: %d/%d extracted, %.3f s wall; %d total recorded' %
              (batch_key, sum(r['status'] == 'extracted' for r in results),
               len(results), elapsed, len(completed)), flush=True)
    counts = collections.Counter(r['extraction'] for r in completed.values())
    all_targets = [r for r in records if r['is_code']]
    map_addresses = {r['address'] for r in all_targets}
    all_targets += [dict(address=r['address'], unit='unattributed/ida_only', library=None)
                    for r in index['functions'] if r['address'] not in map_addresses]
    expected_addresses = {r['address'] for r in all_targets}
    grouped = collections.defaultdict(list)
    for r in all_targets:
        grouped[(r['library'] or '(direct/IDA)', r['unit'])].append(r['address'])
    rows = ['library\tunit\tsymbols\taddresses\textracted\tfailed\tpending\treconstructed\tcompiled\tvalidated']
    for (library, source_unit), addresses in sorted(grouped.items()):
        states = [completed.get('%08X' % ea, {}) for ea in set(addresses)]
        values = [len(addresses), len(states),
                  sum(s.get('extraction') == 'extracted' for s in states),
                  sum(s.get('extraction') == 'failed' for s in states),
                  sum(not s for s in states)]
        values += [sum(bool(s.get(flag)) for s in states)
                   for flag in ('reconstructed', 'compiled', 'validated')]
        rows.append('\t'.join([library, source_unit] + list(map(str, values))))
    (inventory / 'progress_by_unit.tsv').write_text('\n'.join(rows) + '\n', encoding='utf-8')
    save(inventory / 'progress_summary.json',
         dict(expected_addresses=len(expected_addresses), recorded_addresses=len(completed),
              extraction=dict(counts), pending=len(expected_addresses - {int(k, 16) for k in completed}),
              reconstructed=sum(bool(r.get('reconstructed')) for r in completed.values()),
              compiled=sum(bool(r.get('compiled')) for r in completed.values()),
              validated=sum(bool(r.get('validated')) for r in completed.values())))
    print('Progress: ' + str(dict(counts)), flush=True)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__.strip().splitlines()[1],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--map', default=MAP)
    sub = ap.add_subparsers(dest='acao')

    c = sub.add_parser('census', help='summary by section and library')
    c.add_argument('--top', type=int, default=20)
    sub.add_parser('tree', help='the original source tree')
    d = sub.add_parser('data', help='named globals')
    d.add_argument('--grep')
    sub.add_parser('spad', help='the scratchpad layout')
    sub.add_parser('vu', help='the VU microcode map')
    u = sub.add_parser('units', help='symbols grouped by translation unit')
    u.add_argument('--grep')
    u.add_argument('-v', '--verbose', action='store_true')
    e = sub.add_parser('export', help='write the tsv files other tools read')
    e.add_argument('--out', default='output/alpha2004')
    dc = sub.add_parser('decomp', help='resumable alpha inventory and pseudocode corpus')
    dc.add_argument('--project', required=True)
    dc.add_argument('--elf', default=os.path.join(ALPHA_DIR, 'SLUS_123.45_MAPSYM.i64'))
    dc.add_argument('--binary', default=ALPHA_ELF, help='read-only ELF for vtable words')
    dc.add_argument('--sym', default=os.path.join(ALPHA_DIR, 'MC.SYM'))
    dc.add_argument('--inventory-only', action='store_true')
    dc.add_argument('--library', action='append', help='limit extraction to a MAP library')
    dc.add_argument('--batch-size', type=int, default=512)
    dc.add_argument('--max-functions', type=int)
    dc.add_argument('--retry-failed', action='store_true', help='retry failed entries after analysis repair')
    vr = sub.add_parser('vuretail', help='carry the VU microcode map to retail')
    vr.add_argument('--alpha', default=ALPHA_ELF)
    vr.add_argument('--retail', default=RETAIL_ELF)
    st = sub.add_parser('state', help='where the running alpha is, from a savestate')
    st.add_argument('file', nargs='?', help='a .p2s; omit it to boot and take one')
    st.add_argument('--boot', type=float, default=40.0,
                    help='with no file: boot mc3boot_alpha, wait this long, savestate over PINE')
    st.add_argument('--slot', type=int, default=9)
    st.add_argument('--shot', help='also write the savestate screenshot here')

    a = ap.parse_args()
    if a.acao == 'decomp' and (a.batch_size < 1 or
                              (a.max_functions is not None and a.max_functions < 1)):
        ap.error('batch-size and max-functions must be positive')
    if not os.path.isfile(a.map):
        raise SystemExit('map not found: %s' % a.map)
    fn = {'census': cmd_census, 'tree': cmd_tree, 'data': cmd_data,
          'spad': cmd_spad, 'vu': cmd_vu, 'units': cmd_units,
          'export': cmd_export, 'vuretail': cmd_vuretail, 'state': cmd_state,
          'decomp': cmd_decomp}.get(a.acao)
    if not fn:
        ap.print_help()
        return 2
    fn(a)
    return 0


if __name__ == '__main__':
    sys.exit(main())
