"""
mc3_schema.py - read the .pck layout out of the game's own constructors

A `.pck` is a serialized object graph, and the code that reads it back is the
`X::X(datResource&)` constructor of every class in it. That constructor is the
specification: it walks the object, adds the load base to the fields that are
pointers, and recurses into the arrays. Nothing else in the file matters.

    if (field) field += base;                        -> that offset is a POINTER
    for (i < *(u16*)(this+K)) Ctor(ptr + i*S, res)   -> K is a COUNT that drives
                                                        an array of stride S

So a field the constructor never touches is dead weight, and a field it DOES
relocate had better hold a real offset - a wrong one becomes a wild pointer at
the first virtual call, which is the `Jump to unaligned address` this project
keeps hitting. A count written too low is worse than a crash: the constructor
simply stops relocating early, the rest of the array keeps raw file offsets, and
the geometry draws from whatever sits at that address in low memory.

The October 2004 alpha is what makes this readable at scale. Without it these
are 224 anonymous `sub_XXXXXX` and you cannot tell which type each one
serializes; `mc3_symbols.py` carries the names over, and this reads the code.

    python mc3_schema.py dump                 # decompile every ctor (needs IDA)
    python mc3_schema.py extract              # -> schema.tsv
    python mc3_schema.py show rmcModelGeom    # one type, contract plus source
    python mc3_schema.py selftest             # against contracts worked by hand
"""

import argparse
import collections
import importlib.util
import io
import os
import re
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _mod(nome):
    s = importlib.util.spec_from_file_location(nome, os.path.join(_AQUI, nome + '.py'))
    m = importlib.util.module_from_spec(s)
    sys.modules[nome] = m
    s.loader.exec_module(m)
    return m


_ida = _mod('mc3_ida')
_sym = _mod('mc3_symbols')

SAIDA = os.path.join(_AQUI, 'output', 'alpha2004')
FONTE = os.path.join(SAIDA, 'ctors.txt')
ESQUEMA = os.path.join(SAIDA, 'schema.tsv')

# `X__X_datResource__ref` after mc3_symbols' name cleaner: `::` became `__` and
# every other punctuation became `_`. A constructor is the one whose method name
# repeats the class name.
CTOR_RE = re.compile(r'^(\w+?)__(\w+)_datResource__ref(__\w+)?$')


def ctores(target='retail', map_path=None):
    """[(retail_addr, type name)] for every named datResource constructor."""
    if target == 'alpha':
        alpha = _mod('mc3_alpha_map')
        result = []
        for symbol in alpha.named(alpha.read_map(map_path or alpha.MAP)):
            if not alpha.is_code(symbol):
                continue
            match = re.match(r'^(\w+)::\1\(datResource\s*&(?:\)|\s*,)', symbol.name)
            if match:
                result.append((symbol.addr, match.group(1)))
        return sorted(set(result), key=lambda item: (item[1], item[0]))
    buf = io.StringIO()
    stdout, sys.stdout = sys.stdout, buf
    try:
        tab = _sym.camadas()
    finally:
        sys.stdout = stdout
    out = []
    for ea, (nome, _origem) in tab.items():
        m = CTOR_RE.match(nome)
        if m and m.group(1) == m.group(2):
            out.append((ea, m.group(1)))
    return sorted(out, key=lambda x: x[1])


DUMP = r'''
import ida_hexrays, ida_funcs, ida_auto
ida_auto.auto_wait()
try:
    ida_hexrays.init_hexrays_plugin()
except Exception:
    pass
ALVOS = %s
for ea, nome in ALVOS:
    emit('### %%s @ %%08X' %% (nome, ea))
    f = ida_funcs.get_func(ea)
    if not f or f.start_ea != ea:
        emit('!! sem funcao neste endereco')
        continue
    try:
        emit(str(ida_hexrays.decompile(ea)))
    except Exception as e:
        emit('!! falhou: %%r' %% (e,))
'''


def dump(elf, out, target='retail', map_path=None, corpus=None):
    alvos = ctores(target, map_path)
    print('%d construtores datResource& nomeados' % len(alvos))
    if corpus:
        import hashlib
        import json
        from pathlib import Path
        if target != 'alpha':
            raise SystemExit('--corpus requires --target alpha')
        alpha = _mod('mc3_alpha_map')
        expected = hashlib.sha256(Path(map_path or alpha.MAP).read_bytes()).hexdigest()
        results = {}
        for path in (Path(corpus) / 'research' / 'pseudocode').glob('batch_*.json'):
            batch = json.loads(path.read_text(encoding='utf-8'))
            if batch['map_sha256'] != expected:
                raise SystemExit('Corpus MAP identity does not match selected alpha MAP')
            results.update({r['address']: r for r in batch['results']})
        lines = []
        for ea, name in alvos:
            result = results.get(ea, {})
            lines.extend(['### %s @ %08X' % (name, ea),
                          result.get('pseudocode', '!! ' + result.get('error', 'pending extraction'))])
        txt = '\n'.join(lines)
    else:
        txt = _ida.run(_ida.py(DUMP % repr(alvos)), elf)
    if not os.path.isdir(os.path.dirname(out)):
        os.makedirs(os.path.dirname(out))
    io.open(out, 'w', encoding='utf-8').write(txt)
    n = txt.count('### ')
    print('gravado %s (%d funcoes, %d linhas)' % (out, n, txt.count('\n')))


def le_fonte(path=FONTE):
    """{type name: (addr, decompiled text)}"""
    out, nome, ea, buf = {}, None, 0, []
    for line in io.open(path, encoding='utf-8'):
        m = re.match(r'^### (\w+) @ ([0-9A-Fa-f]{8})$', line.rstrip())
        if m:
            if nome:
                out[nome] = (ea, ''.join(buf))
            nome, ea, buf = m.group(1), int(m.group(2), 16), []
        else:
            buf.append(line)
    if nome:
        out[nome] = (ea, ''.join(buf))
    return out


def _n(s):
    return int(s, 16) if s.lower().startswith('0x') else int(s)


# An argument of the constructor, as Hex-Rays names it: `a1`/`this` is the
# object, `a2` the datResource. Which is which is decided per function by
# whichever one is read at +4, since that is the load base.
ARG = r'(?:a\d+|this|v\d+)'
NUM = r'(?:0x[0-9A-Fa-f]+|\d+)'

# `*(_DWORD *)(a1 + 16) += *(_DWORD *)(a2 + 4);`
RELOC_A = re.compile(
    r'\*\(_DWORD \*\)\((%s) \+ (%s)\) \+= \*\(_DWORD \*\)\((%s) \+ 4\)' % (ARG, NUM, ARG))
# `*(_DWORD *)a1 += *(_DWORD *)(a2 + 4);`   (offset 0)
RELOC_A0 = re.compile(
    r'\*\(_DWORD \*\)(%s) \+= \*\(_DWORD \*\)\((%s) \+ 4\)' % (ARG, ARG))
# `*(_DWORD *)(a1 + 16) = v4 + *(_DWORD *)(a2 + 4);`
RELOC_B = re.compile(
    r'\*\(_DWORD \*\)\((%s) \+ (%s)\) = \w+ \+ \*\(_DWORD \*\)\((%s) \+ 4\)' % (ARG, NUM, ARG))
RELOC_B0 = re.compile(
    r'\*\(_DWORD \*\)(%s) = \w+ \+ \*\(_DWORD \*\)\((%s) \+ 4\)' % (ARG, ARG))
# `*(unsigned __int16 *)(a1 + 8)` / `*(_WORD *)(a1 + 8)`
U16 = re.compile(r'\*\((?:unsigned __int16|_WORD|__int16) \*\)\((%s) \+ (%s)\)' % (ARG, NUM))
U16_0 = re.compile(r'\*\((?:unsigned __int16|_WORD|__int16) \*\)(%s)[^+]' % ARG)
# `*(_DWORD *)a1 = &unk_626D98;` and `*(_DWORD *)(a1 + 16) = &unk_625028;`.
# The offset is NOT always zero: mcCullable stamps its vtable at +0x10, and a
# pattern anchored at +0 silently reports it as having none.
VTABLE = re.compile(
    r'\*\(_DWORD \*\)\((%s) \+ (%s)\) = &(?:unk|off|dword)_([0-9A-Fa-f]+)' % (ARG, NUM))
VTABLE_0 = re.compile(
    r'\*\(_DWORD \*\)(%s) = &(?:unk|off|dword)_([0-9A-Fa-f]+)' % ARG)
# any read of a field, to find what is looked at but never relocated
LIDO = re.compile(r'\*\((?:int|_DWORD|unsigned int) \*\)\((%s) \+ (%s)\)' % (ARG, NUM))
LIDO_ATRIB = re.compile(
    r'(\w+) = \*\((?:int|_DWORD|unsigned int) \*\)\((%s) \+ (%s)\)' % (ARG, NUM))
# a call into another datResource constructor
FILHO = re.compile(r'(\w+_datResource__ref(?:__\w+)?)\s*\(')
# `8 * v5` or `v5 * 8` next to a child call - the array stride
STRIDE = re.compile(r'(%s) \* (?:\(int\))?\w+|\w+ \* (%s)' % (NUM, NUM))


def analisa(texto, vtables=None):
    """The contract of one constructor, as far as the decompiled text states it.

    Only the two shapes that are unambiguous are reported as fact. Everything
    else lands in `notas` for a human, because a guess here is worse than a
    blank: it would be copied into a builder and produce a file that loads and
    draws nothing, which is the failure mode this whole exercise is about.
    """
    if vtables:
        texto = re.sub(r'&(\w+_virtual_table)\b',
                       lambda m: '&unk_%X' % vtables[m.group(1)]
                       if m.group(1) in vtables else m.group(0), texto)
    ponteiros, contagens, filhos, vtab, notas = set(), set(), [], None, []

    # Only the BODY. The signature line names the function itself, and counting
    # that as a call made every one of the 226 look like it built children.
    corpo = texto[texto.find('{'):] if '{' in texto else texto

    # qual argumento e o datResource: o que e lido em +4 como base
    bases = collections.Counter()
    for rx in (RELOC_A, RELOC_B):
        for m in rx.finditer(corpo):
            bases[m.group(3)] += 1
    res = bases.most_common(1)[0][0] if bases else None
    texto = corpo

    for m in RELOC_A.finditer(texto):
        ponteiros.add(_n(m.group(2)))
    for m in RELOC_B.finditer(texto):
        ponteiros.add(_n(m.group(2)))
    for rx in (RELOC_A0, RELOC_B0):
        for m in rx.finditer(texto):
            if m.group(1) != res:
                ponteiros.add(0)

    for m in U16.finditer(texto):
        if m.group(1) != res:
            contagens.add(_n(m.group(2)))
    if U16_0.search(texto):
        contagens.add(0)

    vt_off = None
    m = VTABLE.search(texto)
    if m and m.group(1) != res:
        vtab, vt_off = int(m.group(3), 16), _n(m.group(2))
    else:
        m = VTABLE_0.search(texto)
        if m and m.group(1) != res:
            vtab, vt_off = int(m.group(2), 16), 0

    # A 32-bit count: read from the object, never relocated, and the variable it
    # lands in is then compared. mcHood counts its models this way, so a parser
    # that only knows the u16 shape reports it as having no counts at all.
    c32 = set()
    for m in LIDO_ATRIB.finditer(texto):
        var, arg, off = m.group(1), m.group(2), _n(m.group(3))
        if arg == res or off in ponteiros or off == vt_off:
            continue
        if re.search(r'\b%s\b\s*(?:>|<|>=|<=)' % re.escape(var), texto):
            c32.add(off)
    lidos = set()
    for m in LIDO.finditer(texto):
        if m.group(1) != res:
            off = _n(m.group(2))
            if off not in ponteiros and off not in c32 and off != vt_off:
                lidos.add(off)

    for m in FILHO.finditer(texto):
        nome = m.group(1)
        cm = CTOR_RE.match(nome)
        alvo = cm.group(1) if cm and cm.group(1) == cm.group(2) else nome
        # o passo do array, quando a linha da chamada ou a anterior mostra
        janela = texto[max(0, m.start() - 200):m.start()]
        passos = [int(g or h) for g, h in STRIDE.findall(janela)
                  if (g or h) and _n(g or h) in (2, 4, 8, 12, 16, 20, 24, 32, 48, 64)]
        filhos.append((alvo, passos[-1] if passos else None))

    if not ponteiros and not filhos and 'falhou' not in texto:
        notas.append('nenhum ponteiro relocado: objeto folha, ou o decompilador '
                     'nao abriu')
    return dict(ponteiros=sorted(ponteiros), contagens=sorted(contagens),
                contagens32=sorted(c32), lidos=sorted(lidos),
                filhos=filhos, vtable=vtab, vtable_off=vt_off, notas=notas)


def alpha_vtables(map_path=None):
    alpha = _mod('mc3_alpha_map')
    return {re.sub(r'[^A-Za-z0-9_]', '_', s.name): s.addr
            for s in alpha.named(alpha.read_map(map_path or alpha.MAP))
            if s.name.endswith(' virtual table')}


def extract(fonte, out, target='retail', map_path=None):
    src = le_fonte(fonte)
    vtables = alpha_vtables(map_path) if target == 'alpha' else None
    print('%d construtores lidos de %s' % (len(src), fonte))
    linhas = ['# tipo\tendereco\tcampo\tespecie\tdetalhe']
    lidos = vazios = 0
    for nome in sorted(src):
        ea, texto = src[nome]
        if texto.lstrip().startswith('!!'):
            vazios += 1
            continue
        c = analisa(texto, vtables)
        lidos += 1
        if c['vtable']:
            linhas.append('%s\t%08X\t0x%02X\tvtable\tcarimbada com %08X'
                          % (nome, ea, c['vtable_off'] or 0, c['vtable']))
        for off in c['ponteiros']:
            linhas.append('%s\t%08X\t0x%02X\tponteiro\t+= base se != 0' % (nome, ea, off))
        for off in c['contagens']:
            linhas.append('%s\t%08X\t0x%02X\tcontagem16\t' % (nome, ea, off))
        for off in c['contagens32']:
            linhas.append('%s\t%08X\t0x%02X\tcontagem32\tlida e comparada, nao relocada'
                          % (nome, ea, off))
        for off in c['lidos']:
            linhas.append('%s\t%08X\t0x%02X\tlido\tlido e nao relocado' % (nome, ea, off))
        for alvo, passo in c['filhos']:
            linhas.append('%s\t%08X\t-\tfilho\t%s%s'
                          % (nome, ea, alvo,
                             (' passo %d' % passo) if passo else ''))
        for n in c['notas']:
            linhas.append('%s\t%08X\t-\tnota\t%s' % (nome, ea, n))
    io.open(out, 'w', encoding='utf-8', newline='\n').write('\n'.join(linhas) + '\n')
    print('%d analisados, %d sem corpo -> %s' % (lidos, vazios, out))


def show(nome, fonte):
    src = le_fonte(fonte)
    if nome not in src:
        prox = [k for k in src if nome.lower() in k.lower()]
        raise SystemExit('nao achei %r. parecidos: %s' % (nome, ', '.join(prox[:12]) or '-'))
    ea, texto = src[nome]
    c = analisa(texto)
    print('%s @ %08X' % (nome, ea))
    if c['vtable']:
        print('   +0x%02X  vtable      carimbada com %08X (o valor do arquivo nao importa)'
              % (c['vtable_off'] or 0, c['vtable']))
    for off in c['ponteiros']:
        print('   +0x%02X  ponteiro    += base se != 0' % off)
    for off in c['contagens']:
        print('   +0x%02X  contagem16' % off)
    for off in c['contagens32']:
        print('   +0x%02X  contagem32  lida e comparada, nao relocada' % off)
    for off in c['lidos']:
        print('   +0x%02X  lido        lido e nao relocado' % off)
    for alvo, passo in c['filhos']:
        print('          filho       %s%s' % (alvo, (', passo %d' % passo) if passo else ''))
    for n in c['notas']:
        print('   nota: %s' % n)
    print()
    print(texto.rstrip())


# Contracts worked out by hand from the disassembly before this tool existed.
# If the parser stops agreeing with them it has drifted, and every schema it
# emitted since is suspect.
AFERICAO = {
    'rmcModelGeom': dict(ponteiros=[0x10, 0x14], contagens=[8, 10], vtable=0x626D98,
                         vtable_off=0),
    'rmcGeometry': dict(ponteiros=[0x00], contagens=[4]),
    # vtable at +0x10, not at +0 - the case that caught the first parser, which
    # anchored the pattern at offset zero and reported "no vtable"
    'mcCullable': dict(ponteiros=[0x00, 0x04, 0x0C], vtable=0x625028, vtable_off=0x10),
    # 32-bit counts, not u16 - the second case. A parser that only knew the u16
    # shape said mcHood had no counts at all, while it has two.
    'mcHood': dict(ponteiros=[0x00, 0x08, 0x10], contagens=[]),
}


def selftest(fonte):
    src = le_fonte(fonte)
    falhas = 0
    for nome, esperado in sorted(AFERICAO.items()):
        if nome not in src:
            print('   FALTA   %s nao esta no dump' % nome)
            falhas += 1
            continue
        c = analisa(src[nome][1])
        for campo, val in esperado.items():
            got = c[campo]
            ok = got == val
            print('   %-7s %-16s %-11s esperado %s, veio %s'
                  % ('OK' if ok else 'DIFERE', nome, campo, val, got))
            falhas += not ok
    print()
    print('%s' % ('afericao passou' if not falhas else '%d divergencia(s)' % falhas))
    return 1 if falhas else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='acao')
    d = sub.add_parser('dump', help='decompilar todos os ctors (precisa da IDA)')
    d.add_argument('--elf')
    d.add_argument('--target', choices=['retail', 'alpha'], default='retail')
    d.add_argument('--map', help='alpha linker map; only used with --target alpha')
    d.add_argument('--corpus', help='reuse an alpha decomp project without reopening IDA')
    d.add_argument('--out', default=FONTE)
    e = sub.add_parser('extract', help='schema.tsv a partir do dump')
    e.add_argument('--fonte', default=FONTE)
    e.add_argument('--out', default=ESQUEMA)
    e.add_argument('--target', choices=['retail', 'alpha'], default='retail')
    e.add_argument('--map', help='alpha linker map for resolving named vtables')
    s = sub.add_parser('show', help='o contrato de um tipo, com a fonte')
    s.add_argument('tipo')
    s.add_argument('--fonte', default=FONTE)
    t = sub.add_parser('selftest', help='conferir contra os contratos feitos a mao')
    t.add_argument('--fonte', default=FONTE)
    a = ap.parse_args()
    if a.acao == 'dump':
        elf = a.elf or (_mod('mc3_alpha_map').ALPHA_DIR + '/SLUS_123.45_MAPSYM.i64'
                       if a.target == 'alpha' else _ida.DEFAULT_ELF)
        if a.target == 'alpha' and os.path.abspath(a.out) == os.path.abspath(FONTE):
            ap.error('--target alpha requires --out to preserve the retail dump')
        dump(elf, a.out, a.target, a.map, a.corpus)
    elif a.acao == 'extract':
        if a.target == 'alpha' and os.path.abspath(a.out) == os.path.abspath(ESQUEMA):
            ap.error('--target alpha requires --out to preserve the retail schema')
        extract(a.fonte, a.out, a.target, a.map)
    elif a.acao == 'show':
        show(a.tipo, a.fonte)
    elif a.acao == 'selftest':
        return selftest(a.fonte)
    else:
        ap.print_help()
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
