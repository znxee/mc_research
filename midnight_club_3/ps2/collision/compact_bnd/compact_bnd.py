#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reescreve um ``*_bnd.pck`` em layout compacto, sem mudar nada do conteudo.

POR QUE
=======

O fluxo de construcao deste projeto e incremental: cada rebuild do type9
ANEXA a geometria nova no fim do arquivo e deixa a antiga orfa. Ninguem
apaga nada, entao o arquivo so cresce e a maior parte dele vira lixo que o
jogo carrega para a RAM e nunca le.

Medido: o `losangeles_bnd.pck` de 08/09 ja era **42,4 % espaco morto**, e os
candidatos v17..v20 chegaram a **55 %**. A Fork City MODS mediu o efeito disso
no console e o resultado foi duro: o freeroam parou de entrar: sobravam 2,4 MB
livres no total mas o MAIOR BLOCO CONTIGUO era de 0,48 MB, e o bnd de 3,60 MB
nao cabia. Loading infinito, sem excecao e sem mensagem.

Este compactador ataca exatamente isso e nao custa um poligono.

COMO
====

NAO ha varredura atras de coisa que "parece ponteiro" - isso e proibido neste
projeto e com razao. O arquivo e REMONTADO a partir das estruturas que o
`mc3_bound.py` sabe ler, em ordem canonica, e cada ponteiro e reescrito porque
se sabe exatamente onde ele esta:

    header      +0x0C   tamanho do corpo
    mcPhysics   +0x0C   -> mcLevelBounds
    mcLevelBnd  +0x00   -> phInst(type10)   +0x04 -> phInst(type9)
                +0x10   -> CurveMgr
    phInst      +0x04   -> phArchetype
    phArchetype +0x0C   -> phBound
    phBound     +0x68   -> vertices         +0x6C -> poligonos
                +0x70   -> tabela de material
                +0x78   -> polytree (type10)  ou  +0x94 (type9)
                +0x7C   valor da raiz (type10)
    polytree    +0x00   -> slot da raiz     +0x04 -> phBound dono
                +0x14   -> lista de indices
    bloco       cada slot: ponteiro para outro bloco, ou folha (bit 0 = 1)

A tabela de material sai com os 24 slots que o campo +0x74 declara: as entradas
vivas e `0xCDCDCDCD` no resto, que e a forma do varejo.

O que nao e estrutura conhecida (o `CurveMgr`) e copiado byte a byte, sem
interpretacao.

VERIFICACAO
===========

Compactar e uma operacao de risco alto e valor alto, entao ela se prova sozinha:
depois de escrever, o arquivo novo e REPARSEADO e comparado com o original em
geometria (vertices e poligonos byte a byte), arvore (folhas, refs, ordem),
material, AABB e contagens. Qualquer diferenca aborta e o arquivo nao e usado.

    python compact_bnd.py --in gordo.pck --out magro.pck
"""

import argparse
import hashlib
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mc3_bound as MB

MAT_SLOTS = 24          # o que o campo +0x74 declara nas quatro cidades de varejo
PAD = 0xCD


def tree_parts(b, kind):
    """Todo objeto de uma arvore, ja lido, pronto para ser reemitido."""
    node = b.trees[kind]
    fan = 8 if kind == 9 else 4
    nv, npoly = b.u32(node + 0x4C), b.u32(node + 0x50)
    pay = b.off(b.u32(node + (0x94 if kind == 9 else 0x78)))
    root_slot, idx_off, nref = b.payload(node, kind)

    # blocos, na ordem em que a arvore os alcanca, para o arquivo novo ficar
    # com localidade parecida com a do original
    order, seen, stack = [], set(), [root_slot]
    while stack:
        slot = stack.pop()
        if slot in seen:
            continue
        seen.add(slot)
        v = b.u32(slot)
        if v & 1 or not b.valid(v):
            continue
        base = b.off(v)
        if base not in order:
            order.append(base)
        stack.extend(base + 4 * i for i in range(fan))

    return dict(
        kind=kind, fan=fan, node=node, nverts=nv, npolys=npoly, pay=pay,
        root_slot=root_slot, nrefs=nref,
        inst=b.off(b.u32(b.off(b.u32(0x8C)) + (0x00 if kind == 10 else 0x04))),
        verts=b.data[b.off(b.u32(node + 0x68)):b.off(b.u32(node + 0x68)) + 12 * nv],
        polys=b.data[b.off(b.u32(node + 0x6C)):b.off(b.u32(node + 0x6C)) + 32 * npoly],
        mats=b.materials(node),
        idx=b.data[idx_off:idx_off + 2 * nref],
        blocks=order,
    )


def weld_vertices(t):
    """Funde vertices que estao EXATAMENTE na mesma posicao.

    So duplicata exata, e isso e o que torna a operacao segura: dois vertices
    distintos de um mesmo poligono nunca ocupam a mesma posicao a menos que o
    poligono ja seja degenerado, entao a fusao nao pode criar degenerado - e
    dispensa tolerancia e o risco que viria junto. O ganho vem do fluxo: a
    malha global do MC2 e as superficies instanciadas sao deduplicadas em
    passes separados, e onde uma encosta na outra o mesmo ponto entra duas
    vezes. Medido no v21: 3.726 vertices repetidos, 44 KB.
    """
    nv, raw = t['nverts'], t['verts']
    pos = [raw[12*i:12*i+12] for i in range(nv)]
    first, remap, keep = {}, [0]*nv, []
    for i, q in enumerate(pos):
        j = first.get(q)
        if j is None:
            first[q] = len(keep)
            remap[i] = len(keep)
            keep.append(q)
        else:
            remap[i] = j
    if len(keep) == nv:
        return 0
    polys = bytearray(t['polys'])
    for k in range(t['npolys']):
        o = 32*k + 16
        vi = list(struct.unpack_from('<4H', polys, o))
        tri = vi[3] == 0
        n = 3 if tri else 4
        new_vi = [remap[x] for x in vi[:n]]
        if len(set(new_vi)) != n:
            return -1                       # viraria degenerado: aborta tudo
        if not tri:
            # O jogo distingue quad de triangulo por v3 == 0. Se o remap jogar o
            # vertice 0 na quarta posicao, o quad passa a ser lido como
            # triangulo e uma das metades da face some. Girar e ciclico, entao
            # preserva o poligono e o sentido; um quad tem 4 indices distintos,
            # logo no maximo um deles e 0 e a rotacao sempre acha posicao.
            # A primeira versao nao fazia isso e a verificacao reprovou - foi
            # ela que achou, nao o jogo.
            while new_vi[3] == 0:
                new_vi = new_vi[1:] + new_vi[:1]
        struct.pack_into('<4H', polys, o, *(new_vi + ([0] if tri else [])))
    t['polys'] = bytes(polys)
    t['verts'] = b''.join(keep)
    saved = nv - len(keep)
    t['nverts'] = len(keep)
    return saved


def compact(src_path, dst_path, verbose=True, weld=False):
    b = MB.Bound(src_path)
    base_field = b.u32(0x00)
    lb = b.off(b.u32(0x8C))
    curve = b.u32(lb + 0x10)
    curve_off = b.off(curve) if curve and b.valid(curve) else None

    parts = {k: tree_parts(b, k) for k in sorted(b.trees)}
    for k, t in parts.items():
        t['arch'] = b.off(b.u32(t['inst'] + 4))
    welded = {}
    if weld:
        for k, t in parts.items():
            n = weld_vertices(t)
            if n < 0:
                raise SystemExit('t%d: fundir vertices criaria poligono '
                                 'degenerado; abortado sem escrever' % k)
            welded[k] = n

    # ---- pass 1: onde cada coisa vai ficar --------------------------------
    layout, cur = {}, 0

    def place(name, size, align=16):
        nonlocal cur
        if cur % align:
            cur += align - (cur % align)
        layout[name] = cur
        cur += size
        return layout[name]

    place('header', 0x80, 1)
    place('mcPhysics', 0x18, 16)
    place('mcLevelBounds', 0x14, 16)
    if curve_off is not None:
        place('curve', 0x20, 16)
    for k in (10, 9):
        if k not in parts:
            continue
        t = parts[k]
        place('inst%d' % k, 0x40, 16)
        place('arch%d' % k, 0x20, 16)
        place('node%d' % k, 0xA0, 16)
        place('verts%d' % k, len(t['verts']), 16)
        place('polys%d' % k, len(t['polys']), 16)
        place('mats%d' % k, 4 * MAT_SLOTS, 16)
        place('pay%d' % k, 0x40, 16)
        place('idx%d' % k, len(t['idx']), 16)
        for n, _blk in enumerate(t['blocks']):
            place('blk%d_%d' % (k, n), 16 + 4 * t['fan'], 16)
            layout['blk%d_%d' % (k, n)] += 16      # o ponteiro aponta para os slots
        place('root%d' % k, 4, 16)
    total = cur if cur % 16 == 0 else cur + 16 - (cur % 16)

    data = bytearray(b'\xCD' * total)

    def va(name):
        return layout[name] + base_field - 0x80

    def copy(name, src_off, size):
        data[layout[name]:layout[name] + size] = b.data[src_off:src_off + size]

    # ---- pass 2: escrever -------------------------------------------------
    copy('header', 0, 0x80)
    struct.pack_into('<I', data, 0x0C, total - 0x80)
    copy('mcPhysics', 0x80, 0x18)
    struct.pack_into('<I', data, layout['mcPhysics'] + 0x0C, va('mcLevelBounds'))
    copy('mcLevelBounds', lb, 0x14)
    if curve_off is not None:
        copy('curve', curve_off, 0x20)
        struct.pack_into('<I', data, layout['mcLevelBounds'] + 0x10, va('curve'))
    for slot, k in ((0x00, 10), (0x04, 9)):
        if k in parts:
            struct.pack_into('<I', data, layout['mcLevelBounds'] + slot, va('inst%d' % k))

    for k in (10, 9):
        if k not in parts:
            continue
        t = parts[k]
        copy('inst%d' % k, t['inst'], 0x40)
        struct.pack_into('<I', data, layout['inst%d' % k] + 0x04, va('arch%d' % k))
        copy('arch%d' % k, t['arch'], 0x20)
        struct.pack_into('<I', data, layout['arch%d' % k] + 0x0C, va('node%d' % k))
        copy('node%d' % k, t['node'], 0xA0)
        n = layout['node%d' % k]
        data[layout['verts%d' % k]:layout['verts%d' % k] + len(t['verts'])] = t['verts']
        data[layout['polys%d' % k]:layout['polys%d' % k] + len(t['polys'])] = t['polys']
        data[layout['idx%d' % k]:layout['idx%d' % k] + len(t['idx'])] = t['idx']
        for i, gid in enumerate(t['mats']):
            struct.pack_into('<I', data, layout['mats%d' % k] + 4 * i, gid)
        struct.pack_into('<I', data, n + 0x4C, t['nverts'])
        struct.pack_into('<I', data, n + 0x68, va('verts%d' % k))
        struct.pack_into('<I', data, n + 0x6C, va('polys%d' % k))
        struct.pack_into('<I', data, n + 0x70, va('mats%d' % k))
        struct.pack_into('<I', data, n + 0x74, MAT_SLOTS)
        struct.pack_into('<I', data, n + (0x94 if k == 9 else 0x78), va('pay%d' % k))

        copy('pay%d' % k, t['pay'], 0x40)
        p = layout['pay%d' % k]
        struct.pack_into('<I', data, p + 0x00, va('root%d' % k))
        struct.pack_into('<I', data, p + 0x04, va('node%d' % k))
        struct.pack_into('<I', data, p + 0x0C, t['nverts'])
        struct.pack_into('<I', data, p + 0x14, va('idx%d' % k))

        old2new = {old: va('blk%d_%d' % (k, i)) for i, old in enumerate(t['blocks'])}

        def slot_value(v):
            """Folha continua igual; ponteiro de bloco vira o endereco novo."""
            if v & 1 or not b.valid(v):
                return v
            return old2new[b.off(v)]

        for i, old in enumerate(t['blocks']):
            dst = layout['blk%d_%d' % (k, i)]
            struct.pack_into('<I', data, dst - 16, t['fan'])   # cabecalho de array
            for c in range(t['fan']):
                struct.pack_into('<I', data, dst + 4 * c,
                                 slot_value(b.u32(old + 4 * c)))
        rootv = slot_value(b.u32(t['root_slot']))
        struct.pack_into('<I', data, layout['root%d' % k], rootv)
        if k == 10:
            struct.pack_into('<I', data, n + 0x7C, rootv)

    with open(dst_path, 'wb') as s:
        s.write(data)

    # ---- verificacao: o novo tem de ler igual ao velho ---------------------
    c = MB.Bound(dst_path)
    problems = []
    if sorted(c.trees) != sorted(b.trees):
        problems.append('conjunto de arvores mudou')
    for k in sorted(b.trees):
        nb, nc = b.trees[k], c.trees[k]
        conf = ((('AABB', 0x08, 0x38),) if weld else
                (('AABB', 0x08, 0x38), ('contagens', 0x4C, 8)))
        for label, off, size in conf:
            if b.data[nb+off:nb+off+size] != c.data[nc+off:nc+off+size]:
                problems.append('t%d %s diferente' % (k, label))
        vb, pb = b.u32(nb+0x4C), b.u32(nb+0x50)
        if weld:
            # o array de vertices muda de proposito; o que tem de ficar igual e
            # a POSICAO de cada canto de cada poligono, e a area/material
            gv, gp = b.geometry(nb)
            hv, hp = c.geometry(nc)
            if len(gp) != len(hp):
                problems.append('t%d contagem de poligonos mudou' % k)
            else:
                for (n1, a1, i1, _x), (n2, a2, i2, _y) in zip(gp, hp):
                    p1 = [gv[i] for i in i1]
                    p2 = [hv[i] for i in i2]
                    # o quad pode sair GIRADO, porque v3 nao pode ser 0; giro
                    # ciclico e o mesmo poligono com o mesmo sentido, entao a
                    # comparacao tem de ser ciclica e nao posicional
                    same = len(p1) == len(p2) and any(
                        p1 == p2[r:] + p2[:r] for r in range(len(p2)))
                    if not same or struct.pack('<f', a1) != struct.pack('<f', a2):
                        problems.append('t%d canto/area/material mudou' % k)
                        break
        else:
            if (b.data[b.off(b.u32(nb+0x68)):b.off(b.u32(nb+0x68))+12*vb]
                    != c.data[c.off(c.u32(nc+0x68)):c.off(c.u32(nc+0x68))+12*vb]):
                problems.append('t%d vertices diferentes' % k)
            if (b.data[b.off(b.u32(nb+0x6C)):b.off(b.u32(nb+0x6C))+32*pb]
                    != c.data[c.off(c.u32(nc+0x6C)):c.off(c.u32(nc+0x6C))+32*pb]):
                problems.append('t%d poligonos diferentes' % k)
        if b.materials(nb) != c.materials(nc):
            problems.append('t%d paleta diferente' % k)
        rb, ib, nrb = b.payload(nb, k)
        rc, ic, nrc = c.payload(nc, k)
        if nrb != nrc or b.data[ib:ib+2*nrb] != c.data[ic:ic+2*nrc]:
            problems.append('t%d lista de indices diferente' % k)
        lb_ = sorted(b.leaves(nb, k)); lc_ = sorted(c.leaves(nc, k))
        if [(s, n) for s, n, _ in lb_] != [(s, n) for s, n, _ in lc_]:
            problems.append('t%d folhas diferentes (%d vs %d)' % (k, len(lb_), len(lc_)))
        if k == 10 and c.u32(nc+0x7C) != c.u32(rc):
            problems.append('t10 node+0x7C != raiz')

    src = len(b.data)
    if verbose:
        print('origem   : %s  %d bytes' % (os.path.basename(src_path), src))
        print('compacto : %s  %d bytes' % (os.path.basename(dst_path), total))
        print('reducao  : %d bytes (%.1f%%)' % (src - total, 100.0*(src-total)/src))
        for k in sorted(b.trees):
            t = parts[k]
            print('  t%-2d %6d verts, %6d polys, %6d refs, %4d blocos%s'
                  % (k, t['nverts'], t['npolys'], t['nrefs'], len(t['blocks']),
                     ('  (%d fundidos)' % welded[k]) if welded.get(k) else ''))
        print('SHA256   : %s' % hashlib.sha256(bytes(data)).hexdigest().upper())
        if problems:
            print('VERIFICACAO: FALHOU')
            for p in problems:
                print('  - %s' % p)
        else:
            print('VERIFICACAO: OK - geometria, arvore, indices, paleta e AABB identicos')
    return total, problems


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument('--in', dest='src', required=True)
    ap.add_argument('--out', dest='dst', required=True)
    ap.add_argument('--weld', action='store_true',
                    help='funde vertices em posicao exatamente igual')
    a = ap.parse_args()
    _size, problems = compact(a.src, a.dst, weld=a.weld)
    if problems:
        os.remove(a.dst)
        print('arquivo removido; nada foi entregue')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
