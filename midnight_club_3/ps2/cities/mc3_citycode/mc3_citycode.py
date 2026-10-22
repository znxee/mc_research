"""Clone the assets a city is found by, from one short code to another.

The city's SHORT CODE is not a label. It is the key half of a filename: the
loader builds `loading_generic_<code>.pck` and `loadscreen_career_filler_<code>
06.pck` and opens them. A city registered with a code nothing answers to hangs
on the loading screen, which is how this was found - by scanning EE RAM for the
strings the game had built, not by reading code.

    python mc3_citycode.py --donor t --new m            # what it would copy
    python mc3_citycode.py --donor t --new m --write

WHAT IT WILL AND WILL NOT COPY

A file is city-keyed when its name ends in `_<code>` or `_<code><digits>` before
the extension. That alone would also match `foo_t.pck` where the `t` means
something else entirely, so it is not enough: a file is only cloned when THE
SAME SLOT EXISTS FOR AT LEAST TWO OTHER KNOWN CITY CODES. `loading_generic_t`
qualifies because `_a`, `_d` and `_s` are all there beside it; an accidental
`_t` has no such family and is left alone.

That check is the whole reason this is safe to run over a directory of 156
files. It is also why it can be wrong in the other direction - a city asset that
only ever existed for one city will not be recognised. If a boot still hangs,
scan RAM for the name it built rather than trusting this list.

DIRECTORIES TOO, IN NAME MODE

A city owns four directories named after it, and missing them is not cosmetic:
`tune/traffic/<name>/` holds the traffic densities, so a city cloned without
them comes up with no traffic at all.

    city/<name>          tune/ped/<name>
    tune/race/<name>     tune/traffic/<name>

They are cloned whole, and files INSIDE get the same renaming - `tokyo_dawn
.density` becomes `losangeles_dawn.density`, while `dawn_clear/` and `fped01.cal`
keep the names they have. A destination that already exists is merged into, not
replaced: hand-made files there survive.
"""
import argparse
import os
import re
import shutil

ASSETS_PADRAO = os.path.join(os.environ.get('MC3_HOSTFS', ''), 'ASSETS')
CODIGOS = ('s', 'a', 'd', 't')          # sd, atlanta, detroit, tokyo
NOMES = ('sd', 'atlanta', 'detroit', 'tokyo')
MIN_FAMILIA = 2                          # other cities that must share the slot


def fatia_nome(nome, cidade):
    """('<cidade>_', 'resto') - os assets de dados usam o NOME, nao a sigla.

    Two conventions in one game, and it costs a boot to find out: the loading
    screen builds `loading_generic_<code>.pck` from the short code, while the
    city data builds `city/<name>_<time>_<weather>.ppf` from the full name.
    """
    # Two shapes, and missing the second one cost `tokyo.override` on the first
    # run: `<name>_<rest>` for tokyo_midnight_clear.pck, and `<name>.<ext>` for
    # tokyo.loc / tokyo.locinf / tokyo.override, which have no underscore at all.
    baixo = nome.lower()
    if baixo.startswith(cidade + '_'):
        return cidade + '_', nome[len(cidade) + 1:]
    if baixo.startswith(cidade + '.'):
        return cidade, nome[len(cidade):]        # o resto ja comeca com o ponto
    return None


def fatia(nome, codigo):
    """('prefixo', 'sufixo') se `nome` for do formato <pref>_<codigo><digitos><ext>."""
    m = re.match(r'^(.*_)%s(\d*)(\.[^.]+)$' % re.escape(codigo), nome, re.I)
    if not m:
        return None
    return m.group(1), m.group(2) + m.group(3)


def familia(arquivos, monta, doador, universo):
    """Quantas OUTRAS cidades tem exatamente o mesmo slot."""
    n = 0
    for c in universo:
        if c == doador:
            continue
        if monta(c).lower() in arquivos:
            n += 1
    return n


def varre(raiz, doador, novo):
    por_nome = doador in NOMES
    universo = NOMES if por_nome else CODIGOS
    planos = []
    for base, _dirs, nomes in os.walk(raiz):
        presentes = set(n.lower() for n in nomes)
        for n in nomes:
            if por_nome:
                corte = fatia_nome(n, doador)
                if not corte:
                    continue
                _pref, resto = corte
                # `resto` carries its own separator: '_' was consumed above for
                # the underscore shape, and the dotted shape keeps its dot.
                sep = '' if resto.startswith('.') else '_'
                monta = lambda c, r=resto, j=sep: c + j + r
            else:
                corte = fatia(n, doador)
                if not corte:
                    continue
                prefixo, sufixo = corte
                monta = lambda c, p=prefixo, s=sufixo: p + c + s
            if familia(presentes, monta, doador, universo) < MIN_FAMILIA:
                continue
            planos.append((os.path.join(base, n),
                           os.path.join(base, monta(novo)),
                           familia(presentes, monta, doador, universo)))
    return sorted(planos)


def varre_dirs(raiz, doador, novo):
    """[(origem, destino)] dos diretorios com o nome da cidade.

    Only in name mode: `tune/traffic/t` is not a thing, the directories are
    always spelled out. The family check is the same idea as for files - a
    directory only counts when at least two other cities have one beside it.
    """
    planos = []
    for base, dirs, _f in os.walk(raiz):
        presentes = set(d.lower() for d in dirs)
        for d in dirs:
            if d.lower() != doador:
                continue
            irmaos = sum(1 for c in NOMES if c != doador and c in presentes)
            if irmaos < MIN_FAMILIA:
                continue
            planos.append((os.path.join(base, d), os.path.join(base, novo)))
    return sorted(planos)


def clona_dir(origem, destino, doador, novo, escrever):
    """Copia recursivo, renomeando os arquivos prefixados com a cidade."""
    n = 0
    for base, _dirs, nomes in os.walk(origem):
        rel = os.path.relpath(base, origem)
        alvo = destino if rel == '.' else os.path.join(destino, rel)
        if escrever and not os.path.isdir(alvo):
            os.makedirs(alvo)
        for f in nomes:
            corte = fatia_nome(f, doador)
            saida = (novo + corte[1] if corte and corte[1].startswith('.')
                     else novo + '_' + corte[1] if corte else f)
            cheio = os.path.join(alvo, saida)
            if os.path.exists(cheio):
                continue
            n += 1
            if escrever:
                shutil.copyfile(os.path.join(base, f), cheio)
    return n


def main():
    p = argparse.ArgumentParser(
        description='clona os assets indexados pela sigla da cidade')
    p.add_argument('--assets', default=ASSETS_PADRAO)
    p.add_argument('--donor', default='t',
                   help='sigla (t) para os assets de tela, ou nome (tokyo) '
                        'para os dados de cidade - o modo sai daqui')
    p.add_argument('--new', required=True, help='sigla ou nome da cidade nova')
    p.add_argument('--write', action='store_true',
                   help='sem isso, so lista o que faria')
    a = p.parse_args()

    if a.donor.lower() == a.new.lower():
        raise SystemExit('doador e destino sao a mesma sigla')

    doador = a.donor.lower()
    if doador not in CODIGOS and doador not in NOMES:
        raise SystemExit('doador %r nao e sigla (%s) nem nome (%s)'
                         % (a.donor, '/'.join(CODIGOS), '/'.join(NOMES)))
    modo = 'nome' if doador in NOMES else 'sigla'
    print('modo: %s de cidade  (%s -> %s)' % (modo, doador, a.new.lower()))
    planos = varre(a.assets, doador, a.new.lower())
    if not planos:
        raise SystemExit('nada com %s %r em %s' % (modo, a.donor, a.assets))

    novos = feitos = 0
    for origem, destino, irmaos in planos:
        existe = os.path.exists(destino)
        marca = 'ja existe' if existe else ('copia' if a.write else 'copiaria')
        print('   %-46s -> %-46s [%d irmaos] %s'
              % (os.path.basename(origem), os.path.basename(destino),
                 irmaos, marca))
        if existe:
            continue
        novos += 1
        if a.write:
            shutil.copyfile(origem, destino)
            feitos += 1

    if modo == 'nome':
        dirs = varre_dirs(a.assets, doador, a.new.lower())
        print()
        for origem, destino in dirs:
            n = clona_dir(origem, destino, doador, a.new.lower(), a.write)
            print('   %-46s -> %-30s %d arquivo(s) %s'
                  % (os.path.relpath(origem, a.assets),
                     os.path.relpath(destino, a.assets), n,
                     'copiados' if a.write else 'a copiar'))
            feitos += n if a.write else 0
            novos += n

    print()
    print('%d arquivos com %s %r, %d faltando para %r%s'
          % (len(planos), modo, a.donor, novos, a.new,
             (', %d copiados' % feitos) if a.write else ' (use --write)'))


if __name__ == '__main__':
    main()
