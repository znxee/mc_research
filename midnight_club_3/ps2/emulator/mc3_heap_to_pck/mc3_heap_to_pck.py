r"""Transforma o despejo de heap do `mesh_dump` num `.pck` de malha.

A CADEIA INTEIRA, e cada elo foi medido e nao suposto:

  1. o mod cria um heap privado (mcHeap::CreateMemTopHeap 0x004BD650) e pede ao
     jogo que leia uma malha de TEXTO dentro dele;
  2. USE `.mesh`, NAO `.mod`. O ramo `.mod` do rmcModel::Create monta o
     esqueleto e para: medi packets com ponteiro setado e tamanho ZERO, e o
     fecho transitivo da raiz alcancou 390 bytes de um heap de 148 KB. Pelo
     `.mesh` o mesmo modelo alcanca 46 KB em blocos que comecam com VIF
     (6002409E 3D800000 ...), porque so esse ramo chega em
     rmcGeometry::Packet::Init;
  3. o mod despeja o bloco em hexadecimal e `mc3_heap_dump.py` reconstroi;
  4. este script acha o que a raiz alcanca, COMPACTA e RELOCA.

POR QUE COMPACTAR. O alocador do jogo e bump: o buffer de parse (mshMesh) e
alocado e liberado dentro do mesmo heap e NAO e devolvido, entao o despejo de
169 KB tem so 46 KB de grafo vivo. Um `.pck` e imagem de memoria - lixo dentro
dele seria carregado junto.

COMO A RELOCACAO E FEITA COM SEGURANCA. Nao basta reescrever toda palavra que
caia na faixa do heap: dado VIF e float cairiam junto. So e reescrita a palavra
que aponta para o INICIO de um payload alcancado, ou para inicio+16 - as duas
unicas formas que o motor usa, sendo a segunda o idioma "contagem 16 bytes ANTES
do array" que aparece nos tres niveis (geometrias, packets, cpv).

Cabecalho, conferido num `.pck` de varejo: [baseVA][tipo][versao=1][bytes do
corpo], zeros ate 0x80, corpo a partir dai - ou seja VA base <-> offset 0x80.

    python mc3_heap_to_pck.py output/heap_mesh.bin --base 01E51860 \
        --raiz 01E690D0 --saida output/probe.mesh.pck
"""
import argparse
import bisect
import os
import struct

BASE_PCK = 0x06800000
TIPO_MESH = 0x16
# Um .pck guarda TOKEN de classe em +0x00 da raiz, nao a vtable: o ctor de
# recurso troca por vtable na carga. O despejo traz a vtable de runtime
# (0x00626D98) porque foi montado por new, nao relocado.
TOKEN_MESH = 0x007A0F98
# vtable do rmcTexturePS2, nomeada pela fork C++ e confirmada nos 510 objetos
# que o jogo montou para mim: todos com esta palavra em +0x00.
VT_TEXTURA_PS2 = 0x00627280
CORPO = 0x80


def blocos_do_heap(d):
    """Lista (offset do cabecalho, flags, tamanho) andando a lista de alocacao.

    Cabecalho de 16 bytes, lido do proprio alocador (0x003B0130..): +0x00 elo
    com 3 bits de flag, +0x04 tamanho pedido, +0x0C dono. O passo alinha em 16.
    """
    out, o = [], 0
    while o + 16 <= len(d):
        tam = struct.unpack_from('<I', d, o + 4)[0]
        if tam == 0 or o + 16 + tam > len(d) + 16:
            break
        out.append((o, struct.unpack_from('<I', d, o)[0] & 7, tam))
        o += 16 + ((tam + 15) & ~15)
    return out, o


def emite(d, BASE, raiz_va, saida, tipo=TIPO_MESH, token=TOKEN_MESH, quieto=False):
    """Um .pck a partir de um dump ja carregado. Existe para o MODO LOTE: com
    298 modelos num despejo de 3,2 MB, chamar o script uma vez por modelo releria
    o arquivo 298 vezes."""
    blocos, fim = blocos_do_heap(d)

    def dono(pp):
        lo, hi = 0, len(blocos) - 1
        while lo <= hi:
            m = (lo + hi) // 2
            off, _, tam = blocos[m]
            if pp < off + 16:
                hi = m - 1
            elif pp >= off + 16 + tam:
                lo = m + 1
            else:
                return m
        return None

    raiz = dono(raiz_va - BASE)
    if raiz is None:
        return None
    vistos, fila = {raiz}, [raiz]
    while fila:
        off, _, tam = blocos[fila.pop()]
        for k in range(0, tam & ~3, 4):
            v = struct.unpack_from('<I', d, off + 16 + k)[0]
            if BASE <= v < BASE + len(d):
                t = dono(v - BASE)
                if t is not None and t not in vistos:
                    vistos.add(t); fila.append(t)
    vivos = sorted(vistos)
    ordem = [raiz] + [b for b in vivos if b != raiz]
    novo_mapa, corpo = {}, bytearray()
    for b in ordem:
        off, _, tam = blocos[b]
        novo_mapa[b] = BASE_PCK + len(corpo)
        corpo += d[off + 16:off + 16 + tam]
        corpo += bytes((-len(corpo)) % 16)
    # RELOCACAO QUE PRESERVA O OFFSET DENTRO DO BLOCO. A versao antiga so
    # conhecia inicio de payload e inicio+16, e isso bastava para malha; em
    # TEXTURA nao basta - o manifesto do .ppf diz que os pixels ficam em +144
    # dentro do chunk, e 838 dos 965 datChunkRef apontavam para o meio de um
    # bloco, nao casavam, e ficavam pendurados. Agora qualquer ponteiro para
    # DENTRO de um bloco alcancado e traduzido mantendo o deslocamento.
    # DUAS REGRAS, e a diferenca entre elas ja me custou as duas direcoes.
    #
    # PADRAO (restritiva): so vale quando o alvo e INICIO de payload alcancado,
    # ou inicio+16 (o idioma "contagem 16 bytes antes do array"). Tentei trocar
    # isto por uma traducao que preserva offset e a regressao foi imediata: os
    # pares [u16 qw][u16 nv] da lista de packets sao lidos como palavra de 32
    # bits, casavam como ponteiro e eram REESCRITOS - 19 malhas com qw absurdo
    # (50935, 33855, 47617). Campo de contagem nao e ponteiro.
    #
    # PRESERVANDO OFFSET: so em campo que eu SEI ser ponteiro. Hoje isso e o
    # datChunkRef da textura, que aponta para +144 dentro do chunk (o cabecalho
    # do chunk vem antes dos pixels) e por isso nunca casa com inicio de bloco.
    destino = {}
    for b in ordem:
        off, _, tam = blocos[b]
        destino[BASE + off + 16] = novo_mapa[b]
        if tam > 16:
            destino[BASE + off + 32] = novo_mapa[b] + 16

    def traduz(v):
        return destino.get(v)

    def traduz_interior(v):
        b = dono(v - BASE)
        if b is None or b not in novo_mapa:
            return None
        off, _, _t = blocos[b]
        return novo_mapa[b] + (v - BASE - (off + 16))
    # NAO RELOCAR DENTRO DE PAYLOAD DE VIF. Exigir que o alvo seja inicio de
    # payload alcancado ja descartava quase tudo, mas nao tudo: numa medicao
    # sobre os 729 modelos de LA, 111 palavras em 41 modelos eram COORDENADA DE
    # VERTICE OU UV que por acaso valia o endereco de um bloco - e eram
    # reescritas, corrompendo a geometria em silencio. Dado de vertice produz
    # qualquer padrao de 32 bits; so ha ponteiro onde ha ESTRUTURA. As faixas
    # saem da propria malha: raiz -> tabela de grupos -> lista de packets.
    faixas = []
    ro, _, _rt = blocos[raiz]

    # DUAS FORMAS DE RAIZ. Malha: as faixas protegidas sao os payloads de VIF,
    # alcancados por tabela de grupos -> lista de packets. TEXTURA
    # (rmcTexturePS2, vtable 0x00627280): sao os blocos de PIXEL, apontados
    # pelos quatro datChunkRef de 12 bytes a partir de +0x48. Dado de pixel
    # acerta valor de ponteiro com ainda mais facilidade que vertice, entao a
    # protecao vale ainda mais aqui; e ler +0x10 numa textura pegaria um
    # registrador de GS achando que e ponteiro.
    if struct.unpack_from('<I', d, ro + 16)[0] == VT_TEXTURA_PS2:
        for k in range(4):
            ptr = struct.unpack_from('<I', d, ro + 16 + 0x48 + 12 * k)[0]
            if not (BASE <= ptr < BASE + len(d)):
                continue
            b = dono(ptr - BASE)
            if b is not None:
                off_b, _, tam_b = blocos[b]
                faixas.append((off_b + 16, off_b + 16 + tam_b))
        faixas.sort()

        def em_payload_tex(x, _f=faixas):
            i = bisect.bisect_right(_f, (x, 1 << 30)) - 1
            return i >= 0 and _f[i][0] <= x < _f[i][1]

        trocadas = poupadas = 0
        for b in ordem:
            off, _, tam = blocos[b]
            d0 = novo_mapa[b] - BASE_PCK
            for k in range(0, tam & ~3, 4):
                v = struct.unpack_from('<I', d, off + 16 + k)[0]
                if BASE <= v < BASE + len(d) and traduz(v) is not None:
                    if em_payload_tex(off + 16 + k):
                        poupadas += 1
                        continue
                    struct.pack_into('<I', corpo, d0 + k, traduz(v))
                    trocadas += 1
        # os quatro datChunkRef, por posicao conhecida
        d0r = novo_mapa[raiz] - BASE_PCK
        for k in range(4):
            v = struct.unpack_from('<I', d, ro + 16 + 0x48 + 12 * k)[0]
            if not (BASE <= v < BASE + len(d)):
                continue
            nv = traduz_interior(v)
            if nv is not None:
                struct.pack_into('<I', corpo, d0r + 0x48 + 12 * k, nv)
                trocadas += 1
        if token:
            struct.pack_into('<I', corpo, 0, token)
        cab = struct.pack('<4I', BASE_PCK, tipo, 1, len(corpo)) + bytes(CORPO - 16)
        os.makedirs(os.path.dirname(saida) or '.', exist_ok=True)
        open(saida, 'wb').write(cab + corpo)
        return {'blocos': len(vivos), 'bytes': sum(blocos[b][2] for b in vivos),
                'relocados': trocadas, 'poupadas': poupadas,
                'tamanho': CORPO + len(corpo)}

    gt = struct.unpack_from('<I', d, ro + 16 + 0x10)[0]
    pg = gt - BASE
    # rmcModelGeom+8 is the number of material groups, NOT always one.
    # Protect every group's VIF and its [qw,nv] scalar word. Restricting
    # this walk to group zero still corrupted 219 words in 81 LA meshes.
    ng = struct.unpack_from('<H', d, ro + 16 + 8)[0]
    if not (1 <= ng <= 4096 and 0 <= pg <= len(d) - 8 * ng):
        raise ValueError('invalid mesh group table while protecting VIF')
    for gi in range(ng):
        ge = pg + 8 * gi
        lista = struct.unpack_from('<I', d, ge)[0] - BASE
        nb = struct.unpack_from('<H', d, ge + 4)[0]
        faixas.append((ge + 4, ge + 8))
        if not (0 <= nb <= 4096 and 0 <= lista <= len(d) - 8 * nb):
            raise ValueError('invalid packet table while protecting VIF')
        if nb:
            for k in range(nb):
                e = lista + 8 * k
                faixas.append((e + 4, e + 8))
                dp = struct.unpack_from('<I', d, e)[0] - BASE
                qw = struct.unpack_from('<H', d, e + 4)[0]
                if qw:
                    if not (0 <= dp <= len(d) - 16 * qw):
                        raise ValueError('invalid VIF extent while protecting payload')
                    faixas.append((dp, dp + 16 * qw))
    faixas.sort()
    # Merge overlaps so bisect cannot miss a containing interval.
    merged = []
    for start, end in faixas:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    faixas = merged

    def em_payload(x, _f=faixas):
        i = bisect.bisect_right(_f, (x, 1 << 30)) - 1
        return i >= 0 and _f[i][0] <= x < _f[i][1]

    trocadas = poupadas = 0
    for b in ordem:
        off, _, tam = blocos[b]
        d0 = novo_mapa[b] - BASE_PCK
        for k in range(0, tam & ~3, 4):
            v = struct.unpack_from('<I', d, off + 16 + k)[0]
            if BASE <= v < BASE + len(d) and traduz(v) is not None:
                if em_payload(off + 16 + k):
                    poupadas += 1
                    continue
                struct.pack_into('<I', corpo, d0 + k, traduz(v))
                trocadas += 1
    if token:
        struct.pack_into('<I', corpo, 0, token)
    cab = struct.pack('<4I', BASE_PCK, tipo, 1, len(corpo)) + bytes(CORPO - 16)
    os.makedirs(os.path.dirname(saida) or '.', exist_ok=True)
    open(saida, 'wb').write(cab + corpo)
    return {'blocos': len(vivos), 'bytes': sum(blocos[b][2] for b in vivos),
            'relocados': trocadas, 'poupadas': poupadas,
            'tamanho': CORPO + len(corpo)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('dump')
    ap.add_argument('--base', required=True, type=lambda s: int(s, 16),
                    help='VA onde o heap calhou (a linha BLOB)')
    ap.add_argument('--raiz', type=lambda s: int(s, 16),
                    help='VA do rmcModel (a linha PRB)')
    ap.add_argument('--saida', default='output/malha.mesh.pck')
    ap.add_argument('--tipo', type=lambda s: int(s, 16), default=TIPO_MESH)
    ap.add_argument('--lote', metavar='TSV',
                    help='linhas "<raiz hex>\t<caminho de saida>"; le o dump UMA vez')
    ap.add_argument('--token', type=lambda s: int(s, 16), default=TOKEN_MESH,
                    help='palavra em +0x00 da raiz; 0 mantem a vtable de runtime')
    a = ap.parse_args()

    d = open(a.dump, 'rb').read()
    BASE = a.base

    if a.lote:
        ok = falhou = 0
        for linha in open(a.lote, encoding='utf-8'):
            linha = linha.rstrip()
            if not linha or linha.startswith('#'):
                continue
            hexr, saida = linha.split(chr(9))[:2]
            r = emite(d, BASE, int(hexr, 16), saida, a.tipo, a.token, quieto=True)
            if r:
                ok += 1
            else:
                falhou += 1
                print('  raiz %s nao cai em bloco nenhum' % hexr)
        print('  lote: %d gerado(s), %d falha(s)' % (ok, falhou))
        return
    blocos, fim = blocos_do_heap(d)
    print('%s: %d bytes, %d blocos (caminhada cobriu %.1f%%)'
          % (os.path.basename(a.dump), len(d), len(blocos), 100.0 * fim / len(d)))

    def dono(p):
        lo, hi = 0, len(blocos) - 1
        while lo <= hi:
            m = (lo + hi) // 2
            off, _, tam = blocos[m]
            if p < off + 16:
                hi = m - 1
            elif p >= off + 16 + tam:
                lo = m + 1
            else:
                return m
        return None

    raiz = dono(a.raiz - BASE)
    if raiz is None:
        raise SystemExit('a raiz %08X nao cai em bloco nenhum' % a.raiz)

    vistos, fila = {raiz}, [raiz]
    while fila:
        off, _, tam = blocos[fila.pop()]
        for k in range(0, tam & ~3, 4):
            v = struct.unpack_from('<I', d, off + 16 + k)[0]
            if BASE <= v < BASE + len(d):
                t = dono(v - BASE)
                if t is not None and t not in vistos:
                    vistos.add(t)
                    fila.append(t)
    vivos = sorted(vistos)
    bytes_vivos = sum(blocos[b][2] for b in vivos)
    print('  alcancado da raiz: %d blocos, %d bytes (%.1f%% do despejo)'
          % (len(vivos), bytes_vivos, 100.0 * bytes_vivos / len(d)))

    # A RAIZ VAI PRIMEIRO. Nada aponta para ela (conferido: zero referencias),
    # entao move-la para o inicio do corpo e livre - e o `.pck` exige a raiz em
    # 0x80.
    ordem = [raiz] + [b for b in vivos if b != raiz]
    novo, corpo = {}, bytearray()
    for b in ordem:
        off, _, tam = blocos[b]
        novo[b] = BASE_PCK + len(corpo)
        corpo += d[off + 16:off + 16 + tam]
        corpo += bytes((-len(corpo)) % 16)

    # mapa de destino valido: inicio de payload e inicio+16
    destino = {}
    for b in ordem:
        off, _, tam = blocos[b]
        destino[BASE + off + 16] = novo[b]
        if tam > 16:
            destino[BASE + off + 32] = novo[b] + 16

    trocadas = ignoradas = 0
    for b in ordem:
        off, _, tam = blocos[b]
        d0 = novo[b] - BASE_PCK
        for k in range(0, tam & ~3, 4):
            v = struct.unpack_from('<I', d, off + 16 + k)[0]
            if not (BASE <= v < BASE + len(d)):
                continue
            if v in destino:
                struct.pack_into('<I', corpo, d0 + k, traduz(v))
                trocadas += 1
            else:
                ignoradas += 1
    print('  ponteiros relocados: %d   palavras na faixa mas fora de inicio: %d'
          % (trocadas, ignoradas))

    if a.token:
        struct.pack_into('<I', corpo, 0, a.token)
        print('  raiz +0x00: vtable de runtime -> token %08X' % a.token)

    cab = struct.pack('<4I', BASE_PCK, a.tipo, 1, len(corpo)) + bytes(CORPO - 16)
    os.makedirs(os.path.dirname(a.saida) or '.', exist_ok=True)
    open(a.saida, 'wb').write(cab + corpo)
    print('  -> %s  (%d bytes, corpo %d)' % (a.saida, CORPO + len(corpo), len(corpo)))
    r = struct.unpack_from('<8I', corpo, 0)
    print('  raiz: vtable %08X flags %08X grupos %d tabela %08X geoms %08X'
          % (r[0], r[1], r[2], r[3], r[4]))


if __name__ == '__main__':
    main()
