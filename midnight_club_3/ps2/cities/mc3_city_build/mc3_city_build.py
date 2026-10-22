"""
mc3_city_build.py - build a Midnight Club 3 PS2 city .pck from nothing

Every city experiment so far has been a transplant into atlanta, and that makes
results hard to read: when something looks wrong on screen there is no way to
tell whether it is the imported geometry or the host city that produced it. This
builds the file instead, so everything inside it is accounted for.

WHAT IS GENERATED and what is COPIED, stated plainly, because the difference is
the whole point:

  generated   the 0x80 header, the MapRoot, the hood table, the hood record,
              the unique components, the ComponentData, the meshes, the group
              and block tables, the VIF packets, and the two colour palettes.
  copied      one shader object (0xAC bytes + the sub-object it points at) and
              the MapRoot scalars whose meaning is not established yet. Each
              copy is marked `COPIADO` at the call site.

The copies are what they are because a shader carries GS register state we have
not decoded (see mc3-city-materials); a shader has exactly ONE internal pointer,
at +0x08, aimed at the object right behind it, so relocating one is a single
fixup. Nothing else in it points anywhere - the rest is vtables, which are
absolute ELF addresses and stay valid wherever the object lands.

    python mc3_city_build.py --doador atlanta_midnight_clear.pck --saida novo.pck
    python mc3_city_build.py --doador ... --xmod M.xmod --saida novo.pck
    python mc3_city_build.py --verificar novo.pck

The default content is a test cube, which is the smallest thing that proves the
whole chain: if a cube appears at a known place with a known size, the header,
the hood walk, the component placement, the mesh tables and the VIF packet are
all correct, and anything that fails afterwards is narrower than that.
"""

import argparse
import importlib.util
import math
import os
import struct
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))
_SPEC = importlib.util.spec_from_file_location(
    'mc2_to_mc3', os.path.join(_AQUI, 'experimental', 'mc2_to_mc3.py'))
mc2 = importlib.util.module_from_spec(_SPEC)
sys.modules['mc2_to_mc3'] = mc2
_SPEC.loader.exec_module(mc2)

BASE_VA = 0x06800000        # a mesma de toda cidade do retail
TIPO_CIDADE = 67
VERSAO = 1

# O ESPACO DE TOKEN E POR CIDADE, e ignorar isso foi um bug meu.
#
# As constantes VT_* deste arquivo foram todas medidas no ATLANTA. Medido:
# atlanta, detroit e sd usam o mesmo espaco (MapRoot+0x00 = 0x007A0138) mas o
# TOKYO usa o mesmo espaco deslocado de +0x488 (0x007A05C0). Gerando uma cidade
# hospedada no tokyo eu escrevia MapRoot+0x00 e os 18 descritores de grupo com
# os tokens do ATLANTA - o arquivo saia com estrutura em tokyo e tokens de
# atlanta misturados.
#
# O deslocamento e descoberto do proprio doador em `token_do_doador`, e todo
# token emitido passa por `tok()`. Nao ha tabela de cidades: le-se o
# MapRoot+0x00 do doador e compara-se com a constante medida aqui.
DESLOC_TOKEN = 0            # preenchido por token_do_doador()


def tok(v):
    """Um token de classe no espaco do doador."""
    return v + DESLOC_TOKEN


def token_do_doador(doador):
    """Descobre o deslocamento do espaco de token do doador pelo MapRoot+0x00."""
    with open(doador, 'rb') as f:
        f.seek(0x80)
        v = struct.unpack('<I', f.read(4))[0]
    d = v - VT_MAPROOT
    if d not in (0, 0x488):
        raise SystemExit(
            'espaco de token desconhecido no doador: MapRoot+0x00 = 0x%08X, '
            'esperava 0x%08X (atlanta/detroit/sd) ou 0x%08X (tokyo)'
            % (v, VT_MAPROOT, VT_MAPROOT + 0x488))
    return d


VT_MAPROOT = 0x007A0138
VT_MAPROOT_40 = 0x007A01E8
VT_ARRAY = 0x007A1FB8       # o objeto [vtable][ptr][count][count][0]
# REGRA GERAL, aprendida dolorosamente: um objeto que EU crio nao entra na lista
# que o jogo percorre pra traduzir token -> endereco. Medido na RAM: 607 meshes do
# retail viraram 0x00626D98 e o meu ficou com 0x007A1E18; 240 ComponentData
# viraram 0x00625098 e o meu ficou com 0x0079FF88. Objeto gerado tem que JA
# NASCER com o endereco traduzido.
#
# Isto nao vale pros objetos que o Place CONSTROI (MapRoot, descritor de grupo,
# shader): esses tem a vtable carimbada pelo proprio construtor, entao o que
# estiver no arquivo e sobrescrito.
VT_MESH_TOKEN = 0x007A1E18
VT_MESH = 0x00626D98
VT_SHADER = 0x007A1EF8      # a classe padrao: 1951 dos 4105 objetos do atlanta
# ComponentData+0x28 e uma VTABLE de verdade, chamada quando a camera chega
# perto. No ARQUIVO ela vale 0x0079FF88 nos 651 componentes do atlanta, mas isso
# e um TOKEN: medido na RAM, os componentes do retail viram **0x00625098** e o
# unico que ficou com o token cru era o meu. O tradutor percorre uma lista em que
# o componente gerado nao entra, entao escrever o token deixa a chamada virtual
# saltar pra dentro da tabela de strings UTF-16 do jogo - o `Jump to unaligned
# address (PC: 0x0061004d)` e literalmente "Ma" de um nome de carro, lido do
# slot +0x38 dessa "vtable".
#
# Escrever o endereco JA TRADUZIDO resolve sem depender do tradutor.
# ESCREVER O TOKEN, NAO O ENDERECO DE RAM - e isto e uma REVERSAO da decisao
# anterior, com a medicao que a derruba.
#
# A nota antiga dizia: 'o tradutor percorre uma lista em que o componente
# gerado nao entra, entao escrever o token deixa a chamada virtual saltar pra
# dentro da tabela de strings'. Isso foi medido quando o componente gerado
# ainda NAO estava no array de uniques de um hood como o do varejo. Agora esta,
# e o varejo e inequivoco: o tokyo tem ComponentData+0x28 = 0x007A0410 e
# Componente+0x10 = 0x007A0438 em 650 de 650, o atlanta 0x0079FF88 e 0x0079FFB0
# em 651 de 651 - sempre TOKEN, nunca endereco de RAM.
#
# Escrever o endereco ja traduzido num objeto que o tradutor ALCANCA e pior que
# escrever o token: ele traduz de novo, e o resultado e lixo. O sintoma que
# fechou isso foi o enxerto hood1, que travou com PC=0x00650073 - texto UTF-16,
# ou seja salto pra dentro da tabela de strings, exatamente a assinatura de
# chamada virtual por vtable errada.
VT_COMPDATA_TOKEN = 0x0079FF88   # como aparece no arquivo do retail
VT_COMPDATA = 0x00625098         # como fica na RAM: e este que vale
# O `type_va` do registro de componente (+0x10). No arquivo do atlanta e
# 0x0079FFB0 nos 651; na RAM do savestate de San Diego e 0x006250C0
# (mcCityModel) nos 628. Mesma relacao token/vtable do VT_COMPDATA, entao aqui
# vale a versao de RAM pelo mesmo motivo.
VT_COMPONENTE_TOKEN = 0x0079FFB0
VT_COMPONENTE = 0x006250C0
# As instancias tem tres classes proprias, medidas na RAM do savestate:
#   Instance (o registro de 0x60)        mcInstCityModel      0x006251B8
#   ComponentData do tipo (+0x28)        mcInstCityModelType  0x00625190
# e o proprio registro Instance carrega o token 0x007A00B8 em +0x10.
VT_INST = 0x006251B8            # mcInstCityModel, vai em Instance+0x10
VT_INST_TIPO = 0x00625190      # mcInstCityModelType, vai em ComponentData+0x28
# OS TOKENS DESSAS DUAS CLASSES, medidos por contagem e nao por analogia. A
# relacao afim que serve para COMPDATA/COMPONENTE (token = RAM - 0x625098 +
# 0x79FF88) NAO vale aqui: ela previa 0x007A0080/0x007A00A8 e esses valores
# aparecem ZERO vezes nos arquivos. Os certos foram achados contando: no
# atlanta 0x007A00B8 aparece 3608 vezes (o numero de instancias) e 0x007A0090
# 231 vezes (o numero de tipos); no tokyo, 0x007A0540 x7688 e 0x007A0518 x317,
# os mesmos +0x488 do resto do espaco de token.
VT_INST_TOKEN = 0x007A00B8       # vai em Instance+0x10
VT_INST_TIPO_TOKEN = 0x007A0090  # vai no ComponentData do tipo, +0x28
TAM_INSTANCE = 0x60
# Quantos slots do grupo de shader recebem um objeto de verdade. Os props do
# atlanta indexam de 0 a 91; 128 cobre com folga. O resto do array fica nulo,
# como os 81,5%% de slots nulos do retail.
SLOTS_PREENCHIDOS = 128
PADDING_TESTE = 0            # ver o controle de layout em constroi_place
# Tamanho do objeto CellIndex (MapRoot+0x1C). Medido igual no atlanta e no sd.
TAM_CELLINDEX = 0x7130

TAM_SHADER = 0xAC           # medido: o ponteiro de +0x08 aponta pro fim do objeto
# O MapRoot tem 0x290 bytes: a primeira paleta do atlanta fica no offset 0x310
# do arquivo, ou seja MapRoot+0x290. Eu usava 0x230, e `mcCity+0x268` - a
# CONTAGEM dos dois arrays de scratch do +0x1C - caia fora dele, lida como lixo.
# O MapRoot vai ate 0x2290, nao 0x290: as DUAS paletas de 256 cores moram
# dentro dele, em +0x290 e +0x1290. Nas quatro cidades do varejo os ponteiros
# de +0x2C e +0x30 valem exatamente 0x06800290 e 0x06801290 - sempre inline,
# nunca em bloco separado. Colocar as paletas em outro lugar deixava o ponteiro
# certo mas o layout diferente, e nao ha por que apostar que ninguem le
# MapRoot+0x290 direto quando imitar sai de graca.
TAM_MAPROOT = 0x2290
OFF_PALETA_VIVA = 0x290
OFF_PALETA_FONTE = 0x1290
TAM_COMPONENTE = 28
TAM_HOOD_REC = 176
TAM_ENTRADA_HOOD = 20


class Escritor:
    """Monta o corpo do .pck e resolve os ponteiros no fim.

    Um .pck e uma imagem de memoria: o que esta gravado sao ENDERECOS VIRTUAIS,
    e `file_offset = VA - base + 0x80`. Escrever isso de frente pra tras exige
    saber o endereco de uma coisa antes de ela existir, entao aqui os ponteiros
    entram como pendencias (`aponta`) e sao preenchidos no `fecha`.
    """

    def __init__(self):
        # O MapRoot NAO tem 0x80 bytes. `mcCity::mcCity` mexe em +0x190, +0x194,
        # +0x198, +0x19C, +0x1CC e +0x228, e num laco de 20 ponteiros a partir de
        # +0x1D8. Reservando so 0x80 eu deixava todos esses campos caindo em cima
        # do que fosse anexado em seguida - o simulador pegou o construtor lendo
        # um float do shader (0x3D80000B) como ponteiro. Zero neles e seguro:
        # cada um e guardado por `if (ptr)` antes de ser percorrido.
        self.d = bytearray(0x80 + TAM_MAPROOT)
        self.pend = []                        # [(offset_do_campo, chave)]
        self.marca = {}                       # chave -> offset

    # ---- posicionamento
    def alinha(self, n=16):
        while len(self.d) % n:
            self.d += b'\x00'

    def poe(self, blob, chave=None, align=16):
        self.alinha(align)
        at = len(self.d)
        if chave:
            self.marca[chave] = at
        self.d += blob
        return at

    def rotula(self, chave, off):
        self.marca[chave] = off

    def aponta(self, campo, chave):
        """Grava depois, em `campo`, o VA de `chave`."""
        self.pend.append((campo, chave))

    def u32(self, off, v):
        struct.pack_into('<I', self.d, off, v)

    def va(self, off):
        return off - 0x80 + BASE_VA

    def fecha(self, path):
        for campo, chave in self.pend:
            if chave not in self.marca:
                raise KeyError('ponteiro sem destino: %s' % chave)
            self.u32(campo, self.va(self.marca[chave]))
        self.alinha(16)                       # todos os 6718 .pck do retail sao alinhados
        struct.pack_into('<I', self.d, 0x00, BASE_VA)
        struct.pack_into('<I', self.d, 0x04, TIPO_CIDADE)
        struct.pack_into('<I', self.d, 0x08, VERSAO)
        struct.pack_into('<I', self.d, 0x0C, len(self.d) - 0x80)
        with open(path, 'wb') as f:
            f.write(bytes(self.d))
        return len(self.d)


def cubo(lado=40.0):
    """Um cubo centrado na origem, como o conversor entrega: blocos de tira.

    Face a face, cada uma sua propria tira de 4 vertices, e a costura de
    degenerados junta tudo num bloco so. O enrolamento segue a regra do jogo -
    triangulo i e (i-2,i-1,i) com i par - e as faces apontam pra fora.
    """
    h = lado / 2.0
    v = [(-h, -h, -h), (h, -h, -h), (h, -h, h), (-h, -h, h),
         (-h, h, -h), (h, h, -h), (h, h, h), (-h, h, h)]
    faces = [(7, 6, 4, 5), (0, 1, 3, 2), (4, 5, 0, 1),
             (5, 6, 1, 2), (6, 7, 2, 3), (7, 4, 3, 0)]
    uv = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)]
    tiras = []
    for f in faces:
        pos = [v[i] for i in f]
        nr = [(0.0, 1.0, 0.0)] * 4
        tiras.append((pos, list(uv), nr, False))
    # mesma costura do conversor: ponte de degenerados entre tiras
    cp, cu, cn = [], [], []
    for pos, u, nr, _impar in tiras:
        if not cp:
            cp, cu, cn = list(pos), list(u), list(nr)
            continue
        ponte = 2 if len(cp) % 2 == 0 else 3
        cp += [cp[-1]] + [pos[0]] * (ponte - 1)
        cu += [cu[-1]] + [u[0]] * (ponte - 1)
        cn += [cn[-1]] + [nr[0]] * (ponte - 1)
        cp += pos
        cu += u
        cn += nr
    return [(cp, cu, cn, False)]


def le_modelo(caminho, escala, preservar_origem=False):
    """Blocos a partir de um .xmod do MC2, pelo caminho ja validado.

    `strips_to_blocks` ancora a malha na propria caixa para o caminho de
    componentes. Instancias, porem, ja trazem no place.tsv a matriz escrita
    para o pivô ORIGINAL do .mod. Recentrar a malha e reaplicar essa matriz sem
    compensacao desloca o mundo: nos emissive cards de LAX o erro medido chega
    a 1825.77 unidades e poe planos enormes perto da camera. Para instancias,
    restaure a origem antes da quantizacao; e exatamente a geometria para a
    qual a matriz original foi calculada.
    """
    v, t1, adj, strips = mc2.read_xmod(caminho)
    bl, ancora = mc2.strips_to_blocks(v, t1, adj, strips)
    if preservar_origem:
        bl = [([tuple(q[i] + ancora[i] for i in range(3)) for q in pos],
               u, nr, o) for pos, u, nr, o in bl]
    if escala != 1.0:
        bl = [([tuple(c * escala for c in q) for q in pos], u, nr, o)
              for pos, u, nr, o in bl]
    return bl


def slots_de_shader(doador):
    """[slot] do doador que tem um shader tipico, pelo MESMO teste do bloco_shader.

    A primeira versao disto herdou o modelo do `modelo_shader`, que a propria
    Fork City MODS documenta como errado - sub-objeto em +0xAC, o caso de 3 em
    1900 - e por isso listava zero slots num doador que tem centenas. O teste
    e por ESTRUTURA (tipo 0, sub em +0x10, byte +0x04 do sub em 0..3), que
    tambem e o que faz o tokyo passar: ele tem a mesma classe com o espaco de
    tokens deslocado de +0x488, e comparar contra a vtable o rejeitava.

    E TEM UM SEGUNDO TESTE, que faltava e me custou uma rodada. Aceitar o byte
    +0x04 do sub em 0..3 diz que o LOADER despacha (0x2BA718: 0 rmcTexturePS2,
    1 pula, 2 rmcTextureReference, 3 rmcDictionaryReference, outra coisa = laco
    infinito). Nao diz que o SHADER SOBREVIVE A MINHA COPIA. O `bloco_shader`
    leva 0xB0 bytes e o `limpa` zera todo ponteiro menos o +0x08; num sub do
    tipo 0 isso e inofensivo, porque a rmcTexturePS2 e auto-contida, mas num do
    tipo 2 zera o fallback em sub+0x0C - exatamente o ponteiro que a fork de
    textura documentou como obrigatorio - e o jogo salta em CDCDCDCD.

    Medido no atlanta: dos 92 slots que o teste antigo aprovava, 88 sao tipo 0
    e 4 sao tipo 2, e os 4 do tipo 2 perdem ponteiro do sub. Sobram 84 seguros.
    O slot 65, que era o unico candidato do experimento emparelhado, e um dos
    quatro - o teste que rodei com ele nao vale como resultado negativo, vale
    como teste anulado.
    """
    p = mc2.Pck(doador)
    d = p.data
    a18 = p.F(struct.unpack_from('<I', d, 0x80 + 0x0C)[0])
    g0 = p.F(struct.unpack_from('<I', d, a18 + 4)[0])
    n = struct.unpack_from('<H', d, a18 + 8)[0]
    out = []
    for k in range(n):
        v = struct.unpack_from('<I', d, g0 + 4 * k)[0]
        if not (v and p.inside(p.F(v))):
            continue
        o = p.F(v)
        if struct.unpack_from('<I', d, o + 4)[0] & 0x7F:
            continue
        if struct.unpack_from('<I', d, o + 8)[0] != p.V(o + 0x10):
            continue
        if d[o + 0x14] not in (0, 1, 2, 3):
            continue
        # O BLOCO INTEIRO tem que sobreviver ao `limpa`, nao so o sub-objeto.
        # A minha primeira versao deste teste olhava de +0x10 em diante e por
        # isso aprovava o slot 30 - que era o default, o "primeiro que serve", e
        # portanto o shader de TODAS as cidades que eu gerei ate agora.
        #
        # O campo que ele perdia e o +0x0C. Censo no atlanta, 110 shaders de
        # tipo 0: 86 tem 0xCDCDCDCD (o preenchimento), 14 tem token de classe,
        # 2 sao nulos e OITO apontam para um objeto real dentro do pck. O slot
        # 30 e um dos oito, e o `limpa` zerava esse ponteiro - o bloco copiado
        # ficava com um shader que promete um sub-objeto e entrega nulo.
        #
        # Quem pagava a conta: o guard de shader da Fork City MODS 2 recusava
        # essas chamadas (80.907 em 1472 frames) e a cidade entrava mas ficava
        # INVISIVEL; com o guard desligado, a mesma chamada trava no frame 1.
        # Os dois sintomas que eu persegui por dias eram o mesmo defeito visto
        # de dois lados.
        #
        # 0xCDCDCDCD e token nao sao tocados pelo `limpa` (nao estao na faixa
        # de VA do doador), entao um slot cujo +0x0C seja um dos dois e copiado
        # byte a byte. Sao 78 slots assim no atlanta, contra os 84 que o teste
        # antigo aprovava; o primeiro seguro e o 39, nao o 30.
        bruto = bytes(d[o:o + 0xB0])
        limpo = limpa(bruto, doador, manter=(0x08,))[0]
        if any(bruto[i:i + 4] != limpo[i:i + 4]
               for i in range(0, 0xB0, 4) if i != 0x08):
            continue
        out.append(k)
    return out


def modelo_shader(doador, slot=None):
    """COPIADO: um objeto de shader do doador, pronto pra ser realocado.

    Devolve (bytes_do_shader, bytes_do_sub_objeto, slot). O shader tem 0xAC
    bytes e um unico ponteiro, em +0x08, que aponta pro objeto logo atras dele;
    todo o resto e vtable do ELF (absoluta, continua valida em qualquer lugar)
    ou dado inline de registrador de GS, que ainda nao decodificamos.

    Sem `slot`, pega o PRIMEIRO que serve - que no atlanta e o 30, e que NAO le
    o stream de ITOP+2. Com `slot`, pega aquele e falha alto se ele nao servir,
    porque um doador silenciosamente trocado e pior que um erro.
    """
    p = mc2.Pck(doador)
    d = p.data
    a18 = p.F(struct.unpack_from('<I', d, 0x80 + 0x0C)[0])
    g0 = p.F(struct.unpack_from('<I', d, a18 + 4)[0])
    if slot is not None:
        bons = slots_de_shader(doador)
        if slot not in bons:
            perto = [k for k in bons if abs(k - slot) <= 8]
            raise SystemExit(
                'slot %d nao tem shader da classe padrao em %s.%s'
                % (slot, os.path.basename(doador),
                   ('  Perto: %s' % perto) if perto else
                   '  Use --lista-shaders pra ver os %d que servem.' % len(bons)))
        faixa = range(slot, slot + 1)
    else:
        faixa = range(1329)
    for k in faixa:
        v = struct.unpack_from('<I', d, g0 + 4 * k)[0]
        if not (v and p.inside(p.F(v))):
            continue
        o = p.F(v)
        if struct.unpack_from('<I', d, o)[0] != VT_SHADER:
            continue
        sub = struct.unpack_from('<I', d, o + 8)[0]
        if not p.inside(p.F(sub)) or p.F(sub) != o + TAM_SHADER:
            continue
        so = p.F(sub)
        return bytes(d[o:o + TAM_SHADER]), bytes(d[so:so + 0xA0]), k
    raise SystemExit('nenhum shader da classe padrao com o layout esperado em %s'
                     % os.path.basename(doador))


# Texturas vindas de .tex.pck que O JOGO construiu. Nome -> corpo do pck.
TEXTURAS_DO_JOGO = {}
ORDEM_TEXTURA = []          # nome na posicao = slot de shader
POS_TEXTURA = {}            # nome -> slot
INDICES_DO_JOGO = None
FLIP_WINDING = False        # inverte a ordem dos vertices de cada UNPACK (winding)


def flip_winding_payload(payload):
    """Inverte o winding revertendo a ordem dos vertices de cada batch de VIF.

    Opera POR BATCH (header 0x60/num2 -> MSCAL). Reverte, em lockstep, todos os
    UNPACK por-vertice (posicao, uv, cor, normal), o que inverte a orientacao de
    todo triangulo. Trata os dois formatos de posicao de LA:

      - ABSOLUTO (0x69 V3-16 / 0x68 V3-32): reverte os registros crus.
      - DELTA (0x6A V3-8, STMOD mode 2): decodifica com o STROW do batch,
        reverte as posicoes absolutas, e RE-CODIFICA os deltas apontando o
        STROW para o novo primeiro vertice (cada batch delta de LA tem STROW
        proprio, entao nao ha carry entre batches). |delta| e preservado, cabe
        em int8.

    Ver FORKS: os pacotes vinham com o winding do MC2, oposto ao do culler VU.
    """
    import mc3_vifpos as _vp
    d = bytearray(payload)
    cmds = list(_vp._commands(bytes(d)))
    # agrupa em batches: cada header inicia um; MSCAL/proximo header fecha
    batches = []
    cur = None
    for c in cmds:
        h = _vp._header(c, bytes(d))
        if h is not None:
            if cur:
                batches.append(cur)
            cur = {'base': h[0], 'scale': h[1], 'count': h[2],
                   'strow_off': None, 'pos': None, 'attrs': []}
            continue
        if cur is None:
            continue
        if c['cmd'] == 0x30:
            cur['strow_off'] = c['payload']
        elif 0x60 <= c['cmd'] <= 0x7F and (c['num'] or 256) == cur['count']:
            if _vp._is_position(c, cur['base'], cur['count']):
                cur['pos'] = c
            else:
                cur['attrs'].append(c)
        elif c['cmd'] in (0x14, 0x15, 0x17):
            batches.append(cur)
            cur = None
    if cur:
        batches.append(cur)

    def rev_records(off, cnt, st):
        recs = [bytes(d[off + k * st:off + (k + 1) * st]) for k in range(cnt)]
        recs.reverse()
        d[off:off + cnt * st] = b''.join(recs)

    for bt in batches:
        pos = bt['pos']
        cnt = bt['count']
        # SO reverte batch de posicao ABSOLUTA num unico UNPACK (num==count).
        # Delta (0x6A mode 2) e posicao dividida em varios UNPACK ficam intactos:
        # reverter os bytes crus de delta corromperia, e reverter so parte de um
        # batch desalinha os streams. Esses continuam com o winding do MC2 (o
        # jogo os culla), o que e melhor que a cidade inteira invertida.
        if pos is None or pos['mode'] == 2 or (pos['cmd'] & 0x6F) not in (0x68, 0x69):
            flip_winding_payload.pulados += 1
            continue
        cmd = pos['cmd']
        vn = (cmd >> 2) & 3
        vl = cmd & 3
        st = (vn + 1) * ((32 >> vl if vl else 32) // 8)
        for a in bt['attrs']:
            avn = (a['cmd'] >> 2) & 3
            avl = a['cmd'] & 3
            ast = (avn + 1) * ((32 >> avl if avl else 32) // 8)
            rev_records(a['payload'], cnt, ast)
        rev_records(pos['payload'], cnt, st)
    return bytes(d)


def _s8_local(b):
    return b - 256 if b >= 128 else b


def _s32_local(v):
    return v - (1 << 32) if v >= (1 << 31) else v


flip_winding_payload.pulados = 0

LIGACAO_RUNTIME = False


NIVEIS_TEXTURA = {}     # nome -> niveis do manifesto do .ppf


def carrega_manifesto_ppf(caminho):
    """page/page_offset/page_word por nivel, para o datChunkRef de streaming."""
    import json
    m = json.load(open(caminho))
    for t in m['textures']:
        nome = t['texture']
        if nome.endswith('.tex'):
            nome = nome[:-4]
        NIVEIS_TEXTURA[nome.lower()] = t['levels']
    return len(NIVEIS_TEXTURA)


def carrega_texturas(pasta, mapa_identidade=None):
    """Le os dumps POR IDENTIDADE, nao pelo nome do arquivo.

    447 dos 510 arquivos de `la_tex_pck` tem o nome EXTERNO errado - o nome real
    esta no ponteiro em TexturePS2+0x78 (`tNNN`). Eu "verifiquei" esse mapeamento
    comparando cada objeto com o `.tex` de MESMO NOME DE ARQUIVO, que e circular,
    e as amostras batiam por acaso (quase tudo e 64x64). A fork de textura mediu
    e entregou `native_texture_map.tsv` com a associacao correta; usar isso.
    """
    global TEXTURAS_DO_JOGO, ORDEM_TEXTURA
    TEXTURAS_DO_JOGO, ORDEM_TEXTURA = {}, []
    if mapa_identidade and os.path.isfile(mapa_identidade):
        for ln in open(mapa_identidade, encoding='utf-8', errors='replace'):
            c = ln.rstrip().split(chr(9))
            if len(c) < 3 or not c[0].endswith('.tex'):
                continue
            nome = c[0][:-4].lower()          # identidade REAL da textura
            caminho = c[2]                    # arquivo que contem esse objeto
            if not os.path.isfile(caminho):
                continue
            TEXTURAS_DO_JOGO[nome] = open(caminho, 'rb').read()[0x80:]
            ORDEM_TEXTURA.append(nome)
            POS_TEXTURA[nome] = len(ORDEM_TEXTURA) - 1
        return len(ORDEM_TEXTURA)
    for f in sorted(os.listdir(pasta)):
        if not f.endswith('.tex.pck'):
            continue
        nome = f[:-len('.tex.pck')]
        d = open(os.path.join(pasta, f), 'rb').read()
        TEXTURAS_DO_JOGO[nome.lower()] = d[0x80:]
        ORDEM_TEXTURA.append(nome.lower())
        POS_TEXTURA[nome.lower()] = len(ORDEM_TEXTURA) - 1
    return len(ORDEM_TEXTURA)


def poe_shader_com_textura(e, cab16, corpo_tex, niveis=None):
    """Um shader cuja textura e a que o jogo montou.

    O bloco de shader do varejo tem 0xB0 bytes = cabecalho de 16 + objeto de
    textura de 160 embutido em +0x10, e o `+0x08` do shader aponta para esse
    +0x10. O rmcTexturePS2 tem exatamente 160 bytes, entao [cabecalho][corpo do
    .tex.pck] ja tem a forma certa - e como o corpo fica CONTIGUO, um delta
    unico basta para todos os ponteiros internos dele.

    So os ponteiros DO OBJETO sao traduzidos (os quatro datChunkRef em +0x48).
    Os blocos de pixel nao levam ponteiro, e reescrever palavra dentro deles
    seria repetir o erro que ja produziu 19 malhas com qw absurdo.
    """
    bloco = bytearray(cab16) + bytearray(corpo_tex[:160] if niveis is not None
                                                 else corpo_tex)
    # TOKEN, NAO VTABLE, no +0x00 do objeto. O .tex.pck foi emitido com
    # --token 0, entao guarda a vtable de runtime (0x00627280); mas dentro de um
    # .pck de recurso o +0x00 tem que ser o TOKEN serializado (0x007A2320) - o
    # ctor de recurso rmcTexturePS2(datResource&) troca token por vtable na
    # carga, e achando ja a vtable ele le todos os campos seguintes (resolucao,
    # bpp, datChunkRef) deslocados e trava (os 90 cpuTlbMiss / loading infinito).
    struct.pack_into('<I', bloco, 0x10, VT_TEXTURA_TOKEN)
    off = e.poe(bytes(bloco), align=16)
    va_obj = e.va(off + 0x10)
    delta = va_obj - 0x06800000
    # OS CAMPOS DE PONTEIRO DO OBJETO, medidos e nao supostos: varrendo 60
    # texturas, so tres offsets apontam para dentro do corpo - +0x48 e +0x54
    # (dois dos quatro datChunkRef) e **+0x78**, que no doador e ZERO e por isso
    # eu nao esperava. Deixar o +0x78 sem traduzir foi o que produziu
    # `cpuTlbMiss pc:2ba874 addr:1f00c978` - o PC fica logo depois do
    # rmcTexturePS2::rmcTexturePS2(datResource&) 0x002BA830, ou seja o jogo
    # chegou na minha textura e seguiu um ponteiro do dump.
    if niveis is not None:
        # FORMA DE STREAMING. O objeto que o construtor de RUNTIME monta e
        # RESIDENTE (datChunkRef com ponteiro, pixels no heap) e o ctor de
        # recurso 0x002BA830 **so reloca e espera streaming** - alimentar ele
        # com a forma residente deu 90 cpuTlbMiss em 0x2BA760..0x2BA874. Entao
        # fico com os descritores de GS que o jogo calculou e troco so os refs.
        #
        # O ref paginado, decodificado no atlanta (8793 deles) e confirmado no
        # sd (8048): `[ptr=0][offset na pagina][page_word]`, com page_word =
        # 0x3D80 no u16 alto e a PAGINA no baixo. O alto e constante nas duas
        # cidades. O `page_word` que o meu compilador de .ppf ja gravava no
        # manifesto E esse campo inteiro.
        for k in range(4):
            q = off + 0x10 + 0x48 + 12 * k
            if k < len(niveis):
                n = niveis[k]
                struct.pack_into('<III', e.d, q, 0, n['page_offset'], n['page_word'])
            else:
                struct.pack_into('<III', e.d, q, 0, 0, 0)
        # +0x78 era ponteiro do heap de runtime; no doador e ZERO.
        struct.pack_into('<I', e.d, off + 0x10 + 0x78, 0)
    else:
        campos = [0x48 + 12 * k for k in range(4)] + [0x78]
        for c in campos:
            q = off + 0x10 + c
            v = struct.unpack_from('<I', e.d, q)[0]
            if 0x06800000 <= v < 0x06800000 + len(corpo_tex):
                struct.pack_into('<I', e.d, q, v + delta)
    struct.pack_into('<I', e.d, off + 0x08, va_obj)
    return off


def emite_grupos_shader(e, doador_shader, n_grupos, n_slots, slot=None,
                        indice_material=0):
    """Os grupos de shader da cidade, no formato do varejo.

    O atlanta tem 18 grupos de 1329 slots e os objetos da cidade indexam GRUPO
    de 0 a 17 e SLOT de 0 a 1328. Mais importante: quem indexa os slots nao e
    so a cidade - os props (`atlanta_midnight_clear_props.pck` e os 22 irmaos)
    trazem `material_index` de 0 a 91 e esse indice entra no array de slots do
    grupo. Emitindo 1 grupo de 64 slots, o indice 80 do `a_prop_stlt_02x` lia
    depois do fim do array: vtable nula e `jalr v0` para endereco invalido.

    Cada slot preenchido recebe o SEU proprio objeto: o laco de Place
    (0x2AF9E8) roda uma vez por slot e somaria o delta N vezes num objeto
    compartilhado. Os slots acima de SLOTS_PREENCHIDOS ficam nulos, como os
    81,5%% de slots nulos do retail.

    Devolve (chave do array de descritores, slot doador do shader).
    """
    # O doador de shader TEM que estar no mesmo espaco de token do doador
    # principal, senao o arquivo sai com estrutura de uma cidade e shader de
    # outra. Foi o que aconteceu com tokyo + shader do atlanta.
    # AVISO, NAO ERRO: o usuario testou e os tokens sao INERTES - espacos
    # diferentes resolvem para a mesma vtable em tempo de execucao. Manter os
    # dois no mesmo espaco continua sendo higiene (o varejo nunca mistura), mas
    # bloquear seria impor uma teoria que a medicao dele ja derrubou.
    if doador_shader and token_do_doador(doador_shader) != DESLOC_TOKEN:
        print('  aviso: --doador-shader esta em outro espaco de token '
              '(0x%X contra 0x%X); inofensivo, mas o varejo nao mistura'
              % (token_do_doador(doador_shader), DESLOC_TOKEN))
    # UM DOADOR DIFERENTE POR SLOT PREENCHIDO. Chunk de pagina tem DONO UNICO.
    #
    # A textura do shader nao carrega pixel: ela carrega quatro datChunkRef de
    # 12 bytes em +0x48, e o pixel mora no .ppf irmao. O datPageFile::PageIn
    # grava um retro-ponteiro no dado paginado apontando para O datChunkRef que
    # o resolveu, e o despejo da pagina anula exatamente UM. Dois refs para o
    # mesmo (pagina, offset) e ponteiro pendurado assim que a pagina reciclar.
    #
    # Eu emitia 128 copias do MESMO shader por grupo, ou seja 2304 objetos de
    # textura apontando para UM chunk (offset 0x2E00, pagina 3). Medido no
    # varejo: atlanta tem 4105 shaders e 4105 texturas DISTINTAS, tokyo 5970 e
    # 5970 - ZERO compartilhamento, nem de chunk nem de objeto. O exportador
    # deles nao deduplica de proposito.
    #
    # Entao cada slot preenchido leva um shader de um SLOT DIFERENTE do doador,
    # que traz o seu proprio chunk. Quando os doadores acabam, o slot fica NULO
    # em vez de repetir - nulo e a forma majoritaria do varejo (81,5% dos slots)
    # e nao cria dono duplicado. De brinde a cidade deixa de ter uma textura so.
    seguros = slots_de_shader(doador_shader)
    if slot is not None:
        seguros = [slot] + [k for k in seguros if k != slot]
    if not seguros:
        raise SystemExit('nenhum shader utilizavel em %s'
                         % os.path.basename(doador_shader))
    n_cheios = min(n_slots, SLOTS_PREENCHIDOS, len(seguros) // max(1, n_grupos))
    n_cheios = max(n_cheios, 1)
    veio_de = seguros[0]
    prox = 0
    shaders_tex = {}
    for g in range(n_grupos):
        vas = []
        for k in range(n_slots):
            if ORDEM_TEXTURA:
                # UM GRUPO SO, e um objeto DISTINTO por slot. Eu compartilhava o
                # mesmo ponteiro de Basic entre os 18 grupos para poupar RAM, e
                # ESSA era a causa do loading infinito: o ctor serializado 2AFF20
                # roda uma vez POR VISITA e RELOCA shader+0x08 de novo a cada
                # uma (medido pela fork de textura: 068022A0 -> 010022A0 ->
                # FB8022A0). Nos meus builds davam 9180 slots para 510 objetos =
                # 8670 visitas extras; a cidade que carrega tem ZERO.
                # Emitir 510 x 18 objetos distintos nao serve porque cada chunk
                # precisa de dono exclusivo, entao a saida e reduzir os grupos:
                # o grupo 0 leva os slots, os outros ficam nulos.
                if g == 0 and k < len(ORDEM_TEXTURA):
                    if True:   # um objeto por (grupo, slot); nunca reusar
                        bl, _veio = bloco_shader(doador_shader,
                                                 seguros[k % len(seguros)])
                        cab = bl
                        nome_t = ORDEM_TEXTURA[k]
                        if LIGACAO_RUNTIME:
                            # SLOT DO ATLANTA INTACTO, para o mod sobrescrever
                            # depois. Zerar os datChunkRef fazia o page-in travar
                            # no LOADING; mante-los (validos, apontando pro .ppf
                            # do atlanta) faz o slot carregar exatamente como a
                            # downtown-atlanta que ja carrega. A duplicacao de
                            # chunk (quando k repete um doador) so morde na
                            # RECICLAGEM da pagina, e o tex_bind sobrescreve
                            # shader+0x08 com a textura de LA antes disso. So o
                            # token e garantido (o bloco do atlanta ja tem).
                            o = e.poe(bytes(bl))
                            shaders_tex[k] = e.va(o)
                        else:
                            shaders_tex[k] = e.va(poe_shader_com_textura(
                                e, cab[:16], TEXTURAS_DO_JOGO[nome_t],
                                NIVEIS_TEXTURA.get(nome_t)))
                    vas.append(shaders_tex[k])
                else:
                    vas.append(0)
            elif k < n_cheios and prox < len(seguros):
                bloco, _ = bloco_shader(doador_shader, seguros[prox])
                prox += 1
                o = e.poe(bloco)
                # cada shader com a sua textura inline em +0x10, como o retail
                struct.pack_into('<I', e.d, o + 0x08, e.va(o + 0x10))
                vas.append(e.va(o))
            else:
                vas.append(0)
        if LIGACAO_RUNTIME and g == 0:
            # MARCADOR. O mod precisa achar os slots na RAM e nao tem como
            # saber o endereco; varrer por uma assinatura e mais barato que
            # descobrir o MapRoot em runtime. Fica logo ANTES do array do grupo
            # 0, com a contagem, entao achar a assinatura e achar os slots.
            e.alinha(16)
            e.poe(b'MC3TEXSLOTS' + bytes(1) + struct.pack('<I', len(ORDEM_TEXTURA)))
        e.poe(b''.join(struct.pack('<I', v) for v in vas), 'grupo%d_dados' % g)
    print('  shaders: %d slot(s) por grupo, %d doadores distintos usados '
          '(chunk unico por textura)' % (n_cheios, prox))
    # O indice de material da geometria TEM que cair num slot preenchido. Com
    # doadores distintos por slot, quantos slots enchem passou a depender de
    # quantos shaders seguros o doador tem - e um doador magro deixa o indice
    # apontando para NULO sem avisar. Este teste e a rede.
    if ORDEM_TEXTURA:
        n_cheios = len(ORDEM_TEXTURA)
    if not ORDEM_TEXTURA and indice_material >= n_cheios:
        raise SystemExit(
            'material %d mas so %d slot(s) por grupo enchem (o doador tem %d '
            'shaders seguros para %d grupos). Use --material menor que %d, '
            'menos grupos, ou um doador com mais shaders.'
            % (indice_material, n_cheios, len(seguros), n_grupos, n_cheios))

    # os descritores TEM que ser contiguos: MapRoot+0x0C aponta para o array
    descs = e.poe(bytes(0x10 * n_grupos), 'grupos')
    for g in range(n_grupos):
        off = descs + 0x10 * g
        struct.pack_into('<IIHHI', e.d, off, tok(VT_ARRAY), 0, n_slots, n_slots, 0)
        e.aponta(off + 4, 'grupo%d_dados' % g)
    return 'grupos', veio_de


def textura_com_pixels(e, doador):
    """COPIA a textura raiz do doador COM o bloco de pixels, relocando os
    ponteiros internos. Devolve a chave da textura.

    Esta e a peca que faltava e travava a cidade do zero: o shader copiado
    apontava para uma textura sem pixels (nivel[].dados nulos, carimbo
    0x80000000 = nao colocada no GS), e a maioria das texturas da cidade pega
    os pixels do streaming .aib, que nao existe numa cidade gerada. No Bind, o
    jogo tentava colocar uma textura sem fonte de pixel e travava no primeiro
    frame - a mesma trava que o cubo so mostrava ao virar a camera.

    A raiz do MapRoot (+0x1D4) e uma das 18 texturas do atlanta com pixels
    INLINE: 256x256 PSMT8, um MipBuffer de 0x10500 bytes (0x100 cabecalho +
    0x10000 pixels + 0x400 CLUT). Copiando ela com os pixels, o Bind coloca a
    textura a partir do proprio arquivo.
    """
    p = mc2.Pck(doador)
    d = p.data
    tva = struct.unpack_from('<I', d, 0x80 + 0x1D4)[0]
    t = p.F(tva)
    mbva = struct.unpack_from('<I', d, t + 0x48)[0]   # nivel[0].dados
    mb = p.F(mbva)
    tam = struct.unpack_from('<I', d, mb + 0x0C)[0]    # 0x10500

    # 1) o bloco de pixels (MipBuffer + pixels + CLUT), limpo dos ponteiros
    buf = bytearray(d[mb:mb + tam])
    struct.pack_into('<I', buf, 0x00, 0)               # zero_00
    struct.pack_into('<I', buf, 0x04, 0)               # no_compartilhado (runtime)
    struct.pack_into('<I', buf, 0x08, 0)               # dono: reaponta abaixo
    struct.pack_into('<I', buf, 0x10, 0)               # unk_10 (era CDCD)
    off_buf = e.poe(bytes(buf), 'tex_pixels')

    # 2) o objeto de textura de 0x90, com os ponteiros zerados menos nivel[0]
    obj = bytearray(d[t:t + 0x90])
    for k in range(4):
        struct.pack_into('<I', obj, 0x48 + 12 * k, 0)  # nivel[k].dados
    struct.pack_into('<I', obj, 0x78, 0)               # nome
    off_tex = e.poe(bytes(obj), 'tex_inline')
    # nivel[0].dados -> o bloco de pixels; e o dono do bloco -> nivel[0]
    e.aponta(off_tex + 0x48, 'tex_pixels')
    struct.pack_into('<I', e.d, off_buf + 0x08, e.va(off_tex + 0x48))
    return 'tex_inline'


def bloco_shader(doador, slot=None):
    """COPIADO: um shader TIPICO, com o sub-objeto em +0x10.

    Errei isto duas vezes seguidas e a segunda foi pior que a primeira. Medido
    nos ~1900 shaders de tipo 0 do atlanta, a distancia entre o shader e o
    objeto que seu `+0x08` aponta e:

        +0x10 -> 1889 vezes     +0xC -> 11     +0xAC -> 3

    Eu tinha SELECIONADO o caso de 3 em 1900, porque foi nele que tropecei
    primeiro, e construi o modelo "shader = bloco de 0xB0 com sub-objeto no fim"
    em cima dele. O normal e o sub-objeto vir logo depois do cabecalho de 16
    bytes. Com o ponteiro em +0xAC o byte `+0x04` do sub-objeto cai fora do
    bloco copiado, e `0x2BA718` despacha em lixo -> loc_2BA7E0, laco infinito.

    O passo entre shaders consecutivos e 0xB0, entao o bloco tem 0xB0 bytes com
    o sub-objeto embutido em +0x10.
    """
    p = mc2.Pck(doador)
    d = p.data
    a18 = p.F(struct.unpack_from('<I', d, 0x80 + 0x0C)[0])
    g0 = p.F(struct.unpack_from('<I', d, a18 + 4)[0])
    n = struct.unpack_from('<H', d, a18 + 8)[0]
    # Com `slot`, so aquele; sem, o primeiro que serve. Escolher importa: quem
    # decide se o stream de ITOP+2 e lido e a palavra de flags do MATERIAL, nao
    # o bloco, entao ligar as normais com um shader que nao as le corrompe em
    # vez de iluminar - foi assim que uma cidade travou no primeiro quadro.
    faixa = range(slot, slot + 1) if slot is not None else range(n)
    for k in faixa:
        if k >= n:
            raise SystemExit('slot %d nao existe: o doador tem %d' % (k, n))
        v = struct.unpack_from('<I', d, g0 + 4 * k)[0]
        if not (v and p.inside(p.F(v))):
            continue
        o = p.F(v)
        # ACHAR PELA ESTRUTURA, NAO PELO VALOR DA VTABLE. Comparar contra
        # VT_SHADER fazia o tokyo ser recusado, e eu registrei isso no log como
        # "o tokyo nao tem shader desse tipo" - estava errado. A fork de textura
        # mediu e eu confirmei: o tokyo tem a MESMA classe, com o espaco de
        # tokens inteiro deslocado de +0x488 (007A1EF8 -> 007A2380,
        # 007B2318 -> 007B27A0, 007A1FC8 -> 007A2450). Atlanta, sd e detroit
        # usam os tokens de baixo. Testar a forma cobre os quatro sem tabela de
        # valores.
        if struct.unpack_from('<I', d, o + 4)[0] & 0x7F:      # tem que ser tipo 0
            continue
        if struct.unpack_from('<I', d, o + 8)[0] != p.V(o + 0x10):
            continue
        if d[o + 0x14] not in (0, 1, 2, 3):                   # byte +0x04 do sub
            continue
        # O MESMO teste estrito do slots_de_shader: o bloco tem que sobreviver
        # inteiro ao `limpa`. Sem isto o default voltava a ser o slot 30, que
        # perde o +0x0C. Ver a nota la.
        bruto = bytes(d[o:o + 0xB0])
        limpo = limpa(bruto, doador, manter=(0x08,))[0]
        perdidos = [i for i in range(0, 0xB0, 4)
                    if i != 0x08 and bruto[i:i + 4] != limpo[i:i + 4]]
        if perdidos:
            if slot is not None:
                raise SystemExit(
                    'slot %d perde %d campo(s) no `limpa` (+%s) - use '
                    '--lista-shaders'
                    % (slot, len(perdidos), ', +'.join('0x%02X' % i for i in perdidos)))
            continue
        return limpo, k
    raise SystemExit(
        'slot %d do %s nao tem shader tipico (sub em +0x10); use '
        '--lista-shaders' % (slot, os.path.basename(doador)) if slot is not None
        else 'nenhum shader tipico (sub em +0x10) em %s'
        % os.path.basename(doador))


def array_vazio(e, chave):
    """Um objeto de array com contagem ZERO, no lugar de um ponteiro nulo.

    Descoberto no savestate do primeiro teste: `Place` conserta os ponteiros na
    ordem em que a classe os declara, e o MapRoot parou logo depois do grupo de
    shader - o campo seguinte, `+0x10`, era o nulo que eu tinha deixado. No PS2
    ler o endereco 0 nao falha: devolve o inicio da RAM, e o `Place` sai andando
    num grafo de lixo. Loading infinito, sem erro.

    Um array de contagem zero e a forma VAZIA legitima: o ponteiro e valido, o
    laco roda zero vezes.
    """
    dados = e.poe(bytes(16), chave + '_dados')
    obj = e.poe(struct.pack('<IIHHI', tok(VT_ARRAY), 0, 0, 0, 0), chave)
    e.aponta(obj + 4, chave + '_dados')
    return obj


def hood_vazio(e):
    """Um bloco zerado para HoodEntry+0x08/+0x10 de hood sem conteudo.

    Medido: NENHUM hood do varejo tem contagem zero - as quatro cidades enchem
    os seis ou sete - entao nao existe exemplo de "hood vazio" para copiar. O
    que existe e a invariante: `unique_array` e `instance_array` nunca sao
    nulos, nas 25 entradas de hood das quatro cidades. Como a contagem que
    acompanha e zero, o laco nao le nada; o ponteiro so precisa ser um endereco
    legitimo. Vale a licao do `array_vazio`: no PS2 ler o endereco 0 nao falha,
    devolve o inicio da RAM e o Place sai andando em lixo.

    Os 16 bytes ANTES do array sao o cookie do new[] (contagem, como no varejo:
    `[count][CD CD CD]`). mcHood::DeleteModels 0x25D418 le a contagem DALI, nao
    do HoodEntry, e chama o destrutor virtual de cada elemento: sem esse cookie
    o bloco herdava a palavra do objeto anterior (1) e sair da cidade saltava
    para uma vtable nula (medido: pc=0 ao voltar do Arcade, 27/09/2026).
    """
    if 'hood_vazio' not in e.marca:
        at = e.poe(struct.pack('<I', 0) + b'\xCD' * 12 + bytes(0x60), 'hood_vazio_cookie')
        e.rotula('hood_vazio', at + 16)
    return 'hood_vazio'


def limpa(blob, doador, manter=()):
    """Zera TODO ponteiro de dentro de um blob copiado, menos os que eu reaponto.

    Copiar uma estrutura do doador traz os ponteiros dela, que apontam pro
    espaco de 8 MB de origem. Num arquivo de 26 KB isso e ponteiro pendurado, e
    eu vinha tratando so um ou dois por estrutura: o `+0x194` tem 23 e eu
    cuidava de 2; as cadeias de `+0x1D4` tem de 1 a 9 e eu nao cuidava de
    nenhuma; o bloco de shader tem DOIS (`+0x08` e `+0x0C`) e eu so consertava
    o primeiro — copiado 64 vezes, dava 64 ponteiros pendurados iguais.

    Zerar e seguro onde o consumidor testa antes de usar, que e o caso desses
    campos; manter o valor do doador nunca e.
    """
    p = mc2.Pck(doador)
    b = bytearray(blob)
    n = 0
    for o in range(0, len(b) - 3, 4):
        if o in manter:
            continue
        v = struct.unpack_from('<I', b, o)[0]
        if BASE_VA <= v < BASE_VA + 0x1000000 and p.inside(p.F(v)):
            struct.pack_into('<I', b, o, 0)
            n += 1
    return bytes(b), n


def campos_ponteiro_maproot():
    """Todo offset do MapRoot que guarda PONTEIRO, segundo `mcCity::mcCity`.

    Copiar o MapRoot do doador traz junto os ponteiros dele, que apontam pra
    dentro do arquivo de origem e nao valem aqui. Todos sao guardados por
    `if (ptr)` antes de percorridos, entao zerar e seguro; deixar o valor do
    doador nao e.
    """
    return ([0x0C, 0x10, 0x18, 0x1C, 0x2C, 0x30, 0x190, 0x194, 0x198,
             0x19C, 0x1CC, 0x228, 0x1D4] + [0x1D8 + 4 * k for k in range(20)])


def maproot_base(doador):
    """COPIADO: o MapRoot inteiro do doador (0x2290), com os ponteiros zerados.

    O que sobra sao os ESCALARES da cidade - extents, distancias de LOD, fog,
    saturacao - que eu vinha zerando sem saber. Sao ~0x250 bytes de parametro.
    As duas paletas do doador vem junto e sao sobrescritas por `paletas_inline`;
    so os offsets de `campos_ponteiro_maproot()` sao zerados, e todos ficam
    abaixo de 0x290, entao a area das paletas nao e tocada aqui.
    """
    d = mc2.Pck(doador).data
    m = bytearray(d[0x80:0x80 + TAM_MAPROOT])
    for off in campos_ponteiro_maproot():
        struct.pack_into('<I', m, off, 0)
    struct.pack_into('<I', m, 0x04, 0)       # flag "ja colocado"
    return m


def bloco_1c(e, doador, chave, componentes=(), instancias=(), scratch=64,
             cel_por_unico=None, cel_por_inst=None):
    """O indice de culling da cidade, em `MapRoot+0x1C`.

        +0x00 contagem de componentes     +0x04 contagem de instances
        +0x08 -> array de UniqueComponent (unique_array)
        +0x0C -> array de Instance        (instance_array)
        +0x10 -> CellRecord[cell_count]   A GRADE DE CELULAS
        +0x14 -> ponteiro por celula      (a lista `extra`, ver mc3_cobertura)
        +0x18.. escalares (copiados)

    CORRECAO (o que travava a cidade do zero): `+0x10` NAO e scratch. E a grade
    de origem que o jogo LE - cada CellRecord de 12 bytes e
    `{s16 unique_count, s16 instance_count, u32 unique_list, u32 instance_list}`,
    e `unique_list` aponta para um `u16[unique_count]` de INDICES no
    unique_array. No atlanta a celula 51 e `{1, 0, ->[237], 0}` e
    unique_array[237] e o componente que mora naquela celula.

    Deixando a grade toda zerada, o cubo entrava no unique_array mas nenhuma
    celula o listava; ao virar a camera para a celula do cubo o jogo entrava num
    laco escrevendo naquela celula (contador subindo 0x123 -> 0x242 entre dois
    frames) e congelava. Com a grade preenchida ele le dados validos.

    `cel_por_unico` mapeia indice-de-unique -> lista de indices de celula que a
    sua tile box cobre. Cada celula listada recebe um CellRecord que aponta para
    aquele unique.
    """
    # O OBJETO TEM 0x7130 BYTES, NAO 0x60. Medido no atlanta e no sd: do inicio
    # do CellIndex ate o cookie do unique_array vao 28976 bytes, e `+0x64`/`+0x84`
    # - as listas de visiveis que o runtime enche - vem ZERADAS no arquivo.
    # Copiando so 0x60 eu deixava `+0x64` cair na alocacao seguinte, e o jogo lia
    # um PONTEIRO onde espera um indice limitado a 0x190. Foi o que o guard de
    # packet da Fork City MODS 2 pegou como `bad packet lists` no meu arquivo.
    p = mc2.Pck(doador)
    d = p.data
    o = p.F(struct.unpack_from('<I', d, 0x80 + 0x1C)[0])
    ua = p.F(struct.unpack_from('<I', d, o + 8)[0])
    # O unique_array comeca IMEDIATAMENTE depois do CellIndex; nao existe um
    # cookie de 0x10 entre os dois. Subtrair 0x10 truncava o objeto de 0x7130
    # para 0x7120 e fazia mcPVS::Update ler os quatro primeiros ponteiros do
    # unique_array como os campos finais do proprio PVS. Em particular,
    # +0x7120 e o incremento da distancia adaptativa (10.0 no varejo).
    tam_obj = ua - o if ua > o else TAM_CELLINDEX
    if not (0x60 <= tam_obj <= 0x20000):
        tam_obj = TAM_CELLINDEX
    blob = bytearray(limpa(bytes(d[o:o + 0x60]), doador)[0])
    blob += bytes(tam_obj - 0x60)          # listas de runtime nascem zeradas
    # O rodape 0x7104..0x7124 nao e scratch. Sao, respectivamente, as duas
    # distancias atuais, limites de tempo, contadores e passos adaptativos.
    # Todas as quatro cidades retail usam 800/800, 34/40, 0/0, 40/10, 0.
    # Preservar do doador mantem o contrato e ainda deixa SetIntendedFrameRate
    # substituir somente os dois limites, como o jogo original faz.
    if tam_obj >= 0x7128:
        blob[0x7104:0x7128] = d[o + 0x7104:o + 0x7128]
    struct.pack_into('<II', blob, 0, len(componentes), len(instancias))
    obj = e.poe(bytes(blob), chave)
    e.poe(b''.join(struct.pack('<I', v) for v in componentes) or bytes(4),
          chave + '_comps')
    e.poe(b''.join(struct.pack('<I', v) for v in instancias) or bytes(4),
          chave + '_insts')

    # inverter os mapas: celula -> [indices]. Um CellRecord tem os DOIS lados,
    # unique_list e instance_list, cada um u16[] de indices no seu array.
    def por_celula_de(mapa):
        fora = {}
        for idx, celulas in (mapa or {}).items():
            for c in celulas:
                if 0 <= c < scratch:
                    fora.setdefault(c, []).append(idx)
        return fora

    pc_u = por_celula_de(cel_por_unico)
    pc_i = por_celula_de(cel_por_inst)

    # as u16-listas, deduplicadas por conteudo (muitas celulas repetem a lista)
    listas = {}

    def lista_de(idxs, marca):
        ch = tuple(sorted(idxs))
        if ch not in listas:
            nome = '%s_%s_%d' % (chave, marca, len(listas))
            e.poe(b''.join(struct.pack('<H', u) for u in ch), nome)
            listas[ch] = nome
        return listas[ch]

    cells = bytearray(12 * scratch)
    obj_cells = e.poe(bytes(cells), chave + '_s1')
    for c in set(pc_u) | set(pc_i):
        unis = pc_u.get(c, [])
        inss = pc_i.get(c, [])
        struct.pack_into('<hh', e.d, obj_cells + 12 * c, len(unis), len(inss))
        if unis:
            e.aponta(obj_cells + 12 * c + 4, lista_de(unis, 'ul'))
        if inss:
            e.aponta(obj_cells + 12 * c + 8, lista_de(inss, 'il'))

    e.poe(bytes(4 * scratch), chave + '_s2')
    for k, alvo in enumerate(('_comps', '_insts', '_s1', '_s2')):
        e.aponta(obj + 8 + 4 * k, chave + alvo)
    return obj


def nomes_dos_hoods(doador):
    """Os nomes de hood do doador, na ordem (`bh, dt, fwy, lf, mt, ug, we`)."""
    p = mc2.Pck(doador)
    d = p.data
    n = struct.unpack_from('<I', d, 0x80 + 0x14)[0]
    hb = p.F(struct.unpack_from('<I', d, 0x80 + 0x18)[0])
    out = []
    for h in range(n):
        rec = p.F(struct.unpack_from('<I', d, hb + 20 * h)[0])
        out.append(bytes(d[rec:rec + 4]).split(bytes(1))[0].decode('latin1'))
    return out


def registro_hood(e, doador, nome, chave, qual=0, ultimo=False):
    """COPIADO e religado: o registro de 0xB0 bytes de um hood.

    Os 7 registros do atlanta sao contiguos com passo 0xB0 e cada um e
    `[nome 4][cadeia de vtable 0x7A2320, 0xA0][cabeca 12]`; a cabeca (`+0xA4`)
    tem `+0x08` apontando pra cadeia do registro SEGUINTE, por isso sao colados.
    Aqui o registro vem inteiro do doador, o nome e reescrito, e o ponteiro da
    cabeca passa a mirar uma copia PROPRIA da cadeia.

    **O ULTIMO REGISTRO E O TERMINADOR.** No atlanta o `we` (indice 6) tem
    `+0xA4`, `+0xA8` e `+0xAC` todos ZERO, e os outros seis tem vtable em +0xA4 e
    ponteiro em +0xAC. Reciclando os registros do doador para uma cidade com mais
    hoods, o terminador cai no meio e o ultimo fica com ponteiro valido - a
    cadeia nao termina. `ultimo=True` zera a cabeca inteira, custe o que custar
    ao doador de onde ela veio.
    """
    p = mc2.Pck(doador)
    d = p.data
    base = p.F(struct.unpack_from('<I', d, 0x80 + 0x18)[0])
    rec = p.F(struct.unpack_from('<I', d, base + 20 * qual)[0])
    blob = bytearray(limpa(bytes(d[rec:rec + 0xB0]), doador, manter=(0xAC,))[0])
    nb = nome.encode('latin1')[:3]
    blob[0:4] = nb.ljust(4, bytes(1))
    cadeia = bytes(d[rec + 0xB0 + 4:rec + 0xB0 + 4 + 0xA0])
    if ultimo:
        struct.pack_into('<3I', blob, 0xA4, 0, 0, 0)
    off = e.poe(bytes(blob), chave)
    e.poe(cadeia, chave + '_cadeia')
    if not ultimo:
        e.aponta(off + 0xAC, chave + '_cadeia')
    return off


def doadores_de_hood(doador, n):
    """Qual registro do doador usar em cada um dos `n` hoods.

    O terminador do doador (o unico com `+0xA4` zerado) fica reservado para o
    ULTIMO; os demais ciclam sobre os que nao sao terminador, para que nenhum
    terminador caia no meio da cadeia.
    """
    p = mc2.Pck(doador)
    d = p.data
    nd = struct.unpack_from('<I', d, 0x80 + 0x14)[0]
    base = p.F(struct.unpack_from('<I', d, 0x80 + 0x18)[0])
    termina = []
    normais = []
    for h in range(nd):
        rec = p.F(struct.unpack_from('<I', d, base + 20 * h)[0])
        if struct.unpack_from('<I', d, rec + 0xA4)[0]:
            normais.append(h)
        else:
            termina.append(h)
    if not normais:
        normais = list(range(nd))
    # NAO forcar terminador no ultimo: medido, o atlanta tem um registro de
    # cabeca zerada no fim mas o tokyo e o detroit NAO TEM NENHUM e carregam.
    # O que importa e nao deixar o registro estranho do atlanta cair no MEIO.
    return [(normais[i % len(normais)], False) for i in range(n)]


# As tres estruturas de MapRoot+0x190/+0x194/+0x198 sao CLASSES DE CULLABLE, e a
# de +0x228 e rmcTextureProxyPS2 (miniaturas), NAO visibilidade. O campo +0x00 de +0x194/+0x198 NAO e
# contagem: e a mascara de passes da classe (0x4E no retail = 2|4|8|64). Zera-lo
# tira as duas classes do scheduler e deixa a cidade invisivel mesmo com a lista
# de celulas preenchida. +0x1C conta objetos: preencher abaixo com comp/inst+1.
# TextureProxy so e usado por Bind quando TEX1 tem ID nao zero nos bits 21..31.
# Os dumps LA atuais tem ID zero: nao preencher +0x228 com tabelas do doador.
#
# Cada tupla e (offset no MapRoot, quem percorre, offsets de CONTAGEM a zerar,
# offsets de PONTEIRO a reapontar).
# (offset, quem percorre, contagens a zerar, TAMANHO REAL)
# O tamanho importa: +0x194 fica em 0xFC6B0 e +0x198 em 0xFC6F0, **0x40 um do
# outro**. Copiar 0x100 arrastava a estrutura vizinha inteira pra dentro da
# minha - por isso o +0x194 aparecia com 23 ponteiros quando o objeto so tem 2.
ESTRUTURAS_EXTRA = [
    (0x190, 'sub_25C998', (0x30,),      0x100),
    (0x194, 'sub_24C528', (0x1C,),      0x40),
    (0x198, 'sub_2571B0', (0x1C,),      0x40),
    (0x228, 'sub_2BA6B0', (0x00,),      0x100),
]


def estruturas_extra(e, doador, cabeca_ordem3=None, cabeca_ordem2=None,
                     n_comp=0, n_inst=0):
    """Cria as quatro estruturas que eu deixava NULAS, com estado inicial valido.

    ATENCAO ao que "vazio" significa em cada campo - a regra nao e uma so:

    * `MapRoot+0x10` e desreferenciado SEM guarda, entao ali o vazio legitimo e
      um objeto de array com contagem zero. Nulo faz o PS2 ler o endereco 0.
    * `+0x04`/`+0x08` destas classes sao CABECA DE LISTA LIGADA:
      `CullableTypeFixup` (0x24AE58) faz `while (v3) { construtor(v3); v3 =
      *(v3+12); }` — anda ate NULL, sem contagem. Apontar pra um bloco de zeros
      faz o construtor rodar UMA VEZ sobre zeros; **aqui o vazio correto e NULO**.

    Foi essa confusao que produziu o `Jump to unaligned address (PC:
    0xcdcdcdcd)`: o Place completou 11 de 11 ponteiros e a execucao foi parar em
    padding, saindo de um construtor rodado sobre bloco vazio.

    Ou seja: **ler o codigo do consumidor e o que diz se o vazio e NULO ou um
    objeto** — generalizar uma das duas formas quebra a outra.
    """
    p = mc2.Pck(doador)
    d = p.data
    feitas = []
    for off, quem, contagens, tam in ESTRUTURAS_EXTRA:
        va = struct.unpack_from('<I', d, 0x80 + off)[0]
        if not va or not p.inside(p.F(va)):
            continue
        o = p.F(va)
        blob = bytearray(limpa(bytes(d[o:o + tam]), doador)[0])
        for c in contagens:
            struct.pack_into('<I', blob, c, 0)
        # O +0x1C DE +0x194/+0x198 NAO E "contagem de runtime que nasce zerada",
        # como eu tinha anotado: e a CONTAGEM DE OBJETOS que a classe de cullable
        # gerencia, e zera-la faz o scheduler ver zero objeto e NAO DESENHAR NADA
        # - com a geometria toda no arquivo, no lugar certo. Medido em tres
        # cidades de varejo:
        #     atlanta 651 comp / 3608 inst -> +194=4260  +198=3609
        #     sd                5008 inst -> +198=5009
        #     detroit           5156 inst -> +198=5157
        # ou seja **+0x198 = inst + 1** e **+0x194 = comp + inst + 1** (a
        # diferenca entre os dois e exatamente o numero de componentes: 651).
        if off == 0x194 and (n_comp or n_inst):
            struct.pack_into('<I', blob, 0x1C, n_comp + n_inst + 1)
        elif off == 0x198 and n_inst:
            struct.pack_into('<I', blob, 0x1C, n_inst + 1)
        chave = 'extra_%X' % off
        base = e.poe(bytes(blob), chave)
        # A CLASSE DE ORDEM 3 recebe a nossa lista de tipos.
        #
        # Medido: a lista ligada de `MapRoot+0x194` tem **651 nos, e os 651 sao
        # os objetos que o componente aponta em +0x0C**. Ou seja o que eu chamava
        # de "ComponentData" e um `mcCityModelType`, e `CullableTypeFixup(3,
        # cabeca, res)` (0x24AE58) percorre a lista chamando
        # `mcCityModelType::mcCityModelType` em cada um — que carimba a vtable de
        # +0x28 e roda `mcCityModelInfo::mcCityModelInfo` sobre o +0x2C (posicao,
        # raio, slots de LOD).
        #
        # Escrever a vtable na mao, como eu fazia, so imitava o ULTIMO efeito do
        # construtor. Sem estar na lista, o resto dele nunca roda.
        ordem = struct.unpack_from('<I', blob, 0x20)[0]
        # +0x194 e ordem 3 (comps), +0x198 e ordem 2 (instancias). Cada uma
        # recebe a cabeca da sua propria cadeia de tipos.
        cabeca = cabeca_ordem3 if ordem == 3 else (
            cabeca_ordem2 if ordem == 2 else None)
        if cabeca:
            e.aponta(base + 0x04, cabeca)
            e.aponta(base + 0x08, cabeca)
        e.aponta(0x80 + off, chave)
        feitas.append(off)
    return feitas


def cadeias_1d4(e, doador, doador_tex=None):
    """COPIADO: os 21 slots de MapRoot+0x1D4/+0x1D8 que o retail preenche.

    Cada um aponta pra um objeto da cadeia `0x7A2320` - a mesma classe do
    sub-objeto do shader - e e processado por `0x2BA718` com contagem 1,
    despachando no byte `+0x04` (0..3). No atlanta so 5 dos 21 estao
    preenchidos, com bytes 0 e 2.

    Sao guardados por `if (ptr)`, entao nulo NAO trava o Place. Copio porque o
    arquivo do zero morre depois do Place e cada campo que o retail tem e o meu
    nao e uma variavel a menos.
    """
    p = mc2.Pck(doador)
    d = p.data
    feitos = 0
    for k in range(21):
        off = 0x1D4 + 4 * k
        va = struct.unpack_from('<I', d, 0x80 + off)[0]
        if not va or not p.inside(p.F(va)):
            continue
        o = p.F(va)
        if d[o + 4] not in (0, 1, 2, 3):      # o que 0x2BA718 sabe tratar
            continue
        # O SLOT +0x1D4 LEVA A TEXTURA COM PIXELS, os outros vao limpos.
        #
        # Medido: no atlanta o objeto em +0x1D4 tem nivel[0] apontando para um
        # MipBuffer de 0x10500 bytes (256x256 PSMT8: 0x100 de cabecalho, 0x10000
        # de pixels, 0x400 de CLUT). No meu arquivo esse mesmo campo saia NULO,
        # porque o `limpa` zera todo ponteiro do bloco copiado - e a cidade
        # gerada carregava sem UMA textura sequer.
        #
        # A textura_com_pixels() foi escrita exatamente para isto e nunca era
        # chamada por ninguem. Agora e, e so para este slot: os outros 20 sao
        # objetos da mesma classe mas sem pixel inline no varejo, entao copia-los
        # limpos continua sendo o certo.
        if off == 0x1D4:
            # Medido: o MipBuffer deste slot varia MUITO por cidade - atlanta
            # tem 0x10500 (256x256 PSMT8) e tokyo tem 0x160. Como a cidade
            # hospedada no tokyo quer os 7688 slots de instancia dele mas uma
            # textura de verdade, o doador da textura e separavel.
            e.aponta(0x80 + off, textura_com_pixels(e, doador_tex or doador))
            feitos += 1
            continue
        chave = 'cadeia_%X' % off
        e.poe(limpa(bytes(d[o:o + 0xA0]), doador)[0], chave)
        e.aponta(0x80 + off, chave)
        feitos += 1
    return feitos


def escalares_maproot(doador):
    """COPIADO: os campos do MapRoot cujo significado ainda nao esta fechado.

    Sao +0x20..+0x2B (flags e um float) e todo o bloco +0x40..+0x7F, que comeca
    com a vtable 0x7A01E8 e segue com floats de aparencia de extents/fog. Copiar
    e mais honesto do que chutar zero: zero num campo de escala apaga a cidade
    inteira sem dar erro.
    """
    d = mc2.Pck(doador).data
    return bytes(d[0x80 + 0x20:0x80 + 0x2C]), bytes(d[0x80 + 0x40:0x80 + 0x80])


# A rampa preto->branco era otima para LER o indice na tela, e pessima como
# padrao: eu nao gero o vetor de um byte por vertice (rmcModelGeom+0x14 sai
# NULO nas minhas 543 malhas, contra 74%% preenchido no varejo), entao o indice
# efetivo e 0 - o primeiro degrau da rampa, PRETO. A cidade desenhava (531 e
# 580 draw calls nas capturas) e ninguem via nada: geometria preta, a meia
# noite, atras de nevoa. Com a paleta branca a geometria aparece mesmo sem o
# vetor por vertice. Ponha PALETA_RAMPA = True para voltar a rampa quando for
# diagnosticar o indice.
PALETA_RAMPA = False

# A cardinalidade de `rmcModelGeom+0x14` nao e a quantidade de LODs. O caminho
# de componente chama DrawCpv com indice zero; o caminho de instancia passa
# diretamente `Instance+0x1C`, que este builder numera de 0 a N-1 dentro da
# cadeia de cada tipo. Nos PCKs retail, o mesh CPV principal de um tipo declara
# exatamente N slots. Assim, componentes precisam de um slot e tipos de
# instancia precisam de tantos slots quanto registros pertencem ao tipo.
SLOTS_CPV_COMPONENTE = 1


# A paleta do MC2, quando ha uma. Preenchida por paleta_do_mc2().
PALETA_MC2 = None


def paleta_do_mc2(caminho_cpvs):
    """Le o CPP0 de um <hora>_cpvs.rsc do MC2 de PS2 e devolve 256 RGB em float.

    O MC2 e o MC3 usam O MESMO DESENHO para cor por vertice - um indice de 1
    byte por vertice indexando uma paleta de 256 - entao a paleta porta par a
    par, sem achatar em RGB. Achado da Fork MC2 PS2.

    Convencao de cor do PS2: o alfa vem 0x80 nas 256 entradas e os componentes
    ficam em 0..127, ou seja 128 e o 1.0. Medido em dusk_clear e midnight_clear:
    alfa 128 em 256 de 256, luminancia maxima 126.2. Entao a conversao para o
    float que o MC3 espera e dividir por 128, nao por 255 - dividir por 255
    deixaria a cidade com metade do brilho.
    """
    import importlib.util as _il
    sp = _il.spec_from_file_location('mc2_rsc', os.path.join(_AQUI, 'mc2_rsc.py'))
    m = _il.module_from_spec(sp)
    sys.modules['mc2_rsc'] = m
    sp.loader.exec_module(m)
    r = m.Rsc(caminho_cpvs)
    for off, fcc, size in r.entries:
        if fcc == 'CPP0':
            buf = r.data[off:off + size]
            return [tuple(c / 128.0 for c in
                          struct.unpack_from('<3B', buf, k * 4))
                    for k in range(256)]
    raise SystemExit('%s nao tem CPP0' % os.path.basename(caminho_cpvs))


# O ALFA da paleta nao e enfeite. Nas quatro cidades de varejo (atlanta,
# detroit, sd, tokyo; todas as variantes conferidas) as entradas 0..7 tem alfa
# 0, as 8..255 tem alfa 1.0 e a 255 e sempre branco opaco (1,1,1,1) - e a
# entrada que rmcCpvPalette::Lookup 0x2ACE68 reserva. A cidade deixa a paleta
# residente na VU1 (mcCityModelClass::SetRenderStates baixa MCCITY+0x2C) e
# quem desenha depois com rmcSetCpvMode(1, 0) sem baixar a propria herda ela:
# a coluna de fumaca do checkpoint (mcCheckpoint::Draw, shaders cp_flare*,
# texcombine modulate + blendset normal) sai com alfa de vertice 0 e some. Com
# alfa 0 nas 256 entradas era exatamente isso nos mapas do MC2.
PALETA_ALFA_ZERO = 8        # entradas 0..7: alfa 0, como no varejo


def paleta_cinza():
    """256 entradas Vector4 - a tabela que o byte por vertice indexa."""
    out = bytearray()
    for i in range(256):
        if PALETA_MC2:
            r, g, b = PALETA_MC2[i]
        else:
            c = (i / 255.0) if PALETA_RAMPA else 1.0
            r = g = b = c
        if i == 255:
            r = g = b = 1.0
        out += struct.pack('<4f', r, g, b, 0.0 if i < PALETA_ALFA_ZERO else 1.0)
    return bytes(out)


def emite_cadeia_por_vertice(e, grupos, chave, slot_count=1, valor=0):
    """Emite uma cadeia independente por indice de ``rmcModelGeom+0x14``.

    O formato e por slot e por grupo: cada grupo carrega a quantidade de
    blocos, a quantidade de vertices de cada bloco e um payload separado de um
    byte por vertice. Nenhuma subestrutura e compartilhada entre slots, porque
    o Place percorre e fixa cada raiz independentemente, como nos PCKs retail.
    """
    if not grupos:
        raise ValueError('cadeia por vertice sem grupo')
    if not 1 <= slot_count <= 0xFFFF:
        raise ValueError('contagem de slots CPV fora de u16: %d' % slot_count)

    off_slots = e.poe(b'\x00' * (4 * slot_count), chave, align=16)
    for slot in range(slot_count):
        chave_tab = '%s_slot%d' % (chave, slot)
        off_tab = e.poe(b'\x00' * (8 * len(grupos)), chave_tab, align=16)
        e.aponta(off_slots + 4 * slot, chave_tab)

        for gi, grupo in enumerate(grupos):
            if not grupo:
                raise ValueError('cadeia por vertice com grupo vazio')
            vertices = [len(bloco_geometrico[0]) for bloco_geometrico in grupo]
            cab = struct.pack('<I', len(grupo)) + b''.join(
                struct.pack('<I', n) for n in vertices)
            chave_a = '%s_s%d_g%d_a' % (chave, slot, gi)
            e.poe(cab, chave_a, align=16)
            e.aponta(off_tab + 8 * gi, chave_a)

            payloads = []
            for bi, n in enumerate(vertices):
                chave_payload = '%s_s%d_g%d_b%d_payload' % (
                    chave, slot, gi, bi)
                e.poe(bytes([valor & 0xFF]) * n, chave_payload, align=16)
                payloads.append(chave_payload)

            chave_b = '%s_s%d_g%d_b' % (chave, slot, gi)
            off_b = e.poe(b'\x00' * (4 * len(payloads)), chave_b, align=16)
            e.aponta(off_tab + 8 * gi + 4, chave_b)
            for bi, chave_payload in enumerate(payloads):
                e.aponta(off_b + 4 * bi, chave_payload)
    return chave


def anexa_cadeia_por_vertice(p, grupos, slot_count=1, valor=0):
    """Versao imediata, tambem sem compartilhar subestruturas entre slots."""
    if not 1 <= slot_count <= 0xFFFF:
        raise ValueError('contagem de slots CPV fora de u16: %d' % slot_count)
    off_slots = p.append(b'\x00' * (4 * slot_count), 16)
    for slot in range(slot_count):
        off_tab = p.append(b'\x00' * (8 * len(grupos)), 16)
        struct.pack_into('<I', p.data, off_slots + 4 * slot, p.V(off_tab))
        for gi, grupo in enumerate(grupos):
            vertices = [len(bloco_geometrico[0]) for bloco_geometrico in grupo]
            cab = struct.pack('<I', len(grupo)) + b''.join(
                struct.pack('<I', n) for n in vertices)
            off_a = p.append(cab, 16)
            payloads = [p.append(bytes([valor & 0xFF]) * n, 16)
                        for n in vertices]
            off_b = p.append(b''.join(struct.pack('<I', p.V(o))
                                      for o in payloads), 16)
            struct.pack_into('<II', p.data, off_tab + 8 * gi,
                             p.V(off_a), p.V(off_b))
    return off_slots


def grade_do_doador(doador):
    """(grid_w, grid_h, origem_x, origem_z) do doador, em CELULAS."""
    d = mc2.Pck(doador).data
    return struct.unpack_from('<4i', d, 0x80 + 0x26C)


def instancias_do_doador(doador):
    """`instance_count` do CellIndex do doador - o orcamento de instancias.

    Medido no varejo: atlanta 3608, sd 5008, detroit 5156, tokyo 7688. A LA do
    MC2 traz 8511, mais que a MAIOR cidade de varejo, e os arquivos de apoio do
    host (props, traffic, peds) sao dimensionados para a cidade que eles
    acompanham. Com 8511 sobre o atlanta, o indice de prop pedido chegou a 4701
    num array cujas entradas validas terminam por volta de 3971, e o guard da
    Fork City MODS 2 registrou uma falha por frame.
    """
    p = mc2.Pck(doador)
    d = p.data
    ci = p.F(struct.unpack_from('<I', d, 0x80 + 0x1C)[0])
    return struct.unpack_from('<I', d, ci + 4)[0]


def grade_dos_extents(mn, mx):
    """(grid_w, grid_h, origem_x, origem_z) a partir dos extents, em CELULAS.

    A INVARIANTE do varejo, conferida em atlanta/sd/tokyo/detroit:
        origem_x = floor(min_x / 40)   grid_w = floor(max_x/40) - origem_x + 1
        origem_z = floor(min_z / 40)   grid_h = floor(max_z/40) - origem_z + 1
        cell_count = grid_w * grid_h
    Copiar a grade do doador com extents diferentes desloca o culling: LA pede
    91x82 e origem (-50,-43), o atlanta da 64x62 e origem (-50,-43)
    tambem - o 62 e do atlanta, e por isso que a troca passa despercebida.
    Medido no arquivo: losangeles_la_v5 sai (91,82,-50,-43), que e exatamente a
    conta dos extents do losangeles.lvl do MC2 (-2000..1600 / -1720..1520).
    """
    ox = int(math.floor(mn[0] / 40.0)); oz = int(math.floor(mn[2] / 40.0))
    gw = int(math.floor(mx[0] / 40.0)) - ox + 1
    gh = int(math.floor(mx[2] / 40.0)) - oz + 1
    return gw, gh, ox, oz


def caixa_de_celulas(grade, cx, cz, meia_x, meia_z):
    """A tile box de +0x14, RELATIVA a origem da grade.

    A caixa e do AABB, nao da esfera. Testei as duas contra o atlanta: com o
    raio da esfera so 91 dos 651 componentes batem, e os que erram erram para
    MAIS (lido 20..26 contra 18..28 calculado) - ou seja o varejo usa a caixa
    de verdade, mais apertada.

    `grade` = (gw, gh, ox, oz). Antes eu lia a grade do DOADOR aqui, o que
    deslocava tudo quando os extents da cidade nova eram outros.
    """
    gw, gh, ox, oz = grade
    def faixa(c, meia, origem, limite):
        a = int(math.floor((c - meia) / 40.0)) - origem
        b = int(math.floor((c + meia) / 40.0)) - origem
        a = max(0, min(limite - 1, a))
        b = max(0, min(limite - 1, b))
        return min(a, b), max(a, b)
    x0, x1 = faixa(cx, meia_x, ox, gw)
    z0, z1 = faixa(cz, meia_z, oz, gh)
    return x0, x1, z0, z1


def paletas_inline(e, r):
    """As duas paletas escritas DENTRO do MapRoot, como no varejo."""
    pal = paleta_cinza()
    e.d[r + OFF_PALETA_VIVA:r + OFF_PALETA_VIVA + len(pal)] = pal
    e.d[r + OFF_PALETA_FONTE:r + OFF_PALETA_FONTE + len(pal)] = pal
    e.rotula('paletaA', r + OFF_PALETA_VIVA)
    e.rotula('paletaB', r + OFF_PALETA_FONTE)


def constroi(saida, doador, blocos, nome_hood='zz', posicao=(0.0, 0.0, 0.0),
             n_slots=1329, n_grupos=18, indice_material=1, sonda=False,
             hoods=None, slot_shader=None, doador_textura=None, extents=None):
    e = Escritor()

    # ---------------------------------------------------------------- shader
    # UMA COPIA POR SLOT. O laco de 0x2AF9E8 nao tem guarda de "ja colocado" e
    # roda o handler uma vez por slot; o mesmo objeto em N slots leva N somas do
    # delta nos ponteiros internos dele. No retail cada objeto aparece em
    # exatamente um slot. Ver mc3_place_sim.py.
    _g, veio_de = emite_grupos_shader(e, doador, n_grupos, n_slots,
                                      slot_shader, indice_material)

    # ---------------------------------------------------------------- paletas


    # ---------------------------------------------------------------- geometria
    # A escala nao vai para o .pck: a quantizacao viaja DENTRO do packet VIF
    # (o float que abre o bloco). Aqui ela serve para make_block e para o
    # relatorio, entao calcula-se sempre, mesmo com os pacotes vindo do jogo.
    escala = mc2.pick_scale(blocos)
    if PACOTES_DO_JOGO:
        # Pacotes VIF prontos, de um mesh.pck montado pelo PROPRIO JOGO. Troca
        # a minha estripificacao, paridade, ADC e corte em bloco pelas dele.
        lista = bytearray()
        for payload, qw, nv in PACOTES_DO_JOGO:
            lista += struct.pack('<IHH', e.va(e.poe(flip_winding_payload(payload) if FLIP_WINDING else payload, align=16)), qw, nv)
        n_blocos = len(PACOTES_DO_JOGO)
    else:
        pacotes = [mc2.make_block(pos, uv, nr, escala, i % 2 == 1)
                   for i, (pos, uv, nr, _o) in enumerate(blocos)]
        offs = [e.poe(pk, align=16) for pk in pacotes]
        lista = bytearray()
        for off, (pos, _u, _n, _o) in zip(offs, blocos):
            qw = (len(pacotes[offs.index(off)]) + 15) // 16
            lista += struct.pack('<IHH', e.va(off), qw, len(pos))
        n_blocos = len(blocos)
    off_lista = e.poe(bytes(lista), 'lista_blocos')

    grupos_tab = struct.pack('<IHH', 0, n_blocos, 0)
    off_gt = e.poe(grupos_tab, 'tabela_grupos')
    e.aponta(off_gt, 'lista_blocos')

    # a tabela de material fica LOGO ANTES do objeto mesh, como no retail
    e.alinha(16)
    off_mt = len(e.d)
    e.d += struct.pack('<H', indice_material) + b'\x00\x00'
    e.rotula('tabela_material', off_mt)

    mesh = struct.pack('<IIHHIIII', tok(VT_MESH_TOKEN), 0, 1,
                       SLOTS_CPV_COMPONENTE, 0, 0, 0, 1)
    off_mesh = e.poe(mesh, 'mesh', align=4)
    e.aponta(off_mesh + 0x0C, 'tabela_material')
    e.aponta(off_mesh + 0x10, 'tabela_grupos')
    # A cadeia por-vertice tem que casar PACOTE A PACOTE com a malha.
    grupo_cpv = ([([0] * nv,) for _p, _q, nv in PACOTES_DO_JOGO]
                 if PACOTES_DO_JOGO else blocos)
    emite_cadeia_por_vertice(e, [grupo_cpv], 'mesh_t14')
    e.aponta(off_mesh + 0x14, 'mesh_t14')

    # ---------------------------------------------------------------- componente
    pts = [c for pos, _u, _n, _o in blocos for c in pos]
    raio = max((q[0] ** 2 + q[1] ** 2 + q[2] ** 2) ** 0.5 for q in pts)

    off_cd = e.poe(compdata(raio, posicao), 'compdata')
    e.aponta(off_cd + 0x3C, 'mesh')            # slot de LOD 0
    # Os tres campos que o varejo NUNCA deixa nulos e que o caminho do cubo
    # deixava (o caminho do --place ja fazia isto):
    #   +0x04  o dono, que e a propria estrutura de MapRoot+0x194
    #   +0x08  o nome deste objeto, que mora nele mesmo em +0x70
    #   +0x18  a entrada de componente que aponta pra ca
    e.rotula('compdata_nome', off_cd + 0x70)
    e.aponta(off_cd + 0x04, 'extra_194')
    e.aponta(off_cd + 0x08, 'compdata_nome')
    e.aponta(off_cd + 0x18, 'componentes')

    comp = bytearray(TAM_COMPONENTE)
    struct.pack_into('<f', comp, 0x18, raio)
    struct.pack_into('<I', comp, 0x10, tok(VT_COMPONENTE_TOKEN))
    # +0x0B pass_mask: NUNCA e zero no varejo (303 dos 651 do atlanta valem 8) e
    # zero quer dizer "nao entra em passe nenhum", ou seja nao desenha. Entre os
    # componentes cuja malha usa a mesma classe de shader que este (007A1EF8),
    # 8 e o valor de longe mais comum: 230 contra 50 do segundo colocado.
    comp[0x0B] = 8
    meia = max(abs(q[i]) for pos, _u, _n, _o in blocos for q in pos for i in (0, 2))
    # A shell de uma cidade pode usar um cubo sintetico, mas ainda precisa da
    # grade dos extents da cidade alvo. Sem extents explicitos, preserve o
    # comportamento historico e herde a grade do doador.
    grade = grade_dos_extents(*extents) if extents else grade_do_doador(doador)
    x0, x1, z0, z1 = caixa_de_celulas(grade, posicao[0], posicao[2], meia, meia)
    comp[0x14], comp[0x15], comp[0x16], comp[0x17] = x0, x1, z0, z1
    off_comp = e.poe(bytes(comp), 'componentes')
    e.aponta(off_comp + 0x0C, 'compdata')
    vas_comp = [e.va(off_comp)]                 # entra no indice de MapRoot+0x1C
    # as celulas que a tile box do cubo cobre, para registrar o unique 0 nelas
    gw = grade[0]
    cel_por_unico = {0: [z * gw + x for z in range(z0, z1 + 1)
                         for x in range(x0, x1 + 1)]}

    # ---------------------------------------------------------------- hoods
    # OS MESMOS NOMES E A MESMA QUANTIDADE do doador.
    #
    # Evidencia: todo arquivo que carregou tem os 7 hoods do atlanta com os nomes
    # originais; os dois que travaram depois do Place completo (`bx2_hood` e o
    # `cubo_v4`) tinham UM hood chamado `zz`. Nome de hood aparece em `.loc`,
    # dados de corrida e no `_bnd`, entao inventar um provavelmente quebra quem
    # procura por nome. Aqui todos os hoods do doador existem; so o primeiro
    # recebe a geometria, os outros ficam com contagem zero.
    # `hoods` overrides the donor's list. THE FIELD IS FOUR BYTES - three
    # characters and a terminator - which is why the retail names are `bh`,
    # `dt`, `fwy` and not the full neighbourhood names. Midnight Club 2 spells
    # its own hoods `l_beverlyhills`, `l_downtown` and so on, so the CODE
    # prefix carries over but the rest has to be abbreviated on the way in.
    #
    # When more hoods are asked for than the donor has, the records cycle: the
    # record is a 0xB0-byte blob copied and relinked, and reusing one is only a
    # matter of the name written over it.
    do_doador = nomes_dos_hoods(doador)
    nomes_hood = list(hoods) if hoods else do_doador
    entradas = bytearray()
    for i, nm in enumerate(nomes_hood):
        registro_hood(e, doador, nm, 'hood_rec%d' % i, i % len(do_doador))
        ent = bytearray(TAM_ENTRADA_HOOD)
        if i == 0:
            struct.pack_into('<I', ent, 4, 1)   # so o primeiro leva o modelo
        entradas += ent
    # O COOKIE DO new[] ANTES DO ARRAY DE HOODS. O destrutor do mcCity (slot +8,
    # chamado por mcCity::Delete 0x2575C0 quando a cidade e descarregada INTEIRA)
    # le a contagem em hoods-16 e chama mcHood::dtor em cada entrada de 20 bytes,
    # do fim para o comeco. Sem cookie valia o que estivesse ali: em Paris
    # 0x80000000 (x20 estoura para 0, nenhum dtor - funcionava por sorte), em LA 1
    # (so o hood 0, vazio), no Tokyo MC2 0xCDCD0008 - o laco andou por lixo e
    # travou em mcHood::DeleteModels 0x25D418 (04/10/2026, saida para o frontend
    # pelo caminho de San Diego). Contagem 0, o mesmo que Paris faz na pratica:
    # os hoods vivem dentro do .pck e o jogo apaga o pck com o paging desligado.
    off_cookie = e.poe(struct.pack('<I', 0) + b'\xCD' * 12 + bytes(entradas), 'hoods_cookie')
    off_ent = off_cookie + 16
    e.rotula('hoods', off_ent)
    vazio = hood_vazio(e)
    for i in range(len(nomes_hood)):
        e.aponta(off_ent + TAM_ENTRADA_HOOD * i + 0, 'hood_rec%d' % i)
        # os dois arrays NUNCA sao nulos no varejo, mesmo com contagem zero
        e.aponta(off_ent + TAM_ENTRADA_HOOD * i + 8,
                 'componentes' if i == 0 else vazio)
        e.aponta(off_ent + TAM_ENTRADA_HOOD * i + 0x10, vazio)

    # ---------------------------------------------------------------- MapRoot
    # COPIADO INTEIRO do doador (0x290 bytes) com os ponteiros zerados, e so
    # depois os campos que eu controlo. Antes eu copiava dois pedacinhos
    # (+0x20..0x2B e +0x40..0x7F) e zerava o resto - ~0x250 bytes de escalares de
    # cidade (extents, distancias de LOD, fog, saturacao) iam a zero sem que eu
    # soubesse que existiam.
    r = 0x80
    e.d[r:r + TAM_MAPROOT] = maproot_base(doador)
    paletas_inline(e, r)
    e.u32(r + 0x00, tok(VT_MAPROOT))
    e.u32(r + 0x08, 0 if sonda else n_grupos)   # grupos de shader
    e.aponta(r + 0x0C, 'grupos')
    array_vazio(e, 'campo10')                   # nunca NULO: ver array_vazio()
    e.aponta(r + 0x10, 'campo10')
    e.u32(r + 0x14, 0 if sonda else len(nomes_hood))
    e.aponta(r + 0x18, 'hoods')
    if extents:
        mn, mx = extents
        for k, values in ((0x238, mn), (0x244, mx)):
            for j, value in enumerate(values):
                struct.pack_into('<f', e.d, r + k + 4 * j, value)
        struct.pack_into('<iiii', e.d, r + 0x26C, *grade)
    # o indice plano, agora com o componente de verdade dentro
    # O TAMANHO DOS DOIS ARRAYS POR CELULA E `grid_w * grid_h`, NAO UM NUMERO
    # QUALQUER. Eu escrevia 64 em +0x268 e deixava +0x26C/+0x270 como vieram do
    # doador (64 x 62 = 3968 no atlanta), quebrando a invariante
    # `cell_count == grid_w * grid_h` que vale nas tres cidades medidas. O laco
    # do culling indexa por `rel_z * grid_w + rel_x`, entao com a grade do
    # doador e um array de 64 ele lia ate 3968 registros de um buffer de 64 -
    # 47 KB de leitura fora do array.
    scratch = abs(struct.unpack_from('<i', e.d, r + 0x26C)[0]
                  * struct.unpack_from('<i', e.d, r + 0x270)[0]) or 64
    e.u32(r + 0x268, scratch)                   # == grid_w * grid_h
    bloco_1c(e, doador, 'campo1c', vas_comp, (), scratch, cel_por_unico)
    e.aponta(r + 0x1C, 'campo1c')
    e.aponta(r + 0x2C, 'paletaA')
    e.aponta(r + 0x30, 'paletaB')
    feitas = estruturas_extra(e, doador, 'compdata')
    n_cadeias = cadeias_1d4(e, doador, doador_textura)

    n = e.fecha(saida)
    print('gravado %s (%d bytes)' % (saida, n))
    print('  shader copiado do slot %d do doador; %d slots no grupo 0' % (veio_de, n_slots))
    print('  estruturas extra criadas: %s; %d cadeia(s) de +0x1D4/+0x1D8'
          % (', '.join('+0x%X' % x for x in feitas), n_cadeias))
    print('  %d bloco(s), %d vertices, raio %.1f, escala 1/%.0f'
          % (len(blocos), sum(len(p) for p, _u, _n, _o in blocos), raio, 1.0 / escala))
    return n


# --------------------------------------------------------------------------
# a cidade de verdade: alimentar o construtor com um place.tsv
# --------------------------------------------------------------------------
#
# `constroi()` monta UM componente a partir de um cubo de teste. Aqui entra a
# tabela que o `mc2_port.py cidade` escreve: uma linha por coisa a desenhar,
# com o nome da malha, a matriz e a AABB.
#
# Primeira fatia de proposito: SO as linhas `comp`. Elas ja estao em coordenada
# de mundo. A AABB do `.hood` pode incluir OUTRAS partes do mesmo objeto,
# portanto nao serve de pivo da parte escolhida. Elas nao dependem do registro
# de instancia, que ainda nao foi
# decodificado. Sao as ruas e os predios; as `inst` sao muros, palmeiras e
# postes repetidos.
#
# O nome de hood do `.pck` cabe em QUATRO BYTES (tres caracteres e o
# terminador), e essa abreviacao e a que a fork C++ fixou dos dois lados.
ABREV_HOOD = {
    'l_beverlyhills': 'bh',  'l_downtown': 'dt',   'l_ghetto': 'gh',
    'l_hills': 'hl',         'l_hollywood': 'hw',  'l_i05': 'i05',
    'l_i10': 'i10',          'l_i101': '101',      'l_i105': '105',
    'l_industrial': 'ind',   'l_lax': 'lax',       'l_santamonica': 'sm',
}


def le_place(caminho):
    """(linhas, extents) de um `<cidade>_place.tsv`."""
    extents = {}
    cab = None
    linhas = []
    with open(caminho, 'r', errors='replace') as f:
        for l in f.read().splitlines():
            if l.startswith('#'):
                p = [x.strip() for x in l[1:].split('\t')]
                if p and p[0] in ('extents_min', 'extents_max'):
                    extents[p[0]] = [float(x) for x in p[1:] if x]
                continue
            if not l.strip():
                continue
            if cab is None:
                cab = l.split('\t')
                continue
            c = l.split('\t')
            if len(c) >= len(cab):
                linhas.append(dict(zip(cab, c)))
    return linhas, extents


def caminho_da_malha(pasta, linha):
    """O `.mod` que uma linha do place.tsv nomeia."""
    if linha['part'] == '-':
        nome = '%s_%s.mod' % (linha['name'], linha['lod'])
    else:
        nome = '%s_%s_%s.mod' % (linha['name'], linha['lod'], linha['part'])
    p = os.path.join(pasta, nome)
    return p if os.path.isfile(p) else None


def centra(blocos):
    """Blocos deslocados para a MEDIA DA CAIXA, e o deslocamento aplicado.

    Medido no atlanta: a geometria de um componente e LOCAL e centrada, e o
    mundo entra por `ComponentData+0x2C`. Em `a_bh_blk_02x#geom` a caixa local
    vai de -121.6 a 121.8 em x e de -162.9 a 162.8 em z, com a posicao em
    (-388.0, 12.4, -1042.2); o raio gravado (203.8) e exatamente a meia-diagonal
    dessa caixa.

    O `le_modelo` ja tira o grosso, mas centra x e z pela caixa e apoia y no
    zero, entao sobra uma diferenca em y que precisa entrar na posicao.
    """
    pts = [q for pos, _u, _n, _o in blocos for q in pos]
    mn = [min(q[i] for q in pts) for i in range(3)]
    mx = [max(q[i] for q in pts) for i in range(3)]
    c = [(mn[i] + mx[i]) / 2.0 for i in range(3)]
    if max(abs(v) for v in c) < 1e-4:
        return blocos, c
    fora = [([tuple(q[i] - c[i] for i in range(3)) for q in pos], u, nr, o)
            for pos, u, nr, o in blocos]
    return fora, c


def le_componente_mundo(caminho):
    """Localiza a parte de um componente sem mudar seus vertices de mundo.

    O .mod escolhido pode ser so main/refl/emissive, mas emin/emax do TSV
    pertencem ao objeto inteiro do .hood. Usar o centro daquela caixa como
    posicao depois de centrar esta parte desloca a geometria (368.26 unidades
    no l_santamonica_blk_14). Restaure a origem MC2 e guarde exatamente o
    centro retirado por centra em ComponentData+0x2C. AABB e culling, nao pivo.
    """
    blocos = le_modelo(caminho, 1.0, preservar_origem=True)
    return centra(blocos) if blocos else ([], (0.0, 0.0, 0.0))


def emite_geometria(e, blocos, chave, posicao, indice_material=1):
    """Pacotes + lista + tabela de grupos + material + mesh + ComponentData.

    A mesma sequencia que `constroi()` faz para o cubo, extraida para poder
    rodar centenas de vezes. Devolve (chave do ComponentData, raio).
    """
    # TRES CAMINHOS, do mais informado ao menos. Com grupos E indices de
    # textura, uma malha com UM GRUPO POR MATERIAL - o unico jeito de dar
    # mais de uma textura a um componente. Sem eles, o caminho antigo.
    if GRUPOS_DO_JOGO and INDICES_DO_JOGO:
        emite_malha_agrupada(e, GRUPOS_DO_JOGO, chave, INDICES_DO_JOGO,
                             SLOTS_CPV_COMPONENTE)
    else:
        if PACOTES_DO_JOGO:
            # Pacotes prontos, vindos de um mesh.pck que o proprio jogo montou.
            lista = bytearray()
            for payload, qw, nv in PACOTES_DO_JOGO:
                off = e.poe(flip_winding_payload(payload) if FLIP_WINDING else payload, align=16)
                lista += struct.pack('<IHH', e.va(off), qw, nv)
            n_pacotes = len(PACOTES_DO_JOGO)
        else:
            escala = mc2.pick_scale(blocos)
            pacotes = [mc2.make_block(pos, uv, nr, escala, i % 2 == 1)
                       for i, (pos, uv, nr, _o) in enumerate(blocos)]
            offs = [e.poe(pk, align=16) for pk in pacotes]
            lista = bytearray()
            for off, pk, (pos, _u, _n, _o) in zip(offs, pacotes, blocos):
                lista += struct.pack('<IHH', e.va(off), (len(pk) + 15) // 16, len(pos))
            n_pacotes = len(blocos)
        e.poe(bytes(lista), chave + '_lista')

        off_gt = e.poe(struct.pack('<IHH', 0, n_pacotes, 0), chave + '_gt')
        e.aponta(off_gt, chave + '_lista')

        # a tabela de material fica LOGO ANTES do objeto mesh, como no retail
        e.alinha(16)
        off_mt = len(e.d)
        e.d += struct.pack('<H', indice_material) + b'\x00\x00'
        e.rotula(chave + '_mt', off_mt)

        # +0x18 nunca e zero no varejo: 624 malhas do atlanta tem 1, 408 tem
        # ponteiro e 190 tem CDCDCDCD. 1 e a forma mais comum e a unica que da
        # para escrever sem inventar um destino.
        off_mesh = e.poe(struct.pack('<IIHHIIII', tok(VT_MESH_TOKEN), 0, 1,
                                     SLOTS_CPV_COMPONENTE, 0, 0, 0, 1),
                         chave + '_mesh', align=4)
        # NAO mudar para align=16. O varejo tem 100% das malhas alinhadas a 16 e as
        # minhas ficam em %16==4, mas trocar para 16 REGREDIU: a cidade que rodava a
        # 60 FPS passou a travar no PRIMEIRO frame (game frames = 1). Alinhar
        # desloca todas as alocacoes seguintes, e alguma coisa depende do layout que
        # o align=4 produz - provavelmente a adjacencia entre a tabela de material e
        # o objeto mesh, que o retail mantem colados. Medido, nao suposto.
        e.aponta(off_mesh + 0x0C, chave + '_mt')
        e.aponta(off_mesh + 0x10, chave + '_gt')
        grupo_cpv = ([([0] * nv,) for _p, _q, nv in PACOTES_DO_JOGO]
                     if PACOTES_DO_JOGO else blocos)
        emite_cadeia_por_vertice(e, [grupo_cpv], chave + '_t14')
        e.aponta(off_mesh + 0x14, chave + '_t14')

    # o raio do retail e a meia-diagonal da caixa local, nao a distancia ao
    # vertice mais longe do centroide
    pts = [q for pos, _u, _n, _o in blocos for q in pos]
    raio = max((q[0] ** 2 + q[1] ** 2 + q[2] ** 2) ** 0.5 for q in pts)

    off_cd = e.poe(compdata(raio, posicao), chave + '_cd')
    # O MESH VAI DENTRO, na forma majoritaria do varejo (431 de 650 no tokyo).
    # O objeto de mesh separado emitido acima continua no arquivo e continua
    # valido - o varejo tambem tem os dois -, mas quem manda e o embutido.
    poe_mesh_embutido(e, off_cd, chave + '_mt', chave + '_gt',
                      blocos, chave + '_emb')
    e.rotula(chave + '_cd_nome', off_cd + 0x70)
    return chave + '_cd', raio, off_cd


CENTRO_REAL_DO_PCK = {}      # tipo -> (cx, cz) medido no .pck do jogo


def centro_real_do_pck(caminho):
    """Centro XZ dos vertices que o JOGO montou, nao os do .mod.

    A matriz de cada Instance no place.tsv assume a malha RECENTRADA: medindo
    as 8511 instancias, 6249 (73%) so batem com `final = (tx,tz)`. Mas dos 431
    tipos que vieram do jogo, 71 preservam o pivo original (centro a ate 1894
    da origem) - as instancias desses voam, e e o que aparecia empilhado longe.
    Como a geometria vem do `.pck` e nao da para recentrar os vertices, eu meco
    o centro real aqui e COMPENSO na translacao.
    """
    import struct as _s
    d = open(caminho, 'rb').read()
    N = len(d)
    vb = _s.unpack_from('<I', d, 0)[0]
    fo = lambda v: v - vb + 0x80
    w = lambda o: _s.unpack_from('<I', d, o)[0]
    h = lambda o: _s.unpack_from('<H', d, o)[0]
    g, geo = w(0x88) & 0xFFFF, fo(w(0x90))
    xs = []
    zs = []
    for gi in range(g):
        ge = geo + 8 * gi
        lst, n = fo(w(ge)), h(ge + 4)
        for k in range(n):
            e = lst + 8 * k
            dp, qw = fo(w(e)), h(e + 4)
            if not (0x80 <= dp < N) or dp + 16 * qw > N:
                continue
            sc = _s.unpack_from('<f', d, dp + 4)[0]
            nv = _s.unpack_from('<I', d, dp + 8)[0]
            if not (0 < nv <= 64) or not (0 < sc < 100):
                continue
            if d[dp + 15] != 0x69:          # so o stream de POSICAO
                continue
            for i in range(nv):
                o = dp + 16 + 6 * i
                if o + 6 > N:
                    break
                x, _y, z = _s.unpack_from('<hhh', d, o)
                xs.append(x * sc)
                zs.append(z * sc)
    if not xs:
        return None
    return (sum(xs) / len(xs), sum(zs) / len(zs))


def _matriz_da_linha(l):
    """A Matrix34 de uma linha `inst` do place.tsv: 12 floats na ordem do jogo,
    tres linhas de rotacao 3x3 e depois a translacao."""
    return [float(l[c]) for c in
            ('m00', 'm01', 'm02', 'm10', 'm11', 'm12',
             'm20', 'm21', 'm22', 'tx', 'ty', 'tz')]


def _centro_aabb(l):
    return tuple((float(l['emin' + a]) + float(l['emax' + a])) / 2.0
                 for a in ('x', 'y', 'z'))


def compdata_inst(raio, centro, nome):
    """ComponentData de um TIPO de instancia: igual ao do comp, mas com o token
    mcInstCityModelType em +0x28 e o centro em coordenada LOCAL (a matriz de
    cada Instance e que o poe no mundo)."""
    cd = bytearray(0xF0)
    struct.pack_into('<I', cd, 0x00, 1)
    struct.pack_into('<I', cd, 0x28, tok(VT_INST_TIPO_TOKEN))
    struct.pack_into('<3f', cd, 0x2C, *centro)
    struct.pack_into('<f', cd, 0x38, raio)
    cd[0x70:0x70 + len(nome)] = nome
    return bytes(cd)


# Pacotes VIF vindos de um .pck que O PROPRIO JOGO gerou (ver
# mc3_heap_to_pck.py). Quando isto esta preenchido, _emite_mesh copia estes
# blocos em vez de chamar mc2.make_block - o que troca a MINHA estripificacao,
# paridade, ADC e corte em bloco pelas do jogo, que sao as quatro coisas em que
# a emissao a mao errava. Lista de (payload, quadwords, vertices).
PACOTES_DO_JOGO = None
VT_TEXTURA_TOKEN = 0x007A2320  # token serializado do rmcTexturePS2 (vtable runtime = 0x00627280)
# Quando --pck-malha aponta para uma pasta: nome do modelo -> pacotes do jogo.
PASTA_PCK = None
PCK_POR_MODELO = {}
GRUPOS_POR_MODELO = {}
GRUPOS_DO_JOGO = None      # grupos do modelo corrente
TEXTURAS_POR_MODELO = {}   # nome do modelo -> nomes de textura, na ordem dos mtl
do_jogo = [0]
DEPURA = [0]


def le_grupos_de_pck(caminho):
    """Os pacotes de um mesh.pck AGRUPADOS, um item por grupo.

    O `.pck` que o jogo montou preserva a divisao por material (27 grupos num
    modelo de 27 materiais). Achatar isso num grupo so, como eu vinha fazendo,
    obriga a cidade inteira a um indice de material e e por isso que tudo saia
    com a mesma cara. Guardo a divisao para poder dar uma textura por grupo.
    """
    import struct as _s
    d = open(caminho, 'rb').read()
    vb = _s.unpack_from('<I', d, 0)[0]
    fo = lambda a: a - vb + 0x80
    grupos = _s.unpack_from('<I', d, 0x88)[0] & 0xFFFF
    geo = fo(_s.unpack_from('<I', d, 0x90)[0])
    out = []
    for g in range(grupos):
        go = geo + 8 * g
        pk, n = _s.unpack_from('<IH', d, go)
        e0 = fo(pk)
        item = []
        for k in range(n):
            dp, qw, nv = _s.unpack_from('<IHH', d, e0 + 8 * k)
            if nv == 0 or qw == 0:
                continue
            o = fo(dp)
            item.append((d[o:o + 16 * qw], qw, nv))
        out.append(item)
    return out


def le_pacotes_de_pck(caminho):
    """Extrai os pacotes VIF de um mesh.pck, na ordem dos grupos."""
    import struct as _s
    d = open(caminho, 'rb').read()
    vb = _s.unpack_from('<I', d, 0)[0]
    fo = lambda a: a - vb + 0x80
    grupos = _s.unpack_from('<I', d, 0x88)[0] & 0xFFFF
    geo = fo(_s.unpack_from('<I', d, 0x90)[0])
    out = []
    for g in range(grupos):
        go = geo + 8 * g
        pk, n = _s.unpack_from('<IH', d, go)
        e0 = fo(pk)
        for k in range(n):
            dp, qw, nv = _s.unpack_from('<IHH', d, e0 + 8 * k)
            # PACKET VAZIO NAO PROPAGA. O jogo emite alguns com nv=0, e eles
            # criavam assimetria entre a lista de blocos e a cadeia por-vertice
            # (a malha declarava 2 blocos, [74, 0], e a cadeia 1) - o
            # verificador acusava "count 1 != 2" e "payload fora" em 194 malhas.
            # Um bloco sem vertice nao desenha nada, entao some.
            if nv == 0 or qw == 0:
                continue
            o = fo(dp)
            out.append((d[o:o + 16 * qw], qw, nv))
    return out


def slots_de_textura(modelo, n_grupos):
    """Slot de shader de cada grupo, pelo NOME da textura que o mtl pedia.

    A LISTA TEM QUE ESTAR ALINHADA POR MATERIAL, uma entrada por `mtl` do .mod,
    inclusive os que tem `textures: 0`. O mapa antigo listava so os materiais COM
    textura, e como o `.pck` tem um grupo por material, tudo depois de um
    material sem textura ficava deslocado de um: o grupo recebia a textura do
    material seguinte e o ultimo caia no slot 0. Medido: 29 modelos tem material
    sem textura e neles **379 grupos** saiam trocados; e o slot 0 e o
    `fx_rearlight_glow`, uma textura de brilho branca e difusa - eram os planos
    chapados claros no meio da cidade. A Fork City MODS 2 viu os mesmos dois
    modelos (`industrial_blk_06` e `_04`) na lista visivel "com apenas
    fx_rearlight_glow", o que fecha com esta medicao.

    Material sem textura HERDA o do anterior em vez de cair no slot 0: ele
    desenha com cor difusa propria (0.4 0.4 0.4 no caso tipico), entao qualquer
    coisa neutra e melhor que carimbar um glow.
    """
    nomes = TEXTURAS_POR_MODELO.get(modelo, [])
    # Material sem textura ANTES do primeiro texturizado nao tem "anterior" de
    # quem herdar, e cair no slot 0 e a pior escolha que existe: o slot 0 e o
    # `fx_rearlight_glow`. MEDIDO EM 12/09, com bisseccao de uma variavel: um
    # mapa alinhado por material, que passa a declarar o vazio inicial de 26
    # modelos, mandou 205 grupos para o slot 0 e o jogo morreu no PRIMEIRO
    # QUADRO com `R5900 Exception: Jump to unaligned address (PC 0x00000633)`.
    # O unico delta entre o build que roda e o que morre eram 410 bytes, todos
    # em tabela de material. Entao o vazio INICIAL herda para FRENTE, do
    # primeiro material texturizado, e nunca para o slot 0.
    # E O SLOT 0 E FATAL, nao apenas feio. Medido em 12/09 em duas falhas
    # independentes: (a) 205 grupos mandados para o slot 0 pelo vazio inicial
    # mataram o jogo no primeiro quadro; (b) as 216 pecas novas, que nao tem
    # entrada no mapa, caiam TODAS no slot 0 e o boot morreu em
    # `datPageFile::PageIn` (pc 0x42cae4/0x42cbec/0x42cc1c/0x42cc40) lendo
    # enderecos de lixo. O motivo esta do lado do .ppf: o slot 0 e o
    # `fx_rearlight_glow` e o chunk dele e o UNICO dos 965 com o corpo
    # inteiramente zerado, entao o page-in desreferencia cabecalho vazio.
    # Por isso o fallback final e 1, nunca 0.
    FALLBACK = 1
    primeiro = FALLBACK
    for n in nomes:
        k = n.lower() if n else ''
        if k and k in POS_TEXTURA:
            primeiro = POS_TEXTURA[k]
            break
    fora = []
    ultimo = primeiro
    for g in range(n_grupos):
        n = nomes[g].lower() if g < len(nomes) else ''
        if n and n in POS_TEXTURA:
            ultimo = POS_TEXTURA[n]
        fora.append(ultimo)
    return fora


def emite_malha_agrupada(e, grupos, chave, indices, slot_count=1):
    """Malha com UM GRUPO POR MATERIAL, para poder dar uma textura a cada um.

    `grupos` e a saida do le_grupos_de_pck (lista de listas de pacotes) e
    `indices` traz o slot de shader de cada grupo. A versao anterior achatava
    tudo num grupo so e usava um indice unico - por isso a cidade inteira saia
    com a mesma cara.

    Layout, o mesmo dos tres niveis do resto do arquivo: a CONTAGEM vem 16
    bytes ANTES do array, e o array tem uma entrada de 8 bytes por grupo
    (`[ptr para a lista][u16 pacotes][u16 0]`).
    """
    for g, pacotes in enumerate(grupos):
        lista = bytearray()
        for payload, qw, nv in pacotes:
            off = e.poe(flip_winding_payload(payload) if FLIP_WINDING else payload, align=16)
            lista += struct.pack('<IHH', e.va(off), qw, nv)
        e.poe(bytes(lista), '%s_lista%d' % (chave, g))

    e.alinha(16)
    e.poe(struct.pack('<I', len(grupos)) + bytes(12))      # a contagem, em -16
    off_gt = e.poe(bytes(8 * len(grupos)), chave + '_gt')
    for g, pacotes in enumerate(grupos):
        e.aponta(off_gt + 8 * g, '%s_lista%d' % (chave, g))
        struct.pack_into('<H', e.d, off_gt + 8 * g + 4, len(pacotes))

    e.alinha(16)
    off_mt = len(e.d)
    for g in range(len(grupos)):
        e.d += struct.pack('<H', indices[g] if g < len(indices) else 0)
    e.d += bytes((-len(e.d)) % 4)
    e.rotula(chave + '_mt', off_mt)

    off_mesh = e.poe(struct.pack('<IIHHIIII', tok(VT_MESH_TOKEN), 0,
                                 len(grupos), slot_count, 0, 0, 0, 1),
                     chave + '_mesh', align=4)
    e.aponta(off_mesh + 0x0C, chave + '_mt')
    e.aponta(off_mesh + 0x10, chave + '_gt')
    grupo_cpv = [[([0] * nv,) for _p, _q, nv in pac] for pac in grupos]
    emite_cadeia_por_vertice(e, grupo_cpv, chave + '_t14', slot_count=slot_count)
    e.aponta(off_mesh + 0x14, chave + '_t14')
    return off_mesh


def _emite_mesh(e, blocos, chave, indice_material=1, slot_count=1):
    """So a malha (pacotes + lista + grupos + material + rmcModelGeom), sem
    ComponentData. Extraido de emite_geometria para os tipos de instancia."""
    if PACOTES_DO_JOGO:
        # Os pacotes vem prontos do jogo: copiar e refazer so a lista.
        lista = bytearray()
        for payload, qw, nv in PACOTES_DO_JOGO:
            off = e.poe(flip_winding_payload(payload) if FLIP_WINDING else payload, align=16)
            lista += struct.pack('<IHH', e.va(off), qw, nv)
        n_pacotes = len(PACOTES_DO_JOGO)
    else:
        escala = mc2.pick_scale(blocos)
        pacotes = [mc2.make_block(pos, uv, nr, escala, i % 2 == 1)
                   for i, (pos, uv, nr, _o) in enumerate(blocos)]
        offs = [e.poe(pk, align=16) for pk in pacotes]
        lista = bytearray()
        for off, pk, (pos, _u, _n, _o) in zip(offs, pacotes, blocos):
            lista += struct.pack('<IHH', e.va(off), (len(pk) + 15) // 16, len(pos))
        n_pacotes = len(blocos)
    e.poe(bytes(lista), chave + '_lista')
    # n_pacotes, NAO len(blocos): com --pck-malha a lista tem os pacotes do
    # jogo e os blocos sao so a leitura do modelo. Declarar len(blocos) fazia a
    # tabela de grupos prometer mais blocos do que a lista tem, e o verificador
    # acusava "count 1 != 2" com um bloco fantasma de 0 vertices.
    off_gt = e.poe(struct.pack('<IHH', 0, n_pacotes, 0), chave + '_gt')
    e.aponta(off_gt, chave + '_lista')
    e.alinha(16)
    off_mt = len(e.d)
    e.d += struct.pack('<H', indice_material) + b'\x00\x00'
    e.rotula(chave + '_mt', off_mt)
    off_mesh = e.poe(struct.pack('<IIHHIIII', tok(VT_MESH_TOKEN), 0, 1,
                                 slot_count, 0, 0, 0, 1),
                     chave + '_mesh', align=4)
    # NAO mudar para align=16. O varejo tem 100% das malhas alinhadas a 16 e as
    # minhas ficam em %16==4, mas trocar para 16 REGREDIU: a cidade que rodava a
    # 60 FPS passou a travar no PRIMEIRO frame (game frames = 1). Alinhar
    # desloca todas as alocacoes seguintes, e alguma coisa depende do layout que
    # o align=4 produz - provavelmente a adjacencia entre a tabela de material e
    # o objeto mesh, que o retail mantem colados. Medido, nao suposto.
    e.aponta(off_mesh + 0x0C, chave + '_mt')
    e.aponta(off_mesh + 0x10, chave + '_gt')
    # A cadeia por-vertice tem que casar PACOTE A PACOTE com a malha. Com
    # --pck-malha os pacotes sao os do jogo, entao a contagem de vertices sai
    # deles e nao dos meus blocos - senao a cadeia declara 93 blocos para uma
    # malha de 27 e o Place percorre lixo.
    if PACOTES_DO_JOGO:
        grupo_cpv = [([0] * nv,) for _payload, _qw, nv in PACOTES_DO_JOGO]
    else:
        grupo_cpv = blocos
    emite_cadeia_por_vertice(e, [grupo_cpv], chave + '_t14', slot_count=slot_count)
    e.aponta(off_mesh + 0x14, chave + '_t14')


def emite_instancias(e, insts, modelos, grade, indice_material=1,
                     mapa_hood=None):
    """Constroi os TIPOS de instancia e os registros Instance de 0x60.

    Cada modelo distinto vira UM tipo (mesh em coord local + ComponentData
    mcInstCityModelType), encadeado em MapRoot+0x198. Cada linha `inst` vira um
    registro Instance que aponta para o tipo, com a sua Matrix34, a tile box do
    centro de mundo e o raio local do tipo. Instances do mesmo tipo formam uma
    lista ligada por next/prev.

    Devolve (inst_vas, cel_por_inst, por_hood_inst, chave_cabeca, n_tipos).
    """
    contagem_por_tipo = {}
    for l in insts:
        key = (l['name'], l['lod'], l['part'])
        contagem_por_tipo[key] = contagem_por_tipo.get(key, 0) + 1

    tipos = {}                      # key -> (chave, raio, centro) ou None
    ordem_tipos = []
    for l in insts:
        key = (l['name'], l['lod'], l['part'])
        if key in tipos:
            continue
        p = caminho_da_malha(modelos, l)
        if not p:
            tipos[key] = None
            continue
        try:
            # A matriz do place.tsv pertence ao pivô original desta malha.
            blocos = le_modelo(p, 1.0, preservar_origem=True)
        except Exception:
            tipos[key] = None
            continue
        if not blocos:
            tipos[key] = None
            continue
        chave = 'itipo_%d' % len(ordem_tipos)
        pts = [q for pos, _u, _n, _o in blocos for q in pos]
        centro = tuple((min(p[i] for p in pts) + max(p[i] for p in pts)) / 2.0
                       for i in range(3))
        raio = max(((q[0] - centro[0]) ** 2 + (q[1] - centro[1]) ** 2
                    + (q[2] - centro[2]) ** 2) ** 0.5 for q in pts)
        slot_count = contagem_por_tipo[key]
        # Cada TIPO de instancia tambem tem o seu .pck vindo do jogo. Sem isto
        # os 431 tipos ficavam na emissao a mao enquanto os 298 componentes
        # vinham do jogo - metade da cidade de cada jeito.
        global PACOTES_DO_JOGO
        globals()['GRUPOS_DO_JOGO'] = None
        globals()['INDICES_DO_JOGO'] = None
        if PASTA_PCK:
            base_nome = os.path.splitext(os.path.basename(p))[0].lower()
            PACOTES_DO_JOGO = PCK_POR_MODELO.get(base_nome)
            if PACOTES_DO_JOGO:
                do_jogo[0] += 1
            # OS TIPOS DE INSTANCIA TAMBEM. Eu tinha posto um grupo por material
            # so no caminho dos COMPONENTES; os 431 tipos continuavam no caminho
            # antigo e a cadeia por-vertice deles nao casava com a tabela de
            # grupos - 299 de 729 malhas validas em LA inteira.
            globals()['GRUPOS_DO_JOGO'] = GRUPOS_POR_MODELO.get(base_nome)
            globals()['INDICES_DO_JOGO'] = (
                slots_de_textura(base_nome, len(GRUPOS_POR_MODELO[base_nome]))
                if (base_nome in GRUPOS_POR_MODELO) else None)
        if GRUPOS_DO_JOGO and INDICES_DO_JOGO:
            emite_malha_agrupada(e, GRUPOS_DO_JOGO, chave, INDICES_DO_JOGO,
                                 slot_count)
        else:
            _emite_mesh(e, blocos, chave, indice_material, slot_count=slot_count)
        off_cd = e.poe(compdata_inst(raio, centro, b'gerado_inst'), chave + '_cd')
        poe_mesh_embutido(e, off_cd, chave + '_mt', chave + '_gt',
                          blocos, chave + '_emb', slot_count=slot_count)
        e.rotula(chave + '_nome', off_cd + 0x70)
        tipos[key] = (chave, raio, centro)
        ordem_tipos.append(chave)

    # encadear os tipos em +0x198 (mesma forma da cadeia de comps em +0x194)
    for k, chave in enumerate(ordem_tipos):
        cd = e.marca[chave + '_cd']
        e.aponta(cd + 0x04, 'extra_198')
        e.aponta(cd + 0x08, chave + '_nome')
        if k:
            e.aponta(cd + 0x0C, ordem_tipos[k - 1] + '_cd')
            e.aponta(cd + 0x14, ordem_tipos[k - 1] + '_cd')
        if k + 1 < len(ordem_tipos):
            e.aponta(cd + 0x10, ordem_tipos[k + 1] + '_cd')

    # os registros Instance, contiguos por hood
    gw = grade[0]
    inst_vas = []
    cel_por_inst = {}
    por_hood_inst = {}
    cadeia_do_tipo = {}
    # agrupar pelo hood de DESTINO (o do doador), nao pelo hood do MC2: os
    # registros de um hood tem que ficar contiguos, e o arquivo so pode ter os
    # hoods que o doador tem.
    por_hood = {}
    for l in insts:
        dest = mapa_hood.get(l['hood'], l['hood']) if mapa_hood else l['hood']
        por_hood.setdefault(dest, []).append(l)

    for hood, itens in por_hood.items():
        base_nome = None
        n_hood = 0
        for l in itens:
            key = (l['name'], l['lod'], l['part'])
            t = tipos.get(key)
            if not t:
                continue
            chave_tipo, raio, _centro = t
            cx, cy, cz = _centro_aabb(l)
            x0, x1, z0, z1 = caixa_de_celulas(grade, cx, cz, raio, raio)
            rec = bytearray(TAM_INSTANCE)
            struct.pack_into('<I', rec, 0x10, tok(VT_INST_TOKEN))
            rec[0x0B] = 8
            rec[0x14], rec[0x15], rec[0x16], rec[0x17] = x0, x1, z0, z1
            struct.pack_into('<f', rec, 0x18, raio)
            # NAO COMPENSAR O PIVO. Tentei subtrair o centro real do .pck da
            # translacao, achando que os tipos com pivo preservado deslocavam as
            # instancias. MEDIDO ANTES DE INSTALAR: dos 431 tipos, so 74
            # instancias (0,9% de 8511) vem de tipo com pivo grande, e dessas
            # **70 ficam mais perto do lugar certo SEM a compensacao**. A
            # correcao piorava. O pivo nao e a causa da cidade faltando.
            struct.pack_into('<12f', rec, 0x20, *_matriz_da_linha(l))
            struct.pack_into('<3f', rec, 0x50, cx, cy, cz)
            idx = len(inst_vas)
            chave_i = 'inst_%d' % idx
            # DoSetWorld (0x2ADB48) uploads Instance+0x20 with three LQ.
            # LQ silently rounds down to 16 bytes. With align=4 the scalar
            # scratchpad mirror is right but DMA reads the preceding CPV
            # index as matrix[0], losing tz and flattening/stacking objects.
            # 0x60-byte records remain contiguous after aligning the first.
            off = e.poe(bytes(rec), chave_i, align=16)
            e.aponta(off + 0x0C, chave_tipo + '_cd')
            if base_nome is None:
                base_nome = 'insts_%s' % hood
                e.rotula(base_nome, off)
            inst_vas.append(e.va(off))
            cel_por_inst[idx] = [z * gw + x for z in range(z0, z1 + 1)
                                 for x in range(x0, x1 + 1)]
            cadeia_do_tipo.setdefault(key, []).append((chave_i, off))
            n_hood += 1
        if base_nome is not None:
            por_hood_inst[hood] = (base_nome, n_hood)

    # a lista ligada por tipo: next/prev e chain_index; e o +0x18 do TIPO
    # aponta de volta para a PRIMEIRA instancia dele (nunca nulo no varejo).
    for key, cadeia in cadeia_do_tipo.items():
        chave_tipo = tipos[key][0]
        e.aponta(e.marca[chave_tipo + '_cd'] + 0x18, cadeia[0][0])
        for j, (chave_i, off) in enumerate(cadeia):
            struct.pack_into('<I', e.d, off + 0x1C, j)
            # O SENTIDO DOS DOIS ELOS ESTAVA TROCADO, e isso apagava 95 por
            # cento da cidade. Quem percorre a lista e
            # `mcCullableType::RenderAllInstances` (varejo 0x0024B1A8):
            #
            #     cull = *(tipo + 0x18);                  // cabeca dos ATIVOS
            #     while (cull) { Render(cull); cull = *(cull + 0x04); }
            #
            # ou seja +0x04 E O NEXT. O `mcCullableType::AddToActive` da alpha
            # (varejo 0x0024B030) confirma o par: ele zera `cull[0]` e poe a
            # cabeca antiga em `cull[1]`, isto e +0x00 = prev e +0x04 = next.
            # Escrito ao contrario, o render anda o sentido do PREV a partir da
            # cabeca e para no primeiro no. Medido: a v7 alcancava 431 de 8511
            # instancias (5,1 por cento), exatamente uma por tipo, enquanto o sd
            # de varejo alcanca 5008 de 5008.
            if j + 1 < len(cadeia):
                e.aponta(off + 0x04, cadeia[j + 1][0])
            if j:
                e.aponta(off + 0x00, cadeia[j - 1][0])

    cabeca = ordem_tipos[-1] + '_cd' if ordem_tipos else None
    return inst_vas, cel_por_inst, por_hood_inst, cabeca, len(ordem_tipos)


# LIGAR O STREAM DE LUZ POR VERTICE.
#
# Medido no atlanta: so 4,5%% dos blocos (471 de 10361) carregam o stream de
# ITOP+2, e mesmo assim a cidade inteira aparece - porque o bloco SEM stream
# HERDA o que o anterior deixou na memoria da VU. Numa cidade gerada do zero
# nenhum bloco escreve, entao todos herdam lixo, e a meia-noite isso e preto:
# a geometria desenhava (531 e 580 draw calls medidos) e nao se via nada.
#
# TENTADO E REVERTIDO: ligar em todos os blocos travou no PRIMEIRO frame
# (game frames = 1), mesma assinatura da tentativa de alinhar a 16.
#
# EU EXPLIQUEI ESSA REVERSAO ERRADO, e a FORK C++ MODS AND PATCHES desmentiu
# por decompilacao. Eu tinha escrito que 'quem decide se o stream e lido e a
# palavra de flags do MATERIAL'. NAO E. mcCityModelClass::SetRenderStates
# (0x0024B300, a vt[12] da lista 3 de cullables) chama rmcSetCpvMode(1, 0) e
# rmcCpvPalette::Download(*(u32*)(mcCity + 0x2C)) UMA VEZ POR PASSE. O CPV -
# colour per vertex - fica ligado para a cidade inteira, decidido pela CLASSE
# do cullable, nao por material e nao por bloco. O ceu, na mesma posicao da
# vtable, chama rmcSetCpvMode(0, 0). Ou seja: o dado do ITOP+2 e SEMPRE
# consumido no passe da cidade, e escrever o stream nao e proibido.
#
# Entao a travada do primeiro frame e defeito do PACOTE que eu emito, nao uma
# regra do motor. O que ainda pode diferir e o programa de VU vigente, que
# mcCullableMgr::Render reenvia por lowPsxGfx::DoMicrocode em volta de certas
# listas - por isso o teste continua sendo EMPARELHADO: copiar o shader de um
# slot cujos blocos comprovadamente carregam o stream e ligar NORMAIS junto.
# Medido no atlanta, os blocos com stream usam os indices de material 19, 72,
# 65, 24, 293, 7, 71 e 26; destes, todos menos o 293 estao entre os 128 slots
# utilizaveis do doador (ver --lista-shaders).
#
# POR QUE A PALETA BRANCA NAO SALVOU: conferido no arquivo, MapRoot+0x2C
# aponta certo para a paleta inline em +0x290, e o formato bate com o retail
# (256 entradas de 3 floats + pad). A minha e branca em todas as 256; a do
# retail tem 233 distintas. Se a cor final fosse so paleta[indice], a cidade
# gerada seria BRANCA, nao preta - o indice nao teria como escapar da tabela.
# Ela e preta, entao o que falha esta antes da consulta: sem nenhum bloco
# escrevendo o ITOP+2, o campo que vira VI10 e lixo de outro sistema, e nao um
# byte pequeno. Isto e mais uma razao para o teste emparelhado, nao uma prova.
#
# Ligado pelo --normais na linha de comando; o padrao continua desligado.
mc2.NORMAIS = False


def constroi_place(saida, doador, place, modelos, n_slots=1329,
                   n_grupos=18, indice_material=1, limite=None, so_hood=None,
                   doador_shader=None, max_inst=None, slot_shader=None,
                   doador_textura=None, hoods=None):
    """Uma cidade a partir do place.tsv, com a geometria de verdade."""
    globals()['DESLOC_TOKEN'] = token_do_doador(doador)
    linhas, extents = le_place(place)
    comps = [l for l in linhas if l['kind'] == 'comp']
    insts = [l for l in linhas if l['kind'] == 'inst']
    # O ORCAMENTO DE INSTANCIAS E O DO DOADOR. Ver instancias_do_doador().
    teto = max_inst if max_inst else instancias_do_doador(doador)
    if teto and len(insts) > teto:
        print('  instancias: %d no place.tsv, cortadas para %d (orcamento do doador)'
              % (len(insts), teto))
        insts = insts[:teto]
    if so_hood:
        comps = [l for l in comps if l['hood'] == so_hood]
        insts = [l for l in insts if l['hood'] == so_hood]
    if limite:
        comps = comps[:limite]
    if not comps:
        raise SystemExit('nenhuma linha `comp` selecionada em %s' % place)

    # A GRADE VEM DOS EXTENTS DA CIDADE, nao do doador. Sem isto, LA (que pede
    # 91x62 origem -50,-43) herdava a grade 64x62 do atlanta e o culling saia
    # deslocado 17 celulas em x.
    if extents.get('extents_min') and extents.get('extents_max'):
        mn = [float(v) for v in extents['extents_min'][:3]]
        mx = [float(v) for v in extents['extents_max'][:3]]
        grade = grade_dos_extents(mn, mx)
    else:
        grade = grade_do_doador(doador)

    # OS HOODS SAO OS DO DOADOR, EM NOME E EM QUANTIDADE.
    #
    # Isto ja estava registrado no caminho do cubo e eu nao apliquei aqui: nome
    # de hood aparece em `.loc`, nos dados de corrida, no `_bnd` e - medido
    # agora - no caminho que coloca os PROPS. A LA do MC2 tem 12 hoods
    # (bh dt gh hl hw i05 i10 101 105 ind lax sm) e o atlanta tem 7
    # (bh dt fwy lf mt ug we); emitindo os 12 de LA, os props do atlanta caiam
    # em hood que nao existe do lado deles. Com os props desativados o mesmo
    # arquivo roda limpo (1440 frames, os quatro contadores em zero), o que
    # isola a interacao hood/props.
    #
    # A geometria nao muda de lugar: so a AGRUPACAO por hood muda. Cada hood do
    # MC2 e mapeado para um hood do doador, na ordem, ciclando.
    do_doador = nomes_dos_hoods(doador)
    hoods_mc2 = sorted({l['hood'] for l in comps} | {l['hood'] for l in insts})
    # CASAR POR NOME quando --hoods traz os nomes de verdade. O mapa antigo
    # distribuia por POSICAO na lista do doador, o que e arbitrario e ficou
    # visivel quando um place com um hood so mandou os 34 componentes do
    # downtown para 'bh' (do_doador[0]) em vez de 'dt'. Os doze nomes que o
    # city_slot6 registra sao justamente os doze hoods de LA, entao ha
    # correspondencia um-a-um; a posicao fica so de reserva.
    ABREV = {'beverlyhills': 'bh', 'downtown': 'dt', 'ghetto': 'gh',
             'hills': 'hl', 'hollywood': 'hw', 'i05': 'i05', 'i10': 'i10',
             'i101': '101', 'i105': '105', 'industrial': 'ind',
             'lax': 'lax', 'santamonica': 'sm'}
    declarados = list(hoods) if hoods else list(do_doador)
    mapa_hood = {}
    for i, h in enumerate(hoods_mc2):
        curto = ABREV.get(h[2:] if h.startswith('l_') else h)
        mapa_hood[h] = (curto if curto in declarados
                        else declarados[i % len(declarados)])

    e = Escritor()
    # CONTROLE DE LAYOUT. Bytes mortos logo depois do MapRoot, so para deslocar
    # tudo o que vem em seguida sem mudar UM BYTE de conteudo. Existe porque
    # duas mudancas minhas travaram no primeiro quadro (align=16 nas malhas e o
    # stream de ITOP+2) e as duas tem em comum deslocar o layout inteiro -- este
    # e o experimento que separa "o conteudo esta errado" de "o arquivo nao pode
    # mudar de tamanho". Nao serve para nada em producao.
    if PADDING_TESTE:
        e.poe(bytes([0xCD]) * PADDING_TESTE, 'padding_teste')

    # ---------------------------------------------------------------- shader
    # o shader pode vir de OUTRO doador: o tokyo nao tem shader do tipo
    # tipico (sub-objeto em +0x10), entao serve de base para todo o resto mas
    # nao para essa peca
    _g, veio_de = emite_grupos_shader(e, doador_shader or doador,
                                      n_grupos, n_slots, slot_shader,
                                      indice_material)



    # ------------------------------------------------------------- geometria
    por_hood = {}
    cadeia = []                       # os ComponentData, na ordem do arquivo
    lidos = pulados = 0
    verts = 0
    for i, l in enumerate(comps):
        p = caminho_da_malha(modelos, l)
        if not p:
            pulados += 1
            continue
        try:
            blocos, mundo = le_componente_mundo(p)
        except Exception as ex:                       # malha que o leitor recusa
            print('  pulado %s: %s' % (os.path.basename(p), ex))
            pulados += 1
            continue
        if not blocos:
            pulados += 1
            continue
        # mundo e o centro retirado DA PARTE, nao o da caixa do objeto inteiro.
        # Com --pck-malha apontando para uma PASTA, cada componente usa o
        # .pck que o jogo montou para ELE (<nome do modelo>.mesh.pck). Quem
        # nao tiver arquivo cai na emissao a mao, e o relatorio diz quantos.
        global PACOTES_DO_JOGO
        if PASTA_PCK:
            # SEM DIFERENCIAR CAIXA: os nomes do .hood tem maiuscula que os
            # arquivos nao tem (l_downtown_blk_staplesCntr_x#geom), e a busca
            # exata perdia esse componente em silencio - 33 de 34.
            base_nome = os.path.splitext(os.path.basename(p))[0].lower()
            PACOTES_DO_JOGO = PCK_POR_MODELO.get(base_nome)
            if PACOTES_DO_JOGO:
                do_jogo[0] += 1
            globals()['GRUPOS_DO_JOGO'] = GRUPOS_POR_MODELO.get(base_nome)
            globals()['INDICES_DO_JOGO'] = (
                slots_de_textura(base_nome, len(GRUPOS_POR_MODELO[base_nome]))
                if (base_nome in GRUPOS_POR_MODELO) else None)
        chave, raio, off_cd = emite_geometria(e, blocos, 'c%d' % i, mundo,
                                              indice_material)
        por_hood.setdefault(l['hood'], []).append((chave, raio))
        cadeia.append((chave, off_cd))
        verts += sum(len(b[0]) for b in blocos)
        lidos += 1

    # OS ComponentData SAO UMA LISTA LIGADA, e sem ela so o primeiro e placado.
    #
    # Medido no atlanta: `CullableTypeFixup` (0x24AE58) faz
    # `while (v3) { ctor(v3); v3 = *(v3+0x0C); }` a partir da cabeca que esta em
    # `MapRoot+0x194`, e essa cabeca aponta pro **ULTIMO** ComponentData do
    # arquivo; `+0x0C` anda pra tras ate o primeiro, que tem `+0x0C` nulo. Sao
    # 651 nos e os 651 componentes do atlanta.
    #
    # Com a cabeca no primeiro e `+0x0C` nulo (o que eu fazia), o laco roda UMA
    # vez: medido no savestate do travamento, 1 dos 298 ComponentData tinha o
    # ponteiro de mesh relocado e 297 estavam intactos.
    #
    #   +0x04  o dono, que e a propria estrutura de MapRoot+0x194
    #   +0x08  o nome deste objeto (ele mesmo + 0x70)
    #   +0x0C  o ANTERIOR   (nulo no primeiro)  <- por onde o laco anda
    #   +0x10  o SEGUINTE   (nulo no ultimo)
    #   +0x14  o anterior de novo
    for k, (chave, off_cd) in enumerate(cadeia):
        e.aponta(off_cd + 0x04, 'extra_194')
        e.aponta(off_cd + 0x08, chave + '_nome')
        if k:
            e.aponta(off_cd + 0x0C, cadeia[k - 1][0])
            e.aponta(off_cd + 0x14, cadeia[k - 1][0])
        if k + 1 < len(cadeia):
            e.aponta(off_cd + 0x10, cadeia[k + 1][0])

    # os registros de componente TEM que ser contiguos por hood: a entrada do
    # hood guarda [contagem][ponteiro para o array]
    vas_comp = []
    cel_por_unico = {}
    # regrupar os componentes pelo hood de DESTINO, para ficarem contiguos
    # OS NOMES DE HOOD SAO CONTRATO com quem registra a cidade, e por isso a
    # lista declarada tem que ser conhecida JA AQUI: e neste ponto que os
    # componentes viram blocos contiguos por hood, e realocar depois nao mexe
    # mais nos blocos ja emitidos. O city_slot6.mod registra o losangeles com DOZE
    # hoods; um .pck que declarasse os sete do doador deixava o jogo em LOADING
    # INFINITO - medido em savestate com o jogo vivo a 59,9 Hz e a cidade 5
    # pedida nos dois sinks. Mesma classe do cell_count.
    nomes_hood = list(hoods) if hoods else list(do_doador)
    por_dest = {}
    orfaos = set()
    for h, itens in por_hood.items():
        d = mapa_hood.get(h, h)
        if d not in nomes_hood:
            orfaos.add(d)
            d = nomes_hood[0]
        por_dest.setdefault(d, []).extend(itens)
    por_hood = por_dest
    if orfaos:
        print('  hood(s) fora da lista declarada, movidos para %s: %s'
              % (nomes_hood[0], ', '.join(sorted(orfaos))))
    for hood, itens in por_hood.items():
        base = None
        for k, (chave, raio) in enumerate(itens):
            comp = bytearray(TAM_COMPONENTE)
            struct.pack_into('<f', comp, 0x18, raio)
            struct.pack_into('<I', comp, 0x10, tok(VT_COMPONENTE_TOKEN))
            comp[0x0B] = 8                      # ver a nota em constroi()
            cd_off = e.marca[chave]
            cx = struct.unpack_from('<f', e.d, cd_off + 0x2C)[0]
            cz = struct.unpack_from('<f', e.d, cd_off + 0x34)[0]
            x0, x1, z0, z1 = caixa_de_celulas(grade, cx, cz, raio, raio)
            comp[0x14], comp[0x15], comp[0x16], comp[0x17] = x0, x1, z0, z1
            gw = grade[0]
            cel_por_unico[len(vas_comp)] = [z * gw + x
                                            for z in range(z0, z1 + 1)
                                            for x in range(x0, x1 + 1)]
            off = e.poe(bytes(comp), 'comp_%s_%d' % (hood, k), align=4)
            if base is None:
                base = off
                e.rotula('comps_%s' % hood, off)
            e.aponta(off + 0x0C, chave)
            # e a volta: o ComponentData aponta para a entrada que o alcanca
            e.aponta(e.marca[chave] + 0x18, 'comp_%s_%d' % (hood, k))
            vas_comp.append(e.va(off))

    # ------------------------------------------------------------- instancias
    (inst_vas, cel_por_inst, por_hood_inst,
     cabeca_tipo, n_tipos) = emite_instancias(e, insts, modelos, grade,
                                              indice_material, mapa_hood)

    # ----------------------------------------------------------------- hoods
    # TODOS os hoods do doador existem, na ordem dele, com os nomes dele. Um
    # hood sem geometria fica com contagem zero e array vazio - e assim que o
    # retail faz, e e o que o caminho do cubo ja fazia.
    # OS NOMES DE HOOD SAO CONTRATO com quem registra a cidade. O
    # city_slot6.mod registra o losangeles com DOZE hoods; se o .pck declarar os
    # sete do doador, o jogo pede um hood que nao existe e fica em LOADING
    # INFINITO - medido em 03/09/2026 num savestate que mostrava o jogo vivo a
    # 59,9 Hz, com a cidade 5 pedida nos dois sinks e nunca entrando. Mesma
    # classe do cell_count: contrato entre arquivos, nao detalhe interno.
    nomes_hood = list(hoods) if hoods else list(do_doador)
    # A ordem de indexacao E a lista declarada: o jogo pede o hood pelo INDICE,
    # entao usar a lista do doador como chave estourava assim que --hoods trazia
    # mais nomes que ele. Componente cujo hood nao esta na lista vai para o
    # primeiro, para nao sumir em silencio.
    ordem = list(nomes_hood)
    escolha = doadores_de_hood(doador, len(nomes_hood))
    entradas = bytearray()
    for i, nm in enumerate(nomes_hood):
        qual, ultimo = escolha[i]
        registro_hood(e, doador, nm, 'hood_rec%d' % i, qual, ultimo)
        h = ordem[i]
        ent = bytearray(TAM_ENTRADA_HOOD)
        struct.pack_into('<I', ent, 0x04, len(por_hood.get(h, [])))       # unique_count
        struct.pack_into('<I', ent, 0x0C,
                         por_hood_inst.get(h, ('', 0))[1])                # instance_count
        entradas += ent
    off_ent = e.poe(bytes(entradas), 'hoods')
    vazio = hood_vazio(e)
    for i, h in enumerate(ordem):
        e.aponta(off_ent + TAM_ENTRADA_HOOD * i + 0, 'hood_rec%d' % i)
        e.aponta(off_ent + TAM_ENTRADA_HOOD * i + 8,
                 'comps_%s' % h if h in por_hood else vazio)
        e.aponta(off_ent + TAM_ENTRADA_HOOD * i + 0x10,
                 por_hood_inst[h][0] if h in por_hood_inst else vazio)

    # --------------------------------------------------------------- MapRoot
    r = 0x80
    e.d[r:r + TAM_MAPROOT] = maproot_base(doador)
    paletas_inline(e, r)
    e.u32(r + 0x00, tok(VT_MAPROOT))
    e.u32(r + 0x08, n_grupos)
    e.aponta(r + 0x0C, 'grupos')
    array_vazio(e, 'campo10')
    e.aponta(r + 0x10, 'campo10')
    e.u32(r + 0x14, len(nomes_hood))
    e.aponta(r + 0x18, 'hoods')
    gw, gh, ox, oz = grade
    scratch = gw * gh
    struct.pack_into('<iiii', e.d, r + 0x26C, gw, gh, ox, oz)   # grid + origem
    e.u32(r + 0x268, scratch)                                   # == grid_w*grid_h
    bloco_1c(e, doador, 'campo1c', vas_comp, inst_vas, scratch,
             cel_por_unico, cel_por_inst)
    e.aponta(r + 0x1C, 'campo1c')
    e.aponta(r + 0x2C, 'paletaA')
    e.aponta(r + 0x30, 'paletaB')
    if extents.get('extents_min') and extents.get('extents_max'):
        for k, campo in ((0x238, 'extents_min'), (0x244, 'extents_max')):
            for j, v in enumerate(extents[campo][:3]):
                struct.pack_into('<f', e.d, r + k + 4 * j, v)
    # a cabeca e o ULTIMO da cadeia, nao o primeiro
    feitas = estruturas_extra(e, doador,
                              cadeia[-1][0] if cadeia else None,
                              cabeca_tipo,
                              n_comp=len(vas_comp), n_inst=len(inst_vas))
    n_cadeias = cadeias_1d4(e, doador, doador_textura)

    n = e.fecha(saida)
    print('gravado %s (%d bytes)' % (saida, n))
    print('  %d componentes escritos, %d pulados, %d vertices'
          % (lidos, pulados, verts))
    if PASTA_PCK:
        print('  com pacotes do jogo: %d (componentes + tipos de instancia)'
              % do_jogo[0])
    print('  %d hood(s): %s'
          % (len(nomes_hood),
             ', '.join('%s=%d' % (nomes_hood[i], len(por_hood.get(h, [])))
                       for i, h in enumerate(ordem))))
    print('  shader copiado do slot %d do doador; %d slots no grupo 0'
          % (veio_de, n_slots))
    print('  estruturas extra: %s; %d cadeia(s) de +0x1D4/+0x1D8'
          % (', '.join('+0x%X' % x for x in feitas), n_cadeias))
    return n


def compdata(raio, posicao, nome=b'gerado_00'):
    """Um ComponentData com os campos CONSTANTES que os 651 do atlanta tem.

    Deixar isto zerado foi o que produziu o `R5900 Exception: Jump to unaligned
    address` ao chegar perto do modelo: **`+0x28` e um TOKEN de vtable, igual
    (`0x0079FF88`) nos 651 ComponentData do arquivo**, e `+0x00` vale 1 em todos.
    Com zero ali, a primeira chamada virtual sobre o componente salta por um
    ponteiro lido de lixo - e o endereco nem alinhado fica.

    Os ponteiros de `+0x04..+0x18` variam por componente (`+0x08` aponta pro
    nome, `+0x10` pra outro ComponentData) e ficam nulos aqui: existe pelo menos
    um componente do retail com nulos em `+0x0C/+0x10/+0x14`, entao nulo e
    tolerado nesses.
    """
    cd = bytearray(0xF0)
    struct.pack_into('<I', cd, 0x00, 1)
    struct.pack_into('<I', cd, 0x28, tok(VT_COMPDATA_TOKEN))
    struct.pack_into('<3f', cd, 0x2C, *posicao)
    struct.pack_into('<f', cd, 0x38, raio)
    cd[0x70:0x70 + len(nome)] = nome
    # +0x1C, +0x20 e +0x24 valem 0xCDCDCDCD em 23.814 de 23.814 ComponentData
    # do varejo, e mesmo assim ficam ZERO aqui, por decisao do usuario: 0xCD e
    # o padrao de MEMORIA NAO INICIALIZADA, e imitar 'nao inicializado' num
    # arquivo gerado copia a aparencia do varejo sem copiar o significado.
    # Testado com CD: nao mudou nada.
    return bytes(cd)


# O MESH EMBUTIDO EM ComponentData+0x90.
#
# Medido: em 584 dos 650 ComponentData do tokyo, a palavra em +0x90 e o TOKEN
# DE MESH, e os campos +0x98..+0xAC sao byte a byte os campos +0x08..+0x1C de
# um mesh - alinhei os dois num componente real e a sobreposicao e exata, com
# mesh+0x00 caindo em CD+0x90. Ou seja o ComponentData CARREGA UM MESH DENTRO
# DELE, e em 431 dos 650 o proprio +0x3C aponta para esse mesh interno em vez
# de para um objeto separado.
#
# O meu builder sempre alocou o mesh fora e deixou +0x90 zerado. Escrever o
# mesh embutido preenche de uma vez +0x90, +0x98, +0x9C, +0xA0, +0xA8 e +0xAC
# com valores cuja semantica eu conheco inteira, porque e o mesmo cabecalho de
# mesh que eu ja emito - e poe o componente na forma MAJORITARIA do varejo.
TAM_MESH = 0x20
OFF_MESH_EMBUTIDO = 0x90


def poe_mesh_embutido(e, off_cd, chave_mt, chave_gt, blocos, chave, slot_count=1):
    """Escreve o cabecalho de mesh dentro do ComponentData e aponta +0x3C pra ele."""
    m = off_cd + OFF_MESH_EMBUTIDO
    # A CONTAGEM TEM QUE SER A DA TABELA QUE ESTE MESH REUSA, nao 1 fixo. Este
    # mesh aponta `+0x10` para `chave_gt`, que no caminho agrupado tem
    # `len(GRUPOS_DO_JOGO)` entradas - e o ctor `rmcModelGeom(datResource&)` usa
    # SO este u16 para saber quantos `rmcGeometry` relocar. Com 1 aqui e N na
    # tabela, os N-1 grupos restantes ficam com o offset de arquivo cru no lugar
    # do ponteiro e a geometria deles desenha a partir do inicio da RAM. O
    # comentario abaixo ja tinha percebido o N para a cadeia CPV; faltava aqui.
    n_grupos = len(GRUPOS_DO_JOGO) if GRUPOS_DO_JOGO else 1
    struct.pack_into('<IIHHIIII', e.d, m,
                     tok(VT_MESH_TOKEN), 0, n_grupos, slot_count, 0, 0, 0, 1)
    e.aponta(m + 0x0C, chave_mt)
    e.aponta(m + 0x10, chave_gt)
    # Este mesh REUSA a tabela de grupos do componente (chave_gt), entao a
    # cadeia dele tem que casar com ELA e nao com os meus blocos. Com
    # --pck-malha a tabela tem os pacotes do jogo; montar a cadeia a partir
    # de `blocos` produzia 101 entradas para uma lista de 26.
    # A cadeia tem que casar com a tabela de grupos que este mesh REUSA. Com
    # GRUPOS_DO_JOGO a tabela tem N grupos, entao a cadeia precisa de N tambem -
    # montar a partir dos blocos achatados dava 82 de 298 malhas invalidas.
    if GRUPOS_DO_JOGO:
        grupos_cpv = [[([0] * nv,) for _p, _q, nv in pac] for pac in GRUPOS_DO_JOGO]
    else:
        grupos_cpv = [([0] * nv,) for _p, _q, nv in PACOTES_DO_JOGO]             if PACOTES_DO_JOGO else blocos
        grupos_cpv = [grupos_cpv]
    emite_cadeia_por_vertice(e, grupos_cpv, chave + '_t14', slot_count=slot_count)
    e.aponta(m + 0x14, chave + '_t14')
    e.u32(off_cd + 0x3C, e.va(m))


def geometria_gerada(p, blocos):
    """Anexa mesh + ComponentData + componente num .pck existente.

    Devolve (off_mesh, off_cd, off_comp, raio). Nada do arquivo se move: tudo e
    ANEXADO e so os campos novos apontam pra ca.
    """
    escala = mc2.pick_scale(blocos)
    pks = [mc2.make_block(pos, uv, nr, escala, i % 2 == 1)
           for i, (pos, uv, nr, _o) in enumerate(blocos)]
    offs = [p.append(pk) for pk in pks]
    lista = b''.join(struct.pack('<IHH', p.V(o), (len(pk) + 15) // 16, len(bl[0]))
                     for o, pk, bl in zip(offs, pks, blocos))
    va_lista = p.V(p.append(lista))
    off_gt = p.append(struct.pack('<IHH', 0, len(blocos), 0))
    struct.pack_into('<I', p.data, off_gt, va_lista)
    off_mt = p.append(struct.pack('<H', 1) + bytes([0, 0]))
    off_mesh = p.append(struct.pack('<IIHHIIII', tok(VT_MESH_TOKEN), 0, 1,
                                    SLOTS_CPV_COMPONENTE, 0, 0, 0, 1))
    struct.pack_into('<I', p.data, off_mesh + 0x0C, p.V(off_mt))
    struct.pack_into('<I', p.data, off_mesh + 0x10, p.V(off_gt))
    off_t14 = anexa_cadeia_por_vertice(p, [blocos])
    struct.pack_into('<I', p.data, off_mesh + 0x14, p.V(off_t14))

    pts = [c for pos, _u, _n, _o in blocos for c in pos]
    raio = max((q[0] ** 2 + q[1] ** 2 + q[2] ** 2) ** 0.5 for q in pts)
    off_cd = p.append(compdata(raio, (-400.0, 5.0, 700.0)))
    struct.pack_into('<I', p.data, off_cd + 0x3C, p.V(off_mesh))

    comp = bytearray(TAM_COMPONENTE)
    # +0x10 e o type_va, e ele FALTAVA aqui - o enxerto hood1 gravava zero e
    # travava com PC=0x00650073 (texto UTF-16), que e outra falha que a do
    # builder. Sem isto o enxerto testava o proprio bug, nao o do arquivo.
    struct.pack_into('<I', comp, 0x10, tok(VT_COMPONENTE_TOKEN))
    struct.pack_into('<f', comp, 0x18, raio)
    off_comp = p.append(bytes(comp))
    struct.pack_into('<I', p.data, off_comp + 0x0C, p.V(off_cd))
    return off_mesh, off_cd, off_comp, raio


def enxerta(base, saida, peca, lado=40.0):
    """Bissecção diferencial: um arquivo que CARREGA, com UMA peça gerada.

    Construir do zero falha e não diz onde. Partir do arquivo real e trocar uma
    peça por vez faz cada boot excluir metade do espaço em vez de testar um
    campo. E o critério não precisa nem de tela: o savestate diz **quantos dos
    seis ponteiros do MapRoot foram relocados**, e num arquivo que carrega são
    todos.

    Nada que já está no arquivo se move - as peças novas são ANEXADAS e só os
    ponteiros do MapRoot são reescritos. É a mesma disciplina do hood fill.
    """
    # O espaco de token do enxerto e o da BASE, nao o do atlanta em que as
    # constantes foram medidas. Sem isto o enxerto grava tokens de atlanta num
    # arquivo do tokyo e deixa de ser um teste limpo.
    globals()['DESLOC_TOKEN'] = token_do_doador(base)
    p = mc2.Pck(base)
    r = 0x80

    def poe(blob, align=16):
        return p.V(p.append(blob, align))

    if peca == 'paletas':
        struct.pack_into('<I', p.data, r + 0x2C, poe(paleta_cinza()))
        struct.pack_into('<I', p.data, r + 0x30, poe(paleta_cinza()))
        nota = 'as duas paletas trocadas por rampas geradas'

    elif peca == 'grupo':
        # O DESCRITOR DE GRUPO DE SHADER do jeito que um arquivo do zero o
        # monta: UM grupo de 64 slots no lugar dos 18 de 1329 do retail. Os
        # objetos de shader continuam sendo os do proprio arquivo - so a forma
        # da tabela muda, que e o que ainda nao foi isolado.
        n_grupos = struct.unpack_from('<I', p.data, r + 0x08)[0]
        base_desc = p.F(struct.unpack_from('<I', p.data, r + 0x0C)[0])
        dados = p.F(struct.unpack_from('<I', p.data, base_desc + 4)[0])
        n0 = struct.unpack_from('<H', p.data, base_desc + 8)[0]
        vivos = []
        for i in range(n0):
            v = struct.unpack_from('<I', p.data, dados + 4 * i)[0]
            if v and p.inside(p.F(v)):
                vivos.append(v)
            if len(vivos) == 64:
                break
        arr = poe(b''.join(struct.pack('<I', v) for v in vivos))
        desc = poe(struct.pack('<IIHHI', tok(VT_ARRAY), 0, len(vivos), len(vivos), 0))
        struct.pack_into('<I', p.data, p.F(desc) + 4, arr)
        struct.pack_into('<I', p.data, r + 0x08, 1)
        struct.pack_into('<I', p.data, r + 0x0C, desc)
        nota = ('%d grupos de shader viraram 1 grupo de %d slots'
                % (n_grupos, len(vivos)))

    elif peca == 'extras':
        # AS QUATRO ESTRUTURAS DE +0x190/+0x194/+0x198/+0x228, do jeito que um
        # arquivo do zero as monta: COPIADAS do proprio arquivo, com as
        # CONTAGENS ZERADAS, e a cabeca do +0x194 apontando para a mesma cadeia
        # de ComponentData que ja esta la.
        #
        # E a peca que nenhum enxerto anterior testou. Shader passou, paletas
        # passaram, e os de hood carregaram e so quebraram ao chegar perto -
        # entao o que sobra de um arquivo gerado, e nunca foi isolado, e este
        # bloco de contagens zeradas.
        feitas = []
        for off, _quem, contagens, tam in ESTRUTURAS_EXTRA:
            va = struct.unpack_from('<I', p.data, r + off)[0]
            if not va or not p.inside(p.F(va)):
                continue
            o = p.F(va)
            blob = bytearray(p.data[o:o + tam])
            antes = [struct.unpack_from('<I', blob, c)[0] for c in contagens]
            for c in contagens:
                struct.pack_into('<I', blob, c, 0)
            struct.pack_into('<I', p.data, r + off, poe(bytes(blob)))
            feitas.append('+0x%X %s->0' % (off, antes))
        nota = 'estruturas extra copiadas com contagem zerada: %s' % ', '.join(feitas)

    elif peca == 'shaders':
        # ESPELHA O PADRAO DO RETAIL, em vez de "preencher tudo".
        #
        # O laco de 0x2AF9E8 nao tem guarda de "ja colocado": ele roda o handler
        # uma vez por SLOT. No retail cada objeto aparece em EXATAMENTE um slot
        # (4117 objetos em 4117 slots, medido) e o resto e nulo. Preencher todo
        # slot com o mesmo shader - que eu fiz achando que evitava nulo - poe o
        # mesmo objeto em milhares de slots e o handler re-soma o delta nos
        # ponteiros internos dele uma vez por slot.
        #
        # Entao: onde o retail tem objeto, poe uma copia NOVA; onde tem nulo,
        # deixa nulo.
        bloco, k = bloco_shader(base)
        n_grupos = struct.unpack_from('<I', p.data, r + 0x08)[0]
        base_desc = p.F(struct.unpack_from('<I', p.data, r + 0x0C)[0])
        arrays, feitos = [], 0
        for g in range(n_grupos):
            dados = p.F(struct.unpack_from('<I', p.data, base_desc + 16 * g + 4)[0])
            n = struct.unpack_from('<H', p.data, base_desc + 16 * g + 8)[0]
            slots = []
            for i in range(n):
                v = struct.unpack_from('<I', p.data, dados + 4 * i)[0]
                if v and p.inside(p.F(v)):
                    o = p.append(bloco)
                    struct.pack_into('<I', p.data, o + 8, p.V(o + 0x10))
                    slots.append(p.V(o))
                    feitos += 1
                else:
                    slots.append(0)
            arrays.append(poe(b''.join(struct.pack('<I', x) for x in slots)))
        desc = b''.join(struct.pack('<IIHHI', tok(VT_ARRAY), 0,
                                    struct.unpack_from('<H', p.data, base_desc + 16 * g2 + 8)[0],
                                    struct.unpack_from('<H', p.data, base_desc + 16 * g2 + 8)[0], 0)
                        for g2 in range(n_grupos))
        off_g = p.append(desc)
        for g in range(n_grupos):
            struct.pack_into('<I', p.data, off_g + 16 * g + 4, arrays[g])
        struct.pack_into('<I', p.data, r + 0x0C, p.V(off_g))
        nota = ('%d grupos, %d copias novas (uma por slot que o retail preenche)'
                % (n_grupos, feitos))

    elif peca == 'hood2':
        # Um passo ANTES do hood1: mantem o componente ORIGINAL e so reaponta o
        # `+0x0C` dele pro nosso ComponentData. Assim o trio fica:
        #   cubos_ug  comp original + CD original + geometria nossa  -> CARREGA
        #   hood2     comp original + CD NOSSO    + geometria nossa  -> ?
        #   hood1     comp NOSSO    + CD NOSSO    + geometria nossa  -> ?
        # Qualquer que seja o primeiro a travar, aponta a peca exata.
        hb = p.F(struct.unpack_from('<I', p.data, r + 0x18)[0])
        nh = struct.unpack_from('<I', p.data, r + 0x14)[0]
        alvo = 0
        for h in range(nh):
            rec = p.F(struct.unpack_from('<I', p.data, hb + 20 * h)[0])
            if bytes(p.data[rec:rec + 3]).startswith(b'ug'):
                alvo = h
                break
        au = p.F(struct.unpack_from('<I', p.data, hb + 20 * alvo + 8)[0])
        _m, off_cd, _c, _r = geometria_gerada(p, cubo(lado))
        struct.pack_into('<I', p.data, au + 0x0C, p.V(off_cd))   # 1o componente
        struct.pack_into('<I', p.data, hb + 20 * alvo + 4, 1)    # so ele
        nota = 'hood %d: componente ORIGINAL apontando pro nosso ComponentData' % alvo

    elif peca == 'hood1':
        # DELTA MINIMO a partir do que ja funciona.
        #
        # `cubos_ug` carrega: 7 hoods originais, componentes ORIGINAIS, so a
        # geometria trocada. `zero6` trava: 7 hoods com os nomes certos mas
        # componentes GERADOS. O passo entre os dois e este: manter os 7 hoods e
        # o hood alvo intacto, e trocar so o ARRAY DE UNIQUES dele por um
        # componente + ComponentData gerados por nos. Se travar, o problema esta
        # no componente gerado; se carregar, esta em outro lugar do arquivo do
        # zero.
        hb = p.F(struct.unpack_from('<I', p.data, r + 0x18)[0])
        nh = struct.unpack_from('<I', p.data, r + 0x14)[0]
        alvo = None
        for h in range(nh):
            rec = p.F(struct.unpack_from('<I', p.data, hb + 20 * h)[0])
            if bytes(p.data[rec:rec + 3]).startswith(b'ug'):
                alvo = h
                break
        if alvo is None:
            alvo = 0
        off_mesh, off_cd, off_comp, raio = geometria_gerada(p, cubo(lado))
        struct.pack_into('<I', p.data, hb + 20 * alvo + 4, 1)          # 1 unique
        struct.pack_into('<I', p.data, hb + 20 * alvo + 8, p.V(off_comp))
        nota = ('hood %d intacto, array de uniques trocado por 1 componente gerado'
                % alvo)

    elif peca == 'hood':
        blocos = cubo(lado)
        escala = mc2.pick_scale(blocos)
        pks = [mc2.make_block(pos, uv, nr, escala, i % 2 == 1)
               for i, (pos, uv, nr, _o) in enumerate(blocos)]
        offs = [p.append(pk) for pk in pks]
        lista = b''.join(struct.pack('<IHH', p.V(o), (len(pk) + 15) // 16, len(bl[0]))
                         for o, pk, bl in zip(offs, pks, blocos))
        va_lista = poe(lista)
        off_gt = p.append(struct.pack('<IHH', 0, len(blocos), 0))
        struct.pack_into('<I', p.data, off_gt, va_lista)
        off_mt = p.append(struct.pack('<H', 1) + bytes([0, 0]))
        # Esta sonda antiga nao emite +0x14: desabilite CPV explicitamente.
        off_mesh = p.append(struct.pack('<IIHHIIII', tok(VT_MESH_TOKEN), 0, 1, 0, 0, 0, 0, 1))
        struct.pack_into('<I', p.data, off_mesh + 0x0C, p.V(off_mt))
        struct.pack_into('<I', p.data, off_mesh + 0x10, p.V(off_gt))

        pts = [c for pos, _u, _n, _o in blocos for c in pos]
        raio = max((q[0] ** 2 + q[1] ** 2 + q[2] ** 2) ** 0.5 for q in pts)
        off_cd = p.append(compdata(raio, (-400.0, 5.0, 700.0)))
        struct.pack_into('<I', p.data, off_cd + 0x3C, p.V(off_mesh))

        comp = bytearray(TAM_COMPONENTE)
        struct.pack_into('<f', comp, 0x18, raio)
        off_comp = p.append(bytes(comp))
        struct.pack_into('<I', p.data, off_comp + 0x0C, p.V(off_cd))

        # registro: copia do primeiro hood do proprio arquivo, nome trocado
        hb = p.F(struct.unpack_from('<I', p.data, r + 0x18)[0])
        rec0 = p.F(struct.unpack_from('<I', p.data, hb)[0])
        blob = bytearray(p.data[rec0:rec0 + 0xB0])
        blob[0:4] = b'zz' + bytes(2)
        cadeia = bytes(p.data[rec0 + 0xB4:rec0 + 0xB4 + 0xA0])
        off_rec = p.append(bytes(blob))
        va_cad = poe(cadeia)
        struct.pack_into('<I', p.data, off_rec + 0xAC, va_cad)

        # o array de INSTANCE tem que existir mesmo com contagem zero: ponteiro
        # nulo aqui e a mesma armadilha do MapRoot+0x10 (no PS2 o endereco 0 le,
        # nao falha, e o Place sai andando em lixo)
        va_inst = poe(bytes(96))
        ent = bytearray(TAM_ENTRADA_HOOD)
        struct.pack_into('<I', ent, 4, 1)
        struct.pack_into('<I', ent, 16, va_inst)
        off_ent = p.append(bytes(ent))
        struct.pack_into('<I', p.data, off_ent + 0, p.V(off_rec))
        struct.pack_into('<I', p.data, off_ent + 8, p.V(off_comp))
        struct.pack_into('<I', p.data, r + 0x14, 1)
        struct.pack_into('<I', p.data, r + 0x18, p.V(off_ent))
        nota = '1 hood gerado com 1 cubo; os %d hoods originais ficam no arquivo mas fora da tabela' % 0
    else:
        raise SystemExit('peca desconhecida: %s' % peca)

    p.save(saida)
    print('%-10s -> %s (%d bytes)  %s' % (peca, os.path.basename(saida), len(p.data), nota))


def verifica(caminho):
    """Reabre o arquivo com os leitores que ja existem no toolkit.

    Nao prova que o jogo aceita - prova que a estrutura fecha com a leitura que
    foi validada nos arquivos do retail, que e o unico teste automatico possivel
    antes de bootar.
    """
    spec = importlib.util.spec_from_file_location(
        'hf', os.path.join(_AQUI, 'mc3_hood_fill.py'))
    hf = importlib.util.module_from_spec(spec)
    sys.modules['hf'] = hf
    spec.loader.exec_module(hf)

    p = mc2.Pck(caminho)
    base, tipo, ver, corpo = struct.unpack_from('<4I', p.data, 0)
    print('%s' % os.path.basename(caminho))
    print('  cabecalho: base %08X, tipo %d, versao %d, corpo %d (arquivo %d)'
          % (base, tipo, ver, corpo, len(p.data)))
    ok = True
    if tipo != TIPO_CIDADE:
        print('  ERRO: tipo %d, esperado %d - o carregador falha em SILENCIO'
              % (tipo, TIPO_CIDADE))
        ok = False
    if corpo != len(p.data) - 0x80:
        print('  ERRO: corpo declarado nao bate com o arquivo')
        ok = False
    if len(p.data) % 16:
        print('  ERRO: arquivo nao esta alinhado em 16')
        ok = False

    hs = hf.hoods(p)
    print('  %d hood(s): %s' % (len(hs), ', '.join(h[0] for h in hs)))
    for i, h in enumerate(hs):
        u = hf.uniques_do_hood(p, i)
        print('    [%d] %-6s %d unique, %d instance -> %d componente(s) legivel(is)'
              % (i, h[0], h[1], h[3], len(u)))
        for nm, meshes, comp, cd in u:
            pos = struct.unpack_from('<3f', p.data, cd + 0x2C)
            raio = struct.unpack_from('<f', p.data, cd + 0x38)[0]
            for m in meshes:
                ab = hf.aabb_local(p, m)
                ng = struct.unpack_from('<H', p.data, m + 8)[0]
                print('       %-12s pos (%.1f %.1f %.1f) raio %.1f, %d grupo(s), AABB %s'
                      % (nm, pos[0], pos[1], pos[2], raio, ng,
                         ('%.1f x %.1f x %.1f' % tuple(ab[1][k] - ab[0][k] for k in range(3)))
                         if ab else 'ILEGIVEL'))
                # AABB ilegivel NAO e erro: o proprio atlanta do retail tem 18
                # meshes assim (grupo vazio ou layout que o leitor nao cobre), e
                # o jogo carrega. Contar, nao reprovar.
    # INDICE DE MATERIAL CONTRA O TAMANHO DO GRUPO. `rmcModel::FixupShaders`
    # (0x2A8A18) percorre os grupos do mesh e faz
    #
    #     if (*(u16*)(grupo+8) < indice_material[i])  while (1) ;
    #
    # ou seja, indice maior que a CONTAGEM do grupo trava o jogo num laco vazio
    # - a assinatura exata de "loading infinito". Nao ha nada fixo em 1329: o
    # atlanta dimensiona 1329 e usa ate 1328, o tokyo dimensiona 1720 e usa ate
    # 1719. A tabela e do tamanho do maior indice mais um.
    ng_mr = struct.unpack_from('<I', p.data, 0x80 + 0x08)[0]
    if ng_mr:
        base_g = p.F(struct.unpack_from('<I', p.data, 0x80 + 0x0C)[0])
        menor = min(struct.unpack_from('<H', p.data, base_g + 16 * g + 8)[0]
                    for g in range(ng_mr))
        maior = 0
        for i in range(len(hs)):
            for _n, meshes, _c, _cd in hf.uniques_do_hood(p, i):
                for m in meshes:
                    n = struct.unpack_from('<H', p.data, m + 8)[0]
                    mt = p.F(struct.unpack_from('<I', p.data, m + 0x0C)[0])
                    if not p.inside(mt):
                        continue
                    for k in range(n):
                        maior = max(maior, struct.unpack_from('<H', p.data,
                                                              mt + 2 * k)[0])
        print('  material: maior indice usado %d, menor grupo tem %d slot(s)'
              % (maior, menor))
        if maior > menor:
            print('     indice acima da contagem: FixupShaders cai em while(1)')
            ok = False

    # SLOT NULO NO GRUPO USADO = CHAMADA EM PONTEIRO NULO.
    # `rmcModel::FixupShaders` desreferencia array[indice] e chama o virtual de
    # +24 sem checar. O varejo convive com nulo porque cada malha so participa
    # dos passes onde seu material existe; geometria importada nao tem essa
    # garantia. Aqui so REPROVA indice preenchido em grupo NENHUM, que e erro em
    # qualquer caso, e informa o minimo para dar pista quando travar num shader.
    if ng_mr:
        base_g2 = p.F(struct.unpack_from('<I', p.data, 0x80 + 0x0C)[0])
        n0 = struct.unpack_from('<H', p.data, base_g2 + 8)[0]
        cheio = [0] * n0
        for g in range(ng_mr):
            dd = p.F(struct.unpack_from('<I', p.data, base_g2 + 16 * g + 4)[0])
            if not p.inside(dd):
                continue
            for i in range(n0):
                if struct.unpack_from('<I', p.data, dd + 4 * i)[0]:
                    cheio[i] += 1
        usados = set()
        alvos_mesh = []
        for i in range(len(hs)):
            for _n, meshes, _c, _cd in hf.uniques_do_hood(p, i):
                alvos_mesh.append(meshes)
        try:
            _sl, _tp = hf.tipos_de_instancia(p)
            for _va, (_nm, _cd2, ms) in _tp.items():
                alvos_mesh.append(ms)
        except Exception:
            pass
        for meshes in alvos_mesh:
            if True:
                for m in meshes:
                    nn = struct.unpack_from('<H', p.data, m + 8)[0]
                    mt = p.F(struct.unpack_from('<I', p.data, m + 0x0C)[0])
                    if not p.inside(mt):
                        continue
                    for k in range(nn):
                        usados.add(struct.unpack_from('<H', p.data, mt + 2 * k)[0])
        if usados:
            pior = min(cheio[i] for i in usados if i < n0)
            vazios = [i for i in usados if i < n0 and cheio[i] == 0]
            print('  slots de shader: o indice mais raro em uso existe em %d de '
                  '%d grupo(s)%s' % (pior, ng_mr,
                                     '; %d em NENHUM' % len(vazios) if vazios else ''))
            if vazios:
                print('     indice sem shader em grupo nenhum: chamada em ponteiro nulo')
                ok = False

    # CADEIA POR VERTICE DE rmcModelGeom+0x14. O caminho de Draw monta um
    # UNPACK S-8 a partir desta estrutura. Em um mesh gerado, ponteiro nulo nao
    # significa "sem atributo": NUM=0 no VIF significa 256, e o DMA passa a
    # consumir o pacote geometrico seguinte como dados ate perder alinhamento.
    #
    # O varejo tem alguns meshes especiais sem a cadeia, por isso a ausencia so
    # reprova os ComponentData que este builder marca como gerado_*. Toda cadeia
    # presente, de varejo ou gerada, ainda e validada integralmente.
    requeridos_por_tipo = {}
    hb_cpv = p.F(struct.unpack_from('<I', p.data, 0x80 + 0x18)[0])
    for h_cpv in range(len(hs)):
        entrada_cpv = hb_cpv + 20 * h_cpv
        n_cpv = struct.unpack_from('<I', p.data, entrada_cpv + 0x0C)[0]
        arr_cpv = p.F(struct.unpack_from('<I', p.data, entrada_cpv + 0x10)[0])
        if not p.inside(arr_cpv):
            continue
        for k_cpv in range(n_cpv):
            inst_cpv = arr_cpv + TAM_INSTANCE * k_cpv
            tipo_cpv = struct.unpack_from('<I', p.data, inst_cpv + 0x0C)[0]
            indice_cpv = struct.unpack_from('<I', p.data, inst_cpv + 0x1C)[0]
            requeridos_por_tipo[tipo_cpv] = max(
                requeridos_por_tipo.get(tipo_cpv, 0), indice_cpv + 1)

    alvos_cadeia = []
    for i in range(len(hs)):
        for nm, meshes, _c, _cd in hf.uniques_do_hood(p, i):
            alvos_cadeia += [(m, nm, SLOTS_CPV_COMPONENTE) for m in meshes]
    try:
        _sl4, _tp4 = hf.tipos_de_instancia(p)
        for _va4, (nm4, _cd4, ms4) in _tp4.items():
            exigido4 = requeridos_por_tipo.get(_va4, SLOTS_CPV_COMPONENTE)
            alvos_cadeia += [(m, nm4, exigido4) for m in ms4]
    except Exception:
        pass

    # O mesmo mesh pode ser alcancado por mais de uma tabela; validar uma vez e
    # conservar a maior cardinalidade se houver aliases.
    unicos_cadeia = {}
    for m, nm, exigido in alvos_cadeia:
        anterior = unicos_cadeia.get(m)
        if anterior is None or exigido > anterior[1]:
            unicos_cadeia[m] = (nm, exigido)

    erros_t14 = []
    n_validos_t14 = n_blocos_t14 = n_grupos_slot_t14 = n_nulos_retail = 0
    # A CONTAGEM DE GRUPOS DO MESH CONTRA A DA PROPRIA TABELA. O construtor
    # `rmcModelGeom::rmcModelGeom(datResource&)` (varejo 0x2A9D18) le o u16 de
    # `mesh+0x08` e SO ELE decide quantos `rmcGeometry` construir:
    #
    #     for (i < *(u16*)(this+8))  rmcGeometry(*(this+0x10) + i*8, res)
    #
    # e cada `rmcGeometry` reloca o ponteiro da propria lista de pacotes. Com a
    # contagem menor que o numero real de grupos o passeio para cedo: os grupos
    # que sobram ficam com o OFFSET DE ARQUIVO cru no lugar do ponteiro, e um
    # offset de arquivo lido como endereco de EE cai perto do inicio da RAM -
    # que e exatamente o sintoma "varios objetos empilhados numa faixa estreita".
    # Nada nas outras verificacoes pega isso, porque todas usam `ng` como
    # VERDADE para dimensionar a tabela e so olham os grupos que ele declara.
    #
    # A tabela sabe o proprio tamanho: `emite_malha_agrupada` grava a contagem
    # como u32 16 bytes ANTES do array, a convencao dos tres niveis do resto do
    # arquivo. Se os dois numeros divergem, o arquivo se contradiz.
    #
    # MEDIDO ANTES DE ENTRAR AQUI, para nao criar falso positivo: com
    # `mesh+0x08 != 0` a regra vale em 6152 malhas de varejo (atlanta 807,
    # sd 1751, detroit 1705, tokyo 1889) com ZERO divergencia. O caso
    # `mesh+0x08 == 0` fica de fora de proposito - o laco do ctor nao roda, o
    # ponteiro nunca e percorrido e o prefixo nao quer dizer nada; so o atlanta
    # tem 544 malhas assim, todas legitimas.
    erros_ng = []
    n_ng_ok = n_ng_zero = n_ng_sem_prefixo = 0

    def _off_va_t14(va, tamanho=1):
        if not va:
            return None
        f = p.F(va)
        if f < 0x80 or f + tamanho > len(p.data):
            return None
        return f

    def _nome_gerado_t14(nm):
        if isinstance(nm, bytes):
            nm = nm.decode('ascii', 'ignore')
        return str(nm).lower().startswith('gerado_')

    for m, (nm, slots_exigidos) in sorted(unicos_cadeia.items()):
        if m < 0x80 or m + TAM_MESH > len(p.data):
            erros_t14.append('mesh 0x%X fora do arquivo' % m)
            continue
        ng, ns = struct.unpack_from('<HH', p.data, m + 8)
        gt = _off_va_t14(struct.unpack_from('<I', p.data, m + 0x10)[0], 8 * ng)
        if not ng:
            n_ng_zero += 1
        elif gt is None or gt < 0x90:
            n_ng_sem_prefixo += 1
        else:
            pref = struct.unpack_from('<I', p.data, gt - 16)[0]
            if not 1 <= pref <= 4096:
                n_ng_sem_prefixo += 1
            elif pref == ng:
                n_ng_ok += 1
            else:
                erros_ng.append(
                    'mesh 0x%X (%s) declara %d grupo(s) em +0x08 mas a tabela '
                    'tem %d: o ctor so reloca %d, o resto fica com offset de '
                    'arquivo cru' % (m, nm, ng, pref, ng))
        va_t14 = struct.unpack_from('<I', p.data, m + 0x14)[0]
        t14 = _off_va_t14(va_t14, 4 * ns)
        obrigatorio = _nome_gerado_t14(nm)
        slots_cpv_ok = not obrigatorio or ns >= slots_exigidos
        if not slots_cpv_ok:
            erros_t14.append(
                'mesh gerado 0x%X (%s) declara %d slot(s) CPV; '
                'Instance+0x1C exige %d' % (m, nm, ns, slots_exigidos))
        if not va_t14:
            if obrigatorio:
                erros_t14.append('mesh gerado 0x%X (%s) com +0x14 nulo' % (m, nm))
            else:
                n_nulos_retail += 1
            continue
        if not ng or not ns or gt is None or t14 is None:
            erros_t14.append('mesh 0x%X com cabecalho/ponteiro +0x14 invalido' % m)
            continue

        mesh_ok = slots_cpv_ok
        for s in range(ns):
            tab = _off_va_t14(struct.unpack_from('<I', p.data, t14 + 4 * s)[0],
                              8 * ng)
            if tab is None:
                erros_t14.append('mesh 0x%X slot %d aponta fora' % (m, s))
                mesh_ok = False
                continue
            for g in range(ng):
                gdesc = gt + 8 * g
                va_lista, nb, _res = struct.unpack_from('<IHH', p.data, gdesc)
                n_grupos_slot_t14 += 1
                if not nb:
                    continue
                lista = _off_va_t14(va_lista, 8 * nb)
                pa_va, pb_va = struct.unpack_from('<II', p.data, tab + 8 * g)
                pa = _off_va_t14(pa_va, 4 + 4 * nb)
                pb = _off_va_t14(pb_va, 4 * nb)
                if lista is None or pa is None or pb is None:
                    erros_t14.append('mesh 0x%X slot %d grupo %d aponta fora' %
                                      (m, s, g))
                    mesh_ok = False
                    continue
                declarado = struct.unpack_from('<I', p.data, pa)[0]
                if declarado != nb:
                    erros_t14.append('mesh 0x%X slot %d grupo %d: count %d != %d' %
                                      (m, s, g, declarado, nb))
                    mesh_ok = False
                for b in range(nb):
                    nv = struct.unpack_from('<H', p.data, lista + 8 * b + 6)[0]
                    nv_t14 = struct.unpack_from('<I', p.data, pa + 4 + 4 * b)[0]
                    if nv_t14 != nv:
                        erros_t14.append(
                            'mesh 0x%X slot %d grupo %d bloco %d: vertices %d != %d'
                            % (m, s, g, b, nv_t14, nv))
                        mesh_ok = False
                    payload_va = struct.unpack_from('<I', p.data, pb + 4 * b)[0]
                    if _off_va_t14(payload_va, max(1, nv)) is None:
                        erros_t14.append(
                            'mesh 0x%X slot %d grupo %d bloco %d: payload fora'
                            % (m, s, g, b))
                        mesh_ok = False
                    n_blocos_t14 += 1
        if mesh_ok:
            n_validos_t14 += 1

    print('  cadeia mesh+0x14: %d/%d mesh(es) valida(s), %d grupo-slot, '
          '%d bloco(s)%s' %
          (n_validos_t14, len(unicos_cadeia), n_grupos_slot_t14, n_blocos_t14,
           '; %d nulo(s) de varejo tolerado(s)' % n_nulos_retail
           if n_nulos_retail else ''))
    if erros_t14:
        ok = False
        print('     %d erro(s) na cadeia por vertice:' % len(erros_t14))
        for erro in erros_t14[:8]:
            print('       ' + erro)
        if len(erros_t14) > 8:
            print('       ... e mais %d' % (len(erros_t14) - 8))

    print('  contagem de grupos (mesh+0x08 vs a tabela): %d ok, %d divergente(s)'
          '%s%s'
          % (n_ng_ok, len(erros_ng),
             ', %d com +0x08=0 (o laco do ctor nao roda)' % n_ng_zero
             if n_ng_zero else '',
             ', %d sem prefixo legivel' % n_ng_sem_prefixo
             if n_ng_sem_prefixo else ''))
    if erros_ng:
        ok = False
        for erro in erros_ng[:6]:
            print('       ' + erro)
        if len(erros_ng) > 6:
            print('       ... e mais %d' % (len(erros_ng) - 6))

    # A ORIGEM DA GRADE DE CULLING tem que casar com os extents.
    # `mcCity::CalcAbsCellXZ` (0x257CC8) faz floor(x/40) sem origem, e
    # `CalcRelCellXZ` (0x257C60) subtrai +0x274 e +0x278. Nas quatro cidades de
    # varejo, 8 de 8: +0x274 == floor(extents_min.x/40), +0x278 == floor(min.z/40).
    import math as _m
    _mn = struct.unpack_from('<3f', p.data, 0x80 + 0x238)
    _ox, _oz = struct.unpack_from('<2i', p.data, 0x80 + 0x274)
    _ex = int(_m.floor(_mn[0] / 40.0)); _ez = int(_m.floor(_mn[2] / 40.0))
    print('  grade: origem +0x274/+0x278 = %d, %d (extents pedem %d, %d)'
          % (_ox, _oz, _ex, _ez))
    if (_ox, _oz) != (_ex, _ez):
        print('     origem de celula nao casa com os extents: culling deslocado '
              '%d celulas em x e %d em z' % (_ex - _ox, _ez - _oz))
        ok = False

    # AS INSTANCIAS SAO ENCADEADAS POR TIPO. `+0x00` e o proximo e `+0x04` o
    # anterior, e a cadeia so liga registros com o MESMO `+0x0C`. Medido no
    # atlanta: 3377 elos, todos para o mesmo tipo, nenhum cruzado, 231 cadeias.
    # Reapontar `+0x0C` sem refazer as cadeias mistura os tipos e o jogo fica em
    # loading infinito - foi o que aconteceu na primeira versao do porte de
    # instancia.
    hb3 = p.F(struct.unpack_from('<I', p.data, 0x80 + 0x18)[0])
    ins = []
    for h in range(len(hs)):
        e3 = hb3 + 20 * h
        cnt3 = struct.unpack_from('<I', p.data, e3 + 0x0C)[0]
        arr3 = p.F(struct.unpack_from('<I', p.data, e3 + 0x10)[0])
        if p.inside(arr3):
            ins += [arr3 + 96 * k for k in range(cnt3)]
    if ins:
        desalinhadas = [o for o in ins if (p.V(o) + 0x20) & 15]
        print('  Matrix34 de instancia: %d/%d alinhadas a 16 bytes'
              % (len(ins) - len(desalinhadas), len(ins)))
        if desalinhadas:
            print('     DoSetWorld/LQ truncaria a matriz em %s'
                  % ', '.join('0x%08X' % (p.V(o) + 0x20)
                              for o in desalinhadas[:6]))
            ok = False
        porva = dict((p.V(o), o) for o in ins)
        tp = dict((o, struct.unpack_from('<I', p.data, o + 0x0C)[0]) for o in ins)
        cruzado = 0
        for o in ins:
            d = porva.get(struct.unpack_from('<I', p.data, o)[0])
            if d is not None and tp[d] != tp[o]:
                cruzado += 1
        print('  instancias: %d em %d tipo(s), %d elo(s) cruzando tipo'
              % (len(ins), len(set(tp.values())), cruzado))
        if cruzado:
            print('     cadeia de instancia mistura tipos')
            ok = False

    # AS MASCARAS DE PASSE DAS DUAS CLASSES DE CIDADE. O scheduler global usa
    # diretamente o +0x00; zero impede ate RenderAllTypes de ser chamado. Todas
    # as cidades retail medidas usam 0x4E (passes 2, 4, 8 e 64).
    for off, nome in ((0x194, 'mcCityModelClass'),
                      (0x198, 'mcInstCityModelClass')):
        va = struct.unpack_from('<I', p.data, 0x80 + off)[0]
        mascara = None
        if va and p.inside(p.F(va)):
            mascara = struct.unpack_from('<I', p.data, p.F(va))[0]
        print('  mascara de passes %s (+0x%X): %s'
              % (nome, off,
                 'INVALIDA' if mascara is None else '0x%08X' % mascara))
        if mascara != 0x4E:
            print('     esperado 0x0000004E; zero remove a classe do scheduler')
            ok = False

    # A CADEIA DE ComponentData. `CullableTypeFixup` (0x24AE58) anda
    # `while (v3) { ctor(v3); v3 = *(v3+0x0C); }` a partir da cabeca em
    # `MapRoot+0x194`, que aponta pro ULTIMO objeto do arquivo. Um no fora da
    # cadeia nunca e construido - e o Place para ali, calado.
    #
    # Conferido no varejo antes de virar teste: atlanta anda 651 nos e tem 651
    # componentes.
    total = sum(len(hf.uniques_do_hood(p, i)) for i in range(len(hs)))
    o194 = struct.unpack_from('<I', p.data, 0x80 + 0x194)[0]
    n_cadeia, fora = 0, False
    if o194 and p.inside(p.F(o194)):
        cur = struct.unpack_from('<I', p.data, p.F(o194) + 4)[0]
        while cur and n_cadeia < 20000:
            f = p.F(cur)
            if not p.inside(f):
                fora = True
                break
            cur = struct.unpack_from('<I', p.data, f + 0x0C)[0]
            n_cadeia += 1
    print('  cadeia de ComponentData (MapRoot+0x194): %d no(s) para %d componente(s)%s'
          % (n_cadeia, total, '  PONTEIRO FORA DO ARQUIVO' if fora else ''))
    if fora or (total and n_cadeia != total):
        print('     a cadeia nao cobre todos: o Place constroi so ate onde ela vai')
        ok = False

    # VARREDURA GERAL: nenhum endereco de RAM cru deve sobrar no arquivo.
    # O varejo nunca escreve vtable resolvida - sempre token - e eu descobri
    # isso campo a campo, queimando um boot por campo (ComponentData+0x28,
    # Componente+0x10, Instance+0x10, tipo+0x28 e por fim mesh+0x00). Esta
    # varredura existe para que o proximo campo esquecido apareca aqui e nao
    # num savestate.
    #
    # A faixa inteira 0x62xxxx-0x64xxxx NAO serve de teste: o tokyo do varejo
    # tem 165 palavras la e o atlanta 191, todas dado coincidente (vertice,
    # float). O que o varejo tem em ZERO sao as vtables RESOLVIDAS, entao o
    # teste e por valor exato.
    d = open(caminho, 'rb').read()
    CRUS = {VT_COMPDATA: 'ComponentData+0x28', VT_COMPONENTE: 'Componente+0x10',
            VT_INST: 'Instance+0x10', VT_INST_TIPO: 'tipo de instancia+0x28',
            VT_MESH: 'mesh+0x00'}
    achados = {}
    # PULAR OS PAYLOADS DE VIF. Dado de vertice produz qualquer valor de 32
    # bits, e com 3,9 MB de geometria a varredura crua acusou 0x00625190 cinco
    # vezes como "tipo de instancia" numa cidade que NAO TEM instancia nenhuma -
    # as cinco caiam dentro de payload. So vale procurar vtable onde ha
    # estrutura.
    faixas_payload = []
    for o in range(0x80, len(d) - 32, 4):
        if struct.unpack_from('<I', d, o)[0] >> 20 != 0x007:
            continue
        g = struct.unpack_from('<H', d, o + 8)[0]
        gt = struct.unpack_from('<I', d, o + 0x10)[0]
        fo_gt = gt - base + 0x80
        if not (1 <= g <= 64) or not (0x80 <= fo_gt < len(d) - 8):
            continue
        # TODOS os grupos, nao so o primeiro. Com uma malha de N grupos (que e
        # o que a textura por material exige) proteger so o grupo 0 deixa o
        # resto do payload exposto, e o falso positivo de vtable volta.
        for gi in range(g):
            ge = fo_gt + 8 * gi
            if ge + 8 > len(d):
                break
            lista = struct.unpack_from('<I', d, ge)[0] - base + 0x80
            nb = struct.unpack_from('<H', d, ge + 4)[0]
            if not (0x80 <= lista < len(d)) or not (1 <= nb <= 4096):
                continue
            for k in range(nb):
                e = lista + 8 * k
                if e + 8 > len(d):
                    break
                dp = struct.unpack_from('<I', d, e)[0] - base + 0x80
                qw = struct.unpack_from('<H', d, e + 4)[0]
                if 0x80 <= dp < len(d) and qw:
                    faixas_payload.append((dp, min(len(d), dp + 16 * qw)))
    faixas_payload.sort()

    def em_payload(x, _f=faixas_payload):
        import bisect
        i = bisect.bisect_right(_f, (x, 1 << 30)) - 1
        return i >= 0 and _f[i][0] <= x < _f[i][1]

    for i in range(0x80, len(d) - 4, 4):
        if em_payload(i):
            continue
        w = struct.unpack_from('<I', d, i)[0]
        if w in CRUS:
            achados[w] = achados.get(w, 0) + 1
    if achados:
        ok = False
        print('  VTABLE RESOLVIDA GRAVADA NO ARQUIVO (o varejo so grava token):')
        for w, c in sorted(achados.items(), key=lambda x: -x[1]):
            print('     0x%08X  x%-5d  %s' % (w, c, CRUS[w]))
    else:
        print('  tokens: nenhuma vtable resolvida no arquivo, como no varejo')
    print('  %s' % ('estrutura fecha' if ok else 'ESTRUTURA COM ERRO'))
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--texturas', metavar='DIR',
                    help='pasta de .tex.pck que o JOGO construiu; cada um vira '
                         'um slot de shader e a malha ganha um grupo por material')
    ap.add_argument('--ligacao-runtime', action='store_true',
                    help='slots vazios e marcados, para um mod dar a textura '
                         'depois; evita a forma serializada por completo')
    ap.add_argument('--mapa-identidade', metavar='TSV',
                    help='native_texture_map.tsv: identidade REAL de cada dump '
                         '(447/510 nomes de arquivo estao errados)')
    ap.add_argument('--manifesto-ppf', metavar='JSON',
                    help='manifesto do .ppf; liga o datChunkRef de STREAMING '
                         'em vez do residente')
    ap.add_argument('--mapa-textura', metavar='JSON',
                    help='modelo -> nomes de textura na ordem dos mtl')
    ap.add_argument('--pck-malha', metavar='PCK',
                    help='usa os pacotes VIF de um mesh.pck que O JOGO gerou '
                         '(mc3_heap_to_pck.py) em vez de emitir a mao')
    ap.add_argument('--doador', help='.pck de cidade do retail: de onde sai o shader')
    ap.add_argument('--saida')
    ap.add_argument('--xmod', help='modelo do MC2; sem isto usa um cubo de teste')
    ap.add_argument('--escala', type=float, default=1.0)
    ap.add_argument('--lado', type=float, default=40.0, help='lado do cubo de teste')
    ap.add_argument('--pos', default='0,0,0')
    ap.add_argument('--extents-min', metavar='X,Y,Z',
                    help='extents minimos para a shell sintetica (sem --place)')
    ap.add_argument('--extents-max', metavar='X,Y,Z',
                    help='extents maximos para a shell sintetica (sem --place)')
    ap.add_argument('--hoods',
                    help='nomes de hood separados por virgula, no lugar '
                         'dos do doador; MAXIMO TRES CARACTERES cada')
    ap.add_argument('--hood', default='zz')
    ap.add_argument('--slots', type=int, default=1329,
                    help='slots por grupo de shader (retail: 1329)')
    ap.add_argument('--grupos', type=int, default=18,
                    help='grupos de shader (retail: 18)')
    ap.add_argument('--max-inst', type=int, default=None,
                    help='teto de instancias (padrao: o do doador)')
    ap.add_argument('--material', type=int, default=1)
    ap.add_argument('--sonda', action='store_true',
                    help='cidade com ZERO hoods e ZERO grupos de shader: se ela '
                         'carrega, o problema esta no conteudo, nao no esqueleto')
    ap.add_argument('--shader-slot', type=int, metavar='N',
                    help='qual slot do doador fornece o shader. Sem isto pega '
                         'o primeiro que serve (slot 30 no atlanta), que NAO '
                         'le o stream de ITOP+2. Os blocos do atlanta que '
                         'carregam o stream usam os indices 19, 72, 65, 24, '
                         '293, 7, 71 e 26')
    ap.add_argument('--lista-shaders', action='store_true',
                    help='lista os slots do doador que tem shader utilizavel')
    ap.add_argument('--flip-winding', action='store_true',
                    help='inverte o winding de cada pacote (MC2 -> MC3)')
    ap.add_argument('--normais', action='store_true',
                    help='emite o stream de luz por vertice (ITOP+2, V4-8). '
                         'O CPV fica ligado no passe da cidade por '
                         'mcCityModelClass::SetRenderStates, entao o dado e '
                         'sempre consumido; use JUNTO com --shader-slot de um '
                         'slot cujos blocos carreguem o stream')
    ap.add_argument('--padding', type=int, default=0, metavar='N',
                    help='CONTROLE: N bytes mortos logo apos o MapRoot, para '
                         'deslocar o layout sem mudar conteudo nenhum')
    ap.add_argument('--luz', type=int, default=None, metavar='N',
                    help='indice de paleta por vertice do --normais '
                         '(0..255; padrao 148, a mediana do retail)')
    ap.add_argument('--paleta-mc2', metavar='CPVS.RSC',
                    help='usa a paleta CPP0 de um <hora>_cpvs.rsc do MC2 de '
                         'PS2 no lugar da paleta branca')
    ap.add_argument('--doador-textura', metavar='PCK',
                    help='de onde vem a textura raiz de MapRoot+0x1D4. O '
                         'MipBuffer varia por cidade: atlanta 0x10500 '
                         '(256x256), tokyo 0x160')
    ap.add_argument('--doador-shader', metavar='PCK',
                    help='de onde tirar SO o bloco de shader, quando o doador '
                         'principal nao tem um do tipo tipico')
    ap.add_argument('--place', metavar='TSV',
                    help='tabela de colocacao do mc2_port.py; usa a geometria '
                         'de verdade em vez do cubo')
    ap.add_argument('--modelos', metavar='DIR',
                    help='pasta model/ do pacote exportado (padrao: ao lado do '
                         '--place)')
    ap.add_argument('--limite', type=int, help='so os N primeiros componentes')
    ap.add_argument('--so-hood', help='so as linhas deste hood do place.tsv')
    ap.add_argument('--verificar', metavar='ARQ', help='so reabre e confere')
    ap.add_argument('--base', help='.pck real que JA carrega, pra bisseccao')
    ap.add_argument('--enxerta', choices=('paletas', 'shaders', 'extras', 'grupo', 'hood', 'hood1', 'hood2'),
                    help='troca UMA peca do --base pela versao gerada')
    a = ap.parse_args()

    if a.texturas:
        print('  texturas do jogo: %d slot(s) de shader'
              % carrega_texturas(a.texturas, a.mapa_identidade))
    if a.ligacao_runtime:
        globals()['LIGACAO_RUNTIME'] = True
        print('  ligacao em runtime: slots vazios, marcados com MC3TEXSLOTS')
    if a.manifesto_ppf:
        print('  manifesto do .ppf: %d textura(s)' % carrega_manifesto_ppf(a.manifesto_ppf))
    if a.mapa_textura:
        import json
        global TEXTURAS_POR_MODELO
        TEXTURAS_POR_MODELO = {k.lower(): v for k, v in
                               json.load(open(a.mapa_textura)).items()}
        print('  mapa de textura: %d modelo(s)' % len(TEXTURAS_POR_MODELO))
    if a.pck_malha:
        global PACOTES_DO_JOGO, PASTA_PCK
        if os.path.isdir(a.pck_malha):
            PASTA_PCK = a.pck_malha
            for f in sorted(os.listdir(PASTA_PCK)):
                if f.endswith('.mesh.pck'):
                    cam = os.path.join(PASTA_PCK, f)
                    chave_m = f[:-len('.mesh.pck')].lower()
                    PCK_POR_MODELO[chave_m] = le_pacotes_de_pck(cam)
                    GRUPOS_POR_MODELO[chave_m] = le_grupos_de_pck(cam)
                    c = centro_real_do_pck(cam)
                    if c:
                        CENTRO_REAL_DO_PCK[chave_m] = c
            print('  .pck do jogo na pasta: %d modelo(s), %d pacote(s) no total'
                  % (len(PCK_POR_MODELO),
                     sum(len(v) for v in PCK_POR_MODELO.values())))
        else:
            PACOTES_DO_JOGO = le_pacotes_de_pck(a.pck_malha)
            print('  pacotes vindos do jogo: %d, %d quadwords, %d vertices'
                  % (len(PACOTES_DO_JOGO), sum(p[1] for p in PACOTES_DO_JOGO),
                     sum(p[2] for p in PACOTES_DO_JOGO)))

    # As duas mexem em globais do mc2_to_mc3 e tem que valer antes de
    # qualquer make_block. Ver a nota do CPV la em cima.
    if a.flip_winding:
        globals()['FLIP_WINDING'] = True
        print('  flip de winding: ligado')
    if a.normais:
        mc2.NORMAIS = True
    if a.paleta_mc2:
        globals()['PALETA_MC2'] = paleta_do_mc2(a.paleta_mc2)
        print('  paleta: 256 cores do MC2 (%s)'
              % os.path.basename(a.paleta_mc2))
    if a.padding:
        globals()['PADDING_TESTE'] = a.padding
    if a.luz is not None:
        if not 0 <= a.luz <= 255:
            ap.error('--luz vai de 0 a 255')
        mc2.LUZ = a.luz

    if a.base and a.enxerta:
        enxerta(a.base, a.saida, a.enxerta, a.lado)
        raise SystemExit(0)
    if a.verificar:
        raise SystemExit(0 if verifica(a.verificar) else 1)
    if a.lista_shaders:
        alvo = a.doador_shader or a.doador
        bons = slots_de_shader(alvo)
        print('%s: %d slot(s) com shader utilizavel' % (os.path.basename(alvo),
                                                        len(bons)))
        print('   ' + ' '.join(str(k) for k in bons))
        # Os que a Fork City MODS mediu carregando o stream de ITOP+2. Ter um
        # shader utilizavel e ser o par certo para --normais sao coisas
        # diferentes: o CPV esta sempre ligado no passe da cidade, mas o
        # programa de VU vigente e reenviado por lista, entao ainda vale
        # escolher um slot cujos blocos comprovadamente carregam o stream.
        marcados = [k for k in bons if k in (19, 72, 65, 24, 293, 7, 71, 26)]
        print('   dos que os blocos com stream usam: %s'
              % (' '.join(str(k) for k in marcados) if marcados
                 else 'nenhum neste doador'))
        return

    if not (a.doador and a.saida):
        ap.error('--doador e --saida sao obrigatorios (ou use --verificar)')

    if a.place:
        modelos = a.modelos or os.path.join(os.path.dirname(a.place), 'model')
        if not os.path.isdir(modelos):
            ap.error('nao achei a pasta de modelos: %s' % modelos)
        constroi_place(a.saida, a.doador, a.place, modelos, a.slots, a.grupos,
                       a.material, a.limite, a.so_hood, a.doador_shader,
                       a.max_inst, a.shader_slot, a.doador_textura,
                       [h.strip() for h in a.hoods.split(',')] if a.hoods else None)
        print()
        raise SystemExit(0 if verifica(a.saida) else 1)

    blocos = le_modelo(a.xmod, a.escala) if a.xmod else cubo(a.lado)
    if not blocos:
        raise SystemExit('modelo vazio')
    # A guarda vale para a emissao A MAO. Com --pck-malha os pacotes vem
    # prontos do jogo e os `blocos` servem so para extents e contagens, entao
    # contar os meus aqui barraria um arquivo que o proprio jogo montou.
    if len(blocos) > mc2.MAX_BLOCKS and not PACOTES_DO_JOGO:
        raise SystemExit('%d blocos, o retail nunca passa de %d'
                         % (len(blocos), mc2.MAX_BLOCKS))
    if PACOTES_DO_JOGO and len(PACOTES_DO_JOGO) > mc2.MAX_BLOCKS:
        raise SystemExit('%d pacotes vindos do jogo, o retail nunca passa de %d'
                         % (len(PACOTES_DO_JOGO), mc2.MAX_BLOCKS))
    pos = tuple(float(x) for x in a.pos.split(','))
    hoods = [h.strip() for h in a.hoods.split(',')] if a.hoods else None
    if hoods:
        longos = [h for h in hoods if len(h) > 3]
        if longos:
            raise SystemExit('nome de hood tem no maximo 3 caracteres '
                             '(o campo no .pck tem 4 bytes): %s'
                             % ', '.join(longos))
    if bool(a.extents_min) != bool(a.extents_max):
        ap.error('--extents-min e --extents-max devem ser usados juntos')
    extents = None
    if a.extents_min:
        mn = tuple(float(x) for x in a.extents_min.split(','))
        mx = tuple(float(x) for x in a.extents_max.split(','))
        if len(mn) != 3 or len(mx) != 3:
            ap.error('extents devem ter tres valores X,Y,Z')
        extents = (mn, mx)
    constroi(a.saida, a.doador, blocos, a.hood, pos, a.slots, a.grupos, a.material,
             a.sonda, hoods, a.shader_slot, a.doador_textura, extents)
    print()
    verifica(a.saida)


if __name__ == '__main__':
    main()
