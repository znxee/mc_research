#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Le o `.bnd` de texto do MC2 (`type: otgrid`) e devolve UMA malha global.

O otgrid e uma GRADE de celulas (CellDim x CellDim), cada uma com o seu proprio
bound de texto: `verts:`/`materials:`/`edges:`/`polys:` e depois as linhas
`v x y z`, os blocos `mtl <nome> { ... }`, `edge a b nx ny nz` e os poligonos
`tri v0 v1 v2 mtl e0 e1 e2` / `quad v0 v1 v2 v3 mtl e0 e1 e2 e3`.

Os vertices ja estao em coordenada de MUNDO nas 42 celulas de Los Angeles, entao
juntar e so concatenar deslocando o indice. As celulas vazias (`verts: 0`) sao
puladas.
"""
import re


def le_otgrid(caminho):
    L = open(caminho, encoding='latin1').read().splitlines()
    n = len(L)
    verts = []            # [(x,y,z)]
    polys = []            # [(indices, nome_do_material)]
    materiais = []        # nomes, na ordem global de aparicao
    cabecalho = {}
    i = 0
    # cabecalho do grid
    while i < n and not L[i].strip().startswith('verts:'):
        s = L[i].strip()
        if ':' in s:
            k, v = s.split(':', 1)
            cabecalho[k.strip()] = v.strip()
        i += 1

    while i < n:
        s = L[i].strip()
        if not s.startswith('verts:'):
            i += 1
            continue
        nv = int(s.split(':', 1)[1])
        base = len(verts)
        mtl_local = []          # nomes desta celula, na ordem
        i += 1
        # o bloco vai ate o proximo 'verts:'
        while i < n and not L[i].strip().startswith('verts:'):
            t = L[i].strip()
            if t.startswith('v '):
                p = t.split()
                verts.append((float(p[1]), float(p[2]), float(p[3])))
            elif t.startswith('mtl '):
                mtl_local.append(t.split()[1])
            elif t.startswith('tri ') or t.startswith('quad '):
                p = t.split()
                k = 3 if p[0] == 'tri' else 4
                vi = tuple(base + int(x) for x in p[1:1 + k])
                mi = int(p[1 + k])
                nome = mtl_local[mi] if 0 <= mi < len(mtl_local) else '?'
                polys.append((vi, nome))
            i += 1
        for m in mtl_local:
            if m not in materiais:
                materiais.append(m)
        if nv and len(verts) - base != nv:
            raise SystemExit('celula em %d: declarou %d verts, li %d'
                             % (i, nv, len(verts) - base))
    return verts, polys, materiais, cabecalho


if __name__ == '__main__':
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else \
        'output/mc2_losangeles/bound/losangeles.bnd'
    v, po, mt, cab = le_otgrid(p)
    print('cabecalho do grid:', cab)
    print('vertices: %d   poligonos: %d' % (len(v), len(po)))
    tri = sum(1 for vi, _ in po if len(vi) == 3)
    print('  triangulos %d   quads %d' % (tri, len(po) - tri))
    lo = [min(q[a] for q in v) for a in range(3)]
    hi = [max(q[a] for q in v) for a in range(3)]
    print('AABB  (%.0f %.0f %.0f) .. (%.0f %.0f %.0f)' % tuple(lo + hi))
    print('lados %.0f x %.0f x %.0f' % tuple(hi[a] - lo[a] for a in range(3)))
    print('materiais (%d): %s' % (len(mt), mt))
