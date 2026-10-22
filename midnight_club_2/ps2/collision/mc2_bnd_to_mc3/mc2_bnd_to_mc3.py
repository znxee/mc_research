#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Converte a colisao de texto do MC2 (`otgrid`) para o `_bnd.pck` do MC3.

O MC3 le a colisao de escala-cidade SO em .pck (tipo 9) - o leitor ASCII de
`.bnd` (`phBound::LoadFromFile` 0x0047E128) serve a bounds individuais. E um
`_bnd` recusado cai num `while(1)` em 0x001A93D8, ou seja tela preta, entao o
resultado e conferido relendo o arquivo no fim.

O que a fonte do MC2 da e o que precisa ser calculado:

  vertices   vem prontos, ja em coordenada de MUNDO nas 42 celulas do grid
  poligonos  vem os indices (tri/quad); a NORMAL e a AREA sao calculadas
  winding    o do MC2 ja casa com o do MC3 - medido: 94,1% dos quase-horizontais
             apontam +Y, contra 97% do varejo. Nao inverter (inverter faz o
             carro entrar e ficar presa dentro do solido).
  material   o indice local fica no byte menos significativo do float de area;
             cada classe do MC2 e mapeada para a paleta fisica do doador

A arvore e construida do zero porque LA nao cabe no cubo de nenhum doador. As
regras vieram da leitura do varejo:

  - a raiz e um CUBO: a AABB centralizada e crescida ate todo lado igualar o maior
  - `lado/celula` e potencia de 2 (512 atlanta, 1024 sd/detroit, 2048 tokyo)
  - octante: bit0 = x, bit1 = z, bit2 = y (nao x/y/z)
  - um poligono entra em TODA folha cuja celula a sua AABB cruza
  - folha = `(start << 16) | (bytes << 1) | 1`, com `count = (v & 0xFFFF) >> 2`
  - octante VAZIO tem que ser folha de contagem zero, NUNCA ponteiro nulo: o
    leitor so testa o bit 0 e desreferencia qualquer slot par
  - `start` tem 16 bits, teto de 65535 entradas na lista
"""
import os
import argparse
import struct
import sys

from mc2_bnd_parse import le_otgrid


def normal_e_area(pts):
    """Normal unitaria pelo winding e area real do poligono."""
    a, b, c = pts[0], pts[1], pts[2]
    u = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    w = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
    n = (u[1] * w[2] - u[2] * w[1],
         u[2] * w[0] - u[0] * w[2],
         u[0] * w[1] - u[1] * w[0])
    m = (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5
    if m < 1e-12:
        return None, 0.0
    n = (n[0] / m, n[1] / m, n[2] / m)
    # a area pela MESMA projecao que o check() do mc3_bound recalcula
    s2 = 0.0
    for j in range(len(pts)):
        k = (j + 1) % len(pts)
        s2 += ((pts[j][1] * pts[k][2] - pts[j][2] * pts[k][1]) * n[0]
               + (pts[j][2] * pts[k][0] - pts[j][0] * pts[k][2]) * n[1]
               + (pts[j][0] * pts[k][1] - pts[j][1] * pts[k][0]) * n[2])
    return n, abs(s2 / 2.0)


class Folha(object):
    """Uma folha da arvore. E um objeto para poder ser identificada por
    identidade quando o mesmo conteudo aparece em octantes diferentes."""

    __slots__ = ('ids', 'start', 'count')

    def __init__(self, ids):
        self.ids = ids
        self.start = 0
        self.count = 0


def constroi_octree(caixas, clo, chi, prof_max, por_folha):
    """(blocos, raiz). Cada bloco e uma lista de 8 slots; um slot e uma `Folha`
    ou o indice de outro bloco (embrulhado em `('no', i)`)."""
    blocos = []
    fundo = [0]                       # a profundidade que a arvore REALMENTE usa

    def rec(ids, lo, hi, prof):
        if prof > fundo[0]:
            fundo[0] = prof
        if prof >= prof_max or len(ids) <= por_folha:
            return Folha(ids)
        mid = [(lo[a] + hi[a]) / 2.0 for a in range(3)]
        filhos = []
        for oct_ in range(8):
            bx, bz, by = oct_ & 1, (oct_ >> 1) & 1, (oct_ >> 2) & 1
            flo = [mid[0] if bx else lo[0], mid[1] if by else lo[1],
                   mid[2] if bz else lo[2]]
            fhi = [hi[0] if bx else mid[0], hi[1] if by else mid[1],
                   hi[2] if bz else mid[2]]
            dentro = [i for i in ids
                      if all(caixas[i][0][a] <= fhi[a] and caixas[i][1][a] >= flo[a]
                             for a in range(3))]
            filhos.append(rec(dentro, flo, fhi, prof + 1))
        blocos.append(filhos)
        return ('no', len(blocos) - 1)

    raiz = rec(list(range(len(caixas))), clo, chi, 0)
    return blocos, raiz, fundo[0]


def percorre(blocos, raiz):
    """Todas as folhas, na ordem em que a arvore as visita."""
    saida, pilha = [], [raiz]
    while pilha:
        s = pilha.pop()
        if isinstance(s, Folha):
            saida.append(s)
        else:
            pilha.extend(reversed(blocos[s[1]]))
    return saida


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument('--mc2', default='output/mc2_losangeles/bound/losangeles.bnd')
    ap.add_argument('--doador',
                    default=os.path.join(os.environ.get('MC3_HOSTFS', ''), 'ASSETS/resources/city/tokyo_bnd.pck'),
                    help='esqueleto: header, wrappers e a arvore de estradas (tipo 10)')
    ap.add_argument('--out', required=True)
    ap.add_argument('--prof', type=int, default=10, help='profundidade maxima')
    ap.add_argument('--por-folha', type=int, default=22)
    a = ap.parse_args()

    verts, polys, mats, _cab = le_otgrid(a.mc2)
    print('MC2: %d vertices, %d poligonos, %d materiais'
          % (len(verts), len(polys), len(mats)))

    import mc3_bound as MB
    b = MB.Bound(a.doador)
    node = b.trees[9]
    material_ids = b.materials(node)
    if MB.GLOBAL_MATERIAL_IDS['road'] not in material_ids:
        sys.exit('doador nao contem material road (id global 17)')

    saida, caixas, ruins = [], [], 0
    for vi, nome in polys:
        pts = [verts[i] for i in vi]
        n, area = normal_e_area(pts)
        if n is None:
            ruins += 1
            continue
        idx = list(vi) + ([0] if len(vi) == 3 else [])
        material_index, _physical = MB.material_index_for_name(nome, material_ids)
        saida.append((n, area, idx, material_index))
        caixas.append(([min(p[c] for p in pts) for c in range(3)],
                       [max(p[c] for p in pts) for c in range(3)]))
    if ruins:
        print('  %d poligono(s) degenerado(s) descartado(s)' % ruins)
    npoly = len(saida)

    lo = [min(q[c] for q in verts) for c in range(3)]
    hi = [max(q[c] for q in verts) for c in range(3)]
    lado = max(hi[c] - lo[c] for c in range(3))
    centro = [(lo[c] + hi[c]) / 2.0 for c in range(3)]
    clo = [centro[c] - lado / 2.0 for c in range(3)]
    chi = [centro[c] + lado / 2.0 for c in range(3)]
    print('AABB (%.0f %.0f %.0f)..(%.0f %.0f %.0f)  cubo lado %.1f  celula %.3f'
          % tuple(lo + hi + [lado, lado / (2 ** a.prof)]))

    blocos, raiz, fundo = constroi_octree(caixas, clo, chi, a.prof, a.por_folha)
    folhas = percorre(blocos, raiz)
    refs = sum(len(f.ids) for f in folhas)
    # o campo `cell` do payload e lado/2^profundidade; tem que refletir a
    # profundidade que a arvore REALMENTE usa, nao a que foi pedida no --prof
    celula = lado / float(2 ** fundo)
    print('arvore: %d blocos, %d folhas, %d referencias (dup %.2fx), '
          'profundidade real %d, celula %.3f'
          % (len(blocos), len(folhas), refs, refs / float(npoly), fundo, celula))
    if refs > 0xFFFF:
        sys.exit('%d referencias passam do teto de 65535 que um start de 16 bits '
                 'enderece - baixe --prof ou suba --por-folha' % refs)

    data = bytearray(b.data)

    def cola(blob, align=16):
        while len(data) % align:
            data.append(0xCD)
        off = len(data)
        data.extend(blob)
        return off

    def va(off):
        return off + b.base

    bp = bytearray()
    for n, area, idx, material_index in saida:
        bp += struct.pack('<3f', n[0], n[1], n[2])
        bp += MB.pack_area_with_material(area, material_index)
        bp += struct.pack('<8H', idx[0], idx[1], idx[2], idx[3],
                          0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF)
    off_poly = cola(bytes(bp))
    off_vert = cola(b''.join(struct.pack('<3f', *q) for q in verts))

    lista = []
    for f in folhas:
        f.start, f.count = len(lista), len(f.ids)
        lista.extend(f.ids)
    off_idx = cola(struct.pack('<%dH' % len(lista), *lista))

    off_bloco = [cola(bytes(32)) for _ in blocos]

    def valor(slot):
        if isinstance(slot, Folha):
            # folha vazia tambem e folha: contagem zero, nunca ponteiro nulo
            return (slot.start << 16) | ((slot.count * 2) << 1) | 1
        return va(off_bloco[slot[1]])

    for bi, filhos in enumerate(blocos):
        for j, s in enumerate(filhos):
            struct.pack_into('<I', data, off_bloco[bi] + 4 * j, valor(s))
    off_raiz = cola(struct.pack('<I', valor(raiz)))

    struct.pack_into('<3f', data, node + 0x08, *lo)
    struct.pack_into('<3f', data, node + 0x14, *hi)
    struct.pack_into('<3f', data, node + 0x20, *centro)
    struct.pack_into('<3f', data, node + 0x2C, *centro)
    struct.pack_into('<I', data, node + 0x4C, len(verts))
    struct.pack_into('<I', data, node + 0x50, npoly)
    struct.pack_into('<I', data, node + 0x68, va(off_vert))
    struct.pack_into('<I', data, node + 0x6C, va(off_poly))
    p = b.off(b.u32(node + 0x94))
    struct.pack_into('<I', data, p + 0x00, va(off_raiz))
    # phPolytree serializa as contagens de geometria tambem no payload. O
    # doador traz aqui os numeros do Tokyo; deixar esses dois words intactos
    # produz um arquivo contraditorio (node/root dizem LA, payload diz Tokyo).
    struct.pack_into('<I', data, p + 0x08, npoly)
    struct.pack_into('<I', data, p + 0x0C, len(verts))
    struct.pack_into('<I', data, p + 0x10, len(lista))
    struct.pack_into('<I', data, p + 0x14, va(off_idx))
    struct.pack_into('<f', data, p + 0x18, celula)
    struct.pack_into('<3f', data, p + 0x1C, *clo)
    struct.pack_into('<3f', data, p + 0x28, *chi)
    struct.pack_into('<I', data, 0x80, len(verts))
    struct.pack_into('<I', data, 0x84, npoly)

    while len(data) % 16:            # o retail alinha o FIM do arquivo tambem
        data.append(0xCD)
    struct.pack_into('<I', data, 0x0C, len(data) - 128)
    open(a.out, 'wb').write(bytes(data))
    print('gravado %s (%d bytes)' % (a.out, len(data)))

    # Reabrir e validar o que foi realmente serializado. Isto pega ponteiro,
    # tamanho e contagem esquecidos no conversor antes de o PCK chegar ao jogo.
    c = MB.Bound(a.out)
    cn = c.trees[9]
    cp = c.off(c.u32(cn + 0x94))
    campos = (
        ('root vertices', c.verts_total, len(verts)),
        ('root polygons', c.polys_total, npoly),
        ('node vertices', c.u32(cn + 0x4C), len(verts)),
        ('node polygons', c.u32(cn + 0x50), npoly),
        ('payload polygons', c.u32(cp + 0x08), npoly),
        ('payload vertices', c.u32(cp + 0x0C), len(verts)),
        ('payload refs', c.u32(cp + 0x10), len(lista)),
    )
    erros = ['%s: %d != %d' % (nome, atual, esperado)
             for nome, atual, esperado in campos if atual != esperado]
    folhas_c = sorted(c.leaves(cn, 9))
    cursor = 0
    for start, count, _slot in folhas_c:
        if start != cursor:
            erros.append('folhas: intervalo comeca em %d, esperado %d'
                          % (start, cursor))
            break
        cursor += count
    if cursor != len(lista):
        erros.append('folhas: terminam em %d, esperado %d' % (cursor, len(lista)))
    _ok, ruins_area = MB.check(c, 9)
    if ruins_area:
        erros.append('areas: %d poligono(s) divergente(s)' % ruins_area)
    materiais_c = c.material_indices(cn)
    materiais_esperados = [p[3] for p in saida]
    if materiais_c != materiais_esperados:
        erros.append('indices de material divergentes')
    if any(i >= len(material_ids) for i in materiais_c):
        erros.append('indice de material fora da paleta')
    if erros:
        sys.exit('saida invalida:\n  ' + '\n  '.join(erros))
    print('validado: contagens root/node/payload coerentes, %d folhas '
          'particionam %d referencias, 0 areas divergentes; materiais %s'
          % (len(folhas_c), len(lista), sorted(set(materiais_c))))


if __name__ == '__main__':
    main()
