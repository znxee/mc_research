"""Troca as duas paletas de cor por vertice de um .pck de cidade ja montado.

O MC3 guarda a paleta INLINE no MapRoot, em +0x290 e +0x1290 - 256 entradas de
quatro floats, e o `rmcCpvPalette::Download(*(mcCity+0x2C))` a envia para o topo
da memoria da VU1, onde o quarto byte do stream de ITOP+2 a indexa.

O MC2 usa o MESMO desenho: um indice de 1 byte por vertice e uma paleta CPP0 de
256 RGBA. Entao a paleta porta par a par. Convencao de cor do PS2: alfa 0x80 e
componentes em 0..127, ou seja 128 e o 1.0 - dividir por 255 deixaria a cidade
com metade do brilho.

    python mc3_paleta.py <cidade.pck> --cpvs <hora>_cpvs.rsc
"""
import argparse
import importlib.util
import os
import struct
import sys

SETOR_PAL = (0x290, 0x1290)


def paleta_do_cpvs(caminho):
    aqui = os.path.dirname(os.path.abspath(__file__))
    sp = importlib.util.spec_from_file_location('mc2_rsc',
                                                os.path.join(aqui, 'mc2_rsc.py'))
    m = importlib.util.module_from_spec(sp)
    sys.modules['mc2_rsc'] = m
    sp.loader.exec_module(m)
    r = m.Rsc(caminho)
    for off, fcc, size in r.entries:
        if fcc == 'CPP0':
            buf = r.data[off:off + size]
            return [struct.unpack_from('<3B', buf, k * 4) for k in range(256)]
    raise SystemExit('%s nao tem CPP0' % os.path.basename(caminho))


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument('pck')
    ap.add_argument('--cpvs', required=True)
    ap.add_argument('--saida')
    a = ap.parse_args()
    cores = paleta_do_cpvs(a.cpvs)
    d = bytearray(open(a.pck, 'rb').read())
    for base in SETOR_PAL:
        off = 0x80 + base
        # Alfa como no varejo: 0 nas entradas 0..7, 1.0 nas 8..255, e a 255
        # branco opaco (a que rmcCpvPalette::Lookup reserva). Quem desenha com
        # a paleta da cidade residente - a coluna de fumaca do checkpoint - usa
        # esse alfa; com 0 ela some. Ver PALETA_ALFA_ZERO no mc3_city_build.
        for k, (r, g, b) in enumerate(cores):
            rgb = (1.0, 1.0, 1.0) if k == 255 else (r / 128.0, g / 128.0, b / 128.0)
            struct.pack_into('<4f', d, off + 16 * k, *rgb,
                             0.0 if k < 8 else 1.0)
    saida = a.saida or a.pck
    open(saida, 'wb').write(bytes(d))
    lum = [0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2] for c in cores]
    print('%s: 2 paletas trocadas por %s' % (os.path.basename(saida),
                                             os.path.basename(a.cpvs)))
    print('  256 cores, luminancia %.1f..%.1f (0..127 no PS2, 128 = 1.0)'
          % (min(lum), max(lum)))


if __name__ == '__main__':
    main()
