"""Ponte: cidade do MC2 de PS2 -> o place.tsv e os .mod que o mc3_city_build le.

O porte de LA vinha sendo alimentado pelo export do MC2 de PC. A Fork MC2 PS2
decodificou a build de PS2 (mc2_rsc.py) e ela e uma fonte melhor por tres
motivos medidos por eles:

  * a geometria ja esta em formato de PS2 - cada batch PMD0 e UMA TRIANGLE STRIP,
    que e exatamente o que o mc3_city_build consome;
  * a regra de enrolamento e a MESMA dos dois lados. O Batch.triangles() do
    mc2_rsc usa (i-2,i-1,i) para i par e (i-1,i-2,i) para i impar, e o tris_of()
    do mc2_to_mc3 usa a identica. Nao ha conversao de winding no meio;
  * a colocacao vem dos .hood em texto, com 294 unique_component assados em
    mundo e 8500 instance_component com matriz.

O QUE ESTA PONTE NAO RESOLVE, e esta anotado porque a fork avisou:

  * 24 das 8500 matrizes tem DETERMINANTE NEGATIVO - o PS2 trocou malha
    espelhada por matriz espelhada, e o PC nao tem nenhuma. Onde o determinante
    e negativo o winding inverte e a face aparece virada. Aqui elas sao
    MARCADAS na coluna `hood` do tsv? Nao - sao contadas e relatadas, e o
    --sem-espelhadas as descarta, que e o comportamento seguro ate o builder
    saber inverter indice.
  * 1734 das matrizes tem escala != 1 e 1487 delas sao nao uniformes. O raio de
    cull do MC3 e LOCAL do tipo, entao instancia escalada pode sumir cedo. A
    fork mediu a pior razao em 2.54x e a maior folga absoluta em 7.71 unidades.

    python mc2_ps2_place.py <losangeles.rsc> --out output/mc2_la_ps2
"""
import argparse
import struct
import importlib.util
import io
import os
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))
_SPEC = importlib.util.spec_from_file_location(
    'mc2_rsc', os.path.join(_AQUI, 'mc2_rsc.py'))
rsc_mod = importlib.util.module_from_spec(_SPEC)
sys.modules['mc2_rsc'] = rsc_mod
_SPEC.loader.exec_module(rsc_mod)

CABECALHO = ('kind\tname\tlod\tpart\tm00\tm01\tm02\tm10\tm11\tm12\tm20\tm21'
             '\tm22\ttx\tty\ttz\teminx\teminy\teminz\temaxx\temaxy\temaxz\thood')


def indice_cpv(cpvs):
    """nome do PCP0 -> indice de entrada."""
    out = {}
    for h, (fcc, nome) in cpvs.names.items():
        if fcc == 'PCP0':
            out[nome] = (h & 0x3FFF) - 1
    return out


def cpv_do_modelo(nome, mapa):
    """A entrada de CPV que serve para este modelo, e se ela e exata.

    Nos 294 componentes assados o nome do PCP0 e '<nome>_0_main' e a cor e
    EXATA, porque cada componente tem malha propria. Nas instancias o nome e
    '<owner>_<tipo><extension>_<lod>_<main|refl>' - ou seja o MC2 guarda cor
    POR INSTANCIA (13.756 PCP0 para 8.774 batches), enquanto o MC3 compartilha
    uma malha por tipo. Entao para tipo de instancia so da para escolher UMA
    instancia como representante, e a cor das outras sai aproximada. Marcado no
    retorno para o relatorio nao esconder isso.
    """
    exato = mapa.get('%s_0_main' % nome)
    if exato is not None:
        return exato, True
    alvo = '_%s' % nome.lower()
    for k in sorted(mapa):
        kl = k.lower()
        if kl.endswith('_0_main') and alvo in kl:
            return mapa[k], False
    return None, False


def tiras_do_modelo(rsc, modelo, cpvs=None, ent_cpv=None,
                    dup_adc=True):
    """(posicoes, uvs, tiras) de um modelo, ja com o ADC respeitado.

    Um batch e uma strip. O byte de ADC com 0x80 diz "nao desenhe o triangulo
    que termina aqui", e o formato de texto do PC nao tem esse conceito.

    A MINHA PRIMEIRA VERSAO QUEBRAVA A TIRA nesse ponto, e estava errada. O
    enrolamento do MC2 e do MC3 e (i-2,i-1,i) para i PAR e (i-1,i-2,i) para i
    IMPAR, com a paridade contada do inicio da tira. Reiniciar a tira zera essa
    contagem: se o corte cai num k par, todo triangulo seguinte daquele pedaco
    sai com o enrolamento trocado, a face aponta para dentro e some no
    back-face culling. Como o corte cai em par ou impar por acaso, isso apagava
    perto de metade das faces depois de cada ADC - foi o "muita face sem
    aparecer" que o usuario viu na tela.

    A traducao certa e DUPLICAR DOIS VERTICES em vez de cortar:

        ... k-2, k-1, [k-1, k-1], k, k+1 ...

    Os tres triangulos que nascem nos indices duplicados sao degenerados (area
    zero, nao desenham), e um deles ocupa exatamente a posicao do triangulo que
    o ADC queria suprimir. E como sao DOIS vertices, a paridade de tudo o que
    vem depois fica intacta. A tira continua inteira, o que ainda por cima gera
    menos pontes de degenerado no strips_to_blocks.
    """
    pos, uv, cor, tiras = [], [], [], []
    if cpvs is not None and ent_cpv is not None:
        # A cadeia que DESENHA e a do PCP0: ela faz `ref` na geometria dentro do
        # PMD0 e acrescenta a cor, entao read_pcp devolve pos/uv/adc/cpv juntos
        # e nao ha risco de os dois lados sairem fora de ordem. Achado da Fork
        # MC2 PS2; usar read_pmd em paralelo seria reinventar o pareamento.
        lotes = rsc_mod.read_pcp(rsc, cpvs, ent_cpv)
    else:
        lotes = []
        for h in rsc_mod.model_blocks(modelo, lod=None):
            r = rsc.resolve(h)
            if r is not None:
                lotes.extend(rsc_mod.read_pmd(rsc, r[1])[0])
    if True:
        for batch in lotes:
            base = len(pos)
            pos.extend(batch.pos)
            uv.extend(batch.uv)
            # o elemento 0 do stream de CPV E COR, ao contrario do de ADC, onde
            # ele e a contagem de vertices - a fork mediu que so 123 de 50.170
            # batches coincidem por acaso. Entao aqui nao se pula o primeiro.
            cor.extend(getattr(batch, 'cpv', None) or [0] * len(batch.pos))
            corrente = [base, base + 1] if len(batch.pos) >= 2 else []
            for k in range(2, len(batch.pos)):
                if dup_adc and k < len(batch.adc) and (batch.adc[k] & 0x80):
                    corrente += [corrente[-1], corrente[-1]]
                corrente.append(base + k)
            if len(corrente) >= 3:
                tiras.extend(parte_tira(corrente))
    return pos, uv, cor, tiras


# O limite do retail, medido nos 1353 meshes de cidade do atlanta.
MAX_VERTS = 48
TIRA = 'str'          # ver a nota no escreve_mod


def parte_tira(t):
    """Quebra uma tira longa em pedacos de no maximo MAX_VERTS, sem mudar
    nenhum triangulo.

    O strips_to_blocks NUNCA parte uma tira: ele so decide se CONCATENA a
    proxima no bloco corrente. Isso funcionava com o MC2 de PC, onde as tiras
    sao minusculas (a torre wfargo tem 287 tiras, quase todas de 4 vertices),
    e quebra com o PS2, onde um batch e uma tira longa - medido nos 723
    modelos, 62,9%% dos blocos passavam de 48 vertices e o maior tinha 131.

    E ISSO EXPLODE NA VU1: os tres streams do bloco ficam em enderecos fixos
    com 48 qwords cada - normal em 160, uv em 208, posicao em 256. Um bloco de
    131 vertices escreve 131 qwords a partir de 160 e invade os outros dois,
    entao a posicao passa a ser lida de onde estava a UV. Na tela isso vira
    triangulo gigante atravessando a cena, com a VU1 em 99,9%%.

    A QUEBRA PRESERVA A PARIDADE. O enrolamento e (i-2,i-1,i) para i par e
    (i-1,i-2,i) para i impar, contado do inicio da tira, entao um pedaco novo
    so pode comecar num deslocamento PAR. Os pedacos tem 48 vertices e avancam
    de 46, sobrepondo os dois ultimos - 46 e par, entao todo inicio cai em
    indice par e o enrolamento continua o mesmo. A sobreposicao de dois e o que
    mantem a cadeia de triangulos ligada atraves do corte.
    """
    # 46 e nao 48: o `abre()` do strips_to_blocks acrescenta UM vertice
    # duplicado na frente de toda tira `stp` para ela cair em indice impar, e
    # com pedaco de 48 o bloco saia com 49 - um a mais que a regiao da VU1.
    # 46 e par, entao o passo de 44 tambem e, e a paridade continua de pe.
    teto = MAX_VERTS - 2
    if len(t) <= teto:
        return [t]
    passo = teto - 2
    out = []
    s = 0
    while s < len(t) - 2:
        pedaco = t[s:s + teto]
        if len(pedaco) >= 3:
            out.append(pedaco)
        s += passo
    return out


def escreve_mod(caminho, pos, uv, cor, tiras):
    """O texto que o read_xmod do mc2_to_mc3 ja sabe ler.

    `adj` usa os campos 1 e 4 (vertice e uv); o `packet` no inicio zera a base
    dos indices de tira, entao aqui tudo e indexado globalmente.
    """
    with io.open(caminho, 'w', encoding='latin1') as f:
        for x, y, z in pos:
            f.write('v %.6f %.6f %.6f\n' % (x, y, z))
        for u, w in uv:
            f.write('t1 %.6f %.6f\n' % (u, w))
        f.write('packet %d %d\n' % (len(pos), len(tiras)))
        # O campo 3 do `adj` e a COR. No formato do MC2 a tupla e
        # `adj <vertice> <normal> <cor> <uv>` e o read_xmod ja lia os campos
        # 1 e 4; agora le o 3 tambem. E onde o indice de paleta cabe sem
        # inventar registro novo no formato.
        for i in range(len(pos)):
            f.write('adj %d 0 %d %d\n' % (i, cor[i] if i < len(cor) else 0, i))
        # `str` E NAO `stp`, e isto foi MEDIDO, nao escolhido.
        #
        # O strips_to_blocks mapeia `stp` para impar=True, e o abre() dele
        # prepende um vertice duplicado para a tira cair em indice IMPAR. Esse
        # mapeamento foi medido no MC2 de PC, cuja convencao e a INVERSA da do
        # MC3. O dado de PS2 nao e: ele vem de uma display list de PS2 de
        # verdade, com o mesmo (i-2,i-1,i) para i par que o MC3 usa - entao a
        # tira tem que comecar em indice PAR, sem o vertice extra, que e o que
        # `str` produz.
        #
        # Medido bloco a bloco contra o decodificador da Fork MC2 PS2 em 120
        # modelos: com `stp` sao 0 de 120 corretos e 34.817 triangulos apenas
        # INVERTIDOS; com `str` sao 120 de 120 e zero invertidos. Na tela o
        # `stp` aparecia como fileira de triangulos alternados, com a maioria
        # das faces sumindo no back-face culling.
        for t in tiras:
            f.write('str %d %s\n' % (len(t), ' '.join(str(i) for i in t)))


def determinante(m):
    return (m[0] * (m[4] * m[8] - m[5] * m[7])
            - m[1] * (m[3] * m[8] - m[5] * m[6])
            + m[2] * (m[3] * m[7] - m[4] * m[6]))


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('rsc')
    ap.add_argument('--out', default='output/mc2_la_ps2')
    ap.add_argument('--cpvs', metavar='CPVS.RSC',
                    help='<hora>_cpvs.rsc do MC2 de PS2: leva a cor por vertice')
    ap.add_argument('--angel', action='store_true',
                    help='emite o dialeto Angel Studios completo: paridade por '
                         'tira, material por textura e cor por vertice. E o que '
                         'o mc3_mesh_convert e o proprio jogo leem, e o '
                         'read_xmod do toolkit tambem le, porque e superconjunto')
    ap.add_argument('--tira', choices=('stp', 'str'), default='str',
                    help='paridade da tira; str e a medida certa (120/120)')
    ap.add_argument('--sem-adc', action='store_true',
                    help='ignora o bit ADC em vez de degenerar o triangulo')
    ap.add_argument('--sem-espelhadas', action='store_true',
                    help='descarta as instancias de determinante negativo')
    a = ap.parse_args()

    globals()['TIRA'] = a.tira
    rsc = rsc_mod.Rsc(a.rsc)
    cpvs = rsc_mod.Rsc(a.cpvs) if a.cpvs else None
    mapa_cpv = indice_cpv(cpvs) if cpvs else {}
    paleta = None
    if cpvs:
        for _o, _f, _sz in cpvs.entries:
            if _f == 'CPP0':
                _b = cpvs.data[_o:_o + _sz]
                paleta = [struct.unpack_from('<3B', _b, _k * 4)
                          for _k in range(256)]
                break
    porNome = rsc_mod.models_by_name(rsc)
    pasta = rsc_mod.city_folder(a.rsc)
    comps, insts = rsc_mod.read_hoods(pasta)

    dmod = os.path.join(a.out, 'model')
    if not os.path.isdir(dmod):
        os.makedirs(dmod)

    # ---- os modelos, uma vez cada
    precisa = set([c.name for c in comps] + [i.type for i in insts])
    escritos = 0
    vazios = []
    cor_exata = cor_aprox = sem_cor = 0
    for nome in sorted(precisa):
        m = porNome.get(nome.lower()) or porNome.get(nome)
        if m is None:
            vazios.append(nome)
            continue
        ent, exato = cpv_do_modelo(nome, mapa_cpv) if cpvs else (None, False)
        if a.angel:
            lotes = (rsc_mod.read_pcp(rsc, cpvs, ent)
                     if (cpvs and ent is not None) else [])
            if not lotes:
                lotes = []
                for h in rsc_mod.model_blocks(m, lod=None):
                    r = rsc.resolve(h)
                    if r is not None:
                        lotes.extend(rsc_mod.read_pmd(rsc, r[1])[0])
            def _tex(h):
                nm = rsc.texture_name(h)
                return (nm or 'sem_textura').replace(' ', '_')
            if escreve_mod_angel(os.path.join(dmod, '%s_0_main.mod' % nome),
                                 lotes, paleta, _tex):
                escritos += 1
                if cpvs:
                    if ent is None:
                        sem_cor += 1
                    elif exato:
                        cor_exata += 1
                    else:
                        cor_aprox += 1
            else:
                vazios.append(nome)
            continue
        pos, uv, cor, tiras = tiras_do_modelo(rsc, m, cpvs, ent,
                                              not a.sem_adc)
        if not tiras:
            vazios.append(nome)
            continue
        escreve_mod(os.path.join(dmod, '%s_0_main.mod' % nome), pos, uv, cor, tiras)
        escritos += 1
        if cpvs:
            if ent is None:
                sem_cor += 1
            elif exato:
                cor_exata += 1
            else:
                cor_aprox += 1
    print('modelos: %d escritos, %d sem geometria' % (escritos, len(vazios)))
    if cpvs:
        print('cor por vertice: %d exata (componente), %d aproximada (uma '
              'instancia representa o tipo), %d sem cor'
              % (cor_exata, cor_aprox, sem_cor))

    # ---- o place.tsv
    linhas = []
    espelhadas = 0
    for c in comps:
        linhas.append(['comp', c.name, '0', 'main',
                       '1', '0', '0', '0', '1', '0', '0', '0', '1',
                       '0', '0', '0']
                      + ['%.6f' % x for x in list(c.emin) + list(c.emax)]
                      + [c.hood])
    for i in insts:
        m = [x for linha in i.rot for x in linha]
        if determinante(m) < 0:
            espelhadas += 1
            if a.sem_espelhadas:
                continue
        linhas.append(['inst', i.type, '0', 'main']
                      + ['%.6f' % x for x in m]
                      + ['%.6f' % x for x in i.pos]
                      + ['%.6f' % x for x in list(i.emin) + list(i.emax)]
                      + [i.hood])

    mn = [min(float(l[16 + k]) for l in linhas) for k in range(3)]
    mx = [max(float(l[19 + k]) for l in linhas) for k in range(3)]
    saida = os.path.join(a.out, 'losangeles_ps2_place.tsv')
    with io.open(saida, 'w', encoding='latin1') as f:
        f.write('# %s: %d hoods (fonte: MC2 de PS2)\n'
                % (os.path.splitext(os.path.basename(a.rsc))[0],
                   len(set(c.hood for c in comps) | set(i.hood for i in insts))))
        f.write('# extents_min\t%.6f\t%.6f\t%.6f\n' % tuple(mn))
        f.write('# extents_max\t%.6f\t%.6f\t%.6f\n' % tuple(mx))
        f.write(CABECALHO + '\n')
        for l in linhas:
            f.write('\t'.join(l) + '\n')

    ncomp = sum(1 for l in linhas if l[0] == 'comp')
    ninst = len(linhas) - ncomp
    print('place: %d componentes + %d instancias -> %s' % (ncomp, ninst, saida))
    print('extents: x %.1f..%.1f  y %.1f..%.1f  z %.1f..%.1f'
          % (mn[0], mx[0], mn[1], mx[1], mn[2], mx[2]))
    print('instancias com determinante NEGATIVO: %d%s'
          % (espelhadas, ' (descartadas)' if a.sem_espelhadas else
             ' (mantidas - o winding delas vai sair invertido)'))



# ---------------------------------------------------------------------------
#  A ROTA DE TEXTO
# ---------------------------------------------------------------------------
#
# O jogo constroi o .pck sozinho: rmcModel::Create le .mesh/.mod em TEXTO e
# rmcGeometry::Packet::Init 0x2AB110 e quem EMITE O VIF. Estripificacao,
# paridade, ADC e corte em bloco sao trabalho dele. Emitir pacote VIF a mao,
# que era o que esta ponte fazia, foi a origem dos tres ultimos defeitos:
# paridade do ADC (6.486 triangulos errados), estouro de 48 vertices por bloco
# (triangulo gigante, VU1 em 99,9%) e stp/str global (maioria das faces sumindo).
#
# Aqui a ponte passa a emitir o dialeto Angel Studios de verdade - o que o
# mc3_mesh_convert.py le - em vez do dialeto simplificado que so o read_xmod do
# toolkit entendia.
#
# TRES COISAS QUE O DIALETO RESOLVE DE GRACA:
#
#   * PARIDADE POR TIRA. Os .mod de varejo MISTURAM `str` e `stp` no mesmo
#     packet (o arrow4.mod tem 16 str, um stp e outro str). A regra do leitor e
#     `(i-2,i-1,i)` quando `(i par) == (str)`, ou seja `str` e o enrolamento
#     natural do PS2/MC3 e `stp` e o invertido. Entao um pedaco que comeca num
#     deslocamento PAR sai `str` e um que comeca em IMPAR sai `stp`, e o ADC
#     deixa de exigir vertice duplicado.
#   * MATERIAL POR TEXTURA. Cada batch do PMD0 carrega um handle de textura;
#     agrupando por ele saem varios `mtl`, em vez do indice de material unico
#     que a cidade gerada vinha usando.
#   * COR POR VERTICE. O dialeto tem `c r g b a` com quatro floats e o `adj`
#     aponta para ele. O mc3_mesh_convert AINDA descarta esse canal na leitura -
#     a FORK C++ anotou isso e disse que Cpv e a primeira prioridade de melhoria
#     do leitor - mas o texto ja sai correto, entao quando ele passar a ler a
#     cidade ganha cor sem mexer aqui.

CAB_MOD = ('version: 1.10\n'
           'verts: %d\nnormals: %d\ncolors: %d\ntex1s: %d\ntex2s: 0\n'
           'tangents: 0\nmaterials: %d\nadjuncts: %d\nprimitives: %d\n'
           'matrices: 1\nreskins: 1\n\n')


def pedacos_por_adc(n, adc):
    """[(deslocamento, [indices locais])] de um batch, cortando no ADC.

    Sem duplicar vertice: o corte vira um pedaco novo e a paridade dele e
    escolhida pelo deslocamento, que e o que o dialeto permite dizer.
    """
    out = []
    ini = 0
    for k in range(2, n):
        if k < len(adc) and (adc[k] & 0x80):
            if k - ini >= 3:
                out.append((ini, list(range(ini, k))))
            ini = k - 1
    if n - ini >= 3:
        out.append((ini, list(range(ini, n))))
    return out


def escreve_mod_angel(caminho, lotes, paleta, nome_tex):
    """Um .mod no dialeto que o mc3_mesh_convert (e o jogo) leem."""
    V, T1, C = [], [], []
    icor = {}
    pacotes = []                      # (textura, [adj], [(tipo, [locais])])
    for b in lotes:
        base_v = len(V)
        V.extend(b.pos)
        T1.extend(b.uv)
        cpv = getattr(b, 'cpv', None) or [0] * len(b.pos)
        adjs = []
        for k in range(len(b.pos)):
            idx = cpv[k] if k < len(cpv) else 0
            if idx not in icor:
                icor[idx] = len(C)
                r, g, bl = paleta[idx] if paleta else (128, 128, 128)
                C.append((r / 128.0, g / 128.0, bl / 128.0, 1.0))
            adjs.append((base_v + k, 0, icor[idx], base_v + k))
        prims = []
        for desl, idxs in pedacos_por_adc(len(b.pos), b.adc):
            # deslocamento PAR mantem o enrolamento; IMPAR o inverte
            prims.append(('str' if desl % 2 == 0 else 'stp', idxs))
        if prims:
            pacotes.append((nome_tex(b.texture), adjs, prims))

    if not pacotes:
        return 0
    por_mtl = {}
    for tex, adjs, prims in pacotes:
        por_mtl.setdefault(tex, []).append((adjs, prims))
    n_adj = sum(len(a) for _t, a, _p in pacotes)
    n_tri = sum(len(i) - 2 for _t, _a, p in pacotes for _k, i in p)

    with io.open(caminho, 'w', encoding='utf-8') as f:
        f.write(CAB_MOD % (len(V), 1, len(C), len(T1), len(por_mtl),
                           n_adj, n_tri))
        for x, y, z in V:
            f.write('v\t%f\t%f\t%f\n' % (x, y, z))
        f.write('n\t0.000000\t1.000000\t0.000000\n')
        for c in C:
            f.write('c\t%f\t%f\t%f\t%f\n' % c)
        for u, w in T1:
            f.write('t1\t%f\t%f\n' % (u, w))
        f.write('\n')
        for tex, blocos in por_mtl.items():
            f.write('mtl %s {\n\tpackets:\t%d\n\tprimitives:\t%d\n'
                    '\ttextures:\t1\n\tillum: diffuse\n'
                    '\tambient:\t0.000000 0.000000 0.000000\n'
                    '\tdiffuse:\t1.000000 1.000000 1.000000\n'
                    '\tspecular:\t0.000000 0.000000 0.000000\n'
                    '\ttexture: 0 "%s"\n\tattributes:\t0\n}\n\n'
                    % (tex, len(blocos),
                       sum(len(i) - 2 for _a, p in blocos for _k, i in p), tex))
            for adjs, prims in blocos:
                f.write('packet %d %d 1 {\n' % (len(adjs), len(prims)))
                for v, n, c, t in adjs:
                    f.write('\tadj\t%d\t%d\t%d\t%d\t-1\t0\n' % (v, n, c, t))
                base = adjs[0][0]
                for tipo, idxs in prims:
                    f.write('\t%s\t%d\t%s\n'
                            % (tipo, len(idxs), '\t'.join(str(i) for i in idxs)))
                f.write('\tmtx 0 \n}\n\n')
    return len(pacotes)

if __name__ == '__main__':
    main()
