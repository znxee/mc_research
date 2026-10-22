"""Turn the MC2 placement table into something a PS2 module can read.

Of the three legs of porting a city from raw files - geometry, collision,
placement - the first two have live readers in MC3 and the third does not. The
`.lvl`/`.hood` grammar is in the string pool with zero instructions referencing
it: the readers were compiled out. So placement is the one part that has to be
code, and this is its PC half.

    python mc3_place.py output/mc2_losangeles/losangeles_place.tsv \\
        --out Y:/MC3HostFS/losangeles.place

WHY A BINARY AND NOT THE TSV

The module is freestanding - no libc, no strtod. Parsing 8809 lines of decimal
floats on the EE to produce numbers this script already has is work in the wrong
place. Here it is one pass over a text file; there it would be a float parser
nobody should have to debug through a savestate.

THE LUCKY PART

`gfxState::SetWorld` (0x0052E0D0) reads three floats per row and expands them to
four, so its argument is a Matrix34: twelve floats, row-major, translation last.
That is EXACTLY the column order the TSV already has - m00..m22 then tx ty tz -
so the twelve floats are copied through untouched and the module hands the
pointer straight to the game. No conversion, and nothing to get transposed.

FORMAT

    +0   'MC3L'
    +4   version
    +8   name count          unique asset names
    +12  entry count         comp rows and inst rows together: both are draws
    +16  names offset        NUL-terminated, concatenated
    +20  names size
    +24  entries offset
    +28  reserved
    +32  extents min[3]      from the .lvl header, for whoever wants them
    +44  extents max[3]
    +56  padding to 64

    entry, 68 bytes:
    +0   u32   name index
    +4   float m[12]         Matrix34, ready for SetWorld
    +52  float centre[3]     from the AABB, for culling
    +64  float radius
"""
import argparse
import io
import os
import struct

MAGIC = 0x4D43334C          # 'MC3L'
VERSION = 1
HDR = 64
ENTRY = 68


def le_tsv(caminho):
    """(nomes, entradas, emin, emax). `comp` e `inst` viram os dois entradas.

    The `comp` rows carry an identity matrix and a world-space box - they are
    the fixed geometry, already placed. The `inst` rows are the repeated props
    with a real transform. Both get drawn, so both become entries here; the
    distinction only mattered to the exporter.
    """
    nomes, indice, entradas = [], {}, []
    emin = emax = None
    for linha in io.open(caminho, encoding='latin1'):
        linha = linha.rstrip('\n')
        if linha.startswith('# extents_min'):
            emin = [float(x) for x in linha.split('\t')[1:4]]
            continue
        if linha.startswith('# extents_max'):
            emax = [float(x) for x in linha.split('\t')[1:4]]
            continue
        if not linha or linha.startswith('#') or linha.startswith('kind'):
            continue
        c = linha.split('\t')
        if c[0] not in ('comp', 'inst'):
            continue
        # The model file is <name>_<lod>_<part>.mod, and gfxGetModel appends the
        # extension itself, so the asset name is everything before it.
        #
        # '#' is replaced as hygiene, NOT as a fix. It was once believed to be
        # why gfxGetModel hung; renaming all 298 files changed nothing and the
        # hang landed on the identical name with an underscore. Keeping the
        # substitution because an odd character in an asset name is worth
        # avoiding anyway - but nobody should read it as a solved problem.
        # The files in ASSETS/model must match whatever this produces.
        # The FULL spelling, directory and extension included. rmcModel::Create
        # dispatches on the extension - no ".mod" means it takes the binary
        # path - and mc2_probe measured that the directory is required too:
        # "model/checker.mod" loads and "checker.mod" returns nothing. Building
        # it here keeps string handling out of a module that has no libc.
        asset = 'model/%s.mod' % (
            ('%s_%s_%s' % (c[1], c[2], c[3])).replace('#', '_'))
        if asset not in indice:
            indice[asset] = len(nomes)
            nomes.append(asset)
        m = [float(x) for x in c[4:16]]          # m00..m22 then tx ty tz
        caixa = [float(x) for x in c[16:22]]     # emin xyz, emax xyz
        centro = [(caixa[i] + caixa[i + 3]) * 0.5 for i in range(3)]
        raio = max((caixa[i + 3] - caixa[i]) * 0.5 for i in range(3))
        entradas.append((indice[asset], m, centro, raio))
    return nomes, entradas, emin or [0, 0, 0], emax or [0, 0, 0]


def ordena(nomes, entradas, pasta, teto):
    """Entradas da menor malha para a maior, e opcionalmente sem as maiores.

    The module resolves the first N distinct names it meets walking the entry
    list, so the ORDER OF THE ENTRIES decides which meshes it tries first. Draw
    order does not matter, which makes this free.

    It is here to measure rather than to fix: the loader stopped on the largest
    mesh of the set (548 KB, 1511 verts, 31 materials, 3476 adjuncts) having
    taken the 161 KB one before it without complaint. Smallest-first turns the
    number of models resolved into the size at which it gives up - one boot
    instead of a hand bisection.
    """
    tamanho = {}
    for i, n in enumerate(nomes):
        base = n.split('/')[-1]
        # The exporter's directory still spells the 298 component meshes with
        # '#'; only the copies under ASSETS/model were renamed. Looking up just
        # the sanitised name silently returned 0 for every one of them, which
        # sorted the BIGGEST meshes to the front - the exact opposite of the
        # point. Try both spellings, and say so when one is genuinely missing.
        tamanho[i] = 0
        for cand in (base, base.replace('_geom_', '#geom_')):
            try:
                tamanho[i] = os.path.getsize(os.path.join(pasta, cand))
                break
            except OSError:
                pass

    faltando = sum(1 for v in tamanho.values() if v == 0)
    if faltando:
        print('AVISO: %d de %d meshes nao encontrados em %s - vao primeiro na '
              'ordem, o que falseia a medida' % (faltando, len(nomes), pasta))

    manter = [i for i in range(len(nomes))
              if not teto or tamanho[i] <= teto]
    cortados = len(nomes) - len(manter)
    ordem = sorted(manter, key=lambda i: tamanho[i])

    novo_idx = {}
    novos_nomes = []
    for i in ordem:
        novo_idx[i] = len(novos_nomes)
        novos_nomes.append(nomes[i])

    novas = [(novo_idx[idx], m, c, r) for idx, m, c, r in entradas
             if idx in novo_idx]
    novas.sort(key=lambda e: e[0])
    maior = max((tamanho[i] for i in ordem), default=0)
    return novos_nomes, novas, cortados, maior


def escreve(saida, nomes, entradas, emin, emax):
    tabela = b''
    offs = []
    for n in nomes:
        offs.append(len(tabela))
        tabela += n.encode('latin1') + b'\0'
    while len(tabela) % 4:
        tabela += b'\0'

    nomes_off = HDR
    entradas_off = nomes_off + len(tabela)

    out = bytearray()
    out += struct.pack('<8I', MAGIC, VERSION, len(nomes), len(entradas),
                       nomes_off, len(tabela), entradas_off, 0)
    out += struct.pack('<6f', *(emin + emax))
    out += bytes(HDR - len(out))
    out += tabela
    for idx, m, centro, raio in entradas:
        # The name index is stored as the OFFSET into the table, so the module
        # does not need a second indirection to find the string.
        out += struct.pack('<I', offs[idx])
        out += struct.pack('<12f', *m)
        out += struct.pack('<3f', *centro)
        out += struct.pack('<f', raio)

    io.open(saida, 'wb').write(bytes(out))
    return len(out)


def main():
    p = argparse.ArgumentParser(description='tabela de colocacao -> binario')
    p.add_argument('tsv')
    p.add_argument('--out', required=True)
    p.add_argument('--models',
                   help='pasta dos .mod; com ela as entradas saem ordenadas '
                        'do menor mesh para o maior')
    p.add_argument('--max-mesh', type=int, default=0,
                   help='descarta mesh acima de N bytes (0 = sem limite)')
    a = p.parse_args()

    nomes, entradas, emin, emax = le_tsv(a.tsv)
    if a.models:
        nomes, entradas, cortados, maior = ordena(nomes, entradas, a.models,
                                                  a.max_mesh)
        print('ordenado do menor mesh para o maior; o maior que sobrou tem '
              '%d bytes%s' % (maior, (', %d descartados' % cortados)
                              if cortados else ''))
    tam = escreve(a.out, nomes, entradas, emin, emax)
    print('%s: %d entradas, %d nomes unicos, %d bytes (%.0f KB)'
          % (os.path.basename(a.out), len(entradas), len(nomes), tam, tam / 1024.0))
    print('   extents  %s .. %s'
          % (' '.join('%.0f' % v for v in emin), ' '.join('%.0f' % v for v in emax)))
    print('   na RAM do jogo: %.0f KB de entradas + %d KB de nomes'
          % (len(entradas) * ENTRY / 1024.0, (tam - HDR - len(entradas) * ENTRY) // 1024))


if __name__ == '__main__':
    main()
