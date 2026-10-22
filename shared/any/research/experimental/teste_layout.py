# -*- coding: utf-8 -*-
"""Reescreve o mesh com o LAYOUT do retail -- descoberto no mesh_psptops2 do ZNXee.

O conversor de veiculo (`mesh_psptops2_v1.1.py`, ZNXee / mc3rxx / offlbruno) ja
montava assim, e funciona no jogo ha tempo:

    add_padding(count_u32, 16, 0xCD) + lista_de_entradas + BLOCOS

ou seja, por grupo, tudo numa REGIAO CONTIGUA:

    [cabecalho de 16 B com a contagem]
    [N entradas de 8 B: ptr, u16 qwords, u16 vertices]
    [pad ate 16]
    [bloco 0][bloco 1]...[bloco N-1]   <- logo em seguida, colados

e o ponteiro guardado aponta 16 bytes depois do inicio (pulando o cabecalho) --
`offset - block_pointers_size + 16` no script dele.

Conferido byte a byte no atlanta: os blocos de cada grupo comecam 8 bytes depois
do fim da lista (padding pra 16) e ficam colados uns nos outros.

Eu vinha anexando bloco por bloco e a lista depois, tudo espalhado -- estrutura
"valida" mas com layout que o retail nunca usa. E a ultima diferenca que sobrou.

    python teste_layout.py                 # 11 blocos (controle)
    python teste_layout.py --split 2       # 12 blocos
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


def pad16(b, ch=0xCD):
    return b + bytes([ch]) * ((16 - len(b) % 16) % 16)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--split', type=int, default=0)
    ap.add_argument('--saida', default=None)
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
    mesh = F(U(vt + 0x14))
    ngrp = struct.unpack_from('<H', d, mesh + 8)[0]
    g = F(U(mesh + 0x10))

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
            itens.append(dict(bytes=bytes(d[blk:blk + qw * 16]), qw=qw, nv=nv,
                              pos=pos, uv=uv, odd=odd, sc=sc))
        grupos.append(itens)

    if a.split > 1:
        maior = max((it for gr in grupos for it in gr), key=lambda x: x['nv'])
        gi = next(i for i, gr in enumerate(grupos) if maior in gr)
        gr = grupos[gi]
        idx = gr.index(maior)
        n = maior['nv']
        passo = max(4, ((n + a.split - 1) // a.split + 1) // 2 * 2)
        pedacos = []
        s = 0
        while s < n - 2:
            p2, u2 = maior['pos'][s:s + passo + 2], maior['uv'][s:s + passo + 2]
            if len(p2) >= 3:
                pedacos.append(dict(pos=p2, uv=u2, odd=maior['odd'], sc=maior['sc'],
                                    nv=len(p2), bytes=None, qw=None))
            s += passo
        gr[idx:idx + 1] = pedacos
        print('bloco de %d vertices (grupo %d) -> %d pedacos' % (n, gi, len(pedacos)))

    # ---- monta cada grupo como UMA regiao contigua, no layout do retail ----
    while len(d) % 16:
        d.append(0xCD)

    regioes = []          # (offset da lista, bytes da regiao)
    for gr in grupos:
        blobs = []
        for it in gr:
            if it['bytes'] is not None:
                blobs.append(it['bytes'])
            else:
                blobs.append(conv.make_block(it['pos'], it['uv'], it['sc'], it['odd']))
        cab = pad16(struct.pack('<I', len(gr)))            # 16 B com a contagem
        lista_tam = len(pad16(b'\x00' * (8 * len(gr))))
        base_reg = len(d) + sum(len(x) for x in regioes)   # onde essa regiao cai
        lista_off = base_reg + 16
        blocos_off = lista_off + lista_tam
        entradas = bytearray()
        pos = blocos_off
        for it, blob in zip(gr, blobs):
            entradas += struct.pack('<IHH', V(pos), len(blob) // 16, it['nv'])
            pos += len(blob)
        regiao = cab + pad16(bytes(entradas)) + b''.join(blobs)
        regioes.append(regiao)

    tam_ate = 0
    ponteiros = []
    for gr, reg in zip(grupos, regioes):
        ponteiros.append((V(len(d) + tam_ate + 16), len(gr)))
        tam_ate += len(reg)
    for reg in regioes:
        d.extend(reg)

    # tabela de grupos, tambem com cabecalho
    while len(d) % 16:
        d.append(0xCD)
    tab_base = len(d)
    tab = bytearray()
    for p, n in ponteiros:
        tab += struct.pack('<IHH', p, n, 0xCDCD)
    d.extend(pad16(struct.pack('<I', ngrp)))
    tab_off = len(d)
    d.extend(pad16(bytes(tab)))
    struct.pack_into('<I', d, mesh + 0x10, V(tab_off))
    struct.pack_into('<I', d, 0x0C, len(d) - 0x80)

    out = a.saida or _saida.caminho( 'teste_layout%s_atlanta_midnight_clear.pck'
                                  % ('_split%d' % a.split if a.split > 1 else ''))
    open(out, 'wb').write(bytes(d))
    orig = open(SRC, 'rb').read()
    print('%d blocos em %d grupos | %s' % (sum(len(x) for x in grupos), ngrp, os.path.basename(out)))
    print('   %d bytes alterados na regiao original'
          % sum(1 for x, y in zip(orig, d) if x != y))


if __name__ == '__main__':
    main()
