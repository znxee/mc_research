"""Fatia um .mod de texto em pedacos INTERNAMENTE CONSISTENTES.

POR QUE ISTO EXISTE, e vale registrar porque me custou varios boots: a primeira
versao disto cortava blocos `mtl` e reescrevia `adjuncts:` no cabecalho, mas
deixava os arrays `v`/`t1` inteiros no arquivo. O cabecalho dizia 1914 e havia
2926 linhas de array. Se o parser dimensiona o buffer por `adjuncts:` e le os
arrays ate achar `mtl`, ele escreve 2926 entradas num buffer de 1914 - e o que
sai disso e o "Heap %s overrun" do alocador do jogo (0x0065D8BC) e um crash em
endereco aleatorio. Passei a atribuir esses crashes a um teto de materiais que
NAO EXISTE: fatias de 10 blocos comecando em 0, em 11 e em 17 carregam todas.

Entao cortar exige renumerar. Este script recolhe os indices realmente usados
pelos blocos escolhidos, emite so essas entradas de array, e reescreve cada
`adj` para os indices novos. As linhas de array sao COPIADAS, nunca
reformatadas, para nao introduzir deriva de float.

Terminador: LF. Os .mod do proprio jogo usam LF (o heli.mod nao tem um CR
sequer); o meu gerador vinha escrevendo CRLF. Isso sozinho nao derruba - foi
medido - mas nao ha motivo para diferir do que o jogo embarca.

    python mc3_mod_split.py entrada.mod saida_%d.mod --por 10
    python mc3_mod_split.py entrada.mod fatia.mod --fatia 11 21
"""
import argparse
import io
import os

CAMPOS = ('v', 'n', 'c', 't1')          # a ordem dos 4 primeiros campos do adj


def le(caminho):
    txt = io.open(caminho, 'rb').read().decode('latin1').replace('\r\n', '\n')
    linhas = txt.split('\n')
    cab, arrays, i = [], {k: [] for k in CAMPOS}, 0
    while i < len(linhas) and not linhas[i].startswith('mtl'):
        t = linhas[i].split()
        if t and t[0] in arrays:
            arrays[t[0]].append(linhas[i])
        elif ':' in linhas[i]:
            cab.append(linhas[i])
        i += 1
    blocos, atual = [], None
    while i < len(linhas):
        if linhas[i].startswith('mtl'):
            if atual:
                blocos.append(atual)
            atual = [linhas[i]]
        elif atual is not None:
            atual.append(linhas[i])
        i += 1
    if atual:
        blocos.append(atual)
    return cab, arrays, blocos


def escreve(saida, cab, arrays, blocos):
    """Emite so as entradas de array referenciadas, renumeradas."""
    usados = {k: set() for k in CAMPOS}
    for b in blocos:
        for l in b:
            t = l.split()
            if t and t[0] == 'adj':
                for f, k in enumerate(CAMPOS):
                    usados[k].add(int(t[1 + f]))

    mapa, corpo = {}, []
    for k in CAMPOS:
        ordem = sorted(usados[k])
        mapa[k] = {velho: novo for novo, velho in enumerate(ordem)}
        for velho in ordem:
            corpo.append(arrays[k][velho])

    saida_blocos, nadj, nprim = [], 0, 0
    for b in blocos:
        novo = []
        for l in b:
            t = l.split()
            if t and t[0] == 'adj':
                ids = [mapa[k][int(t[1 + f])] for f, k in enumerate(CAMPOS)]
                novo.append('\tadj\t%d\t%d\t%d\t%d\t%s\t%s'
                            % tuple(ids + [t[5], t[6]]))
                nadj += 1
            else:
                novo.append(l)
                if t and t[0] in ('str', 'stp'):
                    nprim += int(t[1]) - 2
                elif t and t[0] == 'tri':
                    nprim += 1
        saida_blocos.append(novo)

    conta = {'verts': len(usados['v']), 'normals': len(usados['n']),
             'colors': len(usados['c']), 'tex1s': len(usados['t1']),
             'materials': len(blocos), 'adjuncts': nadj, 'primitives': nprim}
    novo_cab = []
    for l in cab:
        k = l.split(':')[0].strip()
        novo_cab.append('%s: %d' % (k, conta[k]) if k in conta else l)

    linhas = novo_cab + [''] + corpo + ['']
    for b in saida_blocos:
        linhas += b
    io.open(saida, 'wb').write(('\n'.join(linhas)).encode('latin1'))
    return conta


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('entrada')
    ap.add_argument('saida', help='com --por, use %%d no nome')
    ap.add_argument('--por', type=int, metavar='N', help='N blocos mtl por arquivo')
    ap.add_argument('--fatia', type=int, nargs=2, metavar=('INI', 'FIM'))
    a = ap.parse_args()

    cab, arrays, blocos = le(a.entrada)
    print('%s: %d blocos mtl, arrays v=%d n=%d c=%d t1=%d'
          % (os.path.basename(a.entrada), len(blocos),
             *[len(arrays[k]) for k in CAMPOS]))

    if a.fatia:
        pedacos = [(a.fatia[0], a.fatia[1])]
    elif a.por:
        pedacos = [(i, min(i + a.por, len(blocos)))
                   for i in range(0, len(blocos), a.por)]
    else:
        pedacos = [(0, len(blocos))]

    for n, (i, f) in enumerate(pedacos):
        nome = a.saida % n if '%d' in a.saida else a.saida
        c = escreve(nome, cab, arrays, blocos[i:f])
        print('  %-16s [%2d,%2d)  mtl=%-3d verts=%-5d cores=%-4d adj=%-5d prim=%d'
              % (os.path.basename(nome), i, f, c['materials'], c['verts'],
                 c['colors'], c['adjuncts'], c['primitives']))


if __name__ == '__main__':
    main()
