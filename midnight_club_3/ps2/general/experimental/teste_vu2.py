# -*- coding: utf-8 -*-
"""Reconstroi o mesh E a cadeia de `mesh+0x14`, que e POR BLOCO.

Historico: com o double buffer da VU1 corrigido, tirar bloco passou a funcionar
(10 e 11 blocos passam) mas ACRESCENTAR continuava travando (12 trava). O
motivo apareceu no relocador `sub_2A9D18`:

    mesh+0x14 -> array de `mesh+0x0A` ponteiros (slots)
      cada slot -> ngrp entradas de 8 bytes:  [ptrA][ptrB]
         ptrA -> [u32 count][u32 vertices por bloco] ... e os payloads logo apos
         ptrB -> array de `count` ponteiros, um por bloco

Medido no atlanta: **6893 de 6893 entradas tem `count` igual a quantidade de
blocos daquele grupo** -- 100%. E o payload de cada bloco e **1 byte por
vertice** (bloco de 48 verts -> 48 bytes; de 4 verts -> 4 bytes e o resto zero),
tudo alinhado em 16.

Eu reaproveitava a tabela original inteira. Com menos blocos sobrava entrada e
nada quebrava; com mais, o jogo indexava alem do fim -- exatamente 10 passa,
11 passa, 12 trava.

Curiosidade que confirma a leitura: os "tres ponteiros soltos" que eu tinha
achado em `modelo+0x64` sao o `ptrB` do grupo 2 do slot 0, morando na folga do
proprio objeto do modelo.

    python teste_vu2.py --modo fiel     11 blocos (controle)
    python teste_vu2.py --modo split2   12 blocos
    python teste_vu2.py --modo clone    12 blocos
    python teste_vu2.py --modo menos    10 blocos
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import struct
import importlib.util as _iu
_SP = _iu.spec_from_file_location(
    'mc3_saida', os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              '..', 'mc3_saida.py'))
_saida = _iu.module_from_spec(_SP)
_SP.loader.exec_module(_saida)


HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('conv', _saida.caminho( 'mc2_to_mc3.py'))
conv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conv)

SRC = os.path.join(os.environ.get('MC3_CLEAN_ASSETS', ''), 'ASSETS/resources/city/atlanta_midnight_clear.pck')
ALVO = 'a_inst_low_ghto_06x'
MESH_TAG = 0x007A1E18


def pad16(b, ch=0xCD):
    return b + bytes([ch]) * ((16 - len(b) % 16) % 16)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--modo', choices=['fiel', 'split2', 'clone', 'menos'], default='split2')
    a = ap.parse_args()

    d = bytearray(open(SRC, 'rb').read())
    base = struct.unpack_from('<I', d, 0)[0] - 0x80
    F = lambda v: v - base
    V = lambda o: o + base
    U = lambda o: struct.unpack_from('<I', d, o)[0]

    for o in range(0x80, len(d) - 0x80, 4):
        if U(o) == 0x7A0090 and bytes(d[o + 0x48:o + 0x70]).split(b'\0')[0] == ALVO.encode():
            vt = o
            break
    velho = F(U(vt + 0x14))
    ngrp, nslot = struct.unpack_from('<HH', d, velho + 8)
    f18, f1c = U(velho + 0x18), U(velho + 0x1C)
    matf = F(U(velho + 0x0C))
    materiais = [struct.unpack_from('<H', d, matf + 2 * i)[0] for i in range(ngrp)]
    g = F(U(velho + 0x10))
    t14 = F(U(velho + 0x14))

    # ---- le os blocos e, junto, o payload por bloco de cada slot ----
    grupos = []
    for k in range(ngrp):
        p, c, _ = struct.unpack_from('<IHH', d, g + 8 * k)
        lf = F(p)
        itens = []
        for j in range(c):
            bp, qw, nv = struct.unpack_from('<IHH', d, lf + 8 * j)
            blk = F(bp)
            sc = struct.unpack_from('<f', d, blk + 4)[0]
            pos = [tuple(x * sc for x in struct.unpack_from('<hhh', d, blk + 0x10 + 6 * i))
                   for i in range(nv)]
            u0 = blk + 0x10 + 6 * nv
            while u0 % 4:
                u0 += 1
            uv = [tuple(x / 4096.0 for x in struct.unpack_from('<hh', d, u0 + 4 + 4 * i))
                  for i in range(nv)]
            itens.append(dict(nv=nv, pos=pos, uv=uv, sc=sc, extra=[]))
        grupos.append(itens)

    for s in range(nslot):
        tab = F(U(t14 + 4 * s))
        for k in range(ngrp):
            pa, pb = struct.unpack_from('<II', d, tab + 8 * k)
            n = U(F(pa))
            assert n == len(grupos[k]), 'slot %d grupo %d: %d != %d' % (s, k, n, len(grupos[k]))
            for j in range(n):
                q = F(U(F(pb) + 4 * j))
                nv = grupos[k][j]['nv']
                grupos[k][j]['extra'].append(bytes(d[q:q + nv]))   # 1 byte por vertice

    # ---------------------------- a mexida ----------------------------
    gi4 = ji4 = gi48 = ji48 = None
    for gi, gr in enumerate(grupos):
        for ji, it in enumerate(gr):
            if it['nv'] == 4 and gi4 is None:
                gi4, ji4 = gi, ji
            if it['nv'] == 48 and gi48 is None:
                gi48, ji48 = gi, ji

    if a.modo == 'clone':
        grupos[gi4].insert(ji4 + 1, dict(grupos[gi4][ji4]))
    elif a.modo == 'menos':
        grupos[gi4].pop(ji4)
    elif a.modo == 'split2':
        big = grupos[gi48][ji48]
        n = big['nv']
        passo = ((n // 2) + 1) // 2 * 2
        ped, s = [], 0
        while s < n - 2:
            fim = s + passo + 2
            if fim - s >= 3:
                ped.append(dict(pos=big['pos'][s:fim], uv=big['uv'][s:fim], sc=big['sc'],
                                nv=len(big['pos'][s:fim]),
                                # o payload e por vertice, entao fatia igual
                                extra=[e[s:fim] for e in big['extra']]))
            s += passo
        grupos[gi48][ji48:ji48 + 1] = ped

    # ------------------------- monta tudo novo -------------------------
    while len(d) % 16:
        d.append(0xCD)
    mat_off = len(d)
    mesh_off = mat_off + 2 * ngrp
    ajuste = (16 - mesh_off % 16) % 16
    mat_off += ajuste
    mesh_off = mat_off + 2 * ngrp
    gtab = mesh_off + 0x20 + 16
    corrente = gtab + 8 * ngrp

    regioes, ponteiros = [], []
    for gr in grupos:
        # o buffer da VU1 vem da POSICAO na lista, nunca do bloco de origem
        blobs = [conv.make_block(it['pos'], it['uv'], it['sc'], j % 2 == 1)
                 for j, it in enumerate(gr)]
        lista_off = corrente + 16
        blocos_off = lista_off + len(pad16(b'\x00' * (8 * len(gr))))
        ent, pos = bytearray(), blocos_off
        for it, blob in zip(gr, blobs):
            ent += struct.pack('<IHH', V(pos), len(blob) // 16, it['nv'])
            pos += len(blob)
        regioes.append(pad16(struct.pack('<I', len(gr))) + pad16(bytes(ent)) + b''.join(blobs))
        ponteiros.append((V(lista_off), len(gr)))
        corrente += len(regioes[-1])

    # a cadeia de mesh+0x14, reconstruida: [array de slots][por slot: tabela,
    # depois por grupo o ptrA com os payloads colados e o ptrB]
    t14_off = corrente
    corrente += len(pad16(b'\x00' * (4 * nslot)))
    slots, cadeia = [], bytearray()
    for s in range(nslot):
        slots.append(V(corrente + len(cadeia)))
        tabela = bytearray()
        corpo = bytearray()
        depois = corrente + len(cadeia) + len(pad16(b'\x00' * (8 * ngrp)))
        for gr in grupos:
            a_off = depois + len(corpo)
            cab = pad16(struct.pack('<I', len(gr)) + b''.join(
                struct.pack('<I', it['nv']) for it in gr), 0x00)
            corpo += cab
            alvos = []
            for j, it in enumerate(gr):
                alvos.append(V(depois + len(corpo)))
                corpo += pad16(it['extra'][s], 0x00)
            b_off = depois + len(corpo)
            corpo += pad16(b''.join(struct.pack('<I', x) for x in alvos), 0x00)
            tabela += struct.pack('<II', V(a_off), V(b_off))
        cadeia += pad16(bytes(tabela)) + bytes(corpo)
    corrente += len(cadeia)

    saida = bytearray(bytes([0xCD]) * ajuste)
    for m in materiais:
        saida += struct.pack('<H', m)
    m = bytearray(0x20)
    struct.pack_into('<I', m, 0x00, MESH_TAG)
    struct.pack_into('<H', m, 0x08, ngrp)
    struct.pack_into('<H', m, 0x0A, nslot)
    struct.pack_into('<I', m, 0x0C, V(mat_off))
    struct.pack_into('<I', m, 0x10, V(gtab))
    struct.pack_into('<I', m, 0x14, V(t14_off))       # <<< agora e a cadeia nova
    struct.pack_into('<I', m, 0x18, f18)
    struct.pack_into('<I', m, 0x1C, f1c)
    saida += bytes(m) + pad16(struct.pack('<I', ngrp))
    for p, n in ponteiros:
        saida += struct.pack('<IHH', p, n, 0xCDCD)
    saida += b''.join(regioes)
    saida += pad16(b''.join(struct.pack('<I', x) for x in slots), 0x00)
    saida += bytes(cadeia)

    d.extend(saida)
    while len(d) % 16:
        d.append(0xCD)
    struct.pack_into('<I', d, 0x0C, len(d) - 0x80)
    struct.pack_into('<I', d, vt + 0x14, V(mesh_off))

    # ---- confere a si mesmo: reabre o que escreveu e valida a cadeia ----
    U2 = lambda o: struct.unpack_from('<I', d, o)[0]
    mesh2 = F(U2(vt + 0x14))
    ng2, ns2 = struct.unpack_from('<HH', d, mesh2 + 8)
    g2, t2 = F(U2(mesh2 + 0x10)), F(U2(mesh2 + 0x14))
    blk2 = [struct.unpack_from('<IHH', d, g2 + 8 * k)[1] for k in range(ng2)]
    erros = 0
    for s in range(ns2):
        tab = F(U2(t2 + 4 * s))
        for k in range(ng2):
            pa, pb = struct.unpack_from('<II', d, tab + 8 * k)
            if U2(F(pa)) != blk2[k]:
                erros += 1
            for j in range(blk2[k]):
                nv = struct.unpack_from('<IHH', d, F(U2(g2 + 8 * k)) + 8 * j)[2]
                if U2(F(pa) + 4 + 4 * j) != nv:
                    erros += 1

    out = _saida.caminho( 'teste_vu2_%s_atlanta_midnight_clear.pck' % a.modo)
    open(out, 'wb').write(bytes(d))
    orig = open(SRC, 'rb').read()
    print('%-7s %2d blocos %s | %d slots reconstruidos | %s'
          % (a.modo, sum(len(x) for x in grupos), [len(x) for x in grupos], nslot,
             'cadeia OK' if not erros else '%d ERROS' % erros))
    print('        %s  (%d bytes alterados no original)'
          % (os.path.basename(out), sum(1 for x, y in zip(orig, d) if x != y)))


if __name__ == '__main__':
    main()
