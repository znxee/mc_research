# -*- coding: utf-8 -*-
"""Bisseccao final: a contagem de blocos ou o conteudo dos blocos?

Reusa a construcao do zero do `teste_mesh_novo.py`, que JA PASSOU no jogo com
11 blocos. A unica diferenca entre as variantes e o que entra na lista.

O alvo `a_inst_low_ghto_06x` tem 11 blocos em 6 grupos:
    g0[40] g1[17] g2[48,46,4] g3[46,39] g4[44,47,15] g5[44]

    --modo clone   12 blocos, o extra e uma COPIA BYTE A BYTE do bloco de 4
                   verts (grupo 2). Nenhum make_block. Muda so a contagem.
    --modo troca   11 blocos: o de 48 verts vira 2 pedacos (make_block) e o de
                   4 verts sai. Contagem igual, conteudo novo.
    --modo menos   10 blocos: o de 4 verts sai. Nada de make_block.

Leitura:
    clone trava + troca passa -> e a contagem, nada mais.
    clone passa + troca trava -> e o make_block em pedaco de strip.
    menos trava                -> a contagem tem que bater com a original
                                  (alguem de fora guarda o numero).
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
    ap.add_argument('--modo', choices=['clone', 'troca', 'menos'], required=True)
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
    hi08 = struct.unpack_from('<H', d, velho + 0x0A)[0]
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
            odd = bytes(d[blk + 0x0C:blk + 0x0E]) == b'\x27\x02'
            itens.append(dict(bytes=bytes(d[blk:blk + qw * 16]), nv=nv,
                              pos=pos, uv=uv, odd=odd, sc=sc))
        grupos.append(itens)

    # ---- localiza o bloco de 4 verts e o de 48 verts (ambos no grupo 2) ----
    gi4 = ji4 = gi48 = ji48 = None
    for gi, gr in enumerate(grupos):
        for ji, it in enumerate(gr):
            if it['nv'] == 4 and gi4 is None:
                gi4, ji4 = gi, ji
            if it['nv'] == 48 and gi48 is None:
                gi48, ji48 = gi, ji
    assert gi4 is not None and gi48 is not None

    if a.modo == 'clone':
        it = grupos[gi4][ji4]
        grupos[gi4].insert(ji4 + 1, dict(it))          # copia byte a byte
        print('clone: duplicado o bloco de 4 verts do grupo %d' % gi4)
    elif a.modo == 'menos':
        grupos[gi4].pop(ji4)
        print('menos: removido o bloco de 4 verts do grupo %d' % gi4)
    else:  # troca
        big = grupos[gi48][ji48]
        n = big['nv']
        passo = ((n // 2) + 1) // 2 * 2                # par, mantem a paridade
        ped = []
        s = 0
        while s < n - 2:
            p2, u2 = big['pos'][s:s + passo + 2], big['uv'][s:s + passo + 2]
            if len(p2) >= 3:
                ped.append(dict(pos=p2, uv=u2, odd=big['odd'], sc=big['sc'],
                                nv=len(p2), bytes=None))
            s += passo
        grupos[gi48][ji48:ji48 + 1] = ped
        # tira o de 4 pra contagem voltar a 11
        for gi, gr in enumerate(grupos):
            for ji, it in enumerate(gr):
                if it['nv'] == 4 and it['bytes'] is not None:
                    gr.pop(ji)
                    break
            else:
                continue
            break
        print('troca: 48 verts -> %d pedacos, removido o de 4 verts' % len(ped))

    # ---------------- monta a regiao inteira, contigua ----------------
    while len(d) % 16:
        d.append(0xCD)
    reg = len(d)

    mat_bytes = b''.join(struct.pack('<H', m) for m in materiais)
    mat_off = reg
    mesh_off = mat_off + len(mat_bytes)
    ajuste = (16 - mesh_off % 16) % 16
    mat_off += ajuste
    mesh_off = mat_off + len(mat_bytes)

    gtab = mesh_off + 0x20 + 16
    corrente = gtab + 8 * ngrp

    regioes, ponteiros = [], []
    for gr in grupos:
        blobs = [it['bytes'] if it['bytes'] is not None
                 else conv.make_block(it['pos'], it['uv'], it['sc'], it['odd']) for it in gr]
        lista_off = corrente + 16
        blocos_off = lista_off + len(pad16(b'\x00' * (8 * len(gr))))
        ent = bytearray()
        pos = blocos_off
        for it, blob in zip(gr, blobs):
            ent += struct.pack('<IHH', V(pos), len(blob) // 16, it['nv'])
            pos += len(blob)
        corpo = pad16(struct.pack('<I', len(gr))) + pad16(bytes(ent)) + b''.join(blobs)
        regioes.append(corpo)
        ponteiros.append((V(lista_off), len(gr)))
        corrente += len(corpo)

    saida = bytearray()
    saida += bytes([0xCD]) * ajuste
    saida += mat_bytes
    m = bytearray(0x20)
    struct.pack_into('<I', m, 0x00, MESH_TAG)
    struct.pack_into('<H', m, 0x08, ngrp)
    struct.pack_into('<H', m, 0x0A, hi08)
    struct.pack_into('<I', m, 0x0C, V(mat_off))
    struct.pack_into('<I', m, 0x10, V(gtab))
    struct.pack_into('<I', m, 0x14, f14)
    struct.pack_into('<I', m, 0x18, f18)
    struct.pack_into('<I', m, 0x1C, f1c)
    saida += bytes(m)
    saida += pad16(struct.pack('<I', ngrp))
    for p, n in ponteiros:
        saida += struct.pack('<IHH', p, n, 0xCDCD)
    saida += b''.join(regioes)

    d.extend(saida)
    while len(d) % 16:
        d.append(0xCD)
    struct.pack_into('<I', d, 0x0C, len(d) - 0x80)
    struct.pack_into('<I', d, vt + 0x14, V(mesh_off))

    out = _saida.caminho( 'teste_%s_atlanta_midnight_clear.pck' % a.modo)
    open(out, 'wb').write(bytes(d))
    orig = open(SRC, 'rb').read()
    nb = sum(len(x) for x in grupos)
    print('   mesh novo @%#x | %d blocos em %d grupos | %s' % (mesh_off, nb, ngrp,
                                                               [len(x) for x in grupos]))
    print('   %s  (%d bytes alterados no original)'
          % (os.path.basename(out), sum(1 for x, y in zip(orig, d) if x != y)))


if __name__ == '__main__':
    main()
