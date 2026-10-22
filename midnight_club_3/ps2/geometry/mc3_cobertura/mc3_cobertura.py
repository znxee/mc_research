"""mc3_cobertura.py - quanto do .pck de cidade a gente ja sabe ler

A pergunta que este script responde e "o que AINDA falta". Ele anda o arquivo
a partir da raiz, exatamente pelos caminhos que os dois hexpat ja usam, marca
cada byte que alguma estrutura conhecida cobre, e no fim lista o que sobrou -
os maiores buracos primeiro, com o primeiro u32 de cada um para dar pista.

O .pck de cidade e carregado in-place: o arquivo E a imagem de memoria, com
`file_offset = VA - 0x06800000 + 0x80`. Entao medir cobertura no arquivo e a
mesma coisa que medir na RAM, so que sem o ruido do que o jogo aloca depois.

    python mc3_cobertura.py <cidade.pck>
    python mc3_cobertura.py <cidade.pck> --buracos 40
    python mc3_cobertura.py <cidade.pck> --dump 0x123456

DUAS COISAS QUE O NUMERO NAO DIZ:

  * "coberto" significa que alguma struct reivindica o byte, nao que o campo
    esteja EXPLICADO. Os pacotes VIF entram inteiros como cobertos e por dentro
    sao opacos; o mesmo vale para os pixels de textura.
  * enchimento de 0xCD e zeros sao contados a parte. Eles nao sao buraco de
    conhecimento, sao alinhamento, e misturar os dois inflaria o "falta".
"""
import argparse
import collections
import hashlib
import struct
import sys

BASE = 0x06800000
HDR = 0x80


class Pck:
    def __init__(self, caminho):
        self.d = open(caminho, 'rb').read()
        self.n = len(self.d)
        self.marca = bytearray(self.n)          # 0 = nao coberto
        self.rot = {}                           # id -> nome
        self.conta = collections.Counter()
        self.bytes_por_rotulo = collections.Counter()
        # CONFLITO = alguem reivindicou byte que outra estrutura ja tinha.
        # Nao e detalhe: numa imagem carregada in-place duas structs nao podem
        # ocupar o mesmo byte, entao todo conflito e erro do MEU modelo.
        self.conflito = collections.Counter()
        self.par_conflito = collections.Counter()
        self._prox = 1

    # ---- leitura -----------------------------------------------------
    def off(self, va):
        return va - BASE + HDR

    def ok(self, o, tam=4):
        return o is not None and 0 <= o <= self.n - tam

    def u32(self, o):
        return struct.unpack_from('<I', self.d, o)[0] if self.ok(o) else None

    def u16(self, o):
        return struct.unpack_from('<H', self.d, o)[0] if self.ok(o, 2) else None

    def va_off(self, va):
        """offset de um VA, ou None se o VA nao cai no arquivo."""
        if not va or not (BASE <= va < BASE + 0x01000000):
            return None
        o = self.off(va)
        return o if 0 <= o < self.n else None

    # ---- cobertura ---------------------------------------------------
    def cobre(self, o, tam, rotulo):
        if o is None or tam is None or tam <= 0:
            return False
        if o < 0 or o + tam > self.n:
            return False
        idx = self.rot.setdefault(rotulo, len(self.rot) + 1)
        trecho = self.marca[o:o + tam]
        novos = trecho.count(0)
        alheios = sum(1 for x in trecho if x and x != idx)
        if alheios:
            self.conflito[rotulo] += alheios
            inv = {v: k for k, v in self.rot.items()}
            for x in set(trecho):
                if x and x != idx:
                    self.par_conflito['%s  <-  %s' % (inv.get(x, x), rotulo)] +=                         trecho.count(x)
        self.marca[o:o + tam] = bytes([idx]) * tam
        self.conta[rotulo] += 1
        self.bytes_por_rotulo[rotulo] += novos
        return True

    # ---- relatorio ---------------------------------------------------
    def buracos(self):
        fora = []
        i = 0
        while i < self.n:
            if self.marca[i]:
                i += 1
                continue
            j = i
            while j < self.n and not self.marca[j]:
                j += 1
            fora.append((i, j - i))
            i = j
        return fora


def classifica(p, o, tam):
    """dar um nome ao buraco a partir do que ha dentro dele."""
    s = p.d[o:o + tam]
    if not s.strip(b'\xcd'):
        return 'enchimento CD'
    if not s.strip(b'\x00'):
        return 'zeros'
    if not s.strip(b'\x00\xcd'):
        return 'zeros + CD'
    tex = s.split(b'\0')[0]
    if len(tex) >= 4 and all(32 <= c < 127 for c in tex):
        return 'texto ("%s")' % tex[:24].decode('latin1')
    v = struct.unpack_from('<I', s, 0)[0] if len(s) >= 4 else 0
    if 0x00700000 <= v < 0x00800000:
        return 'comeca com token de classe %08X' % v
    if BASE <= v < BASE + 0x01000000:
        return 'comeca com ponteiro %08X' % v
    return 'comeca com %08X' % v


# =====================================================================
# o passeio
# =====================================================================

def descobre_tokens(p):
    """Os tokens de classe MUDAM de cidade para cidade.

    Nao da para fixar 0x007A1E18 como "rmcModelGeom": no tokyo a mesma classe
    e 0x007A22A0, porque o token e serializado a partir do endereco do modulo.
    Entao o token e DESCOBERTO: pega o mais comum entre os alvos de lod[] dos
    ComponentData (malha) e entre os alvos de shader+parametro (textura).
    """
    u32, u16, vo = p.u32, p.u16, p.va_off
    R = HDR
    malha = collections.Counter()
    nh, vh = u32(R + 0x14), vo(u32(R + 0x18))
    if vh is not None:
        for h in range(nh or 0):
            e = vh + 0x14 * h
            nu, au = u32(e + 4), vo(u32(e + 8))
            if au is None or not nu:
                continue
            for k in range(min(nu, 400)):
                cd = vo(u32(au + 0x1C * k + 0x0C))
                if cd is None:
                    continue
                for l in range(10):
                    alvo = vo(u32(cd + 0x3C + 4 * l))
                    if alvo is not None:
                        malha[u32(alvo)] += 1
    tok_malha = malha.most_common(1)[0][0] if malha else 0
    # a textura raiz da o token de rmcTexturePS2, e o hood desc+4 confirma
    tok_tex = u32(vo(u32(R + 0x1D4)) or 0) or 0
    return tok_malha, tok_tex


def anda(p):
    d, u32, u16, vo = p.d, p.u32, p.u16, p.va_off
    TOK_MALHA, TOK_TEX = descobre_tokens(p)
    print('tokens desta cidade: rmcModelGeom=%08X  rmcTexturePS2=%08X'
          % (TOK_MALHA, TOK_TEX))

    p.cobre(0, HDR, 'cabecalho do pck')
    R = HDR
    p.cobre(R, 0x2290, 'MapRoot (com as duas paletas de 256)')

    # ---- texturas: reusadas por varios donos, entao uma funcao ------
    vistas = set()

    def textura(o, rotulo='rmcTexturePS2'):
        # despachar pelo TOKEN, nao por "parece um ponteiro". Aceitar qualquer
        # destino inflava a conta com pedacos de dado VIF e produzia conflito.
        if o is None or o in vistas:
            return
        tok = u32(o)
        if tok == TOK_TEX - 0x240:           # rmcTextureReference, 0x10 bytes
            vistas.add(o)
            p.cobre(o, 0x10, 'rmcTextureReference')
            nome = vo(u32(o + 8))
            if nome is not None:
                fim = d.find(bytes(1), nome)
                if 0 <= fim < nome + 128:
                    p.cobre(nome, fim - nome + 1, 'nome de textura')
            textura(vo(u32(o + 0x0C)))
            return
        if tok != TOK_TEX:                    # nao e rmcTexturePS2
            return
        vistas.add(o)
        p.cobre(o, 0x90, rotulo)
        nome = vo(u32(o + 0x78))
        if nome is not None:
            fim = d.find(b'\0', nome)
            if 0 <= fim < nome + 128:
                p.cobre(nome, fim - nome + 1, 'nome de textura')
        for k in range(4):
            dados = vo(u32(o + 0x48 + 12 * k))
            if dados is None:
                continue
            p.cobre(dados, 0x90, 'MipBuffer')
            # o tamanho vem do TEX0 do nivel, NAO do campo +0x0C do MipBuffer:
            # aquele campo cobre a alocacao inteira e engolia os vizinhos,
            # inflando a cobertura. Aqui e so o que o nivel realmente ocupa.
            tex0 = struct.unpack_from('<Q', d, o + 8 + 16 * k + 8)[0]
            w = 1 << ((tex0 >> 26) & 0xF)
            h = 1 << ((tex0 >> 30) & 0xF)
            psm = (tex0 >> 20) & 0x1F
            npix = w * h if psm == 0x13 else (w * h // 2 if psm == 0x14 else 0)
            if npix and npix < 0x400000:
                p.cobre(dados + 0x90, npix, 'pixeis')
                mips = d[o + 0x86]
                if mips == k + 1:
                    p.cobre(dados + 0x90 + npix,
                            1024 if psm == 0x13 else 64, 'CLUT')

    # ---- malhas ----------------------------------------------------
    def malha(o):
        # Conferir o TOKEN antes de andar. Sem isso um lod[] com lixo levava a
        # "malhas" cujas tabelas caiam dentro de ComponentData vizinho.
        if o is None or o in vistas or u32(o) != TOK_MALHA:
            return
        vistas.add(o)
        p.cobre(o, 0x20, 'rmcModelGeom (campos)')
        gc = u16(o + 8)
        if not gc or gc > 4096:
            return
        mt = vo(u32(o + 0x0C))
        if mt is not None:
            p.cobre(mt, 2 * gc, 'tabela de material da malha')
        gt = vo(u32(o + 0x10))
        if gt is not None:
            p.cobre(gt - 0x10, 0x10, 'contagem + enchimento de array')
            p.cobre(gt, 8 * gc, 'GroupEntry')
            for g in range(gc):
                e = gt + 8 * g
                lst, nb = vo(u32(e)), u16(e + 4)
                if lst is None or not nb or nb > 4096:
                    continue
                p.cobre(lst - 0x10, 0x10, 'contagem + enchimento de array')
                p.cobre(lst, 8 * nb, 'BlockEntry')
                for k in range(nb):
                    pk, qwc = vo(u32(lst + 8 * k)), u16(lst + 8 * k + 4)
                    if pk is not None and qwc:
                        p.cobre(pk, 16 * qwc, 'pacote VIF')
        # ------------------------------------------------------------
        # +0x14: DOIS NIVEIS de indirecao ate um byte por vertice
        #
        #   +0x14 -> u32 slot[slot_count]              (cookie = slot_count)
        #     slot[k] -> {A, B}[group_count]           (cookie = group_count)
        #        A -> { u32 nblocos, u32 vertices[nblocos] }
        #        B -> u32 vetor[nblocos]
        #              vetor[j] -> u8 dados[vertices[j]], alinhado a 16
        #
        # Conferido no sd_dusk_clear: 1327/1327 cookies de nivel 1 batem com
        # slot_count, 5411/5411 de nivel 2 com group_count, 24396/24396 dos
        # registros A reproduzem exatamente os vertex_count dos BlockEntry do
        # grupo, e 12627/12627 vetores consecutivos ficam a distancia
        # "vertices arredondado para 16".
        # ------------------------------------------------------------
        pb = vo(u32(o + 0x14))
        sc = u16(o + 0x0A)
        if pb is not None and sc and sc <= 4096:
            p.cobre(pb - 0x10, 0x10, 'contagem + enchimento de array')
            # so 4*sc: o resto do quadword NAO e enchimento, o alocador
            # guarda registros pequenos ali (um A de {2,48,4} cabe em 12 bytes)
            p.cobre(pb, 4 * sc, 'tabela de slot (+0x14)')
            for k in range(sc):
                nivel2 = vo(u32(pb + 4 * k))
                if nivel2 is None:
                    continue
                p.cobre(nivel2 - 0x10, 0x10, 'contagem + enchimento de array')
                p.cobre(nivel2, 8 * gc, 'entradas {contagens, vetores} por grupo')
                for g in range(gc):
                    ea, eb = vo(u32(nivel2 + 8 * g)), vo(u32(nivel2 + 8 * g + 4))
                    if ea is None or eb is None:
                        continue
                    n = u32(ea)
                    if not n or n > 4096:
                        continue
                    p.cobre(ea, 4 + 4 * n, 'contagens de vertice por bloco')
                    p.cobre(eb, 4 * n, 'vetor de ponteiros por bloco')
                    for j in range(n):
                        alvo = vo(u32(eb + 4 * j))
                        nv = u32(ea + 4 + 4 * j)
                        if alvo is not None and nv and nv < 0x10000:
                            p.cobre(alvo, nv, 'um byte por vertice')

        for off_ in (0x18, 0x1C):
            q = vo(u32(o + off_))
            if q is not None and u32(q - 8) == 1:
                ln = u32(q - 4)
                if ln and ln < 0x10000:
                    p.cobre(q - 8, 8 + ln, 'par +18/+1C (sem explicacao)')

    # ---- shaders ---------------------------------------------------
    def shader(o):
        # O tamanho vem do BITFIELD em +0x04, nao de uma tabela por token:
        #   bits 22..24 = quantidade de parametros
        #   bits 25..31 = mascara, bit i ligado = parametro i e TEXTURA
        # entao o objeto ocupa 0x08 + 4*n e da para seguir so os parametros
        # que sao mesmo textura.
        if o is None or o in vistas:
            return
        vistas.add(o)
        tok = u32(o)
        flags = u32(o + 4) or 0
        n = (flags >> 22) & 7
        mascara = (flags >> 25) & 0x7F
        # O SLOT 0 EXISTE SEMPRE, mesmo com a contagem zerada. O city_facade
        # (007A1EF8 aqui) tem flags == 0 - indice 0, nenhum parametro - e
        # mesmo assim carrega uma textura em +0x08, e objetos colados desses
        # ficam a 12 bytes um do outro. Usar 8+4*n dava 8 e deixava a textura
        # e os pixels dela de fora: eram 338 KB.
        nslots = max(n, 1)
        p.cobre(o, 8 + 4 * nslots, 'shader %08X' % tok)
        for i in range(nslots):
            if i == 0 or (mascara & (1 << i)):
                textura(vo(u32(o + 8 + 4 * i)))

    # ---- grupos de shader ------------------------------------------
    ngrp, vgrp = u32(R + 0x08), vo(u32(R + 0x0C))
    if vgrp is not None:
        p.cobre(vgrp, 0x10 * ngrp, 'ShaderGroupDesc')
        for g in range(ngrp):
            e = vgrp + 0x10 * g
            arr, n = vo(u32(e + 4)), u16(e + 8)
            if arr is None or not n:
                continue
            p.cobre(arr, 4 * n, 'array de slots do grupo')
            for k in range(n):
                shader(vo(u32(arr + 4 * k)))
    ceu = vo(u32(R + 0x10))
    if ceu is not None:
        p.cobre(ceu, 0x10, 'ShaderGroupDesc do ceu')
        arr, n = vo(u32(ceu + 4)), u16(ceu + 8)
        if arr is not None and n:
            p.cobre(arr, 4 * n, 'array de slots do grupo')
            for k in range(n):
                shader(vo(u32(arr + 4 * k)))

    # ---- classes cullable ------------------------------------------
    for off_ in (0x190, 0x194, 0x198):
        c = vo(u32(R + off_))
        if c is not None:
            p.cobre(c, 0x40, 'CullableClass')

    # ---- textura raiz e proxy --------------------------------------
    textura(vo(u32(R + 0x1D4)), 'rmcTexturePS2 (raiz)')
    for k in range(20):
        textura(vo(u32(R + 0x1D8 + 4 * k)))
    px = vo(u32(R + 0x228))
    if px is not None:
        p.cobre(px, 0x18, 'TextureProxy')
        n = u16(px)
        for campo, mult, rot in ((0x04, 128, 'proxy: indices'),
                                 (0x08, 64, 'proxy: paletas'),
                                 (0x0C, 4, 'proxy: tabela')):
            a = vo(u32(px + campo))
            if a is not None:
                p.cobre(a, n * mult, rot)

    # ---- indice de celulas -----------------------------------------
    ci = vo(u32(R + 0x1C))
    cell_count = u32(R + 0x268)
    if ci is not None:
        # O CellIndex nao tem 0x18 bytes: os seis ponteiros sao so a cabeca.
        # Depois deles vem ~29 KB ZERADOS no arquivo, que sao as listas de
        # visiveis que o runtime enche (+0x64 e +0x84, ver a nota do hexpat).
        # E o maior bloco que restava, e nao e conteudo: e buffer.
        ua = vo(u32(ci + 0x08))
        corpo = (ua - 0x10 - ci) if (ua and ua > ci) else 0x18
        p.cobre(ci, 0x18, 'CellIndex (cabeca)')
        if 0x18 < corpo < 0x100000:
            p.cobre(ci + 0x18, corpo - 0x18,
                    'corpo do CellIndex (zerado no arquivo, listas de visiveis)')
        nu, ni = u32(ci), u32(ci + 4)
        for campo, cnt, mult, rot in ((0x08, nu, 4, 'lista de unicos'),
                                      (0x0C, ni, 4, 'lista de instancias'),
                                      (0x10, cell_count, 0x0C, 'CellRecord'),
                                      (0x14, cell_count, 4, 'extra por celula')):
            a = vo(u32(ci + campo))
            if a is not None and cnt and cnt < 0x100000:
                p.cobre(a, cnt * mult, rot)
        # +0x14 nao e "u32 por celula, nao decifrado": e um vetor de
        # PONTEIROS por celula. Cada destino e
        #   { float; u16 na (bit15 = flag); u16 nb; u16 lista[na+nb] }
        # alinhado a 4. Os valores sao indice de INSTANCIA em 14 bits mais um
        # campo de 2 bits no topo. Conferido: 2390 de 2391 registros fecham
        # exatamente com o inicio do proximo, zero fora.
        extra = vo(u32(ci + 0x14))
        if extra is not None and cell_count and cell_count < 0x100000:
            for i in range(cell_count):
                a = vo(u32(extra + 4 * i))
                if a is None:
                    continue
                na = (p.u16(a + 4) or 0) & 0x7FFF
                nb = p.u16(a + 6) or 0
                if na + nb < 0x8000:
                    p.cobre(a, (8 + 2 * (na + nb) + 3) & ~3,
                            'lista de instancias por celula (+0x14)')

        cells = vo(u32(ci + 0x10))
        if cells is not None and cell_count and cell_count < 0x100000:
            for c in range(cell_count):
                e = cells + 0x0C * c
                for campo, cnt in ((4, p.u16(e) or 0), (8, p.u16(e + 2) or 0)):
                    a = vo(u32(e + campo))
                    if a is not None and cnt:
                        p.cobre(a, 2 * cnt, 'lista de celula (u16)')

    # ---- hoods, componentes e instancias ---------------------------
    def componente(o):
        if o is None or o in vistas:
            return
        vistas.add(o)
        p.cobre(o, 0x90, 'ComponentData')
        for k in range(10):
            malha(vo(u32(o + 0x3C + 4 * k)))

    nh, vh = u32(R + 0x14), vo(u32(R + 0x18))
    if vh is not None:
        p.cobre(vh, 0x14 * nh, 'HoodEntry')
        for h in range(nh):
            e = vh + 0x14 * h
            desc = vo(u32(e))
            if desc is not None:
                p.cobre(desc, 4, 'nome do hood')
                textura(desc + 4, 'rmcTexturePS2 (hood)')
            nu, au = u32(e + 4), vo(u32(e + 8))
            ni, ai = u32(e + 0x0C), vo(u32(e + 0x10))
            if au is not None and nu and nu < 0x100000:
                p.cobre(au, 0x1C * nu, 'UniqueComponent')
                for k in range(nu):
                    componente(vo(u32(au + 0x1C * k + 0x0C)))
            if ai is not None and ni and ni < 0x100000:
                p.cobre(ai, 0x60 * ni, 'Instance')
                for k in range(ni):
                    componente(vo(u32(ai + 0x60 * k + 0x0C)))


def malhas_orfas(p, tok_malha):
    """Malhas que existem no arquivo e que ponteiro nenhum alcanca.

    No sd sao 3 e no detroit 2; atlanta e tokyo nao tem nenhuma. Todas as
    cinco sao DUPLICATA EXATA de uma malha que esta em uso - mesma geometria
    byte a byte e a mesma tabela de material - so que sem dono. E sobra do
    processo que montou o pck, nao estrutura que falte entender.

    A funcao devolve (orfas, grupos de geometria repetida). Repare que
    geometria repetida COM dono nos dois lados e outra coisa e e legitima: os
    pares st_*_01x / st_*_01ax sao a mesma pista com materiais diferentes.
    """
    d, u32, u16 = p.d, p.u32, p.u16
    alvo = struct.pack('<I', tok_malha)
    pos = []
    i = 0
    while True:
        i = d.find(alvo, i)
        if i < 0 or i > p.n - 0x30:
            break
        if i % 16 == 0:
            pos.append(i)
        i += 4
    apontados = set()
    for a in range(0, p.n - 4, 4):
        v = u32(a)
        if v and BASE <= v < BASE + p.n:
            apontados.add(v)

    def digital(a):
        gc, gt = u16(a + 8), p.va_off(u32(a + 0x10))
        mt = p.va_off(u32(a + 0x0C))
        if gt is None or mt is None:
            return None
        h = hashlib.md5()
        for g in range(min(gc, 4096)):
            lst, nb = p.va_off(u32(gt + 8 * g)), u16(gt + 8 * g + 4)
            if lst is None:
                return None
            for k in range(min(nb or 0, 4096)):
                pk = p.va_off(u32(lst + 8 * k))
                n = 16 * (u16(lst + 8 * k + 4) or 0)
                if pk is None:
                    return None
                h.update(d[pk:pk + n])
        return h.hexdigest()

    por_geo = {}
    for a in pos:
        g = digital(a)
        if g:
            por_geo.setdefault(g, []).append(a)
    orfas = [a for a in pos if (a + BASE - HDR) not in apontados]
    repetidas = [v for v in por_geo.values() if len(v) > 1]
    return pos, orfas, repetidas


def main():
    ap = argparse.ArgumentParser(
        description=__doc__.strip().splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pck')
    ap.add_argument('--buracos', type=int, default=25,
                    help='quantos buracos listar (default 25)')
    ap.add_argument('--dump', help='mostrar 128 bytes deste offset (hex)')
    a = ap.parse_args()

    p = Pck(a.pck)
    if a.dump:
        o = int(a.dump, 16)
        for k in range(0, 128, 16):
            s = p.d[o + k:o + k + 16]
            print('%08X  %-47s  %s' % (o + k, ' '.join('%02X' % x for x in s),
                  ''.join(chr(x) if 32 <= x < 127 else '.' for x in s)))
        return 0

    anda(p)
    coberto = p.n - p.marca.count(0)
    print('%s  %d bytes' % (a.pck, p.n))
    print('coberto por estrutura conhecida: %d  (%.1f%%)'
          % (coberto, 100.0 * coberto / p.n))
    print()
    print('%-42s %8s %12s' % ('estrutura', 'quantos', 'bytes'))
    for rot, nb in p.bytes_por_rotulo.most_common():
        print('%-42s %8d %12d' % (rot, p.conta[rot], nb))

    if p.conflito:
        print()
        print('CONFLITOS (byte reivindicado por duas structs - erro de modelo)')
        for rot, nb in p.par_conflito.most_common(12):
            print('%-64s %10d' % (rot, nb))

    fora = p.buracos()
    por_tipo = collections.Counter()
    bytes_tipo = collections.Counter()
    for o, tam in fora:
        t = classifica(p, o, tam)
        if t.startswith('comeca com') or t.startswith('texto'):
            t = t.split(' (')[0].split(' %08X')[0]
            t = 'dado nao mapeado' if 'comeca' in t else 'texto solto'
        por_tipo[t] += 1
        bytes_tipo[t] += tam
    print()
    print('SOBRA: %d trechos, %d bytes (%.1f%%)'
          % (len(fora), p.n - coberto, 100.0 * (p.n - coberto) / p.n))
    print('%-24s %8s %12s' % ('natureza', 'trechos', 'bytes'))
    for t, nb in bytes_tipo.most_common():
        print('%-24s %8d %12d' % (t, por_tipo[t], nb))

    # De quem e o VIZINHO de tras de cada buraco: e a pista mais util para
    # saber por onde continuar - o buraco quase sempre e a continuacao de uma
    # estrutura que eu marquei curta demais, ou o irmao dela.
    inv = {v: k for k, v in p.rot.items()}
    antes = collections.Counter()
    bytes_antes = collections.Counter()
    for o, tam in fora:
        rot = inv.get(p.marca[o - 1], '(inicio do arquivo)') if o else '(inicio)'
        antes[rot] += 1
        bytes_antes[rot] += tam
    print()
    print('BURACO POR VIZINHO DE TRAS')
    print('%-42s %8s %12s' % ('vem logo depois de', 'trechos', 'bytes'))
    for rot, nb in bytes_antes.most_common(12):
        print('%-42s %8d %12d' % (rot, antes[rot], nb))

    tok_malha, _ = descobre_tokens(p)
    if tok_malha:
        todas, orfas, repetidas = malhas_orfas(p, tok_malha)
        print()
        print('MALHAS: %d no arquivo, %d SEM DONO, %d grupos de geometria repetida'
              % (len(todas), len(orfas), len(repetidas)))
        for o in orfas:
            print('   orfa em %08X' % o)

    print()
    print('OS %d MAIORES BURACOS' % a.buracos)
    print('%-10s %10s  %s' % ('offset', 'bytes', 'o que parece'))
    for o, tam in sorted(fora, key=lambda x: -x[1])[:a.buracos]:
        print('%08X %10d  %s' % (o, tam, classifica(p, o, tam)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
