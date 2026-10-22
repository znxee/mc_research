# -*- coding: utf-8 -*-
"""Bisseccao de variavel unica, partindo do estado que JA FUNCIONA.

O `teste_plumbing` passou: 11 blocos originais copiados, anexados, tabela
reconstruida. Dali em diante muda-se UMA coisa por vez:

  --nada       identico ao plumbing (controle: tem que passar)
  --reencoda   os mesmos 11 blocos, mas gerados pelo make_block
  --split N    parte o maior bloco em N pedacos -> 11+N-1 blocos

    python teste_minimo.py --reencoda
    python teste_minimo.py --split 2
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
ALVO = 'a_inst_low_ghto_06x'      # nao tem cor por vertice em nenhum bloco




def append_array(d, corpo, n, align=16):
    """Anexa um array COM O CABECALHO DE 16 BYTES que o jogo espera.

    Descoberto no construtor do mesh (`sub_2A8FA0` no ELF): ele aloca
    `n*8 + 16`, grava a CONTAGEM no inicio do buffer e guarda o ponteiro
    apontando 16 BYTES DEPOIS. Ou seja, `[ptr - 16]` e a contagem de
    elementos. Conferido no retail: 6/6 grupos e 6/6 listas de bloco do
    alvo. Eu nunca escrevia isso -- ficava 0xCDCDCDCD ali.
    """
    pad = 0xCD
    while len(d) % align:
        d.append(pad)
    d.extend(struct.pack("<I", n))
    d.extend(bytes([pad]) * 12)
    corpo_at = len(d)
    d.extend(corpo)
    while len(d) % align:
        d.append(pad)
    struct.pack_into("<I", d, 0x0C, len(d) - 0x80)
    return corpo_at



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--reencoda', action='store_true')
    ap.add_argument('--split', type=int, default=0)
    ap.add_argument('--espalhar', action='store_true',
                    help='parte um bloco em 3 grupos DIFERENTES: mesmo total, mesmo maximo por grupo')
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

    # --split: parte o maior bloco em N tiras (com sobreposicao de 2, preserva a tira)
    if a.split > 1:
        maior = max((it for gr in grupos for it in gr), key=lambda x: x['nv'])
        gi = next(i for i, gr in enumerate(grupos) if maior in gr)
        gr = grupos[gi]
        idx = gr.index(maior)
        n = maior['nv']
        passo = max(3, (n + a.split - 1) // a.split)
        pedacos = []
        s = 0
        while s < n - 2:
            p2, u2 = maior['pos'][s:s + passo + 2], maior['uv'][s:s + passo + 2]
            if len(p2) >= 3:
                pedacos.append(dict(pos=p2, uv=u2, odd=maior['odd'], sc=maior['sc'],
                                    nv=len(p2), bytes=None, qw=None))
            s += passo
        gr[idx:idx + 1] = pedacos
        print('bloco de %d vertices (grupo %d) partido em %d pedacos de ate %d'
              % (n, gi, len(pedacos), passo + 2))

    # --espalhar: chega no mesmo total de blocos SEM aumentar o maximo por grupo.
    # Separa "mais blocos no mesh" de "mais blocos num grupo".
    if a.espalhar:
        alvos = [i for i, gr in enumerate(grupos) if len(gr) == 1][:3]
        for gi in alvos:
            it = grupos[gi][0]
            n = it['nv']
            if n < 8:
                continue
            meio = (n // 2) + (n // 2) % 2          # ponto de corte PAR preserva a paridade
            a1 = dict(it, pos=it['pos'][:meio + 2], uv=it['uv'][:meio + 2],
                      nv=meio + 2, bytes=None, qw=None)
            a2 = dict(it, pos=it['pos'][meio:], uv=it['uv'][meio:],
                      nv=n - meio, bytes=None, qw=None)
            grupos[gi] = [a1, a2]
        print('grupos %s partidos em 2 -> contagens %s'
              % (alvos, [len(g) for g in grupos]))

    def append(blob, align=16):
        while len(d) % align:
            d.extend(b'\xCD')
        at = len(d)
        d.extend(blob)
        while len(d) % align:
            d.extend(b'\xCD')
        struct.pack_into('<I', d, 0x0C, len(d) - 0x80)
        return at

    tab = bytearray()
    nb = 0
    for gr in grupos:
        lb = bytearray()
        for it in gr:
            if it['bytes'] is not None and not a.reencoda:
                blob, qw, nv = it['bytes'], it['qw'], it['nv']
            else:
                blob = conv.make_block(it['pos'], it['uv'], it['sc'], it['odd'])
                qw, nv = len(blob) // 16, len(it['pos'])
            tab_at = append(blob)
            lb += struct.pack('<IHH', V(tab_at), qw, nv)
            nb += 1
        tab += struct.pack('<IHH', V(append_array(d, bytes(lb), len(gr))), len(gr), 0xCDCD)
    struct.pack_into('<I', d, mesh + 0x10,
                     V(append_array(d, bytes(tab), len(grupos))))

    sufixo = ('_reencoda' if a.reencoda else '') + ('_split%d' % a.split if a.split > 1 else '')
    out = a.saida or _saida.caminho( 'teste_minimo%s_atlanta_midnight_clear.pck' % sufixo)
    open(out, 'wb').write(bytes(d))
    orig = open(SRC, 'rb').read()
    print('%d blocos em %d grupos | %s' % (nb, len(grupos), os.path.basename(out)))
    print('   %d bytes alterados na regiao original'
          % sum(1 for x, y in zip(orig, d) if x != y))


if __name__ == '__main__':
    main()
