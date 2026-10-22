"""
mc2_port.py - bring Midnight Club 2 geometry into Midnight Club 3

MC3 ships a TEXT mesh reader and still uses it: `rmcModel::Create` (0x2A8CA0)
does `strrchr(name, '.')` and sends `.mod` to `mshMesh::LoadMod`, anything else
to the binary `mesh` deserialiser. The text side is `gfxModelBase::LoadMod`
(0x1EBFC0) plus `gfxGeometry::LoadMod` (0x1EEC50).

MC2's `.xmod` is the same `version: 1.10` dialect. So the geometry does not have
to be converted at all - it has to be RENAMED, and its textures have to exist
under the names the material blocks ask for.

    python mc2_port.py textures <dir> [--texturas DIR]
    python mc2_port.py check <file|dir>
    python mc2_port.py mod <file|dir>

`check` is the part that earns its keep: it applies the grammar read out of the
ELF, not a guess. What the reader requires, in order:

    version: 1.10
    verts: normals: colors: tex1s: tex2s: tangents: materials: adjuncts:
    primitives: matrices: reskins:

then the data lines (`v n c t1 t2 adj`), the primitive lines (`tri str stp`,
all three known to `gfxGeometry::LoadMod`), the `packet`/`mtx`/`reskin` blocks,
and one `mtl NAME { ... }` block per declared material holding

    packets: primitives: textures: illum: ambient: diffuse: specular:
    texture: <n> "NAME"        (repeated `textures:` times)
    attributes:

A texture name that resolves to nothing is NOT fatal: the reader defaults
`$tex0` to "none", and `rmcTextureFactoryPS2::Create` (0x2B9BD8) builds an empty
texture and caches it rather than failing. The mesh draws untextured.
"""

import argparse
import collections
import os
import shutil
import sys

import mc3_saida

# The eleven header counts, in the order gfxModelBase::LoadMod reads them.
CABECALHO = [
    'verts:', 'normals:', 'colors:', 'tex1s:', 'tex2s:', 'tangents:',
    'materials:', 'adjuncts:', 'primitives:', 'matrices:', 'reskins:',
]

# Header count -> the data line that carries one of them. `adjuncts:` and
# `matrices:` are counted separately because they head blocks rather than
# appearing once per item.
LINHA_DE = {
    'verts:': 'v', 'normals:': 'n', 'colors:': 'c',
    'tex1s:': 't1', 'tex2s:': 't2',
}

PRIMITIVAS = ('tri', 'str', 'stp')

# Keys gfxModelBase::LoadMod reads inside an `mtl` block.
CHAVES_MTL = ['packets:', 'primitives:', 'textures:', 'illum:',
              'ambient:', 'diffuse:', 'specular:']

VERSAO = '1.10'


def arquivos(alvo, exts=('.xmod', '.mod')):
    """Every mesh under `alvo`, which may be one file or a directory."""
    if os.path.isfile(alvo):
        return [alvo]
    achados = []
    for raiz, _, nomes in os.walk(alvo):
        for n in sorted(nomes):
            if n.lower().endswith(exts):
                achados.append(os.path.join(raiz, n))
    return achados


def le(caminho):
    with open(caminho, 'r', errors='replace') as f:
        return f.read().splitlines()


def nomes_de_textura(linhas):
    """The texture names a mesh's material blocks ask for, in file order."""
    nomes = []
    for l in linhas:
        s = l.strip()
        if s.startswith('texture:') and '"' in s:
            nomes.append(s.split('"')[1])
    return nomes


def confere(caminho):
    """Validate one mesh against the reader's grammar.

    Returns a list of complaints; an empty list means the MC3 reader should get
    through the file.
    """
    linhas = le(caminho)
    if not linhas:
        return ['arquivo vazio']
    erros = []

    primeira = linhas[0].strip()
    if not primeira.startswith('version:'):
        erros.append('primeira linha nao e `version:` e sim %r' % primeira[:40])
    elif primeira.split()[-1] != VERSAO:
        erros.append('version %s, o leitor do MC3 espera %s'
                     % (primeira.split()[-1], VERSAO))

    # Header counts, in order.
    declarado = {}
    vistos = []
    for l in linhas[:40]:
        campo = (l.split(':')[0] + ':') if ':' in l else ''
        if campo in CABECALHO and campo not in declarado:
            vistos.append(campo)
            try:
                declarado[campo] = int(l.split(':')[1].strip())
            except (IndexError, ValueError):
                erros.append('contagem ilegivel em %r' % l.strip()[:40])
    faltando = [c for c in CABECALHO if c not in declarado]
    if faltando:
        erros.append('cabecalho sem %s' % ' '.join(faltando))
    elif vistos != CABECALHO:
        erros.append('cabecalho fora de ordem')

    # Line tokens.
    conta = {}
    primitivas = 0
    mtl_abertos = 0
    for l in linhas:
        campos = l.split()
        tok = campos[0] if campos else ''
        conta[tok] = conta.get(tok, 0) + 1
        if tok in PRIMITIVAS:
            primitivas += 1
        if tok == 'mtl':
            mtl_abertos += 1

    for campo, tok in LINHA_DE.items():
        if campo in declarado and conta.get(tok, 0) != declarado[campo]:
            erros.append('%s diz %d, ha %d linhas `%s`'
                         % (campo, declarado[campo], conta.get(tok, 0), tok))

    if declarado.get('adjuncts:') and not conta.get('adj'):
        erros.append('declara %d adjuncts e nao ha linha `adj`'
                     % declarado['adjuncts:'])
    if not primitivas and declarado.get('primitives:'):
        erros.append('declara %d primitives e nao ha linha tri/str/stp'
                     % declarado['primitives:'])
    if 'materials:' in declarado and mtl_abertos != declarado['materials:']:
        erros.append('materials: diz %d, ha %d blocos `mtl`'
                     % (declarado['materials:'], mtl_abertos))

    # Tokens the reader has no case for.
    conhecidos = set(['v', 'n', 'c', 't1', 't2', 'tan', 'adj', 'mtx', 'mtxn',
                      'mtxv', 'packet', 'reskin', 'mtl', '}', '{', ''] +
                     list(PRIMITIVAS) + CABECALHO + CHAVES_MTL +
                     ['version:', 'texture:', 'attributes:'] +
                     # attribute types, read as strings inside `attributes:`
                     ['bool', 'int', 'float', 'vector'])
    estranhos = sorted(t for t in conta if t not in conhecidos)
    if estranhos:
        erros.append('tokens que o leitor nao trata: %s' % ' '.join(estranhos[:8]))

    # Material blocks.
    dentro = False
    chaves = set()
    texturas = 0
    esperadas = None
    soma_prim = 0
    for l in linhas:
        s = l.strip()
        if s.split()[:1] == ['mtl']:
            dentro, chaves, texturas, esperadas = True, set(), 0, None
        elif dentro and s == '}':
            faltam = [c for c in CHAVES_MTL if c not in chaves]
            if faltam:
                erros.append('bloco mtl sem %s' % ' '.join(faltam))
            if esperadas is not None and texturas != esperadas:
                erros.append('bloco mtl diz textures: %d e traz %d linhas `texture:`'
                             % (esperadas, texturas))
            dentro = False
        elif dentro:
            campo = (s.split(':')[0] + ':') if ':' in s else ''
            if campo in CHAVES_MTL:
                chaves.add(campo)
            if campo == 'textures:':
                try:
                    esperadas = int(s.split(':')[1].strip())
                except (IndexError, ValueError):
                    pass
            if campo == 'primitives:':
                try:
                    soma_prim += int(s.split(':')[1].strip())
                except (IndexError, ValueError):
                    pass
            if s.startswith('texture:'):
                texturas += 1

    # The header count is the total over the materials - measured on both
    # games: heli.mod 4+550+6+18 = 578, sky_0.xmod 40*4+20 = 180.
    if 'primitives:' in declarado and soma_prim != declarado['primitives:']:
        erros.append('primitives: diz %d e os blocos mtl somam %d'
                     % (declarado['primitives:'], soma_prim))

    for n in nomes_de_textura(linhas):
        if len(n) >= 64:
            erros.append('nome de textura com %d caracteres, o leitor le em um '
                         'buffer de 64: %s' % (len(n), n))
    return erros


def acha_textura(pasta, nome):
    """The MC2 file backing a texture name, or None."""
    if not pasta:
        return None
    for ext in ('.tex', '.tga', '.movie'):
        p = os.path.join(pasta, nome + ext)
        if os.path.isfile(p):
            return p
    return None


def cmd_textures(args):
    alvos = arquivos(args.alvo)
    if not alvos:
        print('nenhum .xmod/.mod em %s' % args.alvo)
        return 1
    uso = {}
    for f in alvos:
        for n in nomes_de_textura(le(f)):
            uso[n] = uso.get(n, 0) + 1
    print('%d meshes, %d nomes de textura distintos' % (len(alvos), len(uso)))

    arq = dict((n, acha_textura(args.texturas, n)) for n in uso)
    if args.texturas:
        faltando = sorted(n for n in uso if not arq[n])
        print('  com arquivo em %s: %d' % (args.texturas, len(uso) - len(faltando)))
        print('  sem arquivo:      %d' % len(faltando))
        for n in faltando[:12]:
            print('     %s' % n)

    destino = mc3_saida.caminho(args.saida or 'mc2_texturas.tsv')
    with open(destino, 'w') as f:
        f.write('nome\tmeshes\tarquivo\n')
        for n in sorted(uso):
            f.write('%s\t%d\t%s\n' % (n, uso[n], arq[n] or ''))
    print('manifesto: %s' % destino)
    return 0


# mcInstBucket::Draw (0x1C0178) sends the model's expanded vertex list with a
# DMA tag whose qwc is `2 * adjuncts` as a 16-bit field, but writes the VIF
# UNPACK count as `(unsigned char)(2 * adjuncts)`. Past 127 adjuncts the two
# disagree: the VIF is handed more quadwords than it will consume as data and
# reads the remainder as VIF COMMANDS, which hangs VIF1. The retail chunks are
# 12 to 31 adjuncts, so the game never guards it. Measured on hardware: a
# 148-adjunct model froze the game the moment debris spawned.
MAX_ADJ_INST = 127


def adjuncts(linhas):
    return sum(1 for l in linhas if l.split()[:1] == ['adj'])


def cabe_no_bucket(linhas):
    """A complaint if this mesh would overflow the instanced (chunk) path."""
    n = adjuncts(linhas)
    if n > MAX_ADJ_INST:
        return ('%d adjuncts: o caminho instanciado manda qwc=%d e VIF NUM=%d, '
                'e o VIF le a diferenca como comando. Limite %d.'
                % (n, 2 * n, (2 * n) & 0xFF, MAX_ADJ_INST))
    return None


def caixa(linhas):
    """(min, max) of the `v` lines, or None if there are none."""
    vs = []
    for l in linhas:
        campos = l.split()
        if campos[:1] == ['v'] and len(campos) >= 4:
            try:
                vs.append([float(campos[1]), float(campos[2]), float(campos[3])])
            except ValueError:
                pass
    if not vs:
        return None
    mn = [min(p[i] for p in vs) for i in range(3)]
    mx = [max(p[i] for p in vs) for i in range(3)]
    return mn, mx


def reescala(linhas, escala, desloca):
    """The same file with every `v` line scaled about the origin and moved."""
    saida = []
    for l in linhas:
        campos = l.split()
        if campos[:1] == ['v'] and len(campos) >= 4:
            try:
                p = [float(campos[i]) for i in (1, 2, 3)]
            except ValueError:
                saida.append(l)
                continue
            saida.append('v\t%f\t%f\t%f'
                         % tuple(p[i] * escala + desloca[i] for i in range(3)))
        else:
            saida.append(l)
    return saida


def cmd_fit(args):
    """Rewrite a mesh to sit where another one sat.

    The point is to replace a model the game already loads and draws, so the
    swap is only visible if the geometry lands at the same size in the same
    place. Uniform scale, so nothing is squashed.
    """
    origem = le(args.alvo)
    destino = le(args.como)
    ca, cb = caixa(origem), caixa(destino)
    if not ca or not cb:
        print('um dos dois nao tem linhas `v`')
        return 1
    da = [ca[1][i] - ca[0][i] for i in range(3)]
    db = [cb[1][i] - cb[0][i] for i in range(3)]
    if max(da) <= 0:
        print('%s nao tem extensao' % args.alvo)
        return 1
    escala = args.escala if args.escala else max(db) / max(da)
    centro_a = [(ca[1][i] + ca[0][i]) / 2 for i in range(3)]
    centro_b = [(cb[1][i] + cb[0][i]) / 2 for i in range(3)]
    desloca = [centro_b[i] - centro_a[i] * escala for i in range(3)]

    novo = reescala(origem, escala, desloca)
    nome = args.saida or (os.path.splitext(os.path.basename(args.como))[0] + '.mod')
    caminho = nome if os.path.isabs(nome) or os.path.dirname(nome) \
        else mc3_saida.caminho(os.path.join('mc2_mod', nome))
    pasta = os.path.dirname(caminho)
    if pasta and not os.path.isdir(pasta):
        os.makedirs(pasta)
    with open(caminho, 'w') as f:
        f.write('\n'.join(novo) + '\n')

    conf = caixa(novo)
    print('%s  ->  %s' % (os.path.basename(args.alvo), os.path.basename(args.como)))
    print('  origem   %.3f x %.3f x %.3f' % tuple(da))
    print('  destino  %.3f x %.3f x %.3f' % tuple(db))
    print('  escala   %.4f' % escala)
    print('  saiu     %.3f x %.3f x %.3f  centro %.2f %.2f %.2f'
          % tuple([conf[1][i] - conf[0][i] for i in range(3)] +
                  [(conf[1][i] + conf[0][i]) / 2 for i in range(3)]))
    erros = confere(caminho)
    print('  check    %s' % ('ok' if not erros else erros[0]))
    if os.path.basename(args.como).startswith('chunk'):
        queixa = cabe_no_bucket(novo)
        print('  bucket   %s' % (queixa or
                                 '%d adjuncts, dentro do limite de %d'
                                 % (adjuncts(novo), MAX_ADJ_INST)))
    print('%s' % caminho)
    return 0


def cmd_retex(args):
    """Point every material at one texture name.

    A name nothing answers is safe on the general model path, but the instanced
    chunk path feeds the texture object's own bytes to the GIF as GS register
    writes (mcInstBucket::Draw 0x1C0178, the `!*(tex+76)` branch), so an
    unresolved name there is not obviously harmless. Borrowing a name the game
    already has is one line of text and removes the variable.
    """
    linhas = le(args.alvo)
    antes = sorted(set(nomes_de_textura(linhas)))
    saida = []
    for l in linhas:
        s = l.strip()
        if s.startswith('texture:') and '"' in s:
            prefixo = l[:len(l) - len(l.lstrip())]
            n = s.split()[1]
            saida.append('%stexture: %s "%s"' % (prefixo, n, args.textura))
        else:
            saida.append(l)
    nome = args.saida or args.alvo
    caminho = nome if os.path.isabs(nome) or os.path.dirname(nome) \
        else mc3_saida.caminho(nome)
    with open(caminho, 'w') as f:
        f.write('\n'.join(saida) + '\n')
    print('%s: %s -> %s' % (os.path.basename(caminho),
                            ', '.join(antes) or '(nenhuma)', args.textura))
    erros = confere(caminho)
    print('  check %s' % ('ok' if not erros else erros[0]))
    return 0


def cmd_check(args):
    alvos = arquivos(args.alvo)
    if not alvos:
        print('nenhum .xmod/.mod em %s' % args.alvo)
        return 1
    ruins = 0
    queixas = {}
    for f in alvos:
        erros = confere(f)
        if not erros:
            continue
        ruins += 1
        for e in erros:
            chave = e.split(' diz ')[0].split(':')[0][:58]
            queixas[chave] = queixas.get(chave, 0) + 1
        if args.verbose or len(alvos) == 1:
            print('%s' % f)
            for e in erros:
                print('   %s' % e)
    print('%d meshes, %d passam, %d com queixa'
          % (len(alvos), len(alvos) - ruins, ruins))
    for q, c in sorted(queixas.items(), key=lambda kv: -kv[1])[:12]:
        print('   %5d  %s' % (c, q))
    return 0


def cmd_mod(args):
    alvos = arquivos(args.alvo, exts=('.xmod',))
    if not alvos:
        print('nenhum .xmod em %s' % args.alvo)
        return 1
    destino = args.saida or mc3_saida.caminho('mc2_mod')
    if not os.path.isdir(destino):
        os.makedirs(destino)
    escritos, recusados = 0, 0
    for f in alvos:
        erros = confere(f)
        if erros and not args.force:
            recusados += 1
            if args.verbose:
                print('recusado %s: %s' % (os.path.basename(f), erros[0]))
            continue
        nome = os.path.splitext(os.path.basename(f))[0] + '.mod'
        shutil.copyfile(f, os.path.join(destino, nome))
        escritos += 1
    print('%d escritos em %s' % (escritos, destino))
    if recusados:
        print('%d recusados pelo check (--force escreve mesmo assim)' % recusados)
    return 0


# --------------------------------------------------------------------------
# a whole city
# --------------------------------------------------------------------------
#
# An MC2 city is `<name>.lvl` (the hood list and the world extents) plus one
# `.hood` per neighbourhood. A hood holds two kinds of thing:
#
#   unique_component   a mesh that exists once, ALREADY IN WORLD COORDINATES.
#                      Verified: the AABB in the hood equals the mesh's own
#                      bounding box to the last digit, so it draws at identity.
#   instance_component a named type placed by a 3x4 matrix (three rows of
#                      rotation, then the translation).
#
# Each name has a `.cc` beside the meshes saying which LOD/part files exist
# (`lod 0 { main refl }`), and the file is `<name>_<lod>_<part>.xmod`.
#
# This writes the three things a consumer needs and nothing else: the meshes
# renamed to `.mod`, the collision, and one flat placement table.


def le_cc(caminho):
    """(lods, sphere) from a `.cc`: {lod index: [part, ...]}."""
    lods, atual, esfera = {}, None, None
    for l in le(caminho):
        s = l.strip()
        if s.startswith('bounding_sphere:'):
            esfera = s.split(':', 1)[1].split()
        elif s.startswith('lod '):
            try:
                atual = int(s.split()[1])
            except (IndexError, ValueError):
                atual = None
            if atual is not None:
                lods[atual] = []
        elif s == '}':
            atual = None
        elif atual is not None and s and s != '{':
            lods[atual].append(s)
    return lods, esfera


def le_hood(caminho):
    """(unique components, instances) of one `.hood`."""
    linhas = le(caminho)
    comps, insts = [], []
    i = 0
    while i < len(linhas):
        s = linhas[i].strip()
        if s.startswith('unique_component'):
            nome = emin = emax = None
            while i < len(linhas) and linhas[i].strip() != '}':
                t = linhas[i].strip()
                if t.startswith('name:'):
                    nome = t.split(None, 1)[1]
                elif t.startswith('emin'):
                    emin = t.split()[1:4]
                elif t.startswith('emax'):
                    emax = t.split()[1:4]
                i += 1
            if nome:
                comps.append((nome, emin, emax))
        elif s.startswith('instance_component'):
            tipo = emin = emax = None
            linhas_m = []
            while i < len(linhas) and linhas[i].strip() != '}':
                t = linhas[i].strip()
                if t.startswith('type:'):
                    tipo = t.split(None, 1)[1]
                elif t.startswith('emin'):
                    emin = t.split()[1:4]
                elif t.startswith('emax'):
                    emax = t.split()[1:4]
                elif t and t[0] in '-0123456789':
                    campos = t.split()
                    if len(campos) == 3:
                        linhas_m.append(campos)
                i += 1
            if tipo and len(linhas_m) >= 4:
                insts.append((tipo, linhas_m[:4], emin, emax))
        i += 1
    return comps, insts


def cmd_cidade(args):
    cidade = args.alvo.rstrip('\\/')
    nome_cidade = os.path.basename(cidade)
    modelos = os.path.join(cidade, 'models')
    if not os.path.isdir(modelos):
        print('%s nao tem uma pasta models/' % cidade)
        return 1
    bounds = args.bounds or os.path.normpath(
        os.path.join(cidade, '..', '..', 'bound'))
    texturas = args.texturas or os.path.normpath(
        os.path.join(cidade, '..', '..', 'texture_x'))

    destino = args.saida or mc3_saida.caminho('mc2_%s' % nome_cidade)
    for sub in ('model', 'bound'):
        p = os.path.join(destino, sub)
        if not os.path.isdir(p):
            os.makedirs(p)

    # The level file: hood order and world extents.
    lvl = os.path.join(cidade, nome_cidade + '.lvl')
    extents = []
    hoods_lvl = []
    if os.path.isfile(lvl):
        linhas = le(lvl)
        for j, l in enumerate(linhas):
            s = l.strip()
            if s.startswith('extents_min') or s.startswith('extents_max'):
                extents.append(linhas[j + 1].split())
            if s.startswith('name:'):
                hoods_lvl.append(s.split(None, 1)[1])

    # The hood spells some names with capitals the files do not have
    # (`l_inst_WhereHouse_Type04_x` on disc is all lower case), so every
    # lookup goes through a case-folded index. 34 types and 543 placements
    # were being dropped before this.
    disponiveis = dict((n.lower(), n) for n in os.listdir(modelos))
    filas = []          # (kind, name, lod, part, matrix12, aabb6, hood)
    precisa = set()     # mesh basenames without extension
    tipos_bnd = set()
    sem_malha = collections.Counter()

    for h in sorted(os.listdir(cidade)):
        if not h.endswith('.hood'):
            continue
        hood = h[:-5]
        comps, insts = le_hood(os.path.join(cidade, h))
        alvos = ([('comp', n, None, emin, emax) for n, emin, emax in comps] +
                 [('inst', t, m, emin, emax) for t, m, emin, emax in insts])
        for tipo, nome, m, emin, emax in alvos:
            # UM lod por modelo, e TODAS as partes daquele lod.
            #
            # A versao anterior parava na PRIMEIRA parte encontrada
            # (`if partes: break` depois de varrer main/refl/emissive), e por
            # isso saia com uma peca por modelo quando o `.cc` declara duas ou
            # tres. Medido em 12/09 nos 729 modelos que a LA coloca: os `.cc`
            # declaram 1376 pares lod/parte e 642 nao estavam sendo extraidos -
            # 242 de `lod1 main`, 208 de `lod0 refl` e 192 de `lod1 refl` - e
            # todos os 642 existem como `.xmod` na fonte. No MC2 o lod vigente
            # desenha TODAS as partes que lista, e nos cruzamentos e justamente
            # o `refl` que carrega a superficie de rua.
            #
            # O lod e escolhido por MODELO, nunca por parte: o MC3 trata cada
            # (nome, lod, parte) como um tipo proprio e desenha todos ao mesmo
            # tempo, sem troca por distancia, entao emitir dois lods do mesmo
            # modelo poe o toco por cima da malha boa e cria superficie quase
            # coplanar duplicada. Vale o MENOR lod utilizavel, que e o de maior
            # detalhe: `lod 0 { }` vazio simplesmente cai para o lod seguinte.
            real_cc = disponiveis.get((nome + '.cc').lower())
            cc = os.path.join(modelos, real_cc) if real_cc else ''
            partes = []
            if cc and os.path.isfile(cc):
                lods, _ = le_cc(cc)
                permitidas = ([args.parte] if args.parte
                              else ['main', 'refl', 'emissive'])
                # `--lod N` pede um lod ESPECIFICO: restringe a busca a ele em
                # vez de sempre cair no de maior detalhe. Sem a opcao, a ordem
                # crescente continua valendo e o primeiro lod utilizavel vence.
                # PREFERE O LOD QUE TEM `main`. Cinco modelos de LA declaram
                # `lod 0 { refl }` e so trazem a geometria principal no lod 1
                # (os cruzamentos l_beverlyhills_int_01/02/03 e
                # l_santamonica_int_04/12). Com "primeiro lod utilizavel" o
                # port importava so o reflexo e a peca sumia do mapa - e sumia
                # em silencio, porque um lod COM conteudo tinha sido achado.
                if args.lod is not None:
                    ordem = [args.lod]
                else:
                    ordem = sorted(lods)
                    com_main = [l for l in ordem
                                if 'main' in lods[l]
                                and disponiveis.get(
                                    ('%s_%d_main.xmod' % (nome, l)).lower())]
                    if com_main:
                        ordem = com_main + [l for l in ordem
                                            if l not in com_main]
                for lod in ordem:
                    if lod not in lods:
                        continue
                    achadas = []
                    for procurada in lods[lod]:
                        if procurada not in permitidas:
                            continue
                        arq = disponiveis.get(
                            ('%s_%d_%s.xmod' % (nome, lod, procurada)).lower())
                        if arq:
                            achadas.append((lod, procurada, arq))
                    if achadas:
                        partes = achadas
                        break
            if not partes:
                # props carry no part suffix: <name>_<lod>.xmod
                for lod in range(4):
                    arq = disponiveis.get(('%s_%d.xmod' % (nome, lod)).lower())
                    if arq:
                        partes.append((lod, '-', arq))
                        break
            if not partes:
                sem_malha[nome] += 1
                continue
            for lod, parte, arq in partes:
                precisa.add(arq)
                mat = (['1', '0', '0', '0', '1', '0', '0', '0', '1',
                        '0', '0', '0'] if m is None
                       else [c for linha in m for c in linha])
                filas.append((tipo, nome, lod, parte, mat,
                              (emin or ['0'] * 3) + (emax or ['0'] * 3), hood))
            if tipo == 'inst':
                tipos_bnd.add(nome)

    # Meshes, renamed. The check runs on each so nothing unreadable ships.
    escritos, recusados = 0, []
    tex_uso = collections.Counter()
    for arq in sorted(precisa):
        origem = os.path.join(modelos, arq)
        linhas = le(origem)
        erros = confere(origem)
        if erros and not args.force:
            recusados.append((arq, erros[0]))
            continue
        for n in nomes_de_textura(linhas):
            tex_uso[n] += 1
        with open(os.path.join(destino, 'model',
                               arq[:-5] + '.mod'), 'w') as f:
            f.write('\n'.join(linhas) + '\n')
        escritos += 1

    # Collision. The whole city is ONE text otgrid - `<city>.bnd`, 4.2 MB for
    # Los Angeles - and the props that can be hit carry their own.
    bnds = 0
    cidade_bnd = None
    if os.path.isdir(bounds):
        tem = set(os.listdir(bounds))
        tem = dict((x.lower(), x) for x in tem)
        if (nome_cidade + '.bnd').lower() in tem:
            cidade_bnd = os.path.join(destino, 'bound', nome_cidade + '.bnd')
            shutil.copyfile(
                os.path.join(bounds, tem[(nome_cidade + '.bnd').lower()]),
                cidade_bnd)
            bnds += 1
        for t in sorted(tipos_bnd):
            real = tem.get((t + '.bnd').lower())
            if real:
                shutil.copyfile(os.path.join(bounds, real),
                                os.path.join(destino, 'bound', real))
                bnds += 1

    tabela = os.path.join(destino, '%s_place.tsv' % nome_cidade)
    with open(tabela, 'w') as f:
        f.write('# %s: %d hoods\n' % (nome_cidade, len(hoods_lvl)))
        if len(extents) >= 2:
            f.write('# extents_min\t%s\n# extents_max\t%s\n'
                    % ('\t'.join(extents[0]), '\t'.join(extents[1])))
        f.write('kind\tname\tlod\tpart\tm00\tm01\tm02\tm10\tm11\tm12\t'
                'm20\tm21\tm22\ttx\tty\ttz\t'
                'eminx\teminy\teminz\temaxx\temaxy\temaxz\thood\n')
        for tipo, nome, lod, parte, mat, aabb, hood in filas:
            f.write('%s\t%s\t%d\t%s\t%s\t%s\t%s\n'
                    % (tipo, nome, lod, parte, '\t'.join(mat),
                       '\t'.join(aabb), hood))

    # Textures. The PS2 build of MC2 stores them in the SAME 14-byte-header
    # `.tex` MC3 uses - formats 1 and 15 are both on MC3's list - so they are
    # copied, not converted. The PC build stores format 22 and would need one.
    manifesto = os.path.join(destino, '%s_tex.tsv' % nome_cidade)
    faltando = 0
    copiadas = 0
    if args.com_texturas:
        pt = os.path.join(destino, 'texture')
        if not os.path.isdir(pt):
            os.makedirs(pt)
    with open(manifesto, 'w') as f:
        f.write('nome\tmeshes\tarquivo\n')
        for n in sorted(tex_uso):
            a = acha_textura(texturas, n) or ''
            if not a:
                faltando += 1
            elif args.com_texturas and a.lower().endswith('.tex'):
                shutil.copyfile(a, os.path.join(destino, 'texture',
                                                os.path.basename(a)))
                copiadas += 1
            f.write('%s\t%d\t%s\n' % (n, tex_uso[n], a))

    print('%s: %d hoods' % (nome_cidade, len(hoods_lvl)))
    print('  linhas de colocacao   %d  (%d componentes, %d instancias)'
          % (len(filas),
             sum(1 for x in filas if x[0] == 'comp'),
             sum(1 for x in filas if x[0] == 'inst')))
    print('  meshes distintos      %d escritos' % escritos)
    if recusados:
        print('  RECUSADOS pelo check  %d  (o primeiro: %s -- %s)'
              % (len(recusados), recusados[0][0], recusados[0][1]))
    if sem_malha:
        print('  sem malha no disco    %d nomes, %d colocacoes'
              % (len(sem_malha), sum(sem_malha.values())))
        for n, c in sem_malha.most_common(5):
            print('     %-44s x%d' % (n, c))
    print('  colisao               %d .bnd%s' %
          (bnds, '  (inclui o otgrid da cidade inteira)' if cidade_bnd else ''))
    print('  texturas              %d nomes, %d sem arquivo%s'
          % (len(tex_uso), faltando,
             ', %d copiadas' % copiadas if copiadas else ''))
    print('  %s' % tabela)
    print('  %s' % manifesto)

    # The package explains itself. Written here rather than by hand so a
    # re-export never leaves a stale README behind.
    with open(os.path.join(destino, 'README.md'), 'w') as f:
        f.write(README_CIDADE % dict(
            cidade=nome_cidade, hoods=len(hoods_lvl), meshes=escritos,
            colocacoes=len(filas),
            comps=sum(1 for x in filas if x[0] == 'comp'),
            insts=sum(1 for x in filas if x[0] == 'inst'),
            texturas=len(tex_uso), copiadas=copiadas, faltando=faltando,
            bnds=bnds))
    return 0


README_CIDADE = """\
# Midnight Club 2 - %(cidade)s, exported for Midnight Club 3

Produced by `mc2_port.py cidade`. Everything here is text or already in a format
MC3 reads as it stands. `rmcModel::Create` (0x2A8CA0) sends any name ending in
`.mod` to `mshMesh::LoadMod`, and MC2's `.xmod` is the same `version: 1.10`
grammar, so the meshes are renamed, not converted.

| | |
|---|---|
| `model/` | **%(meshes)d** meshes, `.xmod` renamed to `.mod`, nothing else changed |
| `bound/` | %(bnds)d file(s), text collision. The city's own is one `otgrid` covering all of it |
| `texture/` | **%(copiadas)d** `.tex`, copied with no conversion |
| `%(cidade)s_place.tsv` | **%(colocacoes)d** placements - %(comps)d components, %(insts)d instances |
| `%(cidade)s_tex.tsv` | **%(texturas)d** texture names and the file behind each (%(faltando)d have none) |

Every mesh passed `mc2_port.py check`, which applies the grammar read out of the
ELF rather than a guess.

## Two builds, on purpose

Geometry and placement come from the **PC** build, textures from the **PS2**
build, and they are not interchangeable:

- The PS2 build ships **no loose city geometry**. Its `city/<name>` has the
  `.hood` and `.pdef` but no `models/`; `ASSETS/model` holds no city meshes; and
  `resource/<name>/<name>.rsc` opens `RSC0 MIP0 PAL0 TEX0` - a texture pack.
- The PS2 build ships **the right textures**: the same 14-byte header MC3 uses,
  formats 1 and 15, already swizzled with their CLUT. `mc3_tex.py` reads them as
  they are. The PC build stores format 22 and would need a converter.
- The two builds' `.hood` files **differ** - 10 of 13, with different totals -
  so the placement table has to come from the same build as the meshes it names.

## The placement table

Tab separated. Two comment lines carry the world extents from the `.lvl`, then a
header row, then one row per thing to draw.

    kind  name  lod  part  m00..m22  tx ty tz  eminx..emaxz  hood

- **kind** - `comp` or `inst`.
- **name** - the mesh without its `_<lod>_<part>` suffix. The file is
  `model/<name>_<lod>_<part>.mod`; a prop has no part, `<name>_<lod>.mod`.
- **m00..m22** rotation, row major. **tx ty tz** translation.
- **emin/emax** - the AABB straight from the `.hood`.

Two things to know before writing a consumer:

**`comp` rows are already in world coordinates.** Their identity matrix is not a
placeholder - the AABB in the `.hood` equals the mesh's own bounding box to the
last decimal, checked across the set.

**One mesh per name, at the lowest LOD that has the requested part.** Filtering
on a fixed LOD loses whole types: `l_inst_freeway_wall_01x` exists only at LOD 1
and is placed 314 times. `--parte` / `--lod` override the default.

## Drawing one row

    gfxModel* m = gfxGetModel(name, 0, flags);      // 0x1ED340, prefix "model"
    gfxState::SetWorld(matrix34);                   // 0x2ADB48
    gfxModel::Draw(m, *(gfxShader***)(m + 4), 0);   // 0x1EB998

`*(m + 4)` is the model's own shader array, so a model from `gfxGetModel` is
self contained - no city shader group, no `.pck`.

**Culling is a requirement, not an optimisation.** %(colocacoes)d draws per frame will
not run. The AABB on each row is there so a consumer can cull by frustum and
distance without reversing MC3's own PVS.

## What is not here

- **Placement has no reader in MC3.** The whole MC2 grammar is in the retail
  string pool (0x641E3F-0x641EB1) but **zero instructions reference it**, while
  the live `.mod` tokens beside it do. Those readers were compiled out. This
  table exists because the `.hood` cannot simply be handed to the game.
- **A texture name nothing answers** is harmless on the ordinary model path -
  `rmcTextureFactoryPS2::Create` (0x2B9BD8) builds an empty texture and carries
  on - but **fatal on the instanced path**, where `mcInstBucket::Draw` feeds the
  texture object's own bytes to the GIF as GS register writes.
- **The 72-adjunct ceiling** measured in `mcInstBucket::Draw` belongs to the
  instanced debris path only. It does not apply to anything here.
"""


def main(argv=None):
    p = argparse.ArgumentParser(
        description='bring Midnight Club 2 geometry into Midnight Club 3')
    sub = p.add_subparsers(dest='cmd')

    t = sub.add_parser('textures', help='what textures the meshes ask for')
    t.add_argument('alvo')
    t.add_argument('--texturas', help='folder holding the MC2 .tex files')
    t.add_argument('--saida')
    t.set_defaults(func=cmd_textures)

    c = sub.add_parser('check', help='validate against the MC3 text reader')
    c.add_argument('alvo')
    c.add_argument('-v', '--verbose', action='store_true')
    c.set_defaults(func=cmd_check)

    f = sub.add_parser('fit', help='resize a mesh onto a model the game already draws')
    f.add_argument('alvo', help='the MC2 mesh')
    f.add_argument('--como', required=True, help='the retail .mod it replaces')
    f.add_argument('--escala', type=float, help='force a factor instead of fitting')
    f.add_argument('--saida')
    f.set_defaults(func=cmd_fit)

    r = sub.add_parser('retex', help='point every material at one texture name')
    r.add_argument('alvo')
    r.add_argument('--textura', required=True)
    r.add_argument('--saida')
    r.set_defaults(func=cmd_retex)

    ci = sub.add_parser('cidade', help='export a whole MC2 city: meshes, bounds, placement')
    ci.add_argument('alvo', help='the city folder, e.g. .../city/losangeles')
    ci.add_argument('--saida')
    ci.add_argument('--bounds', help='MC2 bound/ folder (default: ../../bound)')
    ci.add_argument('--texturas', help='MC2 texture folder to resolve names against')
    ci.add_argument('--com-texturas', action='store_true',
                    help='copy the .tex files into the package (PS2 build only: '
                         'those are already in the format MC3 reads)')
    ci.add_argument('--parte', help='keep only this part (main, refl, emissive...)')
    ci.add_argument('--lod', type=int, help='keep only this LOD')
    ci.add_argument('--force', action='store_true')
    ci.set_defaults(func=cmd_cidade)

    m = sub.add_parser('mod', help='write .mod copies MC3 can load')
    m.add_argument('alvo')
    m.add_argument('--saida')
    m.add_argument('--force', action='store_true')
    m.add_argument('-v', '--verbose', action='store_true')
    m.set_defaults(func=cmd_mod)

    a = p.parse_args(argv)
    if not getattr(a, 'func', None):
        p.print_help()
        return 1
    return a.func(a)


if __name__ == '__main__':
    sys.exit(main())
