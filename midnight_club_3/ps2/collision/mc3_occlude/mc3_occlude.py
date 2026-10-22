"""mc3_occlude.py - o culling da cidade que NAO esta no .pck

Passei semanas editando `resources/city/<cidade>_<cond>.pck` achando que a
cidade inteira morava la. Nao mora. O que decide o que aparece na tela esta em
`ASSETS/city/<cidade>/`, e nada disso e tocado quando se troca a geometria:

    <cidade>.occlude      TEXTO. Caixas ocluidoras em coordenada de mundo.
                          O atlanta tem 340. Carregado por
                          `mcOccluderSystem::LoadDynamicGeomDataset` (a mensagem
                          de erro dele esta em 0x0065C8D0 do ELF de varejo).
    <cidade>_city.aib     BINARIO. Magica `TSV1`, blocos etiquetados
                          [u8 tag]['A'][u32 tamanho][corpo]. O atlanta tem 4396
                          registros de 28 bytes e 4713 de 20, mais o nome
                          "atlanta" gravado dentro. O jogo monta o nome como
                          `city/%s/%s_city.aib`.
    <cidade>.graph        TEXTO. Grafo de ruas. O `MinExtents` dele bate EXATO
                          com o campo em MapRoot+0x250 do .pck.
    <cidade>_pvs.aib      Mesmo formato do _city.aib, mas o ELF de PS2 nao tem
                          nenhuma string `pvs` que monte esse nome - so `$cpvs`
                          (token de .mod) e `nopvs`. Provavelmente nao e lido
                          nesta build.

Uma caixa ocluidora esconde o que estiver ATRAS dela. As 340 do atlanta
descrevem predios do atlanta; geometria importada que caia atras de uma delas
some, e nao ha nada na tela que explique por que. Como o arquivo e texto, da pra
testar a contribuicao disso em um minuto: afunda todas as caixas para bem abaixo
do mundo e veja quanto reaparece.

    python mc3_occlude.py                        # o que existe hoje
    python mc3_occlude.py --neutraliza           # afunda as caixas (faz backup)
    python mc3_occlude.py --restaura             # volta o backup

Nao e a versao final de nada: e um interruptor pra MEDIR quanto do "sumiu tudo"
e oclusao e quanto e outra coisa.
"""
import argparse
import os
import re
import shutil

RAIZ = os.path.join(os.environ.get('MC3_HOSTFS', ''), 'ASSETS/city')
FUNDO = 100000.0          # quanto afundar, em unidades de mundo


def caminho(cidade):
    return os.path.join(RAIZ, cidade, '%s.occlude' % cidade)


def le(cidade):
    with open(caminho(cidade), 'r', encoding='latin1') as f:
        return f.read()


def resume(texto):
    """(versao, num_geoms, num_primitives, [nome de cada ocluidor])."""
    def campo(nome):
        m = re.search(r'^%s:\s*(\d+)' % nome, texto, re.M)
        return int(m.group(1)) if m else -1
    nomes = re.findall(r'^;\|[^\r\n]*\|([^\t\r\n]+)\t\[(\d+)\]', texto, re.M)
    return campo('version'), campo('num_geoms'), campo('num_primitives'), nomes


def afunda(texto, dy=FUNDO):
    """Desce todo vertice e todo centro de esfera em `dy`.

    Mexer no Y e nao na contagem e de proposito. Zerar `num_geoms` mudaria o
    tamanho de tudo que vem depois e eu nao sei se o leitor aceita zero; assim o
    arquivo continua com a MESMA forma, mesmo numero de caixas, mesma ordem, e
    so o lugar delas muda. Se o jogo travar assim, o problema nao era oclusao.
    """
    saida = []
    for linha in texto.splitlines(True):
        s = linha.rstrip('\r\n')
        fim = linha[len(s):]
        if s.startswith('sphere:'):
            p = s.split()
            if len(p) == 5:
                p[2] = '%.7f' % (float(p[2]) - dy)
                saida.append(' '.join(p) + fim)
                continue
        else:
            p = s.split('\t')
            if len(p) == 3:
                try:
                    v = [float(x) for x in p]
                except ValueError:
                    saida.append(linha)
                    continue
                v[1] -= dy
                saida.append('\t'.join('%.7f' % x for x in v) + fim)
                continue
        saida.append(linha)
    return ''.join(saida)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--cidade', default='atlanta')
    ap.add_argument('--neutraliza', action='store_true')
    ap.add_argument('--restaura', action='store_true')
    ap.add_argument('--raiz', default=RAIZ)
    a = ap.parse_args()

    globals()['RAIZ'] = a.raiz
    alvo = caminho(a.cidade)
    bak = alvo + '.orig'

    if a.restaura:
        if not os.path.isfile(bak):
            raise SystemExit('sem backup em %s' % bak)
        shutil.copyfile(bak, alvo)
        print('restaurado %s' % alvo)
        return

    texto = le(a.cidade)
    ver, ng, npr, nomes = resume(texto)
    print('%s: version %d, num_geoms %d, num_primitives %d, %d caixa(s) nomeada(s)'
          % (os.path.basename(alvo), ver, ng, npr, len(nomes)))
    for nome, idx in nomes[:5]:
        print('   [%s] %s' % (idx, nome))
    if len(nomes) > 5:
        print('   ... mais %d' % (len(nomes) - 5))

    if not a.neutraliza:
        return

    if not os.path.isfile(bak):
        shutil.copyfile(alvo, bak)
        print('backup em %s' % bak)
    novo = afunda(texto)
    with open(alvo, 'w', encoding='latin1', newline='') as f:
        f.write(novo)
    print('afundadas %.0f unidades; %d bytes (era %d)'
          % (FUNDO, len(novo), len(texto)))
    print('para voltar: python mc3_occlude.py --restaura')


if __name__ == '__main__':
    main()
