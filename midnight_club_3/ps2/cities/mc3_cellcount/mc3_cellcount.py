"""Estende os arrays por-celula de props e peds para caber no cell_count da cidade.

O cell_count do .pck de cidade e um CONTRATO ENTRE ARQUIVOS, decompilado pela
FORK C++ MODS AND PATCHES. Tres resources carregam um array de UM PONTEIRO POR
CELULA e o laco que reloca cada um e limitado por mcCity+0x268, lido da cidade
JA CARREGADA:

    a) o CellIndex da propria cidade  - sempre coerente, mesmo arquivo
    b) <cidade>_props.pck   mcPropClass::mcPropClass(datResource&) 0x0038F3F8
    c) <cidade>_peds.pck    mcCreatureCullableClass::...           0x004667E8

Os dois ultimos tem o mesmo corpo:

    if (ptr) ptr += delta;
    for (i = 0; i < cellcount; i++) if (arr[i]) arr[i] += delta;

Se a cidade declara MAIS celulas do que o props/peds foi construido para, o laco
anda alem do fim do array e SOMA O DELTA DO RESOURCE em cada palavra nao-nula
que encontrar depois. Corrompe outro objeto no lugar, em silencio, durante o
load - e o jogo morre no primeiro quadro sem nada apontar para a grade.

A correcao e cirurgica e nao move nada: acrescenta o array novo no FIM do
arquivo, reaponta, e soma ao header[3]. Nenhum outro ponteiro muda porque nada
e realocado.

    python mc3_cellcount.py --celulas 7462 <arquivos...>

Com --preservar as entradas antigas sao copiadas para o inicio do array novo.
Sem ele o array sai ZERADO, que e o que serve para o primeiro boot de
diagnostico: sem props e sem peds, mas prova a causa numa execucao so. As
entradas antigas foram indexadas com o W da cidade DOADORA, entao copiar deixa
props e peds em celula errada na grade nova - seguro em memoria, errado na tela.
"""
import argparse
import os
import struct

# (rotulo, offset do objeto, offset do ponteiro, teste de identidade)
FORMATOS = (
    ('props', 0x9B0, 0x9D8, lambda d: struct.unpack_from('<I', d, 0x9B0)[0] == 102
     and struct.unpack_from('<I', d, 0x9D0)[0] == 4),
    ('peds', 0x280, 0x2A4, lambda d: len(d) > 0x2B0),
)


def entradas_atuais(d, base, ptr, prox):
    """Quantas entradas o array tem hoje: do inicio dele ate o proximo objeto."""
    ini = struct.unpack_from('<I', d, ptr)[0] - base + 0x80
    return ini, max(0, (prox - ini) // 4)


def estende(caminho, celulas, preservar, seco):
    d = bytearray(open(caminho, 'rb').read())
    base, tipo, ver, corpo = struct.unpack_from('<IIII', d, 0)
    if corpo != len(d) - 0x80:
        return '%s: header[3]=%d nao bate com o arquivo (%d)' % (
            os.path.basename(caminho), corpo, len(d) - 0x80)
    for rot, obj, ptr, ok in FORMATOS:
        if len(d) > obj + 0x30 and ok(d):
            break
    else:
        return '%s: nao reconheci como props nem peds' % os.path.basename(caminho)
    va = struct.unpack_from('<I', d, ptr)[0]
    ini = va - base + 0x80
    if not (0 < ini < len(d)):
        return '%s: ponteiro do array fora do arquivo (0x%08X)' % (
            os.path.basename(caminho), va)
    velho = bytes(d[ini:ini + 4 * celulas])          # so o que existir
    novo_off = (len(d) + 15) & ~15
    d += bytes(novo_off - len(d))
    corpo_novo = bytearray(4 * celulas)
    if preservar:
        corpo_novo[:len(velho)] = velho
    d += corpo_novo
    struct.pack_into('<I', d, ptr, base + novo_off - 0x80)
    struct.pack_into('<I', d, 0x0C, len(d) - 0x80)
    if not seco:
        open(caminho, 'wb').write(bytes(d))
    return '%-44s %-6s array 0x%X -> 0x%X, %d entradas, %s (+%d bytes)' % (
        os.path.basename(caminho), rot, ini, novo_off, celulas,
        'copiadas' if preservar else 'zeradas', len(d) - corpo - 0x80)


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument('--celulas', type=int, required=True,
                    help='cell_count da cidade (MapRoot+0x268)')
    ap.add_argument('--preservar', action='store_true',
                    help='copia as entradas antigas em vez de zerar tudo')
    ap.add_argument('--seco', action='store_true', help='nao grava')
    ap.add_argument('arquivos', nargs='+')
    a = ap.parse_args()
    for f in a.arquivos:
        print('  ' + estende(f, a.celulas, a.preservar, a.seco))


if __name__ == '__main__':
    main()
