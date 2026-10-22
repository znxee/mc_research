"""
mc3_cityaudit.py - a associacao instancia -> tipo, conferida uma a uma

A Fork City MODS 2 pediu isto textualmente: a geometria dos 729 tipos esta
validada e os 8511 registros conservam os 12 floats, mas isso NAO prova que cada
`Instance+0x0C` aponta para o TIPO certo, nem que a matriz que sobra e a daquela
instancia. Nome nao serve de chave - a cidade gerada grava `gerado_00` em todos
os ComponentData -, entao aqui a chave e o CONTEUDO:

    a matriz de 12 floats casa a instancia com a linha do place.tsv
    a AABB LOCAL da malha do tipo, transformada por essa matriz, tem que
    cair dentro do emin/emax que a mesma linha declara

Se a associacao estiver trocada, a caixa transformada nao encaixa - um poste com
a matriz de um predio estoura a caixa do predio, e vice-versa. E um teste que nao
depende de ler nome nenhum e que roda nas 8511, nao numa amostra.

A convencao da matriz e VETOR-LINHA (`mundo = p * R + T`), verificada no
microcodigo de VU (programa 14508803, VU 0x09C0) e no `Matrix34::Transform4`
do EE; a fork do MC2 mediu o mesmo lado de la, no `.hood`.

    python mc3_cityaudit.py instancias <cidade.pck> --place la729_place.tsv
    python mc3_cityaudit.py tipo <cidade.pck> --place la729_place.tsv \\
        --nome alpha_palm
"""

import argparse
import collections
import importlib.util
import io
import os
import struct
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _mod(nome, caminho=None):
    s = importlib.util.spec_from_file_location(
        nome, caminho or os.path.join(_AQUI, nome + '.py'))
    m = importlib.util.module_from_spec(s)
    sys.modules[nome] = m
    s.loader.exec_module(m)
    return m


def _abre(caminho):
    mc2 = _mod('mc2_to_mc3', os.path.join(_AQUI, 'experimental', 'mc2_to_mc3.py'))
    hf = _mod('hf', os.path.join(_AQUI, 'mc3_hood_fill.py'))
    return mc2.Pck(caminho), hf


def le_place(caminho):
    """As linhas `inst`, com matriz e caixa, na ordem do arquivo."""
    linhas, cab = [], None
    for l in io.open(caminho, encoding='utf-8', errors='replace'):
        if l.startswith('#'):
            continue
        p = l.rstrip('\n').split('\t')
        if cab is None:
            cab = p
            continue
        d = dict(zip(cab, p))
        if d.get('kind') == 'inst':
            linhas.append(d)
    return linhas


M12 = ('m00', 'm01', 'm02', 'm10', 'm11', 'm12', 'm20', 'm21', 'm22',
       'tx', 'ty', 'tz')


def _mat(d):
    return tuple(round(float(d[c]), 4) for c in M12)


def _caixa(d):
    return ([float(d['emin' + a]) for a in 'xyz'],
            [float(d['emax' + a]) for a in 'xyz'])


def _transforma(mn, mx, m):
    """A AABB dos 8 cantos da caixa local passados por `p * R + T`."""
    r = [[m[0], m[1], m[2]], [m[3], m[4], m[5]], [m[6], m[7], m[8]]]
    t = [m[9], m[10], m[11]]
    lo = [1e18] * 3
    hi = [-1e18] * 3
    for i in range(8):
        p = [mn[0] if i & 1 else mx[0],
             mn[1] if i & 2 else mx[1],
             mn[2] if i & 4 else mx[2]]
        for a in range(3):
            v = t[a] + p[0] * r[0][a] + p[1] * r[1][a] + p[2] * r[2][a]
            lo[a] = min(lo[a], v)
            hi[a] = max(hi[a], v)
    return lo, hi


def coleta(p, hf):
    """[(offset, type_va, matriz, centro, raio)] das instancias do arquivo."""
    slots, tipos = hf.tipos_de_instancia(p)
    out = []
    for o in slots:
        m = tuple(round(x, 4) for x in struct.unpack_from('<12f', p.data, o + 0x20))
        c = struct.unpack_from('<3f', p.data, o + 0x50)
        raio = struct.unpack_from('<f', p.data, o + 0x18)[0]
        out.append((o, p.U(o + 0x0C), m, c, raio))
    return out, tipos


def _aabb_do_vif(p, mesh):
    """A caixa local de uma malha, DECODIFICANDO o VIF de verdade.

    Usa o mesmo `mc3_vifpos` estrito do viewer e do `aabb_local`: o cabecalho do
    sub-lote escolhe o endereco VU da posicao e o decoder cobre V3-16, V3-32 e
    V3-8 diferencial. Contagem igual ao descritor nao basta: o antigo
    `_vif_batches` escolhia o primeiro V3, fechava 301315/301315 e ainda assim
    lia atributos como XYZ em 130 modelos.
    """
    vifpos = _mod('mc3_vifpos')
    ng = struct.unpack_from('<H', p.data, mesh + 8)[0]
    gt = p.F(struct.unpack_from('<I', p.data, mesh + 0x10)[0])
    if not p.inside(gt) or not ng:
        return None
    lo = [1e18] * 3
    hi = [-1e18] * 3
    for g in range(ng):
        va_l, nb, _r = struct.unpack_from('<IHH', p.data, gt + 8 * g)
        lista = p.F(va_l)
        if not p.inside(lista):
            continue
        for b in range(nb):
            pv, qw, n = struct.unpack_from('<IHH', p.data, lista + 8 * b)
            off = p.F(pv)
            if not p.inside(off):
                continue
            carga = bytes(p.data[off:off + 16 * qw])
            try:
                pts = vifpos.decode_positions(carga)
            except ValueError:
                continue
            if len(pts) != n:
                continue
            for v in pts:
                for k, val in enumerate(v):
                    lo[k] = min(lo[k], val)
                    hi[k] = max(hi[k], val)
    return (lo, hi) if hi[0] > -1e17 else None


def caixa_local_do_tipo(p, hf, tipos, va, cache):
    if va in cache:
        return cache[va]
    r = None
    info = tipos.get(va)
    if info:
        for mesh in info[2]:
            ab = _aabb_do_vif(p, mesh)
            if ab:
                r = ab
                break
    cache[va] = r
    return r


def cmd_instancias(a):
    p, hf = _abre(a.pck)
    inst, tipos = coleta(p, hf)
    place = le_place(a.place)
    print('%s' % os.path.basename(a.pck))
    print('   %d instancia(s) no arquivo, %d tipo(s) distintos alcancados'
          % (len(inst), len(tipos)))
    print('   %d linha(s) `inst` no place' % len(place))

    por_mat = collections.defaultdict(list)
    for d in place:
        por_mat[_mat(d)].append(d)

    casadas = semcasar = ambiguas = 0
    encaixa = estoura = semcaixa = 0
    ident_ok = ident_ruim = 0
    piores = []
    porTipoArq = collections.Counter()
    porTipoEsp = collections.Counter()
    cache = {}
    for o, va, m, _c, _raio in inst:
        porTipoArq[va] += 1
        cands = por_mat.get(m)
        if not cands:
            semcasar += 1
            continue
        if len(cands) > 1:
            ambiguas += 1
            # A repeated matrix is not a key. Picking cands[0] contaminates the
            # type with an arbitrary model name and fabricates both AABB
            # failures and "mixed types". Only unambiguous rows are judgeable.
            continue
        d = cands[0]
        casadas += 1
        porTipoEsp[(va, d['name'], d['lod'], d['part'])] += 1
        local = caixa_local_do_tipo(p, hf, tipos, va, cache)
        if not local:
            semcaixa += 1
            continue
        lo, hi = _transforma(local[0], local[1], m)
        emin, emax = _caixa(d)
        folga = max(max(emin[k] - lo[k], lo[k] - emin[k],
                        emax[k] - hi[k], hi[k] - emax[k]) for k in range(3))
        estourou = any(lo[k] < emin[k] - a.tolerancia or hi[k] > emax[k] + a.tolerancia
                       for k in range(3))
        eh_ident = (abs(m[0] - 1) < 1e-4 and abs(m[4] - 1) < 1e-4
                    and abs(m[8] - 1) < 1e-4 and abs(m[1]) < 1e-4
                    and abs(m[2]) < 1e-4 and abs(m[3]) < 1e-4)
        if estourou:
            estoura += 1
            ident_ruim += eh_ident
            if len(piores) < 400:
                piores.append((folga, d['name'], d['lod'], d['part'], o, va))
        else:
            encaixa += 1
            ident_ok += eh_ident

    print()
    print('CASAMENTO PELA MATRIZ (12 floats, 4 casas)')
    print('   %5d casaram INEQUIVOCAMENTE com uma linha do place' % casadas)
    print('   %5d sem linha correspondente' % semcasar)
    print('   %5d excluidas: mais de uma linha candidata (matriz repetida na fonte)'
          % ambiguas)
    print()
    print('ENCAIXE DA CAIXA LOCAL DO TIPO NA CAIXA DA INSTANCIA (tolerancia %g)'
          % a.tolerancia)
    print('   %5d ENCAIXAM' % encaixa)
    print('   %5d ESTOURAM  <- associacao instancia->tipo suspeita' % estoura)
    print('   %5d sem AABB local legivel no tipo' % semcaixa)
    if encaixa + estoura:
        print('   taxa de encaixe: %.1f%%' % (100.0 * encaixa / (encaixa + estoura)))
    print('   das rotacoes identidade: %d encaixam, %d estouram'
          % (ident_ok, ident_ruim))
    if piores:
        piores.sort(reverse=True)
        print()
        print('   piores estouros:')
        print('   %-40s %-4s %-9s %10s %10s' % ('modelo', 'lod', 'parte', 'folga', 'Instance'))
        for f, n, lod, part, o, _va in piores[:12]:
            print('   %-40s %-4s %-9s %10.1f   0x%06X' % (n[:40], lod, part, f, o))
        cont = collections.Counter(n for _f, n, _l, _p, _o, _v in piores)
        print()
        print('   modelos que mais estouram: %s'
              % ', '.join('%s x%d' % (n[:30], c) for n, c in cont.most_common(5)))

    print()
    print('CONTAGEM POR TIPO')
    print('   %d tipo(s) referenciados pelas instancias do arquivo' % len(porTipoArq))
    nomes_por_tipo = collections.defaultdict(set)
    for (va, nome, lod, part), _n in porTipoEsp.items():
        nomes_por_tipo[va].add((nome, lod, part))
    misturados = {va: s for va, s in nomes_por_tipo.items() if len(s) > 1}
    print('   %d tipo(s) recebem instancias de MAIS DE UM modelo <- mistura'
          % len(misturados))
    for va, s in list(misturados.items())[:6]:
        print('      tipo %08X: %s' % (va, ', '.join(n for n, _l, _p in list(s)[:4])))


def cmd_tipo(a):
    p, hf = _abre(a.pck)
    inst, tipos = coleta(p, hf)
    place = [d for d in le_place(a.place) if a.nome.lower() in d['name'].lower()]
    if not place:
        raise SystemExit('nenhuma linha do place casa %r' % a.nome)
    alvo = {_mat(d) for d in place}
    print('%s   filtro %r' % (os.path.basename(a.pck), a.nome))
    print('   %d linha(s) no place, %d matriz(es) distinta(s)'
          % (len(place), len(alvo)))
    achadas = [(o, va, m, c, r) for o, va, m, c, r in inst if m in alvo]
    print('   %d instancia(s) no arquivo com uma dessas matrizes' % len(achadas))
    if not achadas:
        return
    tv = collections.Counter(va for _o, va, _m, _c, _r in achadas)
    print('   apontam para %d tipo(s): %s'
          % (len(tv), ', '.join('%08X x%d' % (v, n) for v, n in tv.most_common(6))))
    xs = [m[9] for _o, _v, m, _c, _r in achadas]
    zs = [m[11] for _o, _v, m, _c, _r in achadas]
    ys = [m[10] for _o, _v, m, _c, _r in achadas]
    print('   translacao no ARQUIVO: X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f'
          % (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
    px = [float(d['tx']) for d in place]
    pz = [float(d['tz']) for d in place]
    py = [float(d['ty']) for d in place]
    print('   translacao na FONTE : X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f'
          % (min(px), max(px), min(py), max(py), min(pz), max(pz)))
    print('   %d translacao(oes) XZ distintas no arquivo'
          % len({(m[9], m[11]) for _o, _v, m, _c, _r in achadas}))
    cache = {}
    for o, va, m, c, r in achadas[:a.mostrar]:
        local = caixa_local_do_tipo(p, hf, tipos, va, cache)
        nome = tipos.get(va, ('?',))[0]
        print('      Instance 0x%06X  tipo %08X (%s)  T=(%.1f, %.1f, %.1f)  '
              'centro=(%.1f, %.1f, %.1f) raio %.1f  AABB local %s'
              % (o, va, nome[:14], m[9], m[10], m[11], c[0], c[1], c[2], r,
                 ('%.0f x %.0f x %.0f' % tuple(local[1][k] - local[0][k] for k in range(3)))
                 if local else 'ILEGIVEL'))


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='acao')
    i = sub.add_parser('instancias', help='auditoria das 8511, uma a uma')
    i.add_argument('pck')
    i.add_argument('--place', required=True)
    i.add_argument('--tolerancia', type=float, default=1.0)
    t = sub.add_parser('tipo', help='foca num modelo pelo nome')
    t.add_argument('pck')
    t.add_argument('--place', required=True)
    t.add_argument('--nome', required=True)
    t.add_argument('--mostrar', type=int, default=6)
    a = ap.parse_args()
    fn = {'instancias': cmd_instancias, 'tipo': cmd_tipo}.get(a.acao)
    if not fn:
        ap.print_help()
        return 2
    fn(a)
    return 0


if __name__ == '__main__':
    sys.exit(main())
