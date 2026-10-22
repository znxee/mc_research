# -*- coding: utf-8 -*-
"""Bisseccao final: geometria do RETAIL passando pelo MEU pipeline inteiro.

O `teste_plumbing` copiou os bytes originais dos blocos, entao provou o
append/tabela/repoint mas **nao** testou o `make_block` nem a costura. Este aqui
decodifica os blocos originais do alvo, joga tudo pela mesma esteira que a
conversao do MC2 usa (re-tirar, costurar com degenerados, re-encodar) e grava.

A geometria e a mesma do jogo. Se ISSO travar, o erro esta no meu pipeline e o
MC2 nao tem nada a ver. Se passar, o problema e o dado que vem do MC2.

    python teste_pipeline.py             # re-encoda, mesma contagem de blocos
    python teste_pipeline.py --picar     # re-corta em blocos pequenos (~41)
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
ALVO = 'a_inst_apt_mid_02x'


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
    ap.add_argument('--alvo', default=ALVO)
    ap.add_argument('--picar', action='store_true',
                    help='re-corta a geometria em tiras curtas e costura (como o MC2)')
    ap.add_argument('--saida', default=None)
    a = ap.parse_args()

    d = bytearray(open(SRC, 'rb').read())
    va = struct.unpack_from('<I', d, 0)[0]
    base = va - 0x80
    F = lambda v: v - base
    V = lambda o: o + base
    U = lambda o: struct.unpack_from('<I', d, o)[0]

    vt = None
    for o in range(0x80, len(d) - 0x80, 4):
        if U(o) == 0x7A0090:
            if bytes(d[o + 0x48:o + 0x70]).split(b'\0')[0].decode('latin1', 'replace') == a.alvo:
                vt = o
                break
    mesh = F(U(vt + 0x14))
    ngrp = struct.unpack_from('<H', d, mesh + 8)[0]
    g = F(U(mesh + 0x10))

    # decodifica os blocos originais -> tiras (posicoes em unidades de mundo)
    tiras = []
    grupos_orig = []
    for k in range(ngrp):
        p, c, _ = struct.unpack_from('<IHH', d, g + 8 * k)
        lf = F(p)
        for j in range(c):
            bp, qw, nv = struct.unpack_from('<IHH', d, lf + 8 * j)
            blk = F(bp)
            sc = struct.unpack_from('<f', d, blk + 4)[0]
            cnt = struct.unpack_from('<I', d, blk + 8)[0]
            pos = [tuple(x * sc for x in struct.unpack_from('<hhh', d, blk + 0x10 + 6 * i))
                   for i in range(cnt)]
            u0 = blk + 0x10 + 6 * cnt
            while u0 % 4:
                u0 += 1
            uv = [tuple(x / 4096.0 for x in struct.unpack_from('<hh', d, u0 + 4 + 4 * i))
                  for i in range(cnt)]
            odd = bytes(d[blk + 0x0C:blk + 0x0E]) == b'\x27\x02'
            tiras.append((pos, uv, odd))
        grupos_orig.append(c)
    print('alvo %s: %d grupos, %d blocos originais, %d vertices'
          % (a.alvo, ngrp, len(tiras), sum(len(p) for p, _u, _o in tiras)))

    if a.picar:
        # quebra em tiras de 6 vertices e deixa a costura remontar -- e o mesmo
        # perfil que o MC2 entrega (muitas tiras curtas)
        curtas = []
        for pos, uv, odd in tiras:
            for s in range(0, len(pos) - 2, 4):
                p2, u2 = pos[s:s + 6], uv[s:s + 6]
                if len(p2) >= 3:
                    curtas.append((p2, u2, odd if s % 2 == 0 else not odd))
        print('   picado em %d tiras curtas' % len(curtas))
        blocos = []
        cur_p, cur_u, cur_odd = [], [], False
        for pos, uv, odd in curtas:
            if not cur_p:
                cur_p, cur_u, cur_odd = list(pos), list(uv), odd
                continue
            quer_par = (cur_odd != (not odd))
            ponte = 2 if ((len(cur_p) + 2) % 2 == 0) == quer_par else 3
            if len(cur_p) + ponte + len(pos) > conv.MAX_VERTS:
                blocos.append((cur_p, cur_u, cur_odd))
                cur_p, cur_u, cur_odd = list(pos), list(uv), odd
                continue
            cur_p += [cur_p[-1]] + [pos[0]] * (ponte - 1)
            cur_u += [cur_u[-1]] + [uv[0]] * (ponte - 1)
            cur_p += pos
            cur_u += uv
        if cur_p:
            blocos.append((cur_p, cur_u, cur_odd))
    else:
        blocos = tiras
    print('   -> %d blocos' % len(blocos))

    sc = conv.pick_scale(blocos)
    print('   escala %g' % sc)

    def append(blob, align=16):
        while len(d) % align:
            d.extend(b'\xCD')
        at = len(d)
        d.extend(blob)
        while len(d) % align:
            d.extend(b'\xCD')
        struct.pack_into('<I', d, 0x0C, len(d) - 0x80)
        return at

    ptrs = []
    for pos, uv, odd in blocos:
        blob = conv.make_block(pos, uv, sc, odd)
        ptrs.append((V(append(blob)), len(blob) // 16, len(pos)))

    if not a.picar and sum(grupos_orig) == len(ptrs):
        fatias, i = [], 0          # preserva o agrupamento original
        for c in grupos_orig:
            fatias.append(ptrs[i:i + c]); i += c
    else:
        fatias = [ptrs[i::ngrp] for i in range(ngrp)]
        fatias = [f if f else [ptrs[0]] for f in fatias]
    tab = bytearray()
    for f in fatias:
        lb = bytearray()
        for va_, qw, nv in f:
            lb += struct.pack('<IHH', va_, qw, nv)
        tab += struct.pack('<IHH', V(append(bytes(lb))), len(f), 0xCDCD)
    struct.pack_into('<I', d, mesh + 0x10, V(append(bytes(tab))))

    out = a.saida or _saida.caminho( 'teste_pipeline%s_atlanta_midnight_clear.pck'
                                  % ('_picado' if a.picar else ''))
    open(out, 'wb').write(bytes(d))
    orig = open(SRC, 'rb').read()
    print('saida: %s' % out)
    print('   %d bytes alterados na regiao original'
          % sum(1 for x, y in zip(orig, d) if x != y))


if __name__ == '__main__':
    main()
