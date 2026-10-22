"""mc3_city_aib.py - gera o .graph e o _pvs.aib de uma cidade nova.

Os dois arquivos ficam FORA do .pck, em ASSETS/city/<cidade>/, e carregam a
identidade da cidade: o .graph e o grafo de navegacao dos pedestres (texto) e o
_pvs.aib e um container TSV1 cujo primeiro registro sao os extents.

Medido em 12/09: losangeles.graph e losangeles_pvs.aib eram COPIA BYTE A BYTE dos de
tokyo - mesmo sha256 - entao Los Angeles rodava com o grafo de pedestres e os
extents de Tokyo (-1873.8..1433.9 contra os -2000..1600 de LA), e o _pvs.aib
ainda declarava o nome 'tokyo' no registro id=08.

FORMATO TSV1 (o mesmo do _city.aib e do _pvs.aib):

    'TSV1' seguido de registros [id:u8][marca:u8][len:u32][payload]

    A marca e 'A' (0x41) ou 'B' (0x42); nao vi outras nas quatro cidades.

    id 0x0C  24 bytes   extents: min x,y,z depois max x,y,z (6 floats)
    id 0x00  10 bytes   cabecalho de versao
    id 0x08  36 bytes   nome da cidade, ASCII terminado em zero e preenchido
    id 0x05  44 bytes   comeca com os mesmos 6 floats de extents
    id 0x01, 0x09, 0x03, 0x04, 0x07, 0x0D   dados de visibilidade
    id 0x06, 0x02                            pequenos, copiados como estao

O comprimento vem do container, entao um array VAZIO e representavel - e ja
aparece no varejo: o id 0x06 do atlanta tem len 0.

O que este gerador escreve NAO e um PVS calculado: e um PVS VAZIO com a
identidade certa, que troca "dados de outra cidade" por "nenhum dado",
preservando a sequencia de registros que o motor espera. Se o motor precisar de
visibilidade de verdade, isto e o ponto de partida, nao o fim.
"""
import argparse
import os
import struct

NULO = bytes(1)

# arrays de visibilidade: saem vazios, porque os da cidade de origem descrevem
# outra geometria e sao pior que nada
VISIBILIDADE = (0x01, 0x09, 0x03, 0x04, 0x07, 0x0D)


def le_registros(caminho):
    """Cadeia de (id, marca, payload) de um TSV1."""
    d = open(caminho, 'rb').read()
    if d[:4] != b'TSV1':
        raise ValueError('%s nao e TSV1' % caminho)
    fora, off = [], 4
    while off + 6 <= len(d):
        tid, marca = d[off], d[off + 1]
        if marca not in (0x41, 0x42):
            raise ValueError('marca %02X inesperada em +%06X' % (marca, off))
        n = struct.unpack_from('<I', d, off + 2)[0]
        fora.append((tid, marca, d[off + 6:off + 6 + n]))
        off += 6 + n
    return fora


def escreve_registros(caminho, registros):
    with open(caminho, 'wb') as f:
        f.write(b'TSV1')
        for tid, marca, corpo in registros:
            f.write(struct.pack('<BBI', tid, marca, len(corpo)))
            f.write(corpo)


def extents_do_place(caminho):
    """(minx, miny, minz, maxx, maxy, maxz) lidos do cabecalho do place."""
    mn = mx = None
    for linha in open(caminho, encoding='utf-8', errors='replace'):
        p = linha.rstrip('\n').split('\t')
        if p[0] == '# extents_min':
            mn = tuple(float(v) for v in p[1:4])
        elif p[0] == '# extents_max':
            mx = tuple(float(v) for v in p[1:4])
        if mn and mx:
            return mn + mx
    raise ValueError('o place nao declara extents_min/extents_max')


def gera_pvs(saida, cidade, ext, referencia):
    """_pvs.aib com a identidade da cidade nova e sem dados de visibilidade."""
    fora = []
    for tid, marca, corpo in le_registros(referencia):
        if tid == 0x0C:
            corpo = struct.pack('<6f', *ext)
        elif tid == 0x08:
            nome = cidade.encode('ascii')[:len(corpo) - 1]
            corpo = nome + NULO * (len(corpo) - len(nome))
        elif tid == 0x05 and len(corpo) >= 24:
            corpo = struct.pack('<6f', *ext) + corpo[24:]
        elif tid in VISIBILIDADE:
            corpo = b''
        fora.append((tid, marca, corpo))
    escreve_registros(saida, fora)


def gera_graph(saida, codigo, ext):
    """.graph com os extents certos e um grafo de pedestres vazio."""
    L = ['MinExtents %f\t%f\t%f ' % ext[0:3],
         'MaxExtents %f\t%f\t%f ' % ext[3:6],
         'Graphs 1',
         '{',
         '\tGraph %s_graph' % codigo,
         '\t{']
    for bloco in ('VertexArray', 'NormalArray', 'ConnectionArray',
                  'GraphNodeArray', 'NodeUserDataArray'):
        L.append('\t\t%s 0 ' % bloco)
        L.append('\t\t{')
        L.append('\t\t}')
    L.append('\t}')
    L.append('}')
    # os arquivos de varejo usam CRLF
    open(saida, 'wb').write(('\r\n'.join(L) + '\r\n').encode('ascii'))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--place', required=True, help='de onde vem os extents')
    p.add_argument('--cidade', default='losangeles',
                   help='nome gravado no registro 0x08')
    p.add_argument('--codigo', default='m', help='prefixo do nome do grafo')
    p.add_argument('--referencia', required=True,
                   help='_pvs.aib de varejo de onde vem a sequencia de registros')
    p.add_argument('--saida', required=True, help='pasta ASSETS/city/<cidade>')
    p.add_argument('--prefixo', default='losangeles', help='prefixo dos arquivos')
    a = p.parse_args(argv)

    ext = extents_do_place(a.place)
    print('extents: min %.1f %.1f %.1f  max %.1f %.1f %.1f' % ext)
    g = os.path.join(a.saida, a.prefixo + '.graph')
    v = os.path.join(a.saida, a.prefixo + '_pvs.aib')
    gera_graph(g, a.codigo, ext)
    gera_pvs(v, a.cidade, ext, a.referencia)
    print('  %s (%d bytes)' % (g, os.path.getsize(g)))
    print('  %s (%d bytes)' % (v, os.path.getsize(v)))

    # reabre o que acabou de escrever, em vez de confiar no que foi gravado
    regs = le_registros(v)
    achou = {}
    for tid, marca, corpo in regs:
        achou.setdefault(tid, corpo)
    lido = struct.unpack('<6f', achou[0x0C])
    if any(abs(x - y) > 0.01 for x, y in zip(lido, ext)):
        raise SystemExit('extents nao fecham: %s' % (lido,))
    nome = achou[0x08].split(NULO)[0].decode('ascii')
    if nome != a.cidade:
        raise SystemExit('nome nao fecha: %r' % nome)
    sobrou = [('%02X' % t) for t, _, c in regs if t in VISIBILIDADE and c]
    if sobrou:
        raise SystemExit('sobrou visibilidade em %s' % ', '.join(sobrou))
    print('  reaberto: %d registros, extents e nome de %s, visibilidade vazia'
          % (len(regs), nome))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
