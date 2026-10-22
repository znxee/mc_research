#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reconstroi a quadtree ``type10`` de um ``*_bnd.pck`` como plano de chao
grosseiro, dentro do teto de 2000/2000 da classe ``phQuadtreeCell``.

POR QUE ISTO EXISTE
===================

``mcPhysics::InitStaticData`` (0x002C2644) roda a cada carga de ``_bnd.pck`` e faz

    phOctreeCell::ClassInit  (a1[1], a1[2], *a1);        // valores DO ARQUIVO
    phQuadtreeCell::ClassInit(2000, 2000, 2000);          // CONSTANTE

``ClassInit`` (0x004A5A08) aloca ``smPolyTouched = new byte[(n+7)>>3]`` e
``smVertTouched`` do mesmo jeito: 250 bytes cada para n=2000. Os dois bitmaps sao
indexados pelo INDICE GLOBAL do poligono e do vertice, sem checagem de faixa
(``CullSpherePolysRecurse`` 0x004A6390, ``FinishCullingVerts`` 0x004A6AE8), e os
dois pontos de entrada de cull chamam ``ClearTouched`` = ``memset(buf, 0,
(n+7)>>3)`` com a contagem DECLARADA do bound.

    => um phBoundQuadtree com mais de 2000 polys ou 2000 verts faz memset fora
       de um bloco de 250 bytes em TODA consulta de colisao.

A octree nao tem esse problema: ``header+0x80/+0x84`` sao exatamente as contagens
do type9 e dimensionam os bitmaps dela. A quadtree nao tem campo nenhum.

Isso explica os tres builds de LA: v13 (1873 polys / 2652 verts) estoura 82 bytes
no bitmap de vertices e sobrevive; v15 (2699/3832) estoura 88+229 e da gelo; v14
(12378/12991) estoura 1298+1375 e trava o loading.

O QUE ESTE GERADOR FAZ
======================

Mede a forma que o varejo da ao type10 e a reproduz. Nas quatro cidades shipadas,
sem uma unica excecao em 604 poligonos, toda face do type10 e perfeitamente
horizontal, virada para cima, e grande (vao mediano de 102 a 280 unidades) - sao
lajes em patamares de altura discretos cobrindo a planta inteira da cidade.

Entao: pega as faces de piso de material ``road`` do type9 (que sao a verdade
sobre onde ha pista), rasteriza a planta delas numa grade, agrupa por faixa de
altura, funde celulas vizinhas em retangulos maximos (greedy meshing) e emite um
quad plano por retangulo.

A altura de um quad e ``indice_da_faixa * band - sink``, o piso da faixa e nao o
minimo do proprio retangulo, para que lajes vizinhas da mesma faixa fiquem na
mesma altura e possam compartilhar vertice. Como toda celula da faixa ``k`` tem
``min_y`` em ``[k*band, (k+1)*band)``, o quad fica sempre NO OU ABAIXO de toda
face de pista do type9 dentro dele, com erro limitado a ``band + sink``. Isso e
deliberado e e verificado na auditoria: assim ele nunca rouba um contato do type9
nem cria degrau. Onde o type9 tiver buraco, ele funciona como rede de seguranca
logo abaixo, em vez de deixar o carro cair do mundo.

A ocupacao da grade e conservadora (ver ``rasterize``): cobrir de menos e
inofensivo, cobrir de mais criaria plataforma invisivel no ar na beira das vias
elevadas.

O type9 sai byte a byte identico.

    python rebuild_type10_ground_plane.py --donor losangeles_bnd.pck \\
        --out saida.pck --audit auditoria.json
"""

import argparse
import hashlib
import json
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mc3_bound as MB

ROAD_GLOBAL_ID = MB.GLOBAL_MATERIAL_IDS['road']


# ---------------------------------------------------------------- fonte type9

def road_floors(bound, min_ny):
    """Faces de piso do type9 cujo material global e ``road``.

    Devolve (pontos_xz_y, ...) por face. So entram faces viradas para cima: uma
    face com normal para baixo e a barriga de um viaduto, nao pista.
    """
    node = bound.trees[9]
    verts, polys = bound.geometry(node)
    mats = bound.materials(node)
    out = []
    skipped_material = skipped_normal = 0
    for (normal, area, vi, nb) in polys:
        local = struct.pack('<f', area)[0]
        if local >= len(mats) or mats[local] != ROAD_GLOBAL_ID:
            skipped_material += 1
            continue
        if normal[1] < min_ny:
            skipped_normal += 1
            continue
        out.append([verts[i] for i in vi])
    return out, dict(type9_polys=len(polys), road_floors=len(out),
                     skipped_not_road=skipped_material,
                     skipped_not_up=skipped_normal)


# ------------------------------------------------------------- rasterizacao

def tri_rect_overlap(tri, x0, z0, x1, z1):
    """SAT entre um triangulo 2D e um retangulo alinhado aos eixos."""
    tx = [p[0] for p in tri]
    tz = [p[1] for p in tri]
    if max(tx) < x0 or min(tx) > x1 or max(tz) < z0 or min(tz) > z1:
        return False
    rect = ((x0, z0), (x1, z0), (x1, z1), (x0, z1))
    for i in range(3):
        ax, az = tri[i]
        bx, bz = tri[(i + 1) % 3]
        nx, nz = -(bz - az), (bx - ax)
        if nx == 0.0 and nz == 0.0:
            continue
        tmin = min(nx * p[0] + nz * p[1] for p in tri)
        tmax = max(nx * p[0] + nz * p[1] for p in tri)
        rmin = min(nx * p[0] + nz * p[1] for p in rect)
        rmax = max(nx * p[0] + nz * p[1] for p in rect)
        if tmax < rmin or rmax < tmin:
            return False
    return True


def point_in_tri(px, pz, tri):
    (ax, az), (bx, bz), (cx, cz) = tri
    d1 = (px - bx) * (az - bz) - (ax - bx) * (pz - bz)
    d2 = (px - cx) * (bz - cz) - (bx - cx) * (pz - cz)
    d3 = (px - ax) * (cz - az) - (cx - ax) * (pz - az)
    neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (neg and pos)


def rasterize(faces, cell, origin, sub, fill):
    """Grade XZ -> menor altura de pista naquela celula, com cobertura medida.

    A ocupacao e CONSERVADORA de proposito, e isto e o ponto mais delicado do
    gerador. Marcar a celula porque "alguma face encostou nela" faz a laje
    transbordar ate uma celula inteira para fora da pista - e uma laje que
    transborda da beira de uma via elevada vira plataforma invisivel no ar, com
    o carro pousando em cima dela. Cobrir de menos e inofensivo (o type9 continua
    com a pista); cobrir de mais cria chao onde nao devia haver.

    A amostragem e feita numa RETICULA de passo ``cell/sub`` cujos pontos caem
    sobre as bordas da celula, e nao em centros de sub-celula. Uma celula so
    entra se ``fill`` dos seus ``(sub+1)^2`` pontos - **os quatro cantos
    inclusive** - estiver dentro de alguma face de pista.

    Isso importa mais do que parece. Amostrando centros de sub-celula, os
    pontos extremos ficam a meio passo da borda: com ``sub=4`` os 12,5 % mais
    externos da celula nunca sao testados, e uma celula "totalmente coberta"
    ainda transborda pelos cantos. Medido: 0,52 % das amostras de auditoria
    ficavam expostas exatamente assim. Com a reticula, a borda e testada.

    A altura e o menor Y entre os pontos cobertos - a menor, nao a media: o
    quad precisa passar por baixo de tudo que o type9 tem ali, e uma media
    colocaria a laje acima de parte da pista.
    """
    ox, oz = origin
    step = cell / float(sub)
    lattice = {}
    for pts in faces:
        xz = [(p[0], p[2]) for p in pts]
        ymin = min(p[1] for p in pts)
        lx0 = int(math.ceil((min(p[0] for p in xz) - ox) / step))
        lx1 = int(math.floor((max(p[0] for p in xz) - ox) / step))
        lz0 = int(math.ceil((min(p[1] for p in xz) - oz) / step))
        lz1 = int(math.floor((max(p[1] for p in xz) - oz) / step))
        tris = [(xz[0], xz[k], xz[k + 1]) for k in range(1, len(xz) - 1)]
        for lx in range(lx0, lx1 + 1):
            px = ox + lx * step
            for lz in range(lz0, lz1 + 1):
                pz = oz + lz * step
                if not any(point_in_tri(px, pz, t) for t in tris):
                    continue
                cur = lattice.get((lx, lz))
                if cur is None or ymin < cur:
                    lattice[(lx, lz)] = ymin
    per_cell = (sub + 1) * (sub + 1)
    need = max(1, int(round(fill * per_cell)))
    counts, lowest = {}, {}
    for (lx, lz), y in lattice.items():
        # Um ponto de reticula pertence a toda celula que o encosta - quatro nos
        # cantos, duas nas bordas, uma no interior - e por isso celulas vizinhas
        # concordam na borda em vez de cada uma julgar a sua metade.
        #
        # O `set` nao e decorativo: para um ponto interior os dois candidatos
        # `(lx-1)//sub` e `lx//sub` sao o MESMO indice, e sem deduplicar o ponto
        # era contado quatro vezes para a mesma celula. A contagem passava de 25
        # sem a celula estar coberta, e a ocupacao virava mais frouxa do que a
        # que ela deveria substituir.
        cells_x = {(lx - 1) // sub, lx // sub}
        cells_z = {(lz - 1) // sub, lz // sub}
        for gx in cells_x:
            for gz in cells_z:
                if not (gx * sub <= lx <= gx * sub + sub
                        and gz * sub <= lz <= gz * sub + sub):
                    continue
                key = (gx, gz)
                counts[key] = counts.get(key, 0) + 1
                if key not in lowest or y < lowest[key]:
                    lowest[key] = y
    return {k: lowest[k] for k, c in counts.items() if c >= need}


# -------------------------------------------------------- greedy rectangles

def greedy_rectangles(cells):
    """Funde celulas de mesma chave em retangulos maximos.

    Varredura por linha: acha corridas horizontais e estende para baixo
    enquanto a linha seguinte tiver exatamente a mesma corrida. E o algoritmo
    classico de greedy meshing; produz poucas lajes grandes, que e justamente a
    forma que o varejo usa.
    """
    remaining = dict(cells)
    rects = []
    for (gx, gz) in sorted(remaining, key=lambda k: (k[1], k[0])):
        if (gx, gz) not in remaining:
            continue
        key = remaining[(gx, gz)]
        width = 0
        while remaining.get((gx + width, gz)) == key:
            width += 1
        height = 1
        while True:
            row = [(gx + i, gz + height) for i in range(width)]
            if all(remaining.get(c) == key for c in row):
                height += 1
            else:
                break
        for i in range(width):
            for j in range(height):
                del remaining[(gx + i, gz + j)]
        rects.append((gx, gz, width, height, key))
    return rects


# ------------------------------------------------------------------- geometria

def build_geometry(rects, cell, origin, heights, sink, band):
    """Um quad plano por retangulo, com vertices compartilhados.

    A altura de uma laje e ``indice_da_faixa * band - sink``, e NAO o minimo do
    proprio retangulo. As duas propriedades que isso compra:

    - **continua garantido** que a laje fica no ou abaixo de toda face de pista
      do type9 dentro dela. Por construcao da faixa, toda celula do grupo tem
      ``min_y`` em ``[k*band, (k+1)*band)``, logo ``k*band <= min_y`` sempre.

      Cuidado com o alcance dessa garantia: ``band + sink`` limita o quanto a
      laje fica abaixo do MINIMO AMOSTRADO da celula, nao abaixo da pista em
      todo ponto. Numa rampa a pista sobe dentro da propria celula, e ali a laje
      fica mais funda - medido, cerca de 8 % das amostras ficam entre 5 e 10
      unidades abaixo. Continua enterrada, que e o que importa; so nao e "no
      maximo band+sink" em todo ponto.
    - **todas as lajes da mesma faixa ficam exatamente na mesma altura**, entao
      os cantos caem sobre as mesmas linhas de grade e os retangulos vizinhos
      passam a compartilhar vertice. Dando a cada laje o seu proprio Y, nenhum
      canto coincide: sai 4 vertices por poligono e zero vizinho reciproco -
      cabe no teto, mas gasta o orcamento de vertices a toa.
    """
    ox, oz = origin
    verts, vmap, polys = [], {}, []
    for (gx, gz, w, h, band_index) in rects:
        y = band_index * band - sink
        x0, x1 = ox + gx * cell, ox + (gx + w) * cell
        z0, z1 = oz + gz * cell, oz + (gz + h) * cell
        # Sentido anti-horario visto de cima, para a normal sair em +Y, que e a
        # convencao verificada nas quatro cidades shipadas.
        corners = ((x0, y, z0), (x0, y, z1), (x1, y, z1), (x1, y, z0))
        idx = []
        for c in corners:
            if c not in vmap:
                vmap[c] = len(verts)
                verts.append(c)
            idx.append(vmap[c])
        if len(set(idx)) != 4:
            continue
        area = (x1 - x0) * (z1 - z0)
        polys.append(((0.0, 1.0, 0.0), area, tuple(idx)))
    return verts, polys


def all_floors(bound):
    """Toda face do type9 virada para cima, de qualquer material, em grade XZ.

    Qualquer material, nao so ``road``: uma laje enterrada sob a calcada esta
    corretamente enterrada, e exigir pista ali marcaria como exposta uma laje
    que esta apoiada.
    """
    node = bound.trees[9]
    verts, polys = bound.geometry(node)
    CELL = 16.0
    grid, faces = {}, []
    for (normal, area, vi, nb) in polys:
        if normal[1] < 0.30:
            continue
        pts = [verts[i] for i in vi]
        idx = len(faces)
        faces.append((normal, pts))
        xs = [q[0] for q in pts]; zs = [q[2] for q in pts]
        for gx in range(int(math.floor(min(xs) / CELL)), int(math.floor(max(xs) / CELL)) + 1):
            for gz in range(int(math.floor(min(zs) / CELL)), int(math.floor(max(zs) / CELL)) + 1):
                grid.setdefault((gx, gz), []).append(idx)
    return faces, grid, CELL


def drop_exposed(rects, cell, origin, band, sink, faces, grid, gcell, samples, near):
    """Remove as lajes que ficariam EXPOSTAS, isto e, sem piso do type9 acima.

    O gerador ja e conservador na ocupacao da grade, mas o retangulo e a uniao
    de celulas e a borda dele ainda pode escapar da pista num ponto ou outro.
    Em vez de deixar a auditoria reprovar por 0,02 % das amostras, a laje que
    falha e simplesmente descartada: ela e redundante com o type9 de qualquer
    modo, entao perder uma custa nada e garante a propriedade por construcao.

    Um ponto sem face que o contenha mas COM piso do type9 a menos de `near`
    esta numa fresta da malha instanciada de LA, nao no ar - ali a laje esta
    tapando um buraco do type9, que e util, e por isso nao conta como exposta.
    """
    ox, oz = origin

    def inside(pts, x, z):
        n = len(pts); s = 0
        for i in range(n):
            ax, az = pts[i][0], pts[i][2]
            bx, bz = pts[(i + 1) % n][0], pts[(i + 1) % n][2]
            cr = (bx - ax) * (z - az) - (bz - az) * (x - ax)
            if cr > 1e-9: s |= 1
            elif cr < -1e-9: s |= 2
            if s == 3: return False
        return True

    def ok(x, z, y):
        g = int(math.floor(x / gcell)), int(math.floor(z / gcell))
        for idx in grid.get(g, ()):
            normal, pts = faces[idx]
            if not inside(pts, x, z) or abs(normal[1]) < 1e-9:
                continue
            ax, ay, az = pts[0]
            h = ay - (normal[0] * (x - ax) + normal[2] * (z - az)) / normal[1]
            if h >= y - 1e-3:
                return True
        span = int(math.ceil(near / gcell))
        for dx in range(-span, span + 1):
            for dz in range(-span, span + 1):
                for idx in grid.get((g[0] + dx, g[1] + dz), ()):
                    normal, pts = faces[idx]
                    if max(q[1] for q in pts) < y - 1e-3:
                        continue
                    for q in pts:
                        if (q[0] - x) ** 2 + (q[2] - z) ** 2 <= near * near:
                            return True
        return False

    kept, dropped = [], 0
    for r in rects:
        gx, gz, w, h, band_index = r
        y = band_index * band - sink
        x0, x1 = ox + gx * cell, ox + (gx + w) * cell
        z0, z1 = oz + gz * cell, oz + (gz + h) * cell
        good = True
        for i in range(samples):
            for j in range(samples):
                x = x0 + (x1 - x0) * (i + 0.5) / samples
                z = z0 + (z1 - z0) * (j + 0.5) / samples
                if not ok(x, z, y):
                    good = False
                    break
            if not good:
                break
        if good:
            kept.append(r)
        else:
            dropped += 1
    return kept, dropped


def build_neighbours(polys):
    """Vizinhanca reciproca por aresta exatamente coincidente.

    Retangulos de tamanhos diferentes formam junta em T, e uma junta em T nao
    tem vizinho reciproco. Nesses casos a aresta fica 0xFFFF, que e o que o
    varejo tambem faz (atlanta tem poligonos com os quatro lados soltos).
    """
    neighbours = [[0xFFFF] * 4 for _ in polys]
    edges = {}
    for pi, (_n, _a, idx) in enumerate(polys):
        for ei in range(4):
            a, b = idx[ei], idx[(ei + 1) % 4]
            edges.setdefault((min(a, b), max(a, b)), []).append((pi, ei))
    paired = nonmanifold = 0
    for uses in edges.values():
        if len(uses) == 2 and uses[0][0] != uses[1][0]:
            (a, ae), (b, be) = uses
            neighbours[a][ae] = b
            neighbours[b][be] = a
            paired += 1
        elif len(uses) > 2:
            nonmanifold += 1
    return neighbours, paired, nonmanifold


# ------------------------------------------------------------------- quadtree

class Leaf:
    __slots__ = ('ids', 'start', 'count')

    def __init__(self, ids):
        self.ids = ids
        self.start = 0
        self.count = 0


def build_quadtree(boxes, root_lo, root_hi, max_depth, per_leaf):
    blocks = []
    deepest = [0]

    def rec(ids, lo, hi, depth):
        deepest[0] = max(deepest[0], depth)
        if depth >= max_depth or len(ids) <= per_leaf:
            return Leaf(ids)
        midx = (lo[0] + hi[0]) / 2.0
        midz = (lo[2] + hi[2]) / 2.0
        children = []
        for child in range(4):
            bx, bz = child & 1, (child >> 1) & 1
            child_lo = [midx if bx else lo[0], lo[1], midz if bz else lo[2]]
            child_hi = [hi[0] if bx else midx, hi[1], hi[2] if bz else midz]
            hits = [i for i in ids
                    if boxes[i][0][0] <= child_hi[0] and boxes[i][1][0] >= child_lo[0]
                    and boxes[i][0][2] <= child_hi[2] and boxes[i][1][2] >= child_lo[2]]
            children.append(rec(hits, child_lo, child_hi, depth + 1))
        blocks.append(children)
        return ('node', len(blocks) - 1)

    return blocks, rec(list(range(len(boxes))), root_lo, root_hi, 0), deepest[0]


def walk_leaves(blocks, root):
    result, stack = [], [root]
    while stack:
        item = stack.pop()
        if isinstance(item, Leaf):
            result.append(item)
        else:
            stack.extend(reversed(blocks[item[1]]))
    return result


# ---------------------------------------------------------------- serializacao

def serialise(donor, verts, polys, neighbours, blocks, root, depth, out_path):
    node = donor.trees[10]
    material_ids = donor.materials(node)
    if ROAD_GLOBAL_ID not in material_ids:
        raise SystemExit('paleta local do type10 doador nao contem road (17)')
    road_index = material_ids.index(ROAD_GLOBAL_ID)
    payload = donor.off(donor.u32(node + 0x78))
    before = donor.data
    data = bytearray(before)

    leaves = walk_leaves(blocks, root)
    refs = []
    for leaf in leaves:
        leaf.start, leaf.count = len(refs), len(leaf.ids)
        refs.extend(leaf.ids)
    if len(refs) > 0xFFFF:
        raise SystemExit('%d refs passam do start u16' % len(refs))

    lo = [min(v[a] for v in verts) for a in range(3)]
    hi = [max(v[a] for v in verts) for a in range(3)]
    centre = [(lo[a] + hi[a]) / 2.0 for a in range(3)]
    side = max(hi[a] - lo[a] for a in range(3))
    grid_lo = [centre[a] - side / 2.0 for a in range(3)]
    grid_hi = [centre[a] + side / 2.0 for a in range(3)]
    radius = max(math.dist(v, centre) for v in verts) * 1.0002
    origin_radius = radius + math.sqrt(sum(x * x for x in centre))
    cell = side / float(2 ** depth) if depth else side

    def append(blob, align=16):
        while len(data) % align:
            data.append(0xCD)
        offset = len(data)
        data.extend(blob)
        return offset

    def virtual(offset):
        return offset + donor.base

    vblob = b''.join(struct.pack('<3f', *v) for v in verts)
    pblob = bytearray()
    for pi, (normal, area, idx) in enumerate(polys):
        pblob += struct.pack('<3f', *normal)
        pblob += MB.pack_area_with_material(area, road_index)
        pblob += struct.pack('<4H', *idx)
        pblob += struct.pack('<4H', *neighbours[pi])
    vert_off = append(vblob)
    poly_off = append(bytes(pblob))
    index_off = append(struct.pack('<%dH' % len(refs), *refs))
    # Cada vetor de quatro filhos foi serializado pelo jogo com o cabecalho de
    # array de 16 bytes antes dele: count=4 e 12 bytes 0xCD. Reproduzir.
    array4 = struct.pack('<I', 4) + bytes([0xCD]) * 12
    block_offs = [append(array4 + bytes(16)) + 16 for _ in blocks]

    def slot_value(item):
        if isinstance(item, Leaf):
            if item.count > 0x3FFF:
                raise SystemExit('folha com %d refs passa do campo de 14 bits'
                                 % item.count)
            return (item.start << 16) | (item.count << 2) | 1
        return virtual(block_offs[item[1]])

    for bi, children in enumerate(blocks):
        for ci, item in enumerate(children):
            struct.pack_into('<I', data, block_offs[bi] + ci * 4, slot_value(item))
    root_value = slot_value(root)
    root_off = append(struct.pack('<I', root_value))

    struct.pack_into('<3f', data, node + 0x08, *lo)
    struct.pack_into('<3f', data, node + 0x14, *hi)
    struct.pack_into('<3f', data, node + 0x20, *centre)
    struct.pack_into('<3f', data, node + 0x2C, *centre)
    struct.pack_into('<f', data, node + 0x38, radius)
    struct.pack_into('<f', data, node + 0x3C, origin_radius)
    struct.pack_into('<I', data, node + 0x4C, len(verts))
    struct.pack_into('<I', data, node + 0x50, len(polys))
    struct.pack_into('<I', data, node + 0x68, virtual(vert_off))
    struct.pack_into('<I', data, node + 0x6C, virtual(poly_off))
    struct.pack_into('<I', data, node + 0x7C, root_value)
    struct.pack_into('<I', data, payload + 0x00, virtual(root_off))
    struct.pack_into('<I', data, payload + 0x08, len(polys))
    struct.pack_into('<I', data, payload + 0x0C, len(verts))
    struct.pack_into('<I', data, payload + 0x10, len(refs))
    struct.pack_into('<I', data, payload + 0x14, virtual(index_off))
    struct.pack_into('<f', data, payload + 0x18, cell)
    struct.pack_into('<3f', data, payload + 0x1C, *grid_lo)
    struct.pack_into('<3f', data, payload + 0x28, *grid_hi)
    while len(data) % 16:
        data.append(0xCD)
    struct.pack_into('<I', data, 0x0C, len(data) - 0x80)

    allowed = set(range(0x0C, 0x10))
    for start, length in ((node + 0x08, 0x38), (node + 0x4C, 8), (node + 0x68, 8),
                          (node + 0x7C, 4), (payload + 0x00, 4), (payload + 0x08, 0x2C)):
        allowed.update(range(start, start + length))
    unexpected = [i for i, (old, new) in enumerate(zip(before, data))
                  if old != new and i not in allowed]
    if unexpected:
        raise SystemExit('bytes inesperados alterados: %s' % unexpected[:20])

    with open(out_path, 'wb') as stream:
        stream.write(data)
    return dict(leaves=len(leaves), blocks=len(blocks), refs=len(refs),
                depth=depth, cell_size=cell, aabb=[lo, hi],
                grid=[grid_lo, grid_hi], radius=radius,
                origin_radius=origin_radius, road_local_index=road_index,
                material_palette=material_ids,
                bytes_appended=len(data) - len(before),
                size=len(data),
                sha256=hashlib.sha256(bytes(data)).hexdigest().upper())


# ------------------------------------------------------------------------ main

def run(args):
    donor = MB.Bound(args.donor)
    donor_sha = hashlib.sha256(donor.data).hexdigest().upper()
    faces, source_stats = road_floors(donor, args.min_ny)
    if not faces:
        raise SystemExit('nenhuma face de pista no type9')
    floors, fgrid, fcell = all_floors(donor)

    ox = min(min(p[0] for p in f) for f in faces)
    oz = min(min(p[2] for p in f) for f in faces)

    attempts = []
    chosen = None
    for cell in args.cells:
        for band in args.bands:
            grid = rasterize(faces, cell, (ox, oz), args.sub, args.fill)
            banded = {k: int(math.floor(v / band)) for k, v in grid.items()}
            rects = greedy_rectangles(banded)
            rects, dropped = drop_exposed(rects, cell, (ox, oz), band, args.sink,
                                          floors, fgrid, fcell, args.verify, args.near)
            heights = {}
            for (gx, gz, w, h, _b) in rects:
                heights[(gx, gz, w, h)] = min(
                    grid[(gx + i, gz + j)] for i in range(w) for j in range(h))
            verts, polys = build_geometry(rects, cell, (ox, oz), heights,
                                          args.sink, band)
            attempts.append(dict(cell=cell, band=band,
                                 cells=len(grid), dropped_exposed=dropped,
                                 rects=len(rects), verts=len(verts),
                                 polys=len(polys),
                                 fits=len(verts) <= args.max_verts
                                 and len(polys) <= args.max_polys))
            if (len(verts) <= args.max_verts and len(polys) <= args.max_polys
                    and chosen is None):
                chosen = (cell, band, grid, rects, heights, verts, polys, dropped)
        if chosen:
            break
    if chosen is None:
        for a in attempts:
            print('  cell=%-5g band=%-4g -> %5d cells %5d rects %5d verts %5d polys'
                  % (a['cell'], a['band'], a['cells'], a['rects'], a['verts'],
                     a['polys']))
        raise SystemExit('nenhuma combinacao coube em %d verts / %d polys'
                         % (args.max_verts, args.max_polys))

    cell, band, grid, rects, heights, verts, polys, dropped = chosen
    neighbours, paired, nonmanifold = build_neighbours(polys)

    boxes = []
    for (_n, _a, idx) in polys:
        pts = [verts[i] for i in idx]
        boxes.append(([min(p[a] for p in pts) for a in range(3)],
                      [max(p[a] for p in pts) for a in range(3)]))
    lo = [min(v[a] for v in verts) for a in range(3)]
    hi = [max(v[a] for v in verts) for a in range(3)]
    centre = [(lo[a] + hi[a]) / 2.0 for a in range(3)]
    side = max(hi[a] - lo[a] for a in range(3))
    glo = [centre[a] - side / 2.0 for a in range(3)]
    ghi = [centre[a] + side / 2.0 for a in range(3)]
    blocks, root, depth = build_quadtree(boxes, glo, ghi, args.depth, args.per_leaf)

    info = serialise(donor, verts, polys, neighbours, blocks, root, depth, args.out)
    info.update(source=source_stats, donor=args.donor, donor_sha256=donor_sha,
                grid_cell=cell, height_band=band, sink=args.sink,
                subsamples=args.sub, fill_threshold=args.fill,
                min_ny=args.min_ny, grid_cells=len(grid), rectangles=len(rects),
                dropped_exposed=dropped, verify_samples=args.verify,
                near_radius=args.near,
                verts=len(verts), polys=len(polys), paired_edges=paired,
                nonmanifold_edges=nonmanifold, attempts=attempts,
                cap_polys=args.max_polys, cap_verts=args.max_verts)

    print('type9 pista       : %d faces road viradas para cima (de %d polys)'
          % (source_stats['road_floors'], source_stats['type9_polys']))
    print('grade             : cell=%g, band=%g -> %d celulas ocupadas'
          % (cell, band, len(grid)))
    print('lajes             : %d retangulos -> %d polys, %d verts '
          '(%d descartadas por ficarem expostas)'
          % (len(rects), len(polys), len(verts), dropped))
    print('teto da classe    : %d/2000 polys, %d/2000 verts  %s'
          % (len(polys), len(verts),
             'OK' if len(polys) <= 2000 and len(verts) <= 2000 else 'ESTOURA'))
    print('quadtree          : %d blocos, %d folhas, %d refs, depth %d, cell %.4f'
          % (info['blocks'], info['leaves'], info['refs'], depth, info['cell_size']))
    print('arestas           : %d pareadas, %d nao-manifold' % (paired, nonmanifold))
    print('gravado           : %s  %d bytes' % (args.out, info['size']))
    print('SHA256            : %s' % info['sha256'])
    if args.audit:
        with open(args.audit, 'w', encoding='utf-8') as stream:
            json.dump(info, stream, indent=2, ensure_ascii=False)
            stream.write('\n')
    return info


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--donor', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--audit')
    ap.add_argument('--cells', type=float, nargs='+',
                    default=[16, 20, 24, 32, 40, 48, 64, 80])
    ap.add_argument('--bands', type=float, nargs='+', default=[2.0, 4.0, 8.0])
    ap.add_argument('--sink', type=float, default=0.05,
                    help='quanto abaixo do menor piso type9 a laje fica')
    ap.add_argument('--min-ny', type=float, default=0.70)
    ap.add_argument('--sub', type=int, default=4,
                    help='amostras por lado dentro de cada celula')
    ap.add_argument('--fill', type=float, default=1.00,
                    help='fracao minima dos pontos de reticula da celula '
                         'cobertos por pista; 1.0 exige os quatro cantos')
    ap.add_argument('--verify', type=int, default=6,
                    help='amostras por lado ao conferir cada laje contra o '
                         'type9; a laje exposta e descartada')
    ap.add_argument('--near', type=float, default=6.0,
                    help='raio que separa fresta da malha do type9 de vazio')
    ap.add_argument('--max-polys', type=int, default=1800)
    ap.add_argument('--max-verts', type=int, default=1800)
    ap.add_argument('--depth', type=int, default=8)
    ap.add_argument('--per-leaf', type=int, default=12)
    run(ap.parse_args())


if __name__ == '__main__':
    main()
