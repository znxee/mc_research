r"""Reconstroi o bloco de heap que o mod `mesh_dump` despejou no console do EE.

O mod cria um heap privado (mcHeap::CreateMemTopHeap), pede ao jogo que leia um
`.mod` de texto dentro dele e despeja o bloco em hexadecimal entre uma linha
`BLOB <base> <bytes>` e uma `ENDB <bytes>`. Este script tira isso do log do
PCSX2 e devolve o binario.

POR QUE PASSAR PELO CONSOLE. Um modulo nao tem escrita de arquivo - o jogo nao
expoe uma para nos - e savestate obrigaria o usuario a agir a cada iteracao. A
SIO em 0x1000F180 e o unico canal, e sai rapido: 148 KB levaram 0,024 s de
tempo emulado.

O QUE SAI DAQUI E O CORPO DE UM `.pck`, com uma ressalva: os ponteiros estao
ABSOLUTOS na base onde o heap calhou (o `base` da linha BLOB). Um `.pck` guarda
os mesmos ponteiros relativos a uma base declarada no cabecalho e o
`datResource` soma o delta na carga - entao converter e subtrair a base de cada
palavra que for ponteiro, nao reescrever estrutura.

    python mc3_heap_dump.py --log X:\...\cli_teste.txt --saida modelo.bin
"""
import argparse
import os
import re
import struct

LINHA = re.compile(r'^([0-9A-F]{8}):([0-9A-F]+)\s*$')


def extrai(caminho):
    """Devolve (base, bytes) do ultimo BLOB completo do log."""
    base = tam = None
    partes = {}
    for cru in open(caminho, encoding='utf-8', errors='replace'):
        l = cru.strip()
        # o PCSX2 prefixa cada linha com [    33,8216]
        corte = l.find(']')
        if corte >= 0 and l.startswith('['):
            l = l[corte + 1:].strip()
        if l.startswith('BLOB '):
            t = l.split()
            base, tam = int(t[1], 16), int(t[2], 16)
            partes = {}
            continue
        if l.startswith('ENDB '):
            continue
        m = LINHA.match(l)
        if m and base is not None:
            off = int(m.group(1), 16)
            d = bytes.fromhex(m.group(2))
            partes[off] = d
    if base is None:
        raise SystemExit('nenhuma linha BLOB no log')
    saida = bytearray(tam)
    vistos = 0
    for off, d in partes.items():
        if off + len(d) <= tam:
            saida[off:off + len(d)] = d
            vistos += len(d)
    return base, bytes(saida), vistos


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--log', default=os.path.join(os.environ.get('MC3_PCSX2_DATA', ''), 'logs/cli_teste.txt'))
    ap.add_argument('--saida', default='output/heap_dump.bin')
    ap.add_argument('--modelo', type=lambda s: int(s, 16), metavar='VA',
                    help='endereco do rmcModel (o PRB1 do log), para relatar')
    a = ap.parse_args()

    base, d, vistos = extrai(a.log)
    print('BLOB base %08X, %d bytes (%d recebidos, %d faltando)'
          % (base, len(d), vistos, len(d) - vistos))
    os.makedirs(os.path.dirname(a.saida) or '.', exist_ok=True)
    open(a.saida, 'wb').write(d)
    print('  -> %s' % a.saida)

    # quantas palavras parecem ponteiro para dentro do proprio bloco: e isso que
    # torna o bloco relocavel como corpo de pck
    n = dentro = 0
    for i in range(0, len(d) - 3, 4):
        v = struct.unpack_from('<I', d, i)[0]
        if base <= v < base + len(d):
            dentro += 1
        n += 1
    print('  palavras: %d, apontando para dentro do bloco: %d (%.1f%%)'
          % (n, dentro, 100.0 * dentro / max(1, n)))

    if a.modelo:
        o = a.modelo - base
        if 0 <= o < len(d) - 32:
            c = struct.unpack_from('<8I', d, o)
            print('  rmcModel em +%06X: vtable %08X, grupos %d, tabela %08X, geoms %08X'
                  % (o, c[0], c[2], c[3], c[4]))


if __name__ == '__main__':
    main()
