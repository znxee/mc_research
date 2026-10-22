r"""Instala um .pck de cidade nas variantes de clima - e SO nelas.

POR QUE ISTO EXISTE. Instalei uma cidade com um laco `startswith('losangeles_')`
que excluia apenas `_fog` e `_bnd`, e ele SOBRESCREVEU `losangeles_peds.pck` (tipo
0x21) e `losangeles_traffic.pck` (tipo 0x3C) com um arquivo de cidade (tipo 0x43).
O jogo abria o peds, encontrava uma cidade, e ficava em LOADING INFINITO - com
o EE vivo a 60 Hz, o que fez o sintoma parecer coisa da geometria. Filtrar por
prefixo e frageil; este script filtra pelo TIPO no cabecalho, que e o que o jogo
de fato le.

O CONTRATO DAS CELULAS TAMBEM E CONFERIDO: cell_count fica em MapRoot+0x268 e
tem que ser igual em <cidade>.pck, _props.pck e _peds.pck. Uma cidade nova com
extents diferentes muda a grade e quebra o contrato em silencio.

    python mc3_instala_cidade.py cidade.pck --destino <ASSETS/resources/city> --prefixo losangeles
"""
import argparse
import os
import struct

TIPO_CIDADE = 0x43

# O que cada irmao de uma cidade DEVE ser. Instalar por prefixo de nome ja
# sobrescreveu peds (0x21), traffic (0x3C) e ate os .ppf de textura com um
# arquivo de cidade - e o sintoma foi loading infinito, nao erro.
TIPOS = {0x43: 'cidade', 0x04: 'fog', 0x21: 'peds', 0x3C: 'traffic',
         0x09: 'bnd', 0x40: 'props'}


def esperado_por_nome(f):
    if f.endswith('.ppf'):
        return 'ppf'
    for suf, rot in (('_peds.pck', 'peds'), ('_traffic.pck', 'traffic'),
                     ('_bnd.pck', 'bnd')):
        if f.endswith(suf):
            return rot
    if 'props' in f:
        return 'props'
    return 'fog' if '_fog' in f else 'cidade'


ESPERADOS_MIN = ('_props.pck', '_peds.pck', '_traffic.pck', '_bnd.pck')


def confere_conjunto(destino, prefixo):
    """Avisa se um IRMAO OBRIGATORIO da cidade nao existe. Faltar um props
    inteiro (nao so estar com cell_count errado) deu loading infinito e demorei
    a achar porque eu so olhava os arquivos que ESTAVAM la."""
    tem = os.listdir(destino)
    falta = []
    for suf in ESPERADOS_MIN:
        if suf == '_props.pck':
            # ha 18: 9 climas x (props, garage_props)
            n = sum(1 for f in tem if f.startswith(prefixo) and 'props' in f)
            if n < 18:
                falta.append('props (achei %d de 18)' % n)
        elif not any(f.startswith(prefixo) and f.endswith(suf) for f in tem):
            falta.append(suf)
    return falta


def audita(destino, prefixo):
    """Confere TIPO de cada irmao contra o que o nome promete. Devolve os erros."""
    erros = []
    print('%-36s %-9s %-11s %s' % ('arquivo', 'tipo', 'bytes', 'estado'))
    for f in sorted(os.listdir(destino)):
        if not f.startswith(prefixo):
            continue
        p = os.path.join(destino, f)
        n = os.path.getsize(p)
        quer = esperado_por_nome(f)
        if quer == 'ppf':
            bom = open(p, 'rb').read(4) == b'pf05'
            tem = 'ppf' if bom else 'CORROMPIDO'
        else:
            t = cabecalho(p)[1]
            tem = TIPOS.get(t, '?%02X' % t)
            bom = tem == quer
        if not bom:
            erros.append('%s: e %s, deveria ser %s' % (f, tem, quer))
        print('%-36s %-9s %-11d %s' % (f, tem, n, 'OK' if bom else 'ESPERADO ' + quer))
    return erros


def cabecalho(p):
    with open(p, 'rb') as f:
        d = f.read(16)
    return struct.unpack('<4I', d) if len(d) == 16 else (0, 0, 0, 0)


def celulas_cidade(p):
    """cell_count da cidade: MapRoot+0x268, que e W*H da grade."""
    with open(p, 'rb') as f:
        d = f.read(0x400)
    return struct.unpack_from('<I', d, 0x80 + 0x268)[0]


def celulas_peds(p):
    """Entradas do array por celula do peds. O offset e OUTRO - ler o da cidade
    aqui dava alarme falso. Ponteiro em 0x2A4, objeto em 0x280; a contagem e a
    distancia ate o proximo objeto, como o mc3_cellcount.py faz."""
    d = open(p, 'rb').read()
    if len(d) <= 0x2B0:
        return None
    base = struct.unpack_from('<I', d, 0)[0]
    ini = struct.unpack_from('<I', d, 0x2A4)[0] - base + 0x80
    if not (0 < ini <= len(d)):
        return None
    return (len(d) - ini) // 4


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cidade', nargs='?', default='')
    ap.add_argument('--destino', required=True)
    ap.add_argument('--prefixo', required=True)
    ap.add_argument('--aplicar', action='store_true')
    ap.add_argument('--auditar', action='store_true',
                    help='so confere o tipo de cada irmao e sai')
    a = ap.parse_args()

    if a.auditar:
        erros = audita(a.destino, a.prefixo)
        falta = confere_conjunto(a.destino, a.prefixo)
        for f in falta:
            erros.append('IRMAO AUSENTE: %s' % f)
        print('')
        print('conjunto %s' % ('COERENTE' if not erros else 'COM PROBLEMA'))
        for e in erros:
            print('   ' + e)
        raise SystemExit(1 if erros else 0)

    _, tipo, _, _ = cabecalho(a.cidade)
    if tipo != TIPO_CIDADE:
        raise SystemExit('%s tem tipo %02X, nao %02X - nao e cidade'
                         % (a.cidade, tipo, TIPO_CIDADE))
    n_cel = celulas_cidade(a.cidade)
    print('%s: tipo %02X, %d celulas' % (os.path.basename(a.cidade), tipo, n_cel))

    alvos, outros = [], []
    for f in sorted(os.listdir(a.destino)):
        if not f.startswith(a.prefixo) or not f.endswith('.pck'):
            continue
        p = os.path.join(a.destino, f)
        t = cabecalho(p)[1]
        (alvos if t == TIPO_CIDADE else outros).append((f, t, p))

    for f, t, p in outros:
        marca = ''
        if f.endswith('_peds.pck') or f.endswith('_props.pck'):
            c = celulas_peds(p)
            if c is None:
                marca = '  (nao consegui ler a contagem)'
            else:
                marca = '  %d entradas %s' % (
                    c, 'OK' if c >= n_cel else '< %d DA CIDADE - rode mc3_cellcount.py' % n_cel)
        print('  preservado %-34s tipo %02X%s' % (f, t, marca))

    print('  %d variante(s) de cidade a substituir' % len(alvos))
    if not a.aplicar:
        print('')
        print('  ENSAIO - nada gravado. Repita com --aplicar.')
        return
    dados = open(a.cidade, 'rb').read()
    for f, t, p in alvos:
        open(p, 'wb').write(dados)
    print('  gravado em %d arquivo(s)' % len(alvos))


if __name__ == '__main__':
    main()
