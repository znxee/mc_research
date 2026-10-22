# -*- coding: utf-8 -*-
"""Converte um modelo do Midnight Club 2 (PC) para dentro de uma cidade do MC3 PS2.

TESTE. Substitui a geometria de UM modelo da cidade e mantem tudo o mais do
arquivo original -- textura, shader, colisao, instancias. Serve pra confirmar
no jogo que a escrita do packet de cidade esta certa, antes de investir em
converter uma cidade inteira.

Nada que ja esta no arquivo se move: a geometria nova e a tabela de blocos nova
sao ANEXADAS no fim e so os ponteiros do modelo alvo sao reescritos. E a mesma
disciplina do Traffic Replacer.

    python mc2_to_mc3.py                      (usa os padroes abaixo)
    python mc2_to_mc3.py --alvo NOME --xmod CAMINHO --saida ARQ.pck --escala F

O QUE ESTE TESTE **NAO** RESOLVE
  * textura: a geometria fica com o atlas do atlanta, entao o UV aponta pro
    lugar errado -- o predio aparece, mas texturizado errado;
  * colisao: o _bnd.pck nao foi tocado, o carro atravessa;
  * nunca foi carregado no jogo por quem escreveu isto.
"""
from __future__ import annotations

import argparse
import io
import os
import struct

MC2_DIR = os.path.join(os.environ.get('MC2_PC_RESEARCH', ''), 'assets_p/city/losangeles/models')
XMOD = os.path.join(MC2_DIR, 'l_downtown_blk_wfargo_x#geom_0_main.xmod')
SRC = os.path.join(os.environ.get('MC3_CLEAN_ASSETS', ''), 'ASSETS/resources/city/atlanta_midnight_clear.pck')
ALVO = 'a_inst_low_ghto_06x'

MODEL_VTABLE = 0x7A0090
VTABLE_AT = 0x28          # a vtable fica 0x28 depois do inicio do objeto modelo
MESH_LOD0 = 0x14          # do inicio da vtable
MESH_BLOCKS = 0x10        # mesh -> tabela de grupos
MESH_PERBLOCK = 0x14      # mesh -> cadeia POR BLOCO (ver emit_mesh_region)
MESH_NSLOT = 0x0A         # quantos slots tem essa cadeia
SPHERE_AT = 0x04          # centro (3 floats) e raio em +0x10
INST_MODEL = 0x0C
INST_RADIUS = 0x18

# (tag S-32 em ITOP+0, posicao em ITOP+98, UV em ITOP+50, normal em ITOP+2)
EVEN = (b'\x9e\x40\x02\x60', b'\x00\x01', b'\xd0\x00', b'\xa0\x00')
ODD = (b'\xc5\x41\x02\x60', b'\x27\x02', b'\xf7\x01', b'\xc7\x01')
UV_FIXO = None            # (u, v) constante: superficie chapada, pra depurar forma
NORMAIS = False           # so 7.3% dos blocos de cidade tem o stream de ITOP+2
LUZ = 148                 # indice de paleta por vertice; 148 e a mediana do retail
MAX_VERTS = 48            # limite do retail (medido nos 1353 meshes do atlanta)
MAX_BLOCKS = 88           # idem: nenhum mesh de cidade passa disso


# ------------------------------------------------------------------ MC2
def read_xmod(path):
    """(posicoes, uvs, tiras) de um .xmod do MC2.

    Texto auto-descritivo: arrays v/n/c/t1, tuplas `adj` que indexam neles, e
    tiras `stp`/`str` (paridades opostas) que indexam nas tuplas.

    A PEGADINHA: os indices das tiras sao RELATIVOS AO PACKET, nao ao array
    inteiro de adjuncts. O arquivo declara isso num registro `packet <num_adjs>
    <num_prims>` -- que e facil de confundir com o campo `packets:` de dentro
    do bloco `mtl`. Lendo tudo como um indice global so, metade dos adjuncts
    fica sem uso e aparecem triangulos gigantes atravessando o modelo: no
    wfargo eram 620 de 1189 adjuncts referenciados e 21 espetos.

    Eu tinha resolvido por heuristica (detectar quando o indice reinicia), o
    que dava o resultado certo mas por sorte. O `mc2-map-toolkit` do jtxredline
    mostra o registro `packet` explicito -- e essa a leitura correta. O mesmo
    toolkit confirma que `stp` comeca horario e `str` anti-horario, alternando,
    que e o modelo de paridade usado aqui.
    """
    v, t1, adj, strips = [], [], [], []
    base = 0
    for line in io.open(path, encoding='latin1'):
        f = line.split()
        if not f:
            continue
        if f[0] == 'v' and len(f) >= 4:
            v.append((float(f[1]), float(f[2]), float(f[3])))
        elif f[0] == 't1' and len(f) >= 3:
            t1.append((float(f[1]), float(f[2])))
        elif f[0] == 'packet' and len(f) >= 3:
            base = len(adj)              # o packet reinicia a numeracao
        elif f[0] == 'adj' and len(f) >= 5:
            # a tupla do MC2 e `adj <vertice> <normal> <cor> <uv>`. O campo 3 e
            # o INDICE DE PALETA por vertice - o mesmo desenho que o MC3 usa no
            # quarto byte do stream de ITOP+2. Era ignorado aqui; agora vai
            # junto, e quem nao tiver cor manda zero.
            adj.append((int(f[1]), int(f[4]), int(f[3])))
        elif f[0] in ('stp', 'str') and len(f) >= 3:
            n = int(f[1])
            strips.append((f[0] == 'str', [base + int(x) for x in f[2:2 + n]]))

    return v, t1, adj, strips


def tris_of(pos, odd=False):
    """Triangulos de uma tira, com a regra de enrolamento do jogo.

    A regra e FIXA: o triangulo do indice `i` sai `(i-2, i-1, i)` quando `i` e
    par e `(i-1, i-2, i)` quando e impar. Nao ha campo no bloco que a inverta --
    o programa da VU1 e o mesmo nas duas metades do double buffer.

    Isto aqui ja teve um `odd` obrigatorio, vindo do campo que hoje se sabe ser
    o endereco de VU1. Era premissa errada: metade dos triangulos saia invertida
    e desaparecia no back-face culling. O parametro so continua existindo pra
    quem quiser decodificar uma tira solta com a paridade trocada.
    """
    out = []
    for i in range(2, len(pos)):
        a, b, c = (i - 2, i - 1, i) if (i % 2 == 0) != odd else (i - 1, i - 2, i)
        out.append((a, b, c))
    return out


def vertex_normals(v, adj, strips):
    """Normal por vertice do MC2, somando as faces que o tocam.

    A cidade do MC3 TEM stream de normal -- `UNPACK V3-8` em ITOP+2, vetores
    unitarios em s8 (mediana |n|/127 = 0.992 medida no atlanta). Eu tinha
    anotado o contrario, mas isso vinha de um walker de VIF que dessincronizava
    no unpack mascarado e nunca chegava no quarto stream.

    O enrolamento acompanha o do jogo -- triangulo i e (i-2,i-1,i) com i par e
    (i-1,i-2,i) com i impar -- pra normal apontar pro mesmo lado da face que vai
    ser desenhada.
    """
    acc = {}
    for _e_str, idxs in strips:
        for k in range(2, len(idxs)):
            x, y, z = idxs[k - 2], idxs[k - 1], idxs[k]
            if k % 2:
                x, y = y, x
            pa, pb, pc = v[adj[x][0]], v[adj[y][0]], v[adj[z][0]]
            u = [pb[i] - pa[i] for i in range(3)]
            w = [pc[i] - pa[i] for i in range(3)]
            n = (u[1] * w[2] - u[2] * w[1],
                 u[2] * w[0] - u[0] * w[2],
                 u[0] * w[1] - u[1] * w[0])
            for idx in (x, y, z):
                t = acc.setdefault(adj[idx][0], [0.0, 0.0, 0.0])
                for i in range(3):
                    t[i] += n[i]
    out = {}
    for k, t in acc.items():
        m = (t[0] ** 2 + t[1] ** 2 + t[2] ** 2) ** 0.5
        out[k] = tuple(c / m for c in t) if m > 1e-9 else (0.0, 1.0, 0.0)
    return out


def strips_to_blocks(v, t1, adj, strips):
    """Tiras do MC2 -> [(posicoes, uvs, impar)], centradas na origem.

    COSTURA. O MC2 entrega centenas de tiras minusculas (a torre wfargo tem 287,
    quase todas de 4 vertices) e o retail nunca passa de **88 blocos por mesh**
    nem de **48 vertices por bloco** -- medido nos 1353 meshes de cidade do
    atlanta. Emitir uma tira por bloco deu 287 blocos e o jogo ficou em tela
    preta. Entao as tiras sao concatenadas numa so, com ponte de degenerados
    (repete o ultimo vertice da anterior e o primeiro da seguinte), respeitando
    os dois limites.
    """
    # ANCORA. Centroide dos vertices nos tres eixos era o obvio e esta errado
    # nos tres. O jogo poe o instance no CHAO (y da instancia = 0.15 em atlanta),
    # entao o modelo tem que ter a BASE na origem, nao o meio: ancorando pelo
    # centroide, o predio wfargo ficou com a AABB local em y -30.90..164.10 e
    # afundou 31 unidades no asfalto, com 80% dos vertices embaixo da rua. E em
    # x/z o centroide nao e o centro da caixa (num predio com sacada, base larga
    # ou qualquer massa assimetrica ele puxa pro lado dos vertices mais densos):
    # deu 11.2 unidades de deslocamento na pegada.
    #
    # O resto do script ja assumia base-na-origem sem que eu percebesse -- a
    # esfera de bound e gravada em (0, dy/2, 0), que so faz sentido com y minimo
    # em zero. Agora as duas pontas concordam.
    cx = (max(p[0] for p in v) + min(p[0] for p in v)) / 2.0
    cy = min(p[1] for p in v)
    cz = (max(p[2] for p in v) + min(p[2] for p in v)) / 2.0

    # A convencao do MC2 e a INVERSA da do MC3: medindo o sinal das normais
    # contra o centroide, `stp` casa com o indice IMPAR do bloco (58.7% das
    # faces pra fora, contra 41.3% do mapeamento direto). No lado do MC3 a
    # medida e bem mais nitida -- 64.8% pra fora nos 156 modelos do atlanta,
    # mediana de 68% por modelo -- e confirma que indice par e a face de frente.
    norm = vertex_normals(v, adj, strips)
    fatias = []
    for e_str, idxs in strips:
        pos = [tuple(a - b for a, b in zip(v[adj[i][0]], (cx, cy, cz))) for i in idxs]
        uv = [t1[adj[i][1]] if 0 <= adj[i][1] < len(t1) else (0.0, 0.0) for i in idxs]
        # A COR VIAJA DENTRO DA NORMAL. O bloco e uma tupla de quatro e ha
        # vinte lugares que a desempacotam assim; acrescentar um quinto campo
        # obrigaria a mexer nos vinte. Como quem consome a normal e so o
        # make_block, e la que ela vira quatro bytes (xyz + indice de paleta),
        # o indice cabe como quarto componente sem tocar em mais nada.
        nr = [norm.get(adj[i][0], (0.0, 1.0, 0.0))
              + ((adj[i][2],) if len(adj[i]) > 2 else ()) for i in idxs]
        if len(pos) >= 3:
            fatias.append((pos, uv, nr, not e_str))

    # ENROLAMENTO. O jogo enrola o triangulo do indice i como (i-2,i-1,i) se i e
    # par e (i-1,i-2,i) se e impar, sempre -- nao ha campo que inverta isso.
    # Logo o que decide o lado da face e onde a tira CAI dentro do bloco:
    #
    #   tira `stp` (horaria)      -> primeiro vertice em indice PAR
    #   tira `str` (anti-horaria) -> primeiro vertice em indice IMPAR
    #
    # (o 1o triangulo dela nasce em s+2, que tem a mesma paridade de s).
    #
    # A versao antiga media essa paridade RELATIVA ao `odd` do bloco, que hoje
    # se sabe ser o endereco do double buffer da VU1. Como o buffer alterna pela
    # posicao do bloco na lista, o enrolamento virava sorteio: metade das faces
    # saia invertida e sumia no back-face culling -- foi o que deixou o predio
    # do MC2 com cara de lajes soltas na primeira vez que ele desenhou no jogo.
    def abre(pos, uv, nr, impar):
        """Comeca um bloco. Tira `str` precisa cair em indice impar, entao leva
        um vertice repetido na frente (degenerado, como o retail faz)."""
        if impar:
            return [pos[0]] + list(pos), [uv[0]] + list(uv), [nr[0]] + list(nr)
        return list(pos), list(uv), list(nr)

    out = []
    cur_p, cur_u, cur_n = [], [], []
    for pos, uv, nr, impar in fatias:
        if not cur_p:
            cur_p, cur_u, cur_n = abre(pos, uv, nr, impar)
            continue
        # a ponte de degenerados tem 2 ou 3 vertices; escolhe a que faz o
        # primeiro vertice da tira cair na paridade certa
        alvo = 1 if impar else 0
        ponte = 2 if (len(cur_p) + 2) % 2 == alvo else 3
        if len(cur_p) + ponte + len(pos) > MAX_VERTS:
            out.append((cur_p, cur_u, cur_n, False))
            cur_p, cur_u, cur_n = abre(pos, uv, nr, impar)
            continue
        cur_p += [cur_p[-1]] + [pos[0]] * (ponte - 1)
        cur_u += [cur_u[-1]] + [uv[0]] * (ponte - 1)
        cur_n += [cur_n[-1]] + [nr[0]] * (ponte - 1)
        cur_p += pos
        cur_u += uv
        cur_n += nr
    if cur_p:
        out.append((cur_p, cur_u, cur_n, False))
    return out, (cx, cy, cz)


# ------------------------------------------------------- packet de cidade
TAIL_HEAD = bytes.fromhex('00000020c0c0c0c0')
TAIL_FOOT = bytes.fromhex('06000014')


def make_block(pos, uv, nrm, scale, odd):
    """Um bloco de cidade, com a CAUDA VIF que fecha o pacote.

    A cauda e 16 bytes constantes logo depois dos UV:
        00 00 00 20 | c0 c0 c0 c0 | 9e 00 00 04 | 06 00 00 14
    com `c5 01 00 04` no lugar do `9e 00 00 04` quando a tira e impar. Depois
    dela vem zeros ate fechar multiplo de 16. Esquecer isso deixa o VIF lendo
    alem do pacote -- foi uma das duas causas do primeiro teste travar.

    `odd` NAO E PARIDADE DE TRIANGULO -- e qual metade do DOUBLE BUFFER da VU1
    o bloco usa. Os quatro campos que ele escolhe sao todos endereco de VU1, e
    a distancia entre as duas metades e sempre 295 qwords:

        campo            buffer A          buffer B
        +00 tag          imm 158           imm 453      (UNPACK S-32, num 2)
        +0C sp           imm 256           imm 551      (UNPACK V3-16 = posicao)
        su (pos os XYZ)  imm 208           imm 503      (UNPACK V2-16 = UV)
        cauda            MSCAL 158         MSCAL 453

    Medido no atlanta: **785 dos 786 grupos alternam A,B,A,B... a partir do
    bloco 0** (a unica excecao e um grupo degenerado com imm 0). Ou seja, o
    valor vem da POSICAO DO BLOCO NA LISTA DO GRUPO, e reseta a cada grupo:

        odd = (indice_na_lista % 2 == 1)

    Copiar o `odd` do bloco de origem quebra a alternancia quando a lista muda
    de tamanho, e ai o DMA sobrescreve a metade que a VU ainda esta rodando --
    e o jogo trava. Foi por isso que todo teste com contagem de bloco diferente
    da original travava, enquanto a reconstrucao fiel passava.
    """
    tag, sp, su, sn = ODD if odd else EVEN
    n = len(pos)
    o = bytearray(tag)
    o += struct.pack('<f', scale)
    o += struct.pack('<I', n)
    o += sp + bytes([n, 0x69])
    for x, y, z in pos:
        o += struct.pack('<hhh', *(max(-32768, min(32767, int(round(c / scale))))
                                   for c in (x, y, z)))
    while len(o) % 4:                       # o padding interno e alinhamento a 4
        o += b'\x00'
    # UV. Com `UV_FIXO` todo vertice recebe a MESMA coordenada, entao a
    # superficie inteira amostra um texel so e sai de uma cor chapada. Nao e
    # bonito, e o ponto: geometria portada usa o atlas da cidade hospedeira, o
    # UV aponta pro lugar errado e o resultado fica ilegivel demais pra julgar
    # se a FORMA esta certa. Chapado, da pra ver silhueta, posicao e escala.
    o += su + bytes([n, 0x65])
    for u, w in (uv if UV_FIXO is None else [UV_FIXO] * len(uv)):
        o += struct.pack('<hh',
                         max(-32768, min(32767, int(round(u * 4096)))),
                         max(-32768, min(32767, int(round(w * 4096)))))
    # NORMAL, o quarto stream: `UNPACK V4-8` (0x6E) em ITOP+2, sem USN. Sem ele
    # o bloco desenha, mas a iluminacao sai do que sobrou na memoria da VU do
    # bloco anterior.
    #
    # V4 e nao V3 de proposito. O microcodigo faz `LQ VF13.xyzw, 2(VI07)` -- le o
    # qword inteiro, `w` incluso -- e o retail escreve os quatro bytes: dos 1073
    # streams em ITOP+2 do atlanta, 740 sao V4-8 e 333 sao V3-8 MASCARADO (com o
    # `w` vindo do ROW). V3-8 puro aparece 16 vezes. Emitindo V3-8 puro, `w`
    # ficaria com o que o bloco anterior deixou na memoria da VU.
    #
    # Os tres primeiros bytes sao a normal em s8: medido nos 8177 vertices V4-8
    # do atlanta, |xyz|/127 tem mediana 0.997 e **100%** cai em [0.95, 1.05].
    # O quarto e o INDICE DE PALETA. O microcodigo faz `MTIR VI10, VF13[fsf]`
    # com fsf = bits 22..21 (nao 24..23 -- trocar os dois foi o que me fez achar
    # que o indice saia do byte x), le com sinal, e busca `LQ 896(VI10)`: a
    # tabela ocupa 768..1023, os 256 qwords do topo da memoria da VU1. O
    # resultado e multiplicado por um global e vai pro pacote GIF como cor.
    #
    # Ou seja a cidade do MC3 **nao tem iluminacao por angulo**: e bake por
    # vertice. Escrever um valor unico deixa o predio uniforme -- foi o que
    # aconteceu com 255, que e a moda do retail mas tambem o extremo.
    #
    # E bake offline de verdade, nao da pra reconstruir: medido nos 8177
    # vertices do atlanta, a correlacao do indice com a normal e +0.045/-0.001/
    # +0.059 e com a altura do vertice e +0.051. A mesma normal aparece com
    # varios indices em 39.5% dos casos. Entao aqui vai um valor ajustavel, com
    # a mediana do retail (148) como padrao em vez do extremo.
    #
    # O bit 0 do byte x e o ADC, que suprime o triangulo terminado naquele
    # vertice (45.1% dos vertices retail o tem). Aqui ele fica SEMPRE em zero de
    # proposito: as quebras de tira ja sao resolvidas pelas pontes de degenerados
    # montadas acima, e marcar ADC por cima suprimiria triangulo bom.
    #
    # DESLIGADO POR PADRAO, e isso foi medido depois de errar: **so 7.3% dos
    # blocos da cidade tem stream em ITOP+2** (759 de 10338 no atlanta), e os 22
    # blocos originais do `a_inst_low_ghto_06x` nao tem nenhum -- so posicao e
    # UV. Escrever num alvo cujo shader nao le so suja a regiao ITOP+2, que e
    # compartilhada entre blocos, e o predio saiu avermelhado no teste.
    # Ligar apenas quando o mesh substituido ja tiver o stream.
    #
    # CORRECAO: a frase 'quem decide se o stream e lido e a palavra de flags do
    # MATERIAL, nao o bloco' estava aqui e esta ERRADA. A FORK C++ MODS AND
    # PATCHES decompilou mcCityModelClass::SetRenderStates (0x0024B300): ela
    # chama rmcSetCpvMode(1, 0) e rmcCpvPalette::Download(*(u32*)(mcCity+0x2C))
    # uma vez POR PASSE. O colour-per-vertex e ligado pela CLASSE do cullable
    # para a cidade inteira -- o ceu, na mesma posicao da vtable, chama
    # rmcSetCpvMode(0, 0). O material nao entra nessa decisao. O que sobra de
    # verdadeiro no aviso e a parte medida: a regiao ITOP+2 e compartilhada, so
    # 7,3% dos blocos escrevem, e os outros herdam -- entao encher um mesh
    # isolado de stream num arquivo que nao o tinha muda o que os VIZINHOS
    # herdam. Numa cidade gerada inteira, onde ninguem escreve, o problema e o
    # oposto: todos herdam lixo.
    if NORMAIS:
        o += sn + bytes([n, 0x6E])
        for n in nrm:
            nx, ny, nz = n[0], n[1], n[2]
            # o quarto componente, quando existe, e o indice de paleta que veio
            # do CPV do MC2; sem ele fica o LUZ constante de sempre
            luz = int(n[3]) & 0xFF if len(n) > 3 else LUZ
            q = [max(-127, min(127, int(round(c * 127.0)))) for c in (nx, ny, nz)]
            q[0] &= ~1
            o += struct.pack('<3bB', q[0], q[1], q[2], luz)
        while len(o) % 4:
            o += b'\x00'
    # A CAUDA, E O STMASK E EXCLUDENTE COM O STREAM.
    #
    # TAIL_HEAD e `STMASK 0xC0C0C0C0`, que masca o campo `w` -- e o par do
    # `UNPACK V3-8 MASCARADO` que o retail usa como ALTERNATIVA ao V4-8: ou o
    # bloco manda os quatro bytes de uma vez, ou manda tres e deixa o `w` vir do
    # ROW sob mascara. MEDIDO no atlanta, cruzando os dois em 525 pacotes:
    #
    #     com stream E com mask :   0      <- nunca, nenhuma vez
    #     com stream, sem mask  :  65
    #     sem stream, com mask  : 410
    #     sem stream, sem mask  :  50
    #
    # Emitir os dois e uma combinacao que NAO EXISTE no retail, e era isso que
    # travava no primeiro quadro toda vez que NORMAIS era ligado -- nao a
    # palavra de flags do material (essa explicacao minha ja caiu, ver a nota
    # do CPV acima) e nao o slot do shader: as duas tentativas, com o shader do
    # slot 30 e com o do 65, morreram no frame 1 pelo mesmo motivo.
    if not NORMAIS:
        o += TAIL_HEAD
    o += (b'\xc5\x01\x00\x04' if odd else b'\x9e\x00\x00\x04') + TAIL_FOOT
    while len(o) % 16:
        o += b'\x00'
    return bytes(o)


def emit_mesh_region(p, mesh, corte, blobs_por_grupo):
    """Escreve, numa unica regiao contigua, a tabela de grupos E a cadeia por
    bloco de `mesh+0x14`. Devolve (offset da tabela de grupos, offset da cadeia).

    A cadeia foi o segundo bug das travadas: ela tem `mesh+0x0A` slots, cada um
    com uma entrada de 8 bytes por grupo, e essa entrada guarda uma contagem que
    tem que ser IGUAL ao numero de blocos do grupo (medido: 6893 de 6893
    entradas do atlanta). Reaproveitar a do arquivo original faz o jogo indexar
    alem do fim assim que um grupo ganha um bloco.

        mesh+0x14 -> [nslot ponteiros]
          cada slot -> ngrp entradas de 8: [ptrA][ptrB]
             ptrA -> [u32 count][u32 vertices de cada bloco], e os payloads
                     colados logo depois -- 1 BYTE POR VERTICE, alinhado a 16
             ptrB -> array de `count` ponteiros, um por payload

    O payload e por vertice e eu nao sei o que significa (alta entropia, valores
    perto de +-127; parece normal ou iluminacao assada). Pra geometria que nao
    veio de um mesh de cidade nao ha o que copiar, entao os bytes do modelo que
    esta sendo substituido sao reciclados ciclicamente: e dado valido, com a
    distribuicao certa, e o jogo aceita.
    """
    ngrp = len(corte)
    nslot = struct.unpack_from('<H', p.data, mesh + MESH_NSLOT)[0]
    contas = [len(g) for g in corte]
    verts = [[len(pos) for pos, _uv, _nr, _o in g] for g in corte]

    # bytes de exemplo do payload, vindos da cadeia que ja existe no arquivo
    amostra = b''
    t14 = p.U(mesh + MESH_PERBLOCK)
    if p.inside(p.F(t14)) and nslot:
        tab = p.F(p.U(p.F(t14)))
        pa, pb = struct.unpack_from('<II', p.data, tab)
        if p.inside(p.F(pb)):
            q = p.F(p.U(p.F(pb)))
            if p.inside(q):
                amostra = bytes(p.data[q:q + 64])
    if not any(amostra):
        amostra = bytes([0x81])

    def enche(n):
        return bytes(amostra[i % len(amostra)] for i in range(n))

    def a16(n):
        return (n + 15) & ~15

    # --- passo 1: so as posicoes relativas, que nao dependem de onde cai ---
    rel = 0
    rel += 16                                   # cabecalho da tabela de grupos
    r_gtab = rel
    rel += a16(8 * ngrp)
    r_lista, r_blocos = [], []
    for gi in range(ngrp):
        rel += 16                               # cabecalho da lista
        r_lista.append(rel)
        rel += a16(8 * contas[gi])
        r_blocos.append(rel)
        rel += sum(len(b) for b in blobs_por_grupo[gi])
        rel = a16(rel)
    r_slots = rel
    rel += a16(4 * nslot)
    r_pa, r_pay, r_pb = [], [], []
    for _s in range(nslot):
        pa_s, pay_s, pb_s = [], [], []
        rel = a16(rel)
        r_tabslot = rel
        rel += a16(8 * ngrp)
        for gi in range(ngrp):
            pa_s.append(rel)
            rel += a16(4 + 4 * contas[gi])
            alvos = []
            for nv in verts[gi]:
                alvos.append(rel)
                rel += a16(nv)
            pay_s.append(alvos)
            pb_s.append(rel)
            rel += a16(4 * contas[gi])
        r_pa.append((r_tabslot, pa_s))
        r_pay.append(pay_s)
        r_pb.append(pb_s)
    total = a16(rel)

    # --- passo 2: reserva e escreve com os enderecos de verdade ---
    at = p.append(b'\x00' * total)
    B = lambda r: at + r                        # offset no arquivo
    W = lambda r: p.V(at + r)                   # endereco virtual

    struct.pack_into('<I', p.data, B(0), ngrp)
    p.data[B(4):B(16)] = b'\xCD' * 12
    for gi in range(ngrp):
        struct.pack_into('<IHH', p.data, B(r_gtab + 8 * gi),
                         W(r_lista[gi]), contas[gi], 0xCDCD)
        struct.pack_into('<I', p.data, B(r_lista[gi] - 16), contas[gi])
        p.data[B(r_lista[gi] - 12):B(r_lista[gi])] = b'\xCD' * 12
        o = r_blocos[gi]
        for j, blob in enumerate(blobs_por_grupo[gi]):
            struct.pack_into('<IHH', p.data, B(r_lista[gi] + 8 * j),
                             W(o), len(blob) // 16, verts[gi][j])
            p.data[B(o):B(o) + len(blob)] = blob
            o += len(blob)

    for s in range(nslot):
        struct.pack_into('<I', p.data, B(r_slots + 4 * s), W(r_pa[s][0]))
        tabslot, pa_s = r_pa[s]
        for gi in range(ngrp):
            struct.pack_into('<II', p.data, B(tabslot + 8 * gi),
                             W(pa_s[gi]), W(r_pb[s][gi]))
            struct.pack_into('<I', p.data, B(pa_s[gi]), contas[gi])
            for j, nv in enumerate(verts[gi]):
                struct.pack_into('<I', p.data, B(pa_s[gi] + 4 + 4 * j), nv)
                q = r_pay[s][gi][j]
                p.data[B(q):B(q) + nv] = enche(nv)
                struct.pack_into('<I', p.data, B(r_pb[s][gi] + 4 * j), W(q))

    struct.pack_into('<I', p.data, 0x0C, len(p.data) - 0x80)
    return B(r_gtab), B(r_slots)


def tile_grid(p):
    """(cell_x, origin_x, cell_z, origin_z) fitted from the file itself.

    Every component carries a culling tile box at +0x14 (x0, x1, z0, z1 as
    bytes) and the placed instances also carry a real position, so the grid can
    be recovered by least squares instead of being assumed. It comes out at
    exactly 40 units per cell in all four cities, with a per-city origin and a
    mean error of about a quarter of a cell - which is just what quantising to
    tiles costs.
    """
    R = 0x80
    nh, hp = p.U(R + 0x14), p.U(R + 0x18)
    if not p.inside(p.F(hp)):
        return None
    hb = p.F(hp)
    pts = []
    for h in range(nh if nh < 64 else 0):
        e = hb + 20 * h
        cnt, arr = p.U(e + 0x0C), p.U(e + 0x10)
        if not p.inside(p.F(arr)) or cnt > 20000:
            continue
        ab = p.F(arr)
        for k in range(cnt):
            c = ab + 96 * k
            try:
                q = struct.unpack_from('<3f', p.data, c + 0x44)
            except Exception:
                continue
            if not all(-5000 < x < 5000 for x in q):
                continue
            pts.append((q[0], q[2],
                        (p.data[c + 0x14] + p.data[c + 0x15] + 1) / 2.0,
                        (p.data[c + 0x16] + p.data[c + 0x17] + 1) / 2.0))
    if len(pts) < 32:
        return None

    def fit(ti, vi):
        n = len(pts)
        st = sum(q[ti] for q in pts)
        sv = sum(q[vi] for q in pts)
        stt = sum(q[ti] * q[ti] for q in pts)
        stv = sum(q[ti] * q[vi] for q in pts)
        den = n * stt - st * st
        if not den:
            return None
        a = (n * stv - st * sv) / den
        return a, (sv - a * st) / n

    fx, fz = fit(2, 0), fit(3, 1)
    if not fx or not fz or not (20.0 < fx[0] < 80.0 and 20.0 < fz[0] < 80.0):
        return None
    return fx[0], fx[1], fz[0], fz[1]


def set_tile_box(p, comp, radius, grid):
    """Recompute the culling tile box of one instance for a new radius."""
    cx, ox, cz, oz = grid
    x, _y, z = struct.unpack_from('<3f', p.data, comp + 0x44)
    x0 = max(0, min(255, int((x - radius - ox) // cx)))
    x1 = max(0, min(255, int((x + radius - ox) // cx)))
    z0 = max(0, min(255, int((z - radius - oz) // cz)))
    z1 = max(0, min(255, int((z + radius - oz) // cz)))
    old = tuple(p.data[comp + 0x14:comp + 0x18])
    p.data[comp + 0x14:comp + 0x18] = bytes((x0, x1, z0, z1))
    return old, (x0, x1, z0, z1)


def pick_scale(blocos):
    """A escala do retail e sempre potencia de dois; pega a menor que nao satura."""
    m = max((abs(c) for p, _u, _nr, _o in blocos for v in p for c in v), default=1.0)
    e = -12
    while m / (2.0 ** e) > 32000 and e < 6:
        e += 1
    return 2.0 ** e


# ------------------------------------------------------------------ .pck
class Pck:
    def __init__(self, path):
        self.data = bytearray(open(path, 'rb').read())
        self.va = struct.unpack_from('<I', self.data, 0)[0]
        self.base = self.va - 0x80
        self.orig = len(self.data)

    def F(self, v):
        return v - self.base

    def V(self, o):
        return o + self.base

    def U(self, o):
        return struct.unpack_from('<I', self.data, o)[0]

    def inside(self, o):
        return 0x80 <= o <= len(self.data) - 4

    def append(self, blob, align=16):
        """Grava um bloco novo e devolve o offset.

        Se `self.livres` existir, uma faixa MORTA que caiba e usada no lugar de
        crescer o arquivo. Isso importa porque o `.pck` de cidade tem teto de
        tamanho - medido em jogo, 12.08 MB carrega e 13.88 MB trava antes de
        chegar na RAM - e portar uma cidade inteira apendando quase dobra o
        arquivo.

        Reaproveitar espaco morto e MUITO mais seguro do que compactar depois:
        nenhum byte se move, entao nenhum ponteiro precisa ser traduzido. E
        traducao por varredura e insegura por natureza - as duas contagens de 16
        bits do descritor de grupo do tokyo valem 1720 cada, empacotadas dao
        0x06B806B8, que cai dentro da janela de VA e vira "ponteiro" para
        qualquer scan cego. No atlanta as mesmas contagens dao 0x05310531 e
        passam despercebidas; foi so sorte.
        """
        # MELHOR ENCAIXE, nao o primeiro que couber: com primeiro-que-cabe a
        # faixa grande e consumida por uma alocacao pequena e o pool fragmenta -
        # medido, 5.39 MB de espaco livre devolviam so 0.36 MB de arquivo.
        n = len(blob)
        livres = getattr(self, 'livres', None)
        if livres:
            melhor = -1
            sobra_melhor = None
            for i, (a, tam) in enumerate(livres):
                ini = a + (-a % align)
                sobra = (a + tam) - (ini + n)
                if sobra >= 0 and (sobra_melhor is None or sobra < sobra_melhor):
                    melhor, sobra_melhor = i, sobra
                    if sobra < align:
                        break
            if melhor >= 0:
                a, tam = livres[melhor]
                ini = a + (-a % align)
                self.data[ini:ini + n] = blob
                if sobra_melhor >= 64:
                    livres[melhor] = (ini + n, sobra_melhor)
                else:
                    livres.pop(melhor)
                return ini
        while len(self.data) % align:
            self.data += b'\xCD'
        at = len(self.data)
        self.data += blob
        while len(self.data) % align:
            self.data += b'\xCD'
        struct.pack_into('<I', self.data, 0x0C, len(self.data) - 0x80)
        return at

    def save(self, path):
        with open(path, 'wb') as f:
            f.write(bytes(self.data))


def find_model(p, nome):
    """Offset do INICIO do objeto modelo (a vtable dele fica em +0x28)."""
    for o in range(0x80, len(p.data) - 0x80, 4):
        if p.U(o) == MODEL_VTABLE:
            raw = bytes(p.data[o + 0x48:o + 0x70]).split(b'\0')[0]
            if raw.decode('latin1', 'replace') == nome:
                return o - VTABLE_AT, o
    return None, None


def instances_of(p, model_off):
    m = p.F(p.U(0x9C))
    arr = p.F(p.U(m + 0x0C))
    out = []
    for k in range(p.U(m + 4)):
        r = p.F(p.U(arr + 4 * k))
        if p.F(p.U(r + INST_MODEL)) == model_off:
            out.append(r)
    return out


def append_array(d, corpo, n, align=16):
    """Anexa um array COM O CABECALHO DE 16 BYTES que o jogo espera.

    Descoberto no construtor do mesh (`sub_2A8FA0` no ELF): ele aloca
    `n*8 + 16`, grava a CONTAGEM no inicio do buffer e guarda o ponteiro
    apontando 16 BYTES DEPOIS. Ou seja, `[ptr - 16]` e a contagem de
    elementos. Conferido no retail: 6/6 grupos e 6/6 listas de bloco do
    alvo. Eu nunca escrevia isso -- ficava 0xCDCDCDCD ali.
    """
    pad = 0xCD
    while len(d) % align:
        d.append(pad)
    d.extend(struct.pack("<I", n))
    d.extend(bytes([pad]) * 12)
    corpo_at = len(d)
    d.extend(corpo)
    while len(d) % align:
        d.append(pad)
    struct.pack_into("<I", d, 0x0C, len(d) - 0x80)
    return corpo_at



def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--xmod', default=XMOD)
    ap.add_argument('--src', default=SRC)
    ap.add_argument('--alvo', default=ALVO)
    ap.add_argument('--saida', default=None)
    ap.add_argument('--manter-esfera', action='store_true',
                    help='nao mexe na esfera de bound nem no raio das instancias')
    ap.add_argument('--blocos', type=int, default=0,
                    help='corta em N blocos (pra bissectar contagem de blocos)')
    ap.add_argument('--uvfixo', metavar='U,V',
                    help='trava o UV num valor so; a superficie sai de uma cor'
                         ' chapada, o que deixa a FORMA legivel enquanto a'
                         ' textura ainda aponta pro atlas errado')
    ap.add_argument('--normais', action='store_true',
                    help='emite o stream de normal/cor em ITOP+2. So 7.3%% dos'
                         ' blocos da cidade tem esse stream e o mesh alvo pode'
                         ' nao ser um deles -- confira antes de ligar')
    ap.add_argument('--luz', type=int, default=LUZ,
                    help='indice de paleta por vertice (0-255). A cidade do MC3'
                         ' nao ilumina por angulo: esse byte escolhe uma cor'
                         ' assada numa tabela de 256 entradas. 148 e a mediana'
                         ' do retail; 255 (a moda) sai claro e chapado')
    ap.add_argument('--escala', type=float, default=1.0,
                    help='multiplica o tamanho do modelo do MC2 (1.0 = tamanho real)')
    a = ap.parse_args()

    globals()['LUZ'] = max(0, min(255, a.luz))
    globals()['NORMAIS'] = bool(a.normais)
    if getattr(a, 'uvfixo', None):
        globals()['UV_FIXO'] = tuple(float(x) for x in a.uvfixo.split(','))
    v, t1, adj, strips = read_xmod(a.xmod)
    blocos, centro = strips_to_blocks(v, t1, adj, strips)
    if a.escala != 1.0:
        blocos = [([tuple(c * a.escala for c in q) for q in p], u, nr, o)
                  for p, u, nr, o in blocos]
    if a.blocos:
        blocos = blocos[:a.blocos]
    pts = [c for p, _u, _nr, _o in blocos for c in p]
    dx = max(q[0] for q in pts) - min(q[0] for q in pts)
    dy = max(q[1] for q in pts) - min(q[1] for q in pts)
    dz = max(q[2] for q in pts) - min(q[2] for q in pts)
    raio = max((q[0] ** 2 + q[1] ** 2 + q[2] ** 2) ** 0.5 for q in pts)
    tris = sum(len(p) - 2 for p, _u, _nr, _o in blocos)
    print('MC2  %s' % os.path.basename(a.xmod))
    print('     %d verts, %d tiras -> %d blocos, %d triangulos' %
          (len(v), len(strips), len(blocos), tris))
    print('     tamanho %.1f x %.1f x %.1f, raio %.1f' % (dx, dy, dz, raio))

    p = Pck(a.src)
    mo, vt = find_model(p, a.alvo)
    if mo is None:
        raise SystemExit('modelo %r nao encontrado' % a.alvo)
    mesh = p.F(p.U(vt + MESH_LOD0))
    raio_antigo = struct.unpack_from('<f', p.data, vt + 0x10)[0]
    inst = instances_of(p, mo)
    print('\nMC3  alvo %s' % a.alvo)
    print('     objeto @%#x (vtable @%#x), mesh @%#x, raio original %.1f, %d instancia(s)'
          % (mo, vt, mesh, raio_antigo, len(inst)))
    for r in inst:
        print('        instancia @%#x em (%8.1f, %6.1f, %8.1f)'
              % (r, *struct.unpack_from('<3f', p.data, r + 0x44)))

    sc = pick_scale(blocos)
    print('\n     escala do packet: %g' % sc)

    # 1) blocos novos, anexados
    #    A metade do double buffer da VU1 vem da POSICAO na lista do grupo, nao
    #    do bloco de origem -- entao os blocos sao repartidos entre os grupos
    #    ANTES de encodar, em fatias contiguas (o `ptrs[i::ngrp]` antigo ainda
    #    embaralhava blocos entre grupos de material diferente).
    ngrp = struct.unpack_from('<H', p.data, mesh + 8)[0]
    n, r = divmod(len(blocos), ngrp)
    corte, k = [], 0
    for i in range(ngrp):
        m = max(1, n + (1 if i < r else 0))
        corte.append(blocos[k:k + m] or [blocos[0]])
        k += m
    if k < len(blocos):
        corte[-1] += blocos[k:]

    blobs_por_grupo = [[make_block(pos, uv, nr, sc, j % 2 == 1)
                        for j, (pos, uv, nr, _odd_da_origem) in enumerate(grupo)]
                       for grupo in corte]

    # 2) O NUMERO DE GRUPOS TEM QUE CONTINUAR O MESMO.
    #    O mesh guarda a contagem num u16 em +0x08 (e de novo em +0x20) e tem
    #    uma tabela de material com um indice de shader POR GRUPO. O primeiro
    #    teste juntou tudo num grupo so e deixou a contagem em 6: o jogo leu as
    #    5 entradas seguintes, que eram 0xCDCDCDCD, como ponteiro -- e travou
    #    ao entrar na cidade. Entao os blocos sao distribuidos entre os grupos
    #    que ja existem, e a tabela de material continua valendo.
    #
    #    O layout e o mesmo do retail e do `teste_vu2.py` (que passou no jogo):
    #    tabela de grupos com cabecalho de 16 bytes, e por grupo uma regiao
    #    contigua [cabecalho][entradas][blocos colados].
    grp_at, t14_at = emit_mesh_region(p, mesh, corte, blobs_por_grupo)
    struct.pack_into('<I', p.data, mesh + MESH_BLOCKS, p.V(grp_at))
    struct.pack_into('<I', p.data, mesh + MESH_PERBLOCK, p.V(t14_at))
    print('     %d blocos em %d grupos (%s), tabela @%#x, cadeia por bloco @%#x'
          % (sum(len(x) for x in corte), ngrp,
             '+'.join(str(len(f)) for f in corte), grp_at, t14_at))

    # 3) esfera de bound: sem isso o jogo corta o predio pelo culling
    if getattr(a, 'manter_esfera', False):
        print('     esfera de bound MANTIDA (raio %.1f) -- os bytes de celula da'
              % raio_antigo)
        print('     instancia sao pre-calculados, mexer no raio pode desalinhar o culling')
    else:
        struct.pack_into('<fff', p.data, vt + SPHERE_AT, 0.0, dy / 2.0, 0.0)
        struct.pack_into('<f', p.data, vt + 0x10, raio)
        for r in inst:
            struct.pack_into('<f', p.data, r + INST_RADIUS, raio)
        print('     esfera de bound: raio %.1f -> %.1f (nas %d instancias tambem)'
              % (raio_antigo, raio, len(inst)))
        # A esfera sozinha nao basta: o culling tambem usa a AABB DE TILE em
        # componente+0x14, quatro bytes pre-calculados. Um predio 6x maior com a
        # caixa antiga some conforme a camera anda. A grade sai ajustada do
        # proprio arquivo (celula de 40 unidades, origem por cidade).
        grade = tile_grid(p)
        if grade is None:
            print('     AVISO: nao consegui ajustar a grade de tile; a AABB de'
                  ' culling ficou a original')
        else:
            print('     grade de tile: celula %.2f x %.2f, origem (%.0f, %.0f)'
                  % (grade[0], grade[2], grade[1], grade[3]))
            for r in inst:
                velha, nova = set_tile_box(p, r, raio, grade)
                print('     AABB de tile da instancia @%#x: %s -> %s'
                      % (r, list(velha), list(nova)))

    out = a.saida or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  os.path.basename(a.src))
    p.save(out)
    orig = open(a.src, 'rb').read()
    novo = open(out, 'rb').read()
    mud = sum(1 for x, y in zip(orig, novo) if x != y)
    print('\nsaida: %s' % out)
    print('     %d -> %d bytes | %d bytes alterados na regiao original'
          % (len(orig), len(novo), mud))


if __name__ == '__main__':
    main()
