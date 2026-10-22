"""
mc3_symbols.py - carry the alpha build's function names over to the retail ELF

The October 2004 alpha ships `MC.MAP`, a linker map with 20275 symbols: full C++
signatures, sizes, and the .obj each came from. The retail executable has none of
that. Both put `.text` at 0x1a0000 but they are different builds, so addresses do
not line up and the bytes differ wherever a relocation does.

What survives a rebuild is what a function TALKS ABOUT. A function that
references the strings "$/resources/city/%s_bnd" and "hood" in one build
references them in the other, so the set of string literals a function touches is
a fingerprint that ignores addresses entirely. Matching on that needs no
disassembly heuristics and no call-graph alignment.

    python mc3_symbols.py dump  --elf ALPHA   --map MC.MAP --out alpha.tsv
    python mc3_symbols.py dump  --elf RETAIL              --out retail.tsv
    python mc3_symbols.py match alpha.tsv retail.tsv --out nomes.tsv
    python mc3_symbols.py apply nomes.tsv --elf RETAIL

`dump` runs inside IDA through mc3_ida.py. With `--map` it first creates a
function at every address the map lists - the alpha's autoanalysis does not find
them all on its own, and decompiling an address with no function there silently
returns nothing.
"""

import argparse
import collections
import importlib.util
import io
import os
import re
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))
_S = importlib.util.spec_from_file_location('mc3_ida', os.path.join(_AQUI, 'mc3_ida.py'))
_ida = importlib.util.module_from_spec(_S)
sys.modules['mc3_ida'] = _ida
_S.loader.exec_module(_ida)

MAP_RE = re.compile(r'^([0-9a-f]{8}) ([0-9a-f]{8})\s+\d+\s+(.*)$')

# The shared symbol store. Every fork of this investigation reads and writes the
# same files, so a name worked out while chasing collision shows up in the next
# session that opens the city loader. Precedence is manual > neighbour > graph >
# string: a hand-verified name always wins over a machine guess, and re-running
# the machine passes never clobbers it.
#
# The three machine passes reach different things, in this order of coverage:
#   match     what a function SAYS      (string literals)      1224 pares
#   grafo     the company it keeps      (callers and callees)  3219 pares
#   vizinhos  where it SITS             (source order + size)  6304 pares
#   token     the DATA it stamps        (vtables, globals)      183 pares
#   dados     the alpha's named GLOBALS carried across         1013 pares
#
# Measured, not assumed: with the string layer held out of the anchors and used
# as ground truth, the neighbour pass - the one that looks weakest - reproduces
# 505 of 508 of its pairs, 99.4%.
SIMB = os.path.join(_AQUI, 'simbolos')
CAMADAS = ('nomes.tsv', 'nomes_grafo.tsv', 'nomes_vizinhos.tsv',
           'nomes_token.tsv', 'nomes_dados.tsv', 'nomes_manuais.tsv')


def le_map(path):
    """[(addr, size, name)] of the real symbols in a linker map."""
    out = []
    for line in io.open(path, encoding='latin1'):
        m = MAP_RE.match(line)
        if not m:
            continue
        nome = m.group(3).strip()
        if (not nome or nome.startswith('.') or nome.endswith(('.obj', '.o'))
                or '.obj)' in nome):
            continue
        addr, size = int(m.group(1), 16), int(m.group(2), 16)
        if addr and size:
            out.append((addr, size, nome))
    return out


DUMP = r'''
import ida_auto, ida_funcs, ida_bytes, idautils, idc, ida_name
from ida_xref import fl_CN, fl_CF, dr_R, dr_W, dr_O

ida_auto.auto_wait()
CRIAR = %s
for ea in CRIAR:
    f = ida_funcs.get_func(ea)
    if not f or f.start_ea != ea:
        ida_funcs.add_func(ea)
if CRIAR:
    ida_auto.auto_wait()

# cada string, uma vez, com os enderecos que a citam
texto = {}
for s in idautils.Strings():
    t = str(s)
    if 4 <= len(t) <= 120:
        texto[s.ea] = t

por_funcao = {}
for sea, t in texto.items():
    for x in idautils.XrefsTo(sea):
        f = ida_funcs.get_func(x.frm)
        if f:
            por_funcao.setdefault(f.start_ea, set()).add(t)

for fea in idautils.Functions():
    f = ida_funcs.get_func(fea)
    ss = sorted(por_funcao.get(fea, ()))
    # O NOME que a base ja tem. Numa base COM SIMBOLOS (o .i64 da alfa) isto
    # substitui o MC.MAP inteiro: 16943 funcoes nomeadas contra as ~2000 que o
    # mapa alcancava, porque o mapa so ajudava onde havia string.
    nm = ida_name.get_name(fea) or ''
    if nm.startswith(('sub_', 'nullsub_', 'unknown_', 'j_sub_', 'loc_')):
        nm = ''
    # quem esta funcao chama. Emitimos TODA funcao, inclusive as mudas: elas nao
    # casam por string mas sao alcancaveis pelo grafo, e sao justamente as que
    # interessam (o carregador de .pck quase nao cita texto).
    ch = set()
    for ea in idautils.FuncItems(fea):
        for x in idautils.XrefsFrom(ea, 0):
            if x.type in (fl_CN, fl_CF):
                g = ida_funcs.get_func(x.to)
                if g and g.start_ea != fea:
                    ch.add(g.start_ea)
    # DADOS que a funcao referencia. E por aqui que se alcanca a classe de
    # funcao que nao cita string nenhuma: `*(a1) = &unk_626F20` referencia uma
    # VTABLE, e vtable e casavel entre builds pelo conjunto de funcoes que ela
    # contem. Strings ficam de fora, ja entram por outro caminho.
    dr = set()
    for ea in idautils.FuncItems(fea):
        for x in idautils.XrefsFrom(ea, 0):
            if x.type in (dr_R, dr_W, dr_O) and x.to not in texto:
                if not ida_funcs.get_func(x.to):
                    dr.add(x.to)
    _out.append('%%08X	%%d	%%s	|	%%s	|	%%s	|	%%s'
                %% (fea, f.end_ea - f.start_ea, nm.replace('	', ' '),
                    '	'.join(s.replace('	', ' ') for s in ss),
                    ' '.join('%%08X' %% c for c in sorted(ch)),
                    ' '.join('%%08X' %% c for c in sorted(dr))))
'''


def dump(elf, mapa, out):
    criar = []
    if mapa:
        criar = sorted({a for a, _s, _n in le_map(mapa)})
        print('%s: %d enderecos do mapa' % (os.path.basename(mapa), len(criar)))
    txt = _ida.run(_ida.py(DUMP % repr(criar)), elf)
    io.open(out, 'w', encoding='utf-8').write(txt)
    print('gravado %s (%d linhas)' % (out, txt.count('\n')))


def le_dump(path):
    """{addr: (size, nome, frozenset(strings), tuple(callees))}

    Linha: `addr TAB size TAB nome TAB | TAB string... TAB | TAB chamadas`.
    O NOME vem da propria base — numa com simbolos (o `.i64` da alfa) ele cobre
    17059 de 17154 funcoes, contra as ~2000 que o `MC.MAP` alcancava, porque o
    mapa so servia onde havia string pra ancorar.
    """
    out = {}
    for line in io.open(path, encoding='utf-8'):
        p = line.rstrip().split(chr(9))
        if len(p) < 3:
            continue
        try:
            addr, size = int(p[0], 16), int(p[1])
        except ValueError:
            continue
        nome = p[2].strip()
        resto = p[3:]
        strings, chamadas = [], ()
        if '|' in resto:
            k = resto.index('|')
            resto2 = resto[k + 1:]
            if '|' in resto2:
                m = resto2.index('|')
                strings = resto2[:m]
                if m + 1 < len(resto2):
                    chamadas = tuple(int(x, 16) for x in resto2[m + 1].split() if x)
            else:
                strings = resto2
        out[addr] = (size, nome, frozenset(x for x in strings if x), chamadas)
    return out


def le_dados(path):
    """{addr: frozenset(enderecos de DADO que a funcao referencia)}.

    Leitor separado de proposito: `le_dump` e usado por outros passos (e por
    outra fork que mexe neste arquivo em paralelo), entao mudar a tupla que ele
    devolve quebraria codigo alheio. Este le so o quarto campo.
    """
    out = {}
    for line in io.open(path, encoding='utf-8'):
        p = line.rstrip().split(chr(9))
        if len(p) < 3:
            continue
        try:
            addr = int(p[0], 16)
        except ValueError:
            continue
        partes, atual = [], []
        for x in p[3:]:
            if x == '|':
                partes.append(atual)
                atual = []
            else:
                atual.append(x)
        partes.append(atual)
        dados = ()
        if len(partes) > 3:
            dados = tuple(int(x, 16) for x in ' '.join(partes[3]).split() if x)
        out[addr] = frozenset(dados)
    return out


def le_ancoras(caminhos):
    """{alfa_addr: retail_addr} from any of the shared layer files.

    Every layer writes the alpha address in the fifth column, so one reader
    serves all of them, and a file that is not there yet is simply skipped.
    """
    par = {}
    for caminho in caminhos:
        if not os.path.isfile(caminho):
            continue
        for l in io.open(caminho, encoding='utf-8'):
            if l.startswith('#'):
                continue
            p = l.rstrip().split(chr(9))
            if len(p) >= 5:
                try:
                    par[int(p[4], 16)] = int(p[0], 16)
                except ValueError:
                    pass
    return par


def _comatch(A, R, dA, dR, par, rodadas, minimo):
    """The two-sided pass shared by `tokens` and `dados`.

    Both subcommands run the same loop and differ only in which half of the
    result they keep, so the loop lives here. `tokens` wants the functions it
    named; `dados` wants `dpar`, the alpha-data-to-retail-data pairing that the
    loop has always computed and, until now, thrown away.

    Returns (par, dpar, dscore, novos_funcoes).
    """
    def por_dado(D):
        inv = collections.defaultdict(set)
        for f, ds in D.items():
            for d in ds:
                inv[d].add(f)
        return inv

    invA, invR = por_dado(dA), por_dado(dR)
    print('%d ancoras de funcao; %d dados na alfa, %d no retail'
          % (len(par), len(invA), len(invR)))
    pesoR = {d: 1.0 / (1 + len(fs)) for d, fs in invR.items()}

    dpar, dscore = {}, {}
    novos_total = []
    for rodada in range(1, rodadas + 1):
        cand = collections.defaultdict(collections.Counter)
        for da, fs in invA.items():
            if da in dpar:
                continue
            for fa in fs:
                fr = par.get(fa)
                if fr is None:
                    continue
                for dr in dR.get(fr, ()):
                    cand[da][dr] += pesoR.get(dr, 0.01)
        melhor_d, inv_d = {}, {}
        for da, c in cand.items():
            melhor_d[da] = c.most_common(1)[0]
        for da, (dr, sc) in melhor_d.items():
            if dr not in inv_d or sc > inv_d[dr][1]:
                inv_d[dr] = (da, sc)
        usados = set(dpar.values())
        n_d = 0
        for dr, (da, sc) in inv_d.items():
            if melhor_d[da][0] == dr and dr not in usados and sc >= minimo:
                dpar[da] = dr
                dscore[da] = sc
                n_d += 1

        ja_r = set(par.values())
        porDR = collections.defaultdict(list)
        for fr, ds in dR.items():
            if fr in ja_r:
                continue
            for d in ds:
                porDR[d].append(fr)
        candf = collections.defaultdict(collections.Counter)
        for fa, ds in dA.items():
            if fa in par:
                continue
            for da in ds:
                dr = dpar.get(da)
                if dr is None:
                    continue
                w = pesoR.get(dr, 0.01)
                for fr in porDR.get(dr, ()):
                    candf[fa][fr] += w
        melhor_f, inv_f = {}, {}
        for fa, c in candf.items():
            top = c.most_common(2)
            fr, sc = top[0]
            melhor_f[fa] = (fr, sc, top[1][1] if len(top) > 1 else 0.0)
        for fa, (fr, sc, _s) in melhor_f.items():
            if fr not in inv_f or sc > inv_f[fr][1]:
                inv_f[fr] = (fa, sc)
        novos = []
        for fr, (fa, sc) in inv_f.items():
            m = melhor_f.get(fa)
            if not m or m[0] != fr or sc < minimo:
                continue
            if m[2] > 0 and sc < m[2] * 1.5:
                continue
            sa, sr = A[fa][0], R[fr][0]
            if sa and sr and not (0.4 <= float(sr) / sa <= 2.5):
                continue
            novos.append((fr, fa, sc))
        for fr, fa, _sc in novos:
            par[fa] = fr
        novos_total.extend(novos)
        print('   rodada %d: +%d dados, +%d funcoes; total %d dados, %d funcoes'
              % (rodada, n_d, len(novos), len(dpar), len(par)))
        if not novos and not n_d:
            break
    return par, dpar, dscore, novos_total


def tokens(alfa_tsv, retail_tsv, ancoras, out, rodadas, minimo):
    """Casa funcoes pelo DADO que elas referenciam, e dados pelas funcoes.

    A classe que sobrou sem nome - `sub_2B3600`, `sub_25D4F0`, os
    `Place`/`datResource&` da cidade - e minuscula e MUDA: das 335 funcoes com
    "datResource" no nome na alfa, **2 citam alguma string**. Nem o casamento por
    texto nem o por grafo entram nesse aglomerado, porque os vizinhos dele estao
    na mesma situacao.

    Mas elas nao sao mudas quanto a DADOS: cada uma carimba uma vtable
    (`*(a1) = &unk_626F20`). E vtable casa entre builds sem depender de endereco:
    **duas vtables sao a mesma classe quando contem as mesmas funcoes ja
    casadas**. Dai sai um co-casamento em duas frentes que se alimentam:

        dado_alfa  <-> dado_retail   pelas FUNCOES ja casadas que os referenciam
        funcao_alfa<-> funcao_retail pelos DADOS ja casados que elas referenciam

    Cada rodada de um lado cria ancora pro outro. Aceita so o melhor mutuo, e o
    peso de cada vizinho cai com a popularidade dele: um dado que meio mundo
    referencia nao identifica ninguem.
    """
    A, R = le_dump(alfa_tsv), le_dump(retail_tsv)
    dA, dR = le_dados(alfa_tsv), le_dados(retail_tsv)
    nomes = {a: v[1] for a, v in A.items() if v[1]}

    _par, _dpar, _dsc, novos_total = _comatch(
        A, R, dA, dR, le_ancoras(ancoras), rodadas, minimo)

    linhas = []
    for fr, fa, sc in sorted(novos_total):
        nm = nomes.get(fa)
        if nm:
            linhas.append('%08X\t%s\t%.4f\ttoken\t%08X' % (fr, nm, sc, fa))
    io.open(out, 'w', encoding='utf-8').write('\n'.join(linhas) + '\n')
    print('%d nomes novos por token -> %s' % (len(linhas), out))
    for l in linhas[:10]:
        p = l.split(chr(9))
        print('   %s  %-56s peso %s' % (p[0], p[1][:56], p[2]))


_MAPMOD = None


def _alpha_map():
    """mc3_alpha_map, loaded the same way mc3_ida is - it sits next to us."""
    global _MAPMOD
    if _MAPMOD is None:
        s = importlib.util.spec_from_file_location(
            'mc3_alpha_map', os.path.join(_AQUI, 'mc3_alpha_map.py'))
        m = importlib.util.module_from_spec(s)
        s.loader.exec_module(m)
        _MAPMOD = m
    return _MAPMOD


def dados(alfa_tsv, retail_tsv, ancoras, out, rodadas, minimo, mapa=None):
    """Carry the alpha's named GLOBALS over to retail.

    Everything above this line names functions. Nothing names data, and data is
    what the rest of this investigation actually spends its time on: the city,
    shader and texture work all navigate by raw global addresses read out of a
    savestate. The alpha names 3266 of them - `mcCity::s_fCellSize`,
    `g_bNewCityFrustumCulling`, `rmcShader::sm_MicrocodeNames`.

    There is no new machinery here. `_comatch` has always paired alpha data with
    retail data on its way to naming functions, because that is how it reaches
    the silent `datResource` cluster; it just discarded the pairing afterwards.
    This keeps it and joins it to the linker map.

    Two outputs, deliberately separate. A pairing that lands exactly on the
    start of a named symbol goes to `out` and is a name. A pairing that lands
    INSIDE one is written beside it as `<symbol>+0xNN` and is NOT a layer: it is
    only as good as the assumption that the struct did not change shape in the
    year between the builds, which is exactly the assumption this project keeps
    getting burned by. Read it, do not apply it.
    """
    import bisect
    A, R = le_dump(alfa_tsv), le_dump(retail_tsv)
    dA, dR = le_dados(alfa_tsv), le_dados(retail_tsv)
    _par, dpar, dsc, _nv = _comatch(
        A, R, dA, dR, le_ancoras(ancoras), rodadas, minimo)

    am = _alpha_map()
    syms = [s for s in am.named(am.read_map(mapa or am.MAP)) if am.is_data(s)]
    exato = {}
    for s in syms:
        exato.setdefault(s.addr, s)
    faixa = sorted((s.addr, s.addr + max(s.size, 1), s.name) for s in syms)
    lo = [f[0] for f in faixa]
    print('%d globais nomeados no mapa da alfa' % len(syms))

    linhas, interior, mudos = [], [], 0
    for da, dr in sorted(dpar.items()):
        sc = dsc.get(da, 0.0)
        s = exato.get(da)
        if s is not None:
            linhas.append('%08X\t%s\t%.4f\tdados\t%08X' % (dr, s.name, sc, da))
            continue
        i = bisect.bisect_right(lo, da) - 1
        if i >= 0 and faixa[i][0] <= da < faixa[i][1]:
            interior.append('%08X\t%s+0x%X\t%.4f\tinterior\t%08X'
                            % (dr, faixa[i][2], da - faixa[i][0], sc, da))
        else:
            mudos += 1

    io.open(out, 'w', encoding='utf-8', newline='\n').write(
        '\n'.join(linhas) + '\n')
    outi = os.path.splitext(out)[0] + '_interior.tsv'
    io.open(outi, 'w', encoding='utf-8', newline='\n').write(
        '# NAO e uma camada: nome do simbolo mais um deslocamento, valido so se\n'
        '# a struct nao mudou de forma entre os dois builds. Consulta, nao apply.\n'
        + '\n'.join(interior) + '\n')
    print('%d dados casados: %d com nome exato, %d no interior de um simbolo, '
          '%d sem nome no mapa' % (len(dpar), len(linhas), len(interior), mudos))
    print('   %s' % out)
    print('   %s' % outi)
    for l in linhas[:12]:
        p = l.split(chr(9))
        print('   %s  %-56s peso %s' % (p[0], p[1][:56], p[2]))


def match(alfa_tsv, retail_tsv, mapa, out, minimo):
    """Pair functions by the strings they reference, then name the retail side.

    A string that dozens of functions use says nothing, so each one is weighted
    by how rare it is; a single shared "$/resources/city/%s_bnd" outweighs ten
    shared "%s". A pair is only accepted when it is the best match for BOTH
    sides, which throws away the ambiguous middle instead of guessing at it.
    """
    A, R = le_dump(alfa_tsv), le_dump(retail_tsv)
    # o nome sai do proprio dump; `--map` so entra como reforco pro que faltar
    nomes = {a: v[1] for a, v in A.items() if v[1]}
    if mapa:
        for addr, _size, nome in le_map(mapa):
            nomes.setdefault(addr, nome)
    print('alfa %d funcoes (%d com nome), retail %d'
          % (len(A), len(nomes), len(R)))

    freq = collections.Counter()
    for _a, (_s, _n, ss, _c) in list(A.items()) + list(R.items()):
        freq.update(ss)
    peso = {s: 1.0 / (1 + freq[s]) for s in freq}

    def pontua(x, y):
        return sum(peso[s] for s in (x & y))

    porstring = collections.defaultdict(list)
    for ra, (_rs, _rn, rss, _rc) in R.items():
        for s in rss:
            porstring[s].append(ra)

    # O TAMANHO COMO DESEMPATE, que esta passada nao tinha e as outras duas tem.
    # Duas funcoes do MESMO .obj costumam citar o MESMO conjunto de strings - o
    # `aiRailNetwork::GetExtents` e o `aiRailNetwork::LoadRailNetwork` citam os
    # dois `%s_city` e `city/%s` e mais nada -, entao o peso EMPATA e a escolha
    # vira sorteio. Foi assim que o retail 0x503798, de 1756 bytes, recebeu o
    # nome do GetExtents, que tem 300: a fork do MC2 percebeu pela contagem de
    # bytes ao descompilar. Tamanho muda entre builds, mas nao por uma ordem de
    # grandeza; e a mesma faixa 0.4..2.5 que `grafo` e `tokens` ja usam.
    def _tam_ok(sa, sr):
        return not (sa and sr) or 0.4 <= float(sr) / sa <= 2.5

    melhor_a = {}
    for aa, (_as_, _an, ass, _ac) in A.items():
        cand = collections.Counter()
        for s in ass:
            for ra in porstring.get(s, ()):
                if _tam_ok(A[aa][0], R[ra][0]):
                    cand[ra] += peso[s]
        if cand:
            ra, sc = cand.most_common(1)[0]
            melhor_a[aa] = (ra, sc)

    melhor_r = {}
    for aa, (ra, sc) in melhor_a.items():
        if ra not in melhor_r or sc > melhor_r[ra][1]:
            melhor_r[ra] = (aa, sc)

    linhas, aceitos = [], 0
    for ra, (aa, sc) in sorted(melhor_r.items()):
        if melhor_a.get(aa, (None,))[0] != ra or sc < minimo:
            continue
        nome = nomes.get(aa)
        if not nome:
            continue
        comuns = len(A[aa][2] & R[ra][2])
        linhas.append('%08X\t%s\t%.4f\t%d\t%08X' % (ra, nome, sc, comuns, aa))
        aceitos += 1
    io.open(out, 'w', encoding='utf-8').write('\n'.join(linhas) + '\n')
    print('%d pares aceitos (mutuos, peso >= %.3f) -> %s' % (aceitos, minimo, out))
    for l in linhas[:12]:
        p = l.split('\t')
        print('   %s  %-56s peso %s, %s strings em comum' % (p[0], p[1][:56], p[2], p[3]))


def grafo(alfa_tsv, retail_tsv, mapa, ancoras_tsv, out, rodadas, minimo):
    """Extend the string matches through the call graph.

    A function with no string literals cannot be fingerprinted by what it says,
    but it can be by the company it keeps: who calls it and what it calls. Every
    already-matched neighbour is a constraint, so each round of matching creates
    the anchors the next round needs.

    Popular neighbours carry almost no information - being called by the same
    allocator says nothing - so a neighbour is weighted 1/(1+degree), the same
    rarity idea the string pass uses. Position in the caller's argument list is
    not available here, so a pair must clear both a score floor and a margin over
    the runner-up; a tie means two siblings look alike and we decline to choose.
    """
    A, R = le_dump(alfa_tsv), le_dump(retail_tsv)
    nomes = {a: v[1] for a, v in A.items() if v[1]}
    if mapa:
        for addr, _size, nome in le_map(mapa):
            nomes.setdefault(addr, nome)

    par = {}          # alfa -> retail
    volta = {}        # retail -> alfa
    for line in io.open(ancoras_tsv, encoding='utf-8'):
        p = line.rstrip().split(chr(9))
        if len(p) >= 5:
            ra, aa = int(p[0], 16), int(p[4], 16)
            par[aa], volta[ra] = ra, aa
    print('alfa %d funcoes, retail %d, %d ancoras de string'
          % (len(A), len(R), len(par)))

    def chamadores(D):
        inv = collections.defaultdict(set)
        for a, (_s, _n, _ss, ch) in D.items():
            for c in ch:
                inv[c].add(a)
        return inv

    caA, caR = chamadores(A), chamadores(R)

    def grau(D, inv):
        return {a: len(D[a][3]) + len(inv.get(a, ())) for a in D}

    gA, gR = grau(A, caA), grau(R, caR)

    novos_total = []
    for rodada in range(1, rodadas + 1):
        # a impressao digital de um no e o conjunto de vizinhos JA casados,
        # traduzidos para o lado do retail para poderem ser comparados
        def vizinhos(a, D, inv, tab):
            out = collections.Counter()
            for c in D[a][3]:
                r = tab.get(c)
                if r is not None:
                    out[('c', r)] += 1
            for c in inv.get(a, ()):
                r = tab.get(c)
                if r is not None:
                    out[('p', r)] += 1
            return out

        idt = {r: r for r in R}
        vA = {a: vizinhos(a, A, caA, par) for a in A if a not in par}
        vR = {r: vizinhos(r, R, caR, idt) for r in R if r not in volta}
        vA = {a: v for a, v in vA.items() if v}
        vR = {r: v for r, v in vR.items() if v}

        # peso do vizinho pela raridade dele: ser chamado pelo mesmo alocador
        # nao diz nada, ser chamado pelo mesmo mcHood::Load diz tudo
        pesoviz = {r: 1.0 / (1 + gR.get(r, 0)) for r in R}

        porviz = collections.defaultdict(list)
        for r, v in vR.items():
            for k in v:
                porviz[k].append(r)

        cand_de = {}
        for a, v in vA.items():
            c = collections.Counter()
            for k in v:
                w = pesoviz.get(k[1], 0.01)
                for r in porviz.get(k, ()):
                    c[r] += w
            if c:
                cand_de[a] = c

        melhor_a = {}
        for a, c in cand_de.items():
            top = c.most_common(2)
            r, sc = top[0]
            segundo = top[1][1] if len(top) > 1 else 0.0
            melhor_a[a] = (r, sc, segundo)

        melhor_r = {}
        for a, (r, sc, _sg) in melhor_a.items():
            if r not in melhor_r or sc > melhor_r[r][1]:
                melhor_r[r] = (a, sc)

        novos = []
        for r, (a, sc) in melhor_r.items():
            m = melhor_a.get(a)
            if not m or m[0] != r or sc < minimo:
                continue
            if m[2] > 0 and sc < m[2] * 1.5:   # empate: dois irmaos parecidos
                continue
            # tamanhos mudam entre builds, mas nao por uma ordem de grandeza
            sa, sr = A[a][0], R[r][0]
            if sa and sr and not (0.4 <= float(sr) / sa <= 2.5):
                continue
            novos.append((r, a, sc))

        for r, a, _sc in novos:
            par[a], volta[r] = r, a
        n_nom = sum(1 for _r, a, _s in novos if a in nomes)
        print('   rodada %d: +%d pares (%d com nome no mapa), total %d'
              % (rodada, len(novos), n_nom, len(par)))
        novos_total.extend(novos)
        if not novos:
            break

    linhas = []
    for r, a, sc in sorted(novos_total):
        nome = nomes.get(a)
        if nome:
            linhas.append('%08X\t%s\t%.4f\tgrafo\t%08X' % (r, nome, sc, a))
    io.open(out, 'w', encoding='utf-8').write('\n'.join(linhas) + '\n')
    print('%d nomes novos pelo grafo -> %s' % (len(linhas), out))
    for l in linhas[:15]:
        p = l.split('\t')
        print('   %s  %-58s peso %s' % (p[0], p[1][:58], p[2]))


def unidades(mapa=None):
    """{alfa_addr: obj} for every code symbol the linker map places.

    The boundary between two translation units, which is the one thing the
    neighbour pass below cannot see for itself.
    """
    am = _alpha_map()
    out = {}
    for s in am.named(am.read_map(mapa or am.MAP)):
        if am.is_code(s):
            out[s.addr] = am.unit(s.obj)[1]
    return out


def vizinhos(alfa_tsv, retail_tsv, ancoras, out, tolerancia, unid=None):
    """Third pass: extend each anchor along its neighbours, matched by size.

    The two builds compile the same source files, and a compiler emits the
    methods of a class in source order. So a matched pair is not one fact but
    the start of a run: the function before it in the alpha is the function
    before it in retail, and so on, until something contradicts. Sizes are the
    check - they survive relocation, and a whole run of them agreeing is far too
    unlikely to be chance.

    This reaches the cluster the other two passes cannot: `datResource` fixups
    are tiny pointer-relocation routines with no string literals, and their
    neighbours are in the same state, so neither text nor call graph has an
    anchor to grip. But they sit in a row, and one named neighbour anywhere in
    the row is enough.

    A run stops at the first size disagreement rather than trying to resync -
    a wrong alignment would then name every function after it wrongly, and a
    silent shift is the one failure mode worth paying to avoid.
    """
    A, R = le_dump(alfa_tsv), le_dump(retail_tsv)
    nomes = {a: v[1] for a, v in A.items() if v[1]}

    par, volta = {}, {}
    for path in ancoras:
        for line in io.open(path, encoding='utf-8'):
            p = line.rstrip('\n').split('\t')
            if len(p) >= 5:
                try:
                    ra, aa = int(p[0], 16), int(p[4], 16)
                except ValueError:
                    continue
                par[aa], volta[ra] = ra, aa
    print('alfa %d funcoes (%d com nome), retail %d, %d ancoras'
          % (len(A), len(nomes), len(R), len(par)))

    la, lr = sorted(A), sorted(R)
    ia = {a: i for i, a in enumerate(la)}
    ir = {r: i for i, r in enumerate(lr)}

    novos = []
    for aa, ra in sorted(par.items()):
        if aa not in ia or ra not in ir:
            continue
        for passo in (1, -1):
            i, j = ia[aa], ir[ra]
            while True:
                i += passo
                j += passo
                if not (0 <= i < len(la) and 0 <= j < len(lr)):
                    break
                a2, r2 = la[i], lr[j]
                if a2 in par or r2 in volta:
                    # ja casados: so seguimos se concordarem, senao a corrida acabou
                    if par.get(a2) == r2:
                        continue
                    break
                # A corrida so vale enquanto ficar dentro do MESMO .cpp. O
                # compilador emite os metodos de uma classe na ordem da fonte, e
                # e isso que sustenta o passo; atravessada a fronteira da unidade
                # de compilacao a premissa acaba, e o que vem depois so casa por
                # coincidencia de tamanho - sem nada na saida dizendo isso.
                if unid:
                    u1, u2 = unid.get(aa), unid.get(a2)
                    if u1 and u2 and u1 != u2:
                        break
                sa, sr = A[a2][0], R[r2][0]
                if not sa or not sr or abs(sa - sr) > tolerancia:
                    break
                par[a2], volta[r2] = r2, a2
                novos.append((r2, a2, sa, sr))

    linhas = []
    for r2, a2, sa, sr in sorted(novos):
        nome = nomes.get(a2)
        if nome:
            linhas.append('%08X\t%s\t%d\tvizinho\t%08X' % (r2, nome, sa, a2))
    io.open(out, 'w', encoding='utf-8').write('\n'.join(linhas) + '\n')
    print('%d pares novos por vizinhanca, %d com nome -> %s'
          % (len(novos), len(linhas), out))
    for l in linhas[:12]:
        p = l.split('\t')
        print('   %s  %-62s %s bytes' % (p[0], p[1][:62], p[2]))


APLICA = r'''
import ida_auto, ida_name
ida_auto.auto_wait()
PARES = %s
n = 0
for ea, nome in PARES:
    limpo = ''.join(c if (c.isalnum() or c == '_') else '_' for c in nome)[:120]
    if ida_name.set_name(ea, limpo, ida_name.SN_NOCHECK | ida_name.SN_FORCE):
        n += 1
_out.append('nomeadas %%d de %%d' %% (n, len(PARES)))
'''


def camadas(extra=()):
    """Merge the shared store into {retail_addr: (name, origin)}.

    Later layers overwrite earlier ones, so a hand-written name in
    nomes_manuais.tsv survives every re-run of the machine passes.
    """
    tab = {}
    arqs = [os.path.join(SIMB, c) for c in CAMADAS] + list(extra)
    for path in arqs:
        if not os.path.isfile(path):
            continue
        origem = os.path.basename(path)
        n = 0
        for line in io.open(path, encoding='utf-8'):
            line = line.rstrip('\n')
            if not line or line.startswith('#'):
                continue
            p = line.split('\t')
            if len(p) >= 2 and p[1].strip():
                try:
                    tab[int(p[0], 16)] = (p[1].strip(), origem)
                except ValueError:
                    continue
                n += 1
        print('   %-20s %d nomes' % (origem, n))
    return tab


def anota(ea, nome, nota):
    """Record a hand-verified name so every other fork picks it up."""
    if not os.path.isdir(SIMB):
        os.makedirs(SIMB)
    path = os.path.join(SIMB, 'nomes_manuais.tsv')
    novo = not os.path.isfile(path)
    with io.open(path, 'a', encoding='utf-8') as f:
        if novo:
            f.write('# retail_addr\tnome\torigem\tnota\n')
        f.write('%08X\t%s\tmanual\t%s\n' % (ea, nome, nota or ''))
    print('anotado %08X = %s   (%s)' % (ea, nome, path))
    print('rode `mc3_symbols.py apply` pra levar pra base da IDA')


def apply(nomes_tsv, elf):
    extra = [nomes_tsv] if nomes_tsv else []
    print('camadas:')
    tab = camadas(extra)
    pares = [(ea, n) for ea, (n, _o) in sorted(tab.items())]
    print('%d nomes unicos apos a fusao' % len(pares))
    print(_ida.run(_ida.py(APLICA % repr(pares)), elf))


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('acao', choices=('dump', 'match', 'grafo', 'tokens', 'dados', 'vizinhos', 'apply', 'anota', 'busca'))
    ap.add_argument('args', nargs='*')
    ap.add_argument('--elf')
    ap.add_argument('--map')
    ap.add_argument('--out')
    ap.add_argument('--minimo', type=float, default=0.02)
    ap.add_argument('--rodadas', type=int, default=6)
    ap.add_argument('--tolerancia', type=int, default=0,
                    help='diferenca de tamanho aceita (0 = exato)')
    # DESLIGADO POR PADRAO, e a medicao e que decidiu isso. A ideia era que uma
    # corrida de vizinhos nao deveria atravessar a fronteira de um .cpp, ja que e
    # a ordem da fonte que sustenta o passo. Testado contra verdade de campo
    # (a camada de string retirada das ancoras): 99,4% de acerto sem a fronteira,
    # 99,5% com ela - e 1102 nomes a menos. Nao se paga. Fica como opcao.
    ap.add_argument('--unidades', action='store_true',
                    help='vizinhos: parar na fronteira de .obj (mais conservador, '
                         '-18%% de nomes, sem ganho medido de precisao)')
    a = ap.parse_args()
    if a.acao == 'dump':
        dump(a.elf or _ida.DEFAULT_ELF, a.map, a.out or _saida.caminho('dump.tsv'))
    elif a.acao == 'match':
        match(a.args[0], a.args[1], a.map, a.out or _saida.caminho('nomes.tsv'), a.minimo)
    elif a.acao == 'tokens':
        tokens(a.args[0], a.args[1], a.args[2:], a.out or _saida.caminho('nomes_token.tsv'),
               a.rodadas, a.minimo)
    elif a.acao == 'dados':
        dados(a.args[0], a.args[1], a.args[2:],
              a.out or os.path.join(SIMB, 'nomes_dados.tsv'),
              a.rodadas, a.minimo, a.map)
    elif a.acao == 'grafo':
        grafo(a.args[0], a.args[1], a.map, a.args[2], a.out or _saida.caminho('nomes_grafo.tsv'),
              a.rodadas, a.minimo)
    elif a.acao == 'vizinhos':
        vizinhos(a.args[0], a.args[1], a.args[2:], a.out or _saida.caminho('nomes_vizinhos.tsv'),
                 a.tolerancia, unidades(a.map) if a.unidades else None)
    elif a.acao == 'anota':
        anota(int(a.args[0], 16), a.args[1],
              a.args[2] if len(a.args) > 2 else '')
    elif a.acao == 'busca':
        alvo = a.args[0].lower()
        print('camadas:')
        tab = camadas()
        achados = [(ea, n, o) for ea, (n, o) in sorted(tab.items())
                   if alvo in n.lower() or alvo in ('%08x' % ea)]
        print('%d resultados para %r' % (len(achados), a.args[0]))
        for ea, n, o in achados[:80]:
            print('   %08X  %-68s [%s]' % (ea, n[:68], (o[:-4].replace('nomes', '').lstrip('_') or 'string') or 'string'))
    else:
        apply(a.args[0] if a.args else None, a.elf or _ida.DEFAULT_ELF)


if __name__ == '__main__':
    main()
