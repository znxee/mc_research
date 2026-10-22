#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auditoria de um ``*_bnd.pck`` candidato cuja mudanca e SO a quadtree type10.

Checa, nesta ordem:

  contrato    numPolys <= 2000 e numVerts <= 2000 (o teto real da classe
              phQuadtreeCell, provado em mcPhysics::InitStaticData 0x002C2644)
  type9       byte a byte identico ao doador
  diff        nenhum byte antigo mudou fora do header de tamanho e dos campos
              conhecidos do type10; o resto so pode ser bloco anexado
  estrutura   header/tamanho, ponteiros dentro do arquivo, as duas arvores
              presentes, contagens root/node/payload coerentes,
              node+0x7C == *(payload root slot), cabecalho retail de 16 bytes
              nos vetores de filhos, profundidade <= 20
  folhas      particionam exatamente a lista de refs, sem lacuna nem sobreposicao
  indices     refs e indices dentro da faixa, todo poly coberto
  contencao   a AABB de cada folha contem as faces dela
  geometria   normais unitarias, area recalculada, byte de material, sem
              degenerado/NaN/Inf, vizinhos reciprocos
  SEGURANCA   a propriedade que o gerador promete e que so um teste geometrico
              pode confirmar: toda laje do type10 tem piso do type9 ACIMA dela,
              ou seja esta enterrada. Uma laje sem piso acima e a superficie de
              cima naquele ponto - plataforma invisivel no ar na beira de via
              elevada, ou degrau sobre a pista - e so isso reprova. Laje
              enterrada mais fundo que band+sink acontece em rampa e e apenas
              relatada: continua sem roubar contato.

    python audit_type10_groundplane.py --donor v13.pck --candidate novo.pck \\
        --json auditoria.json
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

CAP = 2000


def tree_bytes(b, kind):
    """Todos os bytes que pertencem a uma arvore: node, geometria, arvore."""
    node = b.trees[kind]
    spans = [(node, 0xA0)]
    nv, npoly = b.u32(node + 0x4C), b.u32(node + 0x50)
    spans.append((b.off(b.u32(node + 0x68)), 12 * nv))
    spans.append((b.off(b.u32(node + 0x6C)), 32 * npoly))
    pay = b.off(b.u32(node + (0x94 if kind == 9 else 0x78)))
    spans.append((pay, 0x40))
    spans.append((b.off(b.u32(pay + 0x14)), 2 * b.u32(pay + 0x10)))
    out = bytearray()
    for off, length in spans:
        out += b.data[off:off + length]
    return bytes(out), dict(node=node, verts=nv, polys=npoly, pay=pay)


def poly_points(verts, vi):
    return [verts[i] for i in vi]


def real_area(pts):
    total = 0.0
    for k in range(1, len(pts) - 1):
        u = [pts[k][j] - pts[0][j] for j in range(3)]
        v = [pts[k + 1][j] - pts[0][j] for j in range(3)]
        cr = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2],
              u[0] * v[1] - u[1] * v[0])
        total += math.sqrt(sum(t * t for t in cr)) / 2.0
    return total


def check_structure(b, kind, problems, info, note_only_headers=False):
    node = b.trees[kind]
    fan = 8 if kind == 9 else 4
    nv, npoly = b.u32(node + 0x4C), b.u32(node + 0x50)
    pay = b.off(b.u32(node + (0x94 if kind == 9 else 0x78)))
    root_slot, index_off, nref = b.payload(node, kind)

    if b.u32(pay + 0x08) != npoly:
        problems.append('t%d payload+0x08=%d != node poly count %d'
                        % (kind, b.u32(pay + 0x08), npoly))
    if b.u32(pay + 0x0C) != nv:
        problems.append('t%d payload+0x0C=%d != node vertex count %d'
                        % (kind, b.u32(pay + 0x0C), nv))
    if kind == 10 and b.u32(node + 0x7C) != b.u32(root_slot):
        problems.append('t10 node+0x7C=%08x != *(payload root)=%08x'
                        % (b.u32(node + 0x7C), b.u32(root_slot)))

    leaves, stack, seen, depth_max = [], [(root_slot, 0)], set(), 0
    blocks = no_header = 0
    while stack:
        slot, depth = stack.pop()
        depth_max = max(depth_max, depth)
        if slot in seen:
            problems.append('t%d slot %#x visitado duas vezes' % (kind, slot))
            continue
        seen.add(slot)
        v = b.u32(slot)
        if v & 1:
            leaves.append((v >> 16, (v & 0xFFFF) >> 2))
            continue
        if not b.valid(v):
            problems.append('t%d ponteiro de bloco invalido %08x' % (kind, v))
            continue
        base = b.off(v)
        blocks += 1
        # Nas quatro cidades de varejo TODO vetor de filhos, nas duas arvores,
        # e precedido pelo cabecalho de array de 16 bytes (count seguido de
        # 0xCD): os blocos ficam 48 bytes apart no type9 e 32 no type10. O
        # type9 do losangeles nao tem nenhum - e uma divergencia herdada do
        # conversor, nao algo que este candidato introduza, e por isso ela e
        # relatada e nao reprovada quando o doador tem a mesma forma.
        if b.u32(base - 16) != fan:
            no_header += 1
        stack.extend((base + 4 * i, depth + 1) for i in range(fan))
    if no_header and not note_only_headers:
        problems.append('t%d %d de %d vetores de filhos sem cabecalho de array '
                        'count=%d' % (kind, no_header, blocks, fan))
    if depth_max > 20:
        problems.append('t%d profundidade %d passa do limite 20 das pilhas '
                        'estaticas smBoxMinStack/smBoxMaxStack' % (kind, depth_max))

    covered = [0] * nref
    for start, count in leaves:
        if start + count > nref:
            problems.append('t%d folha %d..%d fora da lista de %d refs'
                            % (kind, start, start + count, nref))
            continue
        for i in range(start, start + count):
            covered[i] += 1
    if any(c != 1 for c in covered):
        gaps = sum(1 for c in covered if c == 0)
        dups = sum(1 for c in covered if c > 1)
        problems.append('t%d folhas nao particionam refs: %d lacunas, %d repetidos'
                        % (kind, gaps, dups))

    refs = [struct.unpack_from('<H', b.data, index_off + 2 * i)[0]
            for i in range(nref)]
    if refs and max(refs) >= npoly:
        problems.append('t%d ref %d >= poly count %d' % (kind, max(refs), npoly))
    missing = npoly - len(set(refs))
    if missing:
        problems.append('t%d %d poligonos nao aparecem em folha nenhuma'
                        % (kind, missing))

    info['t%d' % kind] = dict(verts=nv, polys=npoly, refs=nref,
                              leaves=len(leaves), depth=depth_max,
                              blocks=blocks, blocks_without_array_header=no_header,
                              duplication=round(nref / npoly, 3) if npoly else 0)
    return leaves, refs


def check_geometry(b, kind, problems, info):
    node = b.trees[kind]
    verts, polys = b.geometry(node)
    mats = b.materials(node)
    bad_normal = bad_area = degenerate = nonfinite = bad_material = 0
    for (normal, area, vi, nb) in polys:
        if any(not math.isfinite(c) for c in normal) or not math.isfinite(area):
            nonfinite += 1
            continue
        if abs(math.sqrt(sum(c * c for c in normal)) - 1.0) > 1e-3:
            bad_normal += 1
        pts = poly_points(verts, vi)
        if len(set(vi)) != len(vi):
            degenerate += 1
            continue
        # A area guardada tem o indice de material no byte baixo, entao ela
        # nunca bate exatamente com a area recalculada: o byte baixo mexe na
        # mantissa. A tolerancia relativa cobre isso com folga.
        want = real_area(pts)
        if want > 0 and abs(area - want) / max(want, 1.0) > 0.02:
            bad_area += 1
        local = struct.pack('<f', area)[0]
        if local >= len(mats):
            bad_material += 1
    # reciprocidade
    broken = boundary = 0
    for pi, (normal, area, vi, nb) in enumerate(polys):
        n = len(vi)
        for ei in range(n):
            other = nb[ei]
            if other == 0xFFFF:
                boundary += 1
                continue
            if other >= len(polys):
                broken += 1
                continue
            if pi not in polys[other][3]:
                broken += 1
    for label, count in (('normais nao unitarias', bad_normal),
                         ('areas incompativeis', bad_area),
                         ('poligonos degenerados', degenerate),
                         ('NaN/Inf', nonfinite),
                         ('indice de material fora da paleta', bad_material),
                         ('vizinhos nao reciprocos', broken)):
        if count:
            problems.append('t%d %s: %d' % (kind, label, count))
    info['t%d' % kind].update(boundary_edges=boundary,
                              materials=mats,
                              broken_neighbours=broken)
    return verts, polys, mats


def check_containment(b, kind, leaves, refs, problems, info):
    """Cada face esta na celula que a folha dela diz.

    A folha nao guarda AABB - ela e so ``(start<<16)|(len<<2)|1``. A caixa da
    celula vem do CAMINHO na arvore: a raiz cobre a grade inteira e cada nivel
    parte a celula ao meio. Entao a checagem so e possivel descendo a arvore e
    carregando a caixa junto, que e o que este passo faz.

    Bit 0 do indice do filho e X e bit 1 e Z na quadtree; na octree o bit 2 e Y.
    Y nao e subdividido na quadtree, e por isso a comparacao e so em X/Z.
    """
    node = b.trees[kind]
    verts, polys = b.geometry(node)
    root_slot, index_off, nref = b.payload(node, kind)
    pay = b.off(b.u32(node + (0x94 if kind == 9 else 0x78)))
    glo = [b.f32(pay + 0x1C + 4 * i) for i in range(3)]
    ghi = [b.f32(pay + 0x28 + 4 * i) for i in range(3)]
    fan = 8 if kind == 9 else 4

    misplaced = leaf_faces = 0
    stack = [(root_slot, glo, ghi)]
    seen = set()
    while stack:
        slot, lo_, hi_ = stack.pop()
        if slot in seen:
            continue
        seen.add(slot)
        v = b.u32(slot)
        if v & 1:
            start, count = v >> 16, (v & 0xFFFF) >> 2
            for pi in refs[start:start + count]:
                if pi >= len(polys):
                    continue
                pts = poly_points(verts, polys[pi][2])
                leaf_faces += 1
                if (max(q[0] for q in pts) < lo_[0] - 1e-3
                        or min(q[0] for q in pts) > hi_[0] + 1e-3
                        or max(q[2] for q in pts) < lo_[2] - 1e-3
                        or min(q[2] for q in pts) > hi_[2] + 1e-3):
                    misplaced += 1
            continue
        if not b.valid(v):
            continue
        base = b.off(v)
        mid = [(lo_[a] + hi_[a]) / 2.0 for a in range(3)]
        for c in range(fan):
            clo = list(lo_); chi = list(hi_)
            if c & 1: clo[0] = mid[0]
            else:     chi[0] = mid[0]
            if (c >> 1) & 1: clo[2] = mid[2]
            else:            chi[2] = mid[2]
            if kind == 9:
                if (c >> 2) & 1: clo[1] = mid[1]
                else:            chi[1] = mid[1]
            stack.append((base + 4 * c, clo, chi))
    if misplaced:
        problems.append('t%d %d de %d referencias de folha apontam para face '
                        'fora da celula da folha' % (kind, misplaced, leaf_faces))

    outside = 0
    # a AABB do node tem de conter toda a geometria
    lo, hi = b.aabb(node)
    for v in verts:
        for a in range(3):
            if v[a] < lo[a] - 1e-3 or v[a] > hi[a] + 1e-3:
                outside += 1
                break
    if outside:
        problems.append('t%d %d vertices fora da AABB do node' % (kind, outside))
    info['t%d' % kind]['aabb'] = [[round(x, 3) for x in lo],
                                  [round(x, 3) for x in hi]]
    info['t%d' % kind]['leaf_refs_checked'] = leaf_faces
    info['t%d' % kind]['leaf_refs_misplaced'] = misplaced


# ------------------------------------------------------- seguranca geometrica

def safety_vs_type9(donor, cand, problems, info, band, sink, samples, tol, near):
    """As duas promessas do gerador, medidas num teste so.

    Uma laje do type10 e segura num ponto quando existe piso do type9 LOGO
    ACIMA dela - dentro de ``band + sink + tol``. Isso cobre as duas coisas de
    uma vez:

    (a) se ha piso type9 acima, a laje esta enterrada e nao rouba o contato;
    (b) se ha piso type9 acima, a laje nao esta no ar.

    O piso considerado e QUALQUER face do type9 virada para cima, nao so a de
    material ``road``: uma laje enterrada sob a calcada esta corretamente
    enterrada, e cobrar pista ali marcaria como "no ar" algo que esta apoiado.
    Isso e o que a primeira versao desta funcao errou.
    """
    n9 = donor.trees[9]
    v9, p9 = donor.geometry(n9)
    m9 = donor.materials(n9)

    CELL = 16.0
    grid = {}
    for idx, (normal, area, vi, nb) in enumerate(p9):
        if normal[1] < 0.30:
            continue
        pts = poly_points(v9, vi)
        xs = [q[0] for q in pts]; zs = [q[2] for q in pts]
        for gx in range(int(math.floor(min(xs) / CELL)), int(math.floor(max(xs) / CELL)) + 1):
            for gz in range(int(math.floor(min(zs) / CELL)), int(math.floor(max(zs) / CELL)) + 1):
                grid.setdefault((gx, gz), []).append(idx)

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

    def floors_at(x, z):
        out = []
        for idx in grid.get((int(math.floor(x / CELL)), int(math.floor(z / CELL))), ()):
            normal, area, vi, nb = p9[idx]
            pts = poly_points(v9, vi)
            if not inside(pts, x, z):
                continue
            if abs(normal[1]) < 1e-9:
                continue
            ax, ay, az = pts[0]
            out.append(ay - (normal[0] * (x - ax) + normal[2] * (z - az)) / normal[1])
        return out

    # So UMA condicao reprova: a laje estar EXPOSTA, isto e, nao ter piso
    # nenhum do type9 acima dela naquele ponto. Ai ela vira a superficie de
    # cima - plataforma invisivel no ar, ou degrau por cima da pista.
    #
    # Ficar enterrada MAIS FUNDO que band+sink nao reprova. Isso acontece em
    # rampa, onde a pista sobe dentro da propria celula da grade, e uma laje
    # plana nao acompanha. Ela continua enterrada e continua sem roubar
    # contato; so serve de rede de seguranca mais abaixo. E relatado, nao
    # reprovado - tratar como defeito seria exigir do plano grosseiro uma
    # fidelidade que ele nao se propoe a ter.
    def _floor_above_within(x, z, y, near):
        """Existe face de piso do type9 acima de `y` a menos de `near` em X/Z?"""
        g = int(math.floor(x / CELL)), int(math.floor(z / CELL))
        span = int(math.ceil(near / CELL))
        for dx in range(-span, span + 1):
            for dz in range(-span, span + 1):
                for idx in grid.get((g[0] + dx, g[1] + dz), ()):
                    normal, area, vi, nb = p9[idx]
                    pts = poly_points(v9, vi)
                    if max(q[1] for q in pts) < y - 1e-3:
                        continue
                    for q in pts:
                        if (q[0] - x) ** 2 + (q[2] - z) ** 2 <= near * near:
                            return True
        return False

    ceiling = band + sink + tol
    n10 = cand.trees[10]
    v10, p10 = cand.geometry(n10)
    checked = buried = deep = exposed = seam = 0
    worst = 0.0
    exposed_examples = []
    for k, (normal, area, vi, nb) in enumerate(p10):
        pts = poly_points(v10, vi)
        x0 = min(q[0] for q in pts); x1 = max(q[0] for q in pts)
        z0 = min(q[2] for q in pts); z1 = max(q[2] for q in pts)
        y = pts[0][1]
        for i in range(samples):
            for j in range(samples):
                x = x0 + (x1 - x0) * (i + 0.5) / samples
                z = z0 + (z1 - z0) * (j + 0.5) / samples
                checked += 1
                hs = [h for h in floors_at(x, z) if h >= y - 1e-3]
                if not hs:
                    # Nenhuma face CONTEM o ponto. Duas situacoes muito
                    # diferentes se escondem aqui, e so uma e perigosa:
                    #
                    #  - a laje transbordou para o vazio  -> plataforma no ar;
                    #  - o ponto caiu numa FRESTA do proprio type9. A pista de
                    #    LA e geometria instanciada e nao e estanque: ha vaos
                    #    finos entre faces vizinhas. Ali a laje nao esta no ar,
                    #    esta tapando um buraco que o type9 tem - que e
                    #    exatamente o defeito que o usuario relata.
                    #
                    # Separa-se pelo vizinho: se existe face de piso do type9
                    # acima da laje a menos de `near` em X/Z, e fresta.
                    if _floor_above_within(x, z, y, near):
                        seam += 1
                        continue
                    exposed += 1
                    if len(exposed_examples) < 12:
                        exposed_examples.append(
                            [k, round(x, 1), round(y, 2), round(z, 1),
                             'nenhum piso type9 num raio de %.0f u' % near])
                    continue
                gap = min(hs) - y
                worst = max(worst, gap)
                if gap <= ceiling:
                    buried += 1
                else:
                    deep += 1
    info['safety'] = dict(samples=checked, buried=buried, deeply_buried=deep,
                          seam=seam, seam_pct=round(100.0 * seam / checked, 3),
                          near_radius=near, exposed=exposed,
                          exposed_pct=round(100.0 * exposed / checked, 3),
                          deep_pct=round(100.0 * deep / checked, 3),
                          allowed_gap=ceiling, worst_gap=round(worst, 3),
                          exposed_examples=exposed_examples)
    if exposed:
        problems.append('SEGURANCA: %d de %d amostras (%.2f%%) tem laje type10 SEM '
                        'piso type9 acima - ela fica exposta como chao proprio '
                        '(plataforma no ar ou degrau sobre a pista)'
                        % (exposed, checked, 100.0 * exposed / checked))


# ------------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument('--donor', required=True)
    ap.add_argument('--candidate', required=True)
    ap.add_argument('--json')
    ap.add_argument('--band', type=float, default=4.0)
    ap.add_argument('--sink', type=float, default=0.05)
    ap.add_argument('--samples', type=int, default=4)
    ap.add_argument('--tol', type=float, default=0.75,
                    help='folga extra ao exigir piso type9 acima da laje')
    ap.add_argument('--near', type=float, default=6.0,
                    help='raio para separar fresta do type9 de vazio de verdade')
    args = ap.parse_args()

    donor = MB.Bound(args.donor)
    cand = MB.Bound(args.candidate)
    problems, info = [], {}
    info['donor'] = dict(path=args.donor, size=len(donor.data),
                         sha256=hashlib.sha256(donor.data).hexdigest().upper())
    info['candidate'] = dict(path=args.candidate, size=len(cand.data),
                             sha256=hashlib.sha256(cand.data).hexdigest().upper())

    # --- contrato da classe -------------------------------------------------
    n10 = cand.trees[10]
    npoly, nvert = cand.u32(n10 + 0x50), cand.u32(n10 + 0x4C)
    info['contract'] = dict(cap=CAP, polys=npoly, verts=nvert,
                            poly_memset=(npoly + 7) >> 3,
                            vert_memset=(nvert + 7) >> 3, buffer_bytes=(CAP + 7) >> 3,
                            poly_overflow=max(0, ((npoly + 7) >> 3) - ((CAP + 7) >> 3)),
                            vert_overflow=max(0, ((nvert + 7) >> 3) - ((CAP + 7) >> 3)))
    if npoly > CAP:
        problems.append('CONTRATO: type10 tem %d polys, teto e %d' % (npoly, CAP))
    if nvert > CAP:
        problems.append('CONTRATO: type10 tem %d verts, teto e %d' % (nvert, CAP))

    # --- type9 intacto ------------------------------------------------------
    d9, meta9 = tree_bytes(donor, 9)
    c9, meta9c = tree_bytes(cand, 9)
    info['type9_identical'] = (d9 == c9) and meta9 == meta9c
    if not info['type9_identical']:
        problems.append('type9 NAO e byte a byte identico ao doador')

    # --- diff binario -------------------------------------------------------
    old, new = donor.data, cand.data
    common = min(len(old), len(new))
    pay = cand.off(cand.u32(n10 + 0x78))
    allowed = set(range(0x0C, 0x10))
    for start, length in ((n10 + 0x08, 0x38), (n10 + 0x4C, 8), (n10 + 0x68, 8),
                          (n10 + 0x7C, 4), (pay + 0x00, 4), (pay + 0x08, 0x2C)):
        allowed.update(range(start, start + length))
    changed = [i for i in range(common) if old[i] != new[i]]
    unexpected = [i for i in changed if i not in allowed]
    info['diff'] = dict(bytes_changed_in_common=len(changed),
                        unexpected=len(unexpected),
                        first_unexpected=['%#x' % i for i in unexpected[:16]],
                        appended=len(new) - len(old))
    if unexpected:
        problems.append('%d bytes antigos mudaram fora dos campos conhecidos'
                        % len(unexpected))

    # --- estrutura das duas arvores ----------------------------------------
    for kind in (9, 10):
        leaves, refs = check_structure(cand, kind, problems, info,
                                       note_only_headers=(kind == 9))
        check_geometry(cand, kind, problems, info)
        check_containment(cand, kind, leaves, refs, problems, info)

    # --- forma vs varejo ----------------------------------------------------
    v10, p10 = cand.geometry(n10)
    horiz = sum(1 for (n, a, vi, nb) in p10 if n[1] >= 0.999)
    info['shape'] = dict(up_facing_pct=round(100.0 * horiz / len(p10), 2),
                         quads=sum(1 for (n, a, vi, nb) in p10 if len(vi) == 4),
                         tris=sum(1 for (n, a, vi, nb) in p10 if len(vi) == 3))
    if horiz != len(p10):
        problems.append('%d faces do type10 nao sao horizontais viradas para cima; '
                        'nas quatro cidades de varejo sao 604 de 604'
                        % (len(p10) - horiz))

    # --- seguranca ----------------------------------------------------------
    safety_vs_type9(donor, cand, problems, info, args.band, args.sink,
                    args.samples, args.tol, args.near)

    info['problems'] = problems
    info['verdict'] = 'PASS' if not problems else 'FAIL'

    print('doador    %s  %d bytes' % (info['donor']['sha256'][:16], info['donor']['size']))
    print('candidato %s  %d bytes' % (info['candidate']['sha256'][:16], info['candidate']['size']))
    print()
    c = info['contract']
    print('contrato 2000/2000 : %d polys (memset %d B), %d verts (memset %d B), '
          'buffer %d B -> estouro %d/%d'
          % (c['polys'], c['poly_memset'], c['verts'], c['vert_memset'],
             c['buffer_bytes'], c['poly_overflow'], c['vert_overflow']))
    print('type9 identico     : %s' % info['type9_identical'])
    print('diff               : %d bytes antigos mudados (%d inesperados), %d anexados'
          % (info['diff']['bytes_changed_in_common'], info['diff']['unexpected'],
             info['diff']['appended']))
    for kind in (9, 10):
        t = info['t%d' % kind]
        print('type%-2d             : %d verts, %d polys, %d refs, %d folhas, '
              'depth %d, dup %.2fx, %d arestas boundary'
              % (kind, t['verts'], t['polys'], t['refs'], t['leaves'], t['depth'],
                 t['duplication'], t['boundary_edges']))
    print('forma type10       : %.1f%% horizontais p/ cima, %d quads, %d tris'
          % (info['shape']['up_facing_pct'], info['shape']['quads'], info['shape']['tris']))
    s = info['safety']
    print('seguranca          : %d amostras; enterradas %d (<=%.2f u), fundas %d '
          '(%.2f%%, rampa), fresta do type9 %d (%.2f%%), EXPOSTAS %d (%.2f%%)'
          % (s['samples'], s['buried'], s['allowed_gap'], s['deeply_buried'],
             s['deep_pct'], s['seam'], s['seam_pct'], s['exposed'], s['exposed_pct']))
    for kind in (9, 10):
        t = info['t%d' % kind]
        if t['blocks_without_array_header']:
            print('  nota: type%d tem %d de %d vetores de filhos SEM o cabecalho de '
                  'array de 16 bytes que as quatro cidades de varejo tem%s'
                  % (kind, t['blocks_without_array_header'], t['blocks'],
                     ' (herdado do doador, type9 identico)' if kind == 9 else ''))
    print()
    if problems:
        print('VEREDITO: FAIL')
        for p in problems:
            print('  - %s' % p)
    else:
        print('VEREDITO: PASS')
    if args.json:
        with open(args.json, 'w', encoding='utf-8') as stream:
            json.dump(info, stream, indent=2, ensure_ascii=False)
            stream.write('\n')
    return 0 if not problems else 1


if __name__ == '__main__':
    sys.exit(main())
