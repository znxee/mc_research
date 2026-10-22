# -*- coding: utf-8 -*-
"""Mesma construcao do zero do `teste_mesh_novo.py`, mas com o DOUBLE BUFFER
DA VU1 corrigido.

O que estava errado em todos os testes anteriores: os quatro campos do bloco
que eu tratava como "paridade da tira" sao endereco de memoria da VU1, e o
retail alterna as duas metades A,B,A,B... conforme a POSICAO DO BLOCO NA LISTA
DO GRUPO (785 dos 786 grupos do atlanta). Eu copiava o valor do bloco de
origem; quando a lista mudava de tamanho a alternancia quebrava e o DMA
sobrescrevia a metade que a VU ainda estava rodando.

Aqui todo bloco e re-encodado com `odd = (j % 2 == 1)`.

    python teste_vu.py --modo fiel     11 blocos (controle, tem que continuar passando)
    python teste_vu.py --modo split2   12 blocos (o que travava)
    python teste_vu.py --modo clone    12 blocos, o extra e copia do de 4 verts
    python teste_vu.py --modo menos    10 blocos
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
    va = struct.unpack_from('<I', d, 0)[0]
    base = va - 0x80
    F = lambda v: v - base
    V = lambda o: o + base
    U = lambda o: struct.unpack_from('<I', d, o)[0]

    for o in range(0x80, len(d) - 0x80, 4):
        if U(o) == 0x7A0090 and bytes(d[o + 0x48:o + 0x70]).split(b'\0')[0] == ALVO.encode():
            vt = o
            break
    velho = F(U(vt + 0x14))
    ngrp = struct.unpack_from('<H', d, velho + 8)[0]
    hi0a = struct.unpack_from('<H', d, velho + 0x0A)[0]
    f14, f18, f1c = U(velho + 0x14), U(velho + 0x18), U(velho + 0x1C)
    matf = F(U(velho + 0x0C))
    materiais = [struct.unpack_from('<H', d, matf + 2 * i)[0] for i in range(ngrp)]
    g = F(U(velho + 0x10))

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
            buf = struct.unpack_from('<H', d, blk + 0x0C)[0]
            itens.append(dict(nv=nv, pos=pos, uv=uv, sc=sc, buf=buf))
        itens_esperado = [256 if i % 2 == 0 else 551 for i in range(c)]
        assert [x['buf'] for x in itens] == itens_esperado, 'grupo %d fora da alternancia' % k
        grupos.append(itens)

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
            p2, u2 = big['pos'][s:s + passo + 2], big['uv'][s:s + passo + 2]
            if len(p2) >= 3:
                ped.append(dict(pos=p2, uv=u2, sc=big['sc'], nv=len(p2), buf=None))
            s += passo
        grupos[gi48][ji48:ji48 + 1] = ped

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
        # <<< a correcao: a metade do buffer vem do indice, nunca da origem >>>
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

    saida = bytearray(bytes([0xCD]) * ajuste)
    for m in materiais:
        saida += struct.pack('<H', m)
    m = bytearray(0x20)
    struct.pack_into('<I', m, 0x00, MESH_TAG)
    struct.pack_into('<H', m, 0x08, ngrp)
    struct.pack_into('<H', m, 0x0A, hi0a)
    struct.pack_into('<I', m, 0x0C, V(mat_off))
    struct.pack_into('<I', m, 0x10, V(gtab))
    struct.pack_into('<I', m, 0x14, f14)
    struct.pack_into('<I', m, 0x18, f18)
    struct.pack_into('<I', m, 0x1C, f1c)
    saida += bytes(m) + pad16(struct.pack('<I', ngrp))
    for p, n in ponteiros:
        saida += struct.pack('<IHH', p, n, 0xCDCD)
    saida += b''.join(regioes)

    d.extend(saida)
    while len(d) % 16:
        d.append(0xCD)
    struct.pack_into('<I', d, 0x0C, len(d) - 0x80)
    struct.pack_into('<I', d, vt + 0x14, V(mesh_off))

    out = _saida.caminho( 'teste_vu_%s_atlanta_midnight_clear.pck' % a.modo)
    open(out, 'wb').write(bytes(d))
    orig = open(SRC, 'rb').read()
    print('%-8s %2d blocos %s | buffers %s'
          % (a.modo, sum(len(x) for x in grupos), [len(x) for x in grupos],
             ['A' if j % 2 == 0 else 'B' for gr in grupos for j in range(len(gr))]))
    print('         %s  (%d bytes alterados no original)'
          % (os.path.basename(out), sum(1 for x, y in zip(orig, d) if x != y)))


if __name__ == '__main__':
    main()
