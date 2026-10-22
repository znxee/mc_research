"""
mc3_cityobj.py - put the generated city and the MC2 original side by side

The city is wrong on screen and every check on the file passes. That is the
point where a picture beats another audit: the MC2 fork can already dump Los
Angeles as an OBJ (`mc2_rsc.py obj`), so if the generated `.pck` can be dumped
the same way, the difference stops being a description and becomes a
measurement.

The geometry side is not new work: `mc3_view.py` already walks the real graph
(MapRoot -> hood -> component -> data +0x3C -> mesh), decodes the city's planar
VIF packets with the mask handled, and places each mesh through its 3x4. This
only writes what it found as an OBJ and compares two of them.

    python mc3_cityobj.py obj output/losangeles_la_v6.pck --out output/la_pck.obj
    python mc3_cityobj.py stats output/la_pck.obj
    python mc3_cityobj.py compara output/la_pck.obj output/mc2_la/losangeles.obj

ONE CAVEAT THAT DECIDES WHETHER A COMPARISON MEANS ANYTHING: `mc3_view.py`
cannot reach every mesh through the graph, and it gives an unreachable one the
position of its nearest placed neighbour so that the viewer does not pile them
on the origin. That is a display convenience and a lie for measurement, so the
groups it marks with a trailing `~` are counted and, by default, LEFT OUT of the
OBJ. `--com-herdadas` puts them back, for looking rather than for concluding.
"""

import argparse
import collections
import importlib.util
import io
import math
import os
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _mod(nome, caminho=None):
    s = importlib.util.spec_from_file_location(
        nome, caminho or os.path.join(_AQUI, nome + '.py'))
    m = importlib.util.module_from_spec(s)
    sys.modules[nome] = m
    s.loader.exec_module(m)
    return m


def escreve_obj(grupos, saida, com_herdadas=False):
    """OBJ in world space, one `o` per mesh, keeping the group names."""
    n_v = n_f = pulados = 0
    with io.open(saida, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# mc3_cityobj: %d grupo(s) do .pck\n' % len(grupos))
        base = 1
        for g in grupos:
            nome = g.get('name') or ''
            herdada = nome.rstrip().endswith('~')
            if herdada and not com_herdadas:
                pulados += 1
                continue
            vs, ts = g['verts'], g['tris']
            if not ts:
                continue
            f.write('o %s\n' % (nome.strip() or 'mesh'))
            for v in vs:
                f.write('v %.4f %.4f %.4f\n' % (v[0], v[1], v[2]))
            for t in ts:
                f.write('f %d %d %d\n' % (base + t[0], base + t[1], base + t[2]))
            base += len(vs)
            n_v += len(vs)
            n_f += len(ts)
    return n_v, n_f, pulados


def cmd_obj(a):
    view = _mod('mc3_view')
    grupos = view.parse_ps2_city(a.pck, a.limite)
    herdadas = sum(1 for g in grupos if (g.get('name') or '').rstrip().endswith('~'))
    n_v, n_f, pulados = escreve_obj(grupos, a.out, a.com_herdadas)
    print('%s' % os.path.basename(a.pck))
    print('   %d grupo(s) lidos, %d com posicao HERDADA (%s)'
          % (len(grupos), herdadas,
             'incluidas' if a.com_herdadas else 'deixadas de fora'))
    print('   %d vertice(s), %d triangulo(s) -> %s' % (n_v, n_f, a.out))
    if herdadas and not a.com_herdadas:
        print('   AVISO: %d grupo(s) nao sao alcancaveis pelo grafo que o '
              'mc3_view percorre.' % herdadas)
        print('   A posicao deles seria chute, entao ficaram fora. Se esse '
              'numero for grande,')
        print('   ele proprio e um achado: geometria no arquivo que o caminho '
              'de desenho nao alcanca.')


def le_obj(caminho):
    """[(x, y, z)] e a contagem de faces. Sem material, sem normal."""
    vs, nf = [], 0
    for l in io.open(caminho, encoding='utf-8', errors='replace'):
        if l.startswith('v '):
            p = l.split()
            vs.append((float(p[1]), float(p[2]), float(p[3])))
        elif l.startswith('f '):
            nf += 1
    return vs, nf


def _caixa(vs):
    mn = [min(v[i] for v in vs) for i in range(3)]
    mx = [max(v[i] for v in vs) for i in range(3)]
    return mn, mx


def cmd_stats(a):
    vs, nf = le_obj(a.obj)
    if not vs:
        raise SystemExit('%s: sem vertice' % a.obj)
    mn, mx = _caixa(vs)
    print('%s' % os.path.basename(a.obj))
    print('   %d vertice(s), %d face(s)' % (len(vs), nf))
    print('   X %10.1f .. %10.1f   (%.1f)' % (mn[0], mx[0], mx[0] - mn[0]))
    print('   Y %10.1f .. %10.1f   (%.1f)' % (mn[1], mx[1], mx[1] - mn[1]))
    print('   Z %10.1f .. %10.1f   (%.1f)' % (mn[2], mx[2], mx[2] - mn[2]))
    c = [sum(v[i] for v in vs) / len(vs) for i in range(3)]
    print('   centroide (%.1f, %.1f, %.1f)' % tuple(c))


def ocupacao(vs, celula, origem, grade):
    """{(cx, cz)} - as celulas da grade do jogo que tem algum vertice."""
    ox, oz = origem
    gw, gh = grade
    occ = collections.Counter()
    for x, _y, z in vs:
        cx = int(math.floor(x / celula)) - ox
        cz = int(math.floor(z / celula)) - oz
        if 0 <= cx < gw and 0 <= cz < gh:
            occ[(cx, cz)] += 1
    return occ


def cmd_compara(a):
    va, fa = le_obj(a.obj_a)
    vb, fb = le_obj(a.obj_b)
    if not va or not vb:
        raise SystemExit('um dos dois esta vazio')
    na, nb = os.path.basename(a.obj_a), os.path.basename(a.obj_b)
    print('A = %s   %d vertice(s), %d face(s)' % (na, len(va), fa))
    print('B = %s   %d vertice(s), %d face(s)' % (nb, len(vb), fb))
    print()
    ma, xa = _caixa(va)
    mb, xb = _caixa(vb)
    print('%-6s %-28s %-28s %s' % ('eixo', 'A', 'B', 'diferenca'))
    for i, eixo in enumerate('XYZ'):
        print('%-6s %10.1f ..%10.1f  %10.1f ..%10.1f   min %+8.1f  max %+8.1f'
              % (eixo, ma[i], xa[i], mb[i], xb[i], ma[i] - mb[i], xa[i] - xb[i]))
    print()

    # A GRADE DO JOGO como unidade de comparacao, nao um numero inventado: a
    # celula de 40 esta confirmada por tres fontes (mcCity::s_fCellSize no ELF,
    # o `dimensions` do losangeles.lvl do MC2, e a invariante medida nas quatro
    # cidades de varejo), e a origem sai do proprio .pck.
    oa = ocupacao(va, a.celula, (a.origem_x, a.origem_z), (a.grade_w, a.grade_h))
    ob = ocupacao(vb, a.celula, (a.origem_x, a.origem_z), (a.grade_w, a.grade_h))
    sa, sb = set(oa), set(ob)
    print('ocupacao numa grade %dx%d de celulas de %g, origem (%d, %d):'
          % (a.grade_w, a.grade_h, a.celula, a.origem_x, a.origem_z))
    print('   %5d celula(s) com geometria em A' % len(sa))
    print('   %5d celula(s) com geometria em B' % len(sb))
    print('   %5d nas duas' % len(sa & sb))
    print('   %5d SO em A (geometria que o MC2 nao tem ali)' % len(sa - sb))
    print('   %5d SO em B (geometria do MC2 que sumiu no .pck)' % len(sb - sa))
    if sb:
        print('   cobertura: %.1f%% das celulas de B tem algo em A'
              % (100.0 * len(sa & sb) / len(sb)))
    if a.mapa:
        linhas = []
        for cz in range(a.grade_h):
            linha = []
            for cx in range(a.grade_w):
                k = (cx, cz)
                linha.append('#' if k in sa and k in ob else
                             'A' if k in sa else
                             'B' if k in ob else '.')
            linhas.append(''.join(linha))
        io.open(a.mapa, 'w', encoding='utf-8', newline='\n').write(
            '# . vazio   # nas duas   A so no pck   B so no MC2\n'
            + '\n'.join(linhas) + '\n')
        print('   mapa -> %s' % a.mapa)


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='acao')
    o = sub.add_parser('obj', help='exporta a cidade de um .pck como OBJ')
    o.add_argument('pck')
    o.add_argument('--out', required=True)
    o.add_argument('--limite', type=int, default=0)
    o.add_argument('--com-herdadas', action='store_true',
                   help='inclui os grupos cuja posicao o mc3_view chutou')
    s = sub.add_parser('stats', help='caixa e centroide de um OBJ')
    s.add_argument('obj')
    c = sub.add_parser('compara', help='dois OBJ, na grade do jogo')
    c.add_argument('obj_a')
    c.add_argument('obj_b')
    c.add_argument('--celula', type=float, default=40.0)
    c.add_argument('--origem-x', type=int, default=-50)
    c.add_argument('--origem-z', type=int, default=-43)
    c.add_argument('--grade-w', type=int, default=91)
    c.add_argument('--grade-h', type=int, default=82)
    c.add_argument('--mapa', help='grava um mapa de ocupacao em texto')
    a = ap.parse_args()
    fn = {'obj': cmd_obj, 'stats': cmd_stats, 'compara': cmd_compara}.get(a.acao)
    if not fn:
        ap.print_help()
        return 2
    fn(a)
    return 0


if __name__ == '__main__':
    sys.exit(main())
