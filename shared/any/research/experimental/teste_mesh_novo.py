# -*- coding: utf-8 -*-
"""Cria um MESH DE CIDADE INTEIRO do zero e so reaponta o modelo pra ele.

Ideia do usuario: em vez de remendar as tabelas do mesh existente (que sempre
travava), montar tudo novo a partir da tag `18 1E 7A 00` e trocar so o ponteiro
de LOD0 do modelo.

O retail guarda o mesh inteiro como UMA REGIAO CONTIGUA, nesta ordem exata
(medido no `a_inst_low_ghto_06x` do atlanta):

    [tabela de material: ngrp x u16]      <- termina exatamente onde o mesh comeca
    [struct do mesh: 0x20 bytes]
    [cabecalho da tabela de grupos: u32 ngrp + 12 bytes de 0xCD]
    [tabela de grupos: ngrp x 8]
    por grupo:
        [cabecalho da lista: u32 count + 12 de 0xCD]
        [lista: count x 8  (ptr | u16 qwords | u16 vertices)]
        [pad ate 16]
        [bloco 0][bloco 1]...              <- colados

O mesmo formato que o `mesh_psptops2_v1.1.py` (ZNXee) usa pro veiculo.

    python teste_mesh_novo.py              # copia fiel (11 blocos, controle)
    python teste_mesh_novo.py --split 2    # 12 blocos
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
    velho = F(U(vt + 0x14))
    ngrp = struct.unpack_from('<H', d, velho + 8)[0]
    hi08 = struct.unpack_from('<H', d, velho + 0x0A)[0]
    f14, f18, f1c = U(velho + 0x14), U(velho + 0x18), U(velho + 0x1C)
    matf = F(U(velho + 0x0C))
    materiais = [struct.unpack_from('<H', d, matf + 2 * i)[0] for i in range(ngrp)]
    g = F(U(velho + 0x10))
    print('mesh original @%#x: %d grupos, material %s' % (velho, ngrp, materiais))

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

    if a.split > 1:
        maior = max((it for gr in grupos for it in gr), key=lambda x: x['nv'])
        gi = next(i for i, gr in enumerate(grupos) if maior in gr)
        gr = grupos[gi]
        idx = gr.index(maior)
        n = maior['nv']
        passo = max(4, ((n + a.split - 1) // a.split + 1) // 2 * 2)
        ped = []
        s = 0
        while s < n - 2:
            p2, u2 = maior['pos'][s:s + passo + 2], maior['uv'][s:s + passo + 2]
            if len(p2) >= 3:
                ped.append(dict(pos=p2, uv=u2, odd=maior['odd'], sc=maior['sc'],
                                nv=len(p2), bytes=None))
            s += passo
        gr[idx:idx + 1] = ped
        print('   bloco de %d vertices (grupo %d) -> %d pedacos' % (n, gi, len(ped)))

    # ---------------- monta a regiao inteira, contigua ----------------
    while len(d) % 16:
        d.append(0xCD)
    reg = len(d)                       # inicio da regiao nova

    mat_bytes = b''.join(struct.pack('<H', m) for m in materiais)
    # o mesh tem que cair alinhado em 16, e a tabela de material termina nele
    mat_off = reg
    mesh_off = mat_off + len(mat_bytes)
    ajuste = (16 - mesh_off % 16) % 16
    mat_off += ajuste                  # empurra a tabela pra o mesh alinhar
    mesh_off = mat_off + len(mat_bytes)

    gtab_hdr = mesh_off + 0x20
    gtab = gtab_hdr + 16
    corrente = gtab + 8 * ngrp

    regioes = []
    ponteiros = []
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
    struct.pack_into('<I', m, 0x04, 0)
    struct.pack_into('<H', m, 0x08, ngrp)
    struct.pack_into('<H', m, 0x0A, hi08)
    struct.pack_into('<I', m, 0x0C, V(mat_off))
    struct.pack_into('<I', m, 0x10, V(gtab))
    struct.pack_into('<I', m, 0x14, f14)          # tabela de 4 entradas: reusa a original
    struct.pack_into('<I', m, 0x18, f18)
    struct.pack_into('<I', m, 0x1C, f1c)
    saida += bytes(m)
    saida += pad16(struct.pack('<I', ngrp))
    gt = bytearray()
    for p, n in ponteiros:
        gt += struct.pack('<IHH', p, n, 0xCDCD)
    saida += bytes(gt)
    saida += b''.join(regioes)

    d.extend(saida)
    while len(d) % 16:
        d.append(0xCD)
    struct.pack_into('<I', d, 0x0C, len(d) - 0x80)
    struct.pack_into('<I', d, vt + 0x14, V(mesh_off))     # <<< so isso muda no original

    out = a.saida or _saida.caminho( 'teste_mesh_novo%s_atlanta_midnight_clear.pck'
                                  % ('_split%d' % a.split if a.split > 1 else ''))
    open(out, 'wb').write(bytes(d))
    orig = open(SRC, 'rb').read()
    print('mesh novo @%#x | %d blocos em %d grupos' % (mesh_off, sum(len(x) for x in grupos), ngrp))
    print('%s' % os.path.basename(out))
    print('   %d bytes alterados na regiao original'
          % sum(1 for x, y in zip(orig, d) if x != y))


if __name__ == '__main__':
    main()
