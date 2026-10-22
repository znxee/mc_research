# -*- coding: utf-8 -*-
"""Bisseccao: testa SO o encanamento (append + tabela + repoint), sem MC2.

Pega os blocos originais do modelo alvo, RE-ENCODA cada um com o mesmo writer
que a conversao usa, anexa no fim e reconstroi a tabela de grupos apontando pros
novos. A geometria e identica a original -- o round-trip ja provou que sai byte
a byte igual -- entao a unica coisa em teste e o encanamento.

  * se ISSO carregar, o encanamento esta certo e o problema e o dado do MC2
    (contagem, escala, tamanho do predio);
  * se ISSO travar, o erro esta no meu append/tabela/repoint e a conversao nem
    entra na conta.

    python teste_plumbing.py
"""
from __future__ import annotations

import os
import struct

SRC = os.path.join(os.environ.get('MC3_CLEAN_ASSETS', ''), 'ASSETS/resources/city/atlanta_midnight_clear.pck')
ALVO = 'a_inst_low_ghto_06x'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   'teste_plumbing_atlanta_midnight_clear.pck')

MODEL_VTABLE = 0x7A0090
VTABLE_AT = 0x28


def main():
    d = bytearray(open(SRC, 'rb').read())
    va = struct.unpack_from('<I', d, 0)[0]
    base = va - 0x80
    F = lambda v: v - base
    V = lambda o: o + base
    U = lambda o: struct.unpack_from('<I', d, o)[0]

    vt = None
    for o in range(0x80, len(d) - 0x80, 4):
        if U(o) == MODEL_VTABLE:
            if bytes(d[o + 0x48:o + 0x70]).split(b'\0')[0].decode('latin1', 'replace') == ALVO:
                vt = o
                break
    mesh = F(U(vt + 0x14))
    ngrp = struct.unpack_from('<H', d, mesh + 8)[0]
    g = F(U(mesh + 0x10))

    # copia exata de cada bloco, no tamanho DECLARADO (inclui a cauda e o padding)
    grupos = []
    for k in range(ngrp):
        p, c, _pad = struct.unpack_from('<IHH', d, g + 8 * k)
        lf = F(p)
        entradas = []
        for j in range(c):
            bp, qw, nv = struct.unpack_from('<IHH', d, lf + 8 * j)
            blk = F(bp)
            entradas.append((bytes(d[blk:blk + qw * 16]), qw, nv))
        grupos.append(entradas)
    print('alvo %s: %d grupos, %d blocos, %d bytes de geometria'
          % (ALVO, ngrp, sum(len(x) for x in grupos),
             sum(len(b) for x in grupos for b, _q, _n in x)))

    def append(blob, align=16):
        while len(d) % align:
            d.extend(b'\xCD')
        at = len(d)
        d.extend(blob)
        while len(d) % align:
            d.extend(b'\xCD')
        struct.pack_into('<I', d, 0x0C, len(d) - 0x80)
        return at

    listas = []
    for entradas in grupos:
        novas = []
        for blob, qw, nv in entradas:
            at = append(blob)
            novas.append((V(at), qw, nv))
        lb = bytearray()
        for va_, qw, nv in novas:
            lb += struct.pack('<IHH', va_, qw, nv)
        listas.append((append(bytes(lb)), len(novas)))

    tab = bytearray()
    for at, n in listas:
        tab += struct.pack('<IHH', V(at), n, 0xCDCD)
    grp_at = append(bytes(tab))
    struct.pack_into('<I', d, mesh + 0x10, V(grp_at))

    open(OUT, 'wb').write(bytes(d))
    orig = open(SRC, 'rb').read()
    mud = sum(1 for x, y in zip(orig, d) if x != y)
    print('saida: %s' % OUT)
    print('   %d -> %d bytes | %d bytes alterados na regiao original'
          % (len(orig), len(d), mud))
    print('   (so o body size no header e o ponteiro mesh+0x10)')


if __name__ == '__main__':
    main()
