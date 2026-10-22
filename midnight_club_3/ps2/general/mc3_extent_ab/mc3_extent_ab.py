"""mc3_extent_ab.py - por que dois decodificadores discordam da extensao

A Fork Alpha 2004 mediu 120 dos 729 `.mesh.pck` de LA com extensao local de
~4096 e chamou isso de overflow de quantizacao. Com o meu decodificador
consertado eu meco ZERO acima de 2000 nos mesmos arquivos, e no
`l_beverlyhills_blk_hotel_01_x` eu bato a contagem de vertice exata (4150/4150)
mas dou extensao 198,8.

Este script nao decide quem esta certo. Ele roda as DUAS leituras sobre os
mesmos bytes e mostra qual suposicao produz qual numero, para a discordancia
virar uma linha de comando em vez de duas afirmacoes.

A diferenca esta em UMA escolha: quais fluxos de VIF sao posicao.

  A  fluxo V3 so nos enderecos de POSICAO   (0x100..0x1C4 e >= 0x227)
  B  todo fluxo V3, inclusive o V3-8 MASCARADO em 0x0A0/0x1C7

Nas duas, V3-16 e V3-8 contam: a posicao vem nas duas codificacoes, porque o
PackData escolhe delta de 8 bits quando ela sai menor. Uma primeira versao deste
script aceitava so V3-16 na leitura A e por isso perdia 733 dos 4150 vertices do
hotel_01 - o mesmo tipo de erro que ja tinha me custado o decodificador inteiro.

O layout, medido num `.mesh.pck` de varejo: cada buffer de VU tem cor em +2, uv
em +0x32 e posicao em +0x62 a partir do ITOP - 0x0A0/0x0D0/0x100 no primeiro e
0x1C7/0x1F7/0x227 no segundo. O fluxo em 0x0A0 e um V3-8 mascarado, com STMASK
e STROW na frente. Se ele for normal, a leitura A esta certa; se for posicao,
a leitura B esta.

USO

    python mc3_extent_ab.py <arquivo.mesh.pck>      um arquivo, com detalhe
    python mc3_extent_ab.py --todos <pasta>         a pasta inteira, as duas contagens
    python mc3_extent_ab.py --cidade <cidade.pck>  dentro de um .pck de cidade

EXEMPLO QUE REPRODUZ A DISCORDANCIA

    python mc3_extent_ab.py "output/la729_pck/l_beverlyhills_blk_hotel_01_x#geom_0_main.mesh.pck"
    python mc3_extent_ab.py --todos output/la729_pck
"""
import collections
import glob
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mc3_vifdis as V


# Os enderecos de VU medidos num .mesh.pck de varejo.
BUF = ((0x09E, 0x0A0, 0x0D0, 0x100), (0x1C5, 0x1C7, 0x1F7, 0x227))


def classifica(addr):
    """'pos', 'uv', 'cor' ou None, pelo endereco de destino no VU."""
    for itop, cor, uv, pos in BUF:
        if addr == cor:
            return 'cor'
        if addr == uv:
            return 'uv'
        if addr == itop:
            return 'hdr'
    if 0x100 <= addr < 0x1C5 or addr >= 0x227:
        return 'pos'
    return None


def le(pck, modo):
    """Devolve (extensao, escala, vertices, fluxos) sob a leitura A ou B."""
    lo = [1e30] * 3
    hi = [-1e30] * 3
    cru_lo, cru_hi = 32767, -32768     # os valores ANTES da escala
    escala = None
    n = 0
    fluxos = collections.Counter()

    for off, qw, nv in V.walk_graph(pck):
        modo_vif = 0
        row = [0, 0, 0, 0]
        for o, w, t in V.walk_chain(pck, off, qw):
            cmd = (w >> 24) & 0xFF
            if cmd == 0x05:
                modo_vif = w & 0xFF
                continue
            if cmd == 0x30:
                row = [V._s32(pck.w(o + 4 + k * 4)) for k in range(4)]
                continue
            if not (0x60 <= cmd <= 0x7F):
                continue

            addr = w & 0x3FF
            cnt = (w >> 16) & 0xFF
            que = classifica(addr)

            if cmd in (0x60, 0x6C) and cnt == 2:
                f = struct.unpack('<f', struct.pack('<I', pck.w(o + 4)))[0]
                if 0.0 < f <= 1.0:
                    escala = f
                continue
            if escala is None:
                continue

            mascarado = bool(cmd & 0x10)
            fluxos['%s %s%s' % (V.unpack_name(cmd & ~0x10), que or '?',
                                ' masc' if mascarado else '')] += 1

            # AQUI ESTA A DIFERENCA ENTRE AS DUAS LEITURAS.
            if ((cmd & ~0x10) & 0x0C) != 0x08:      # so fluxo V3
                continue
            if modo == 'A' and que != 'pos':
                continue

            b = pck.off + o + 4
            bits = V.unpack_bits(cmd)
            vals = []
            for i in range(cnt):
                r = []
                for c in range(3):
                    if bits == 16:
                        v = V._s16(struct.unpack_from(
                            '<H', pck.data, b + (i * 3 + c) * 2)[0])
                    elif bits == 8:
                        v = pck.data[b + i * 3 + c]
                        v = v - 256 if v & 0x80 else v
                        if modo_vif == 2:
                            v += row[c] if i == 0 else vals[i - 1][c]
                    else:
                        v = V._s32(pck.w(o + 4 + (i * 3 + c) * 4))
                    r.append(v)
                vals.append(r)
            for r in vals:
                for c in range(3):
                    if r[c] < cru_lo:
                        cru_lo = r[c]
                    if r[c] > cru_hi:
                        cru_hi = r[c]
                    f = r[c] * escala
                    if f < lo[c]:
                        lo[c] = f
                    if f > hi[c]:
                        hi[c] = f
                n += 1

    if not n:
        return None
    return (max(hi[c] - lo[c] for c in range(3)), escala, n, fluxos,
            cru_lo, cru_hi)


def um(caminho):
    pck = V.Pck(caminho)
    declarado = sum(nv for _, _, nv in V.walk_graph(pck))
    print('%s' % os.path.basename(caminho))
    print('  %d grupos, %d pacotes, %d vertices declarados nos slots'
          % (pck.h(0x08), len(list(V.walk_graph(pck))), declarado))
    print()
    for modo, texto in (('A', 'V3 so em endereco de posicao'),
                        ('B', 'todo V3, inclusive o mascarado em 0x0A0')):
        r = le(pck, modo)
        if r is None:
            print('  %s  sem geometria' % modo)
            continue
        ext, esc, n, fluxos, cl, ch = r
        alcance = 32767.0 * esc
        print('  leitura %s (%s)' % (modo, texto))
        print('     extensao %10.1f   escala %-12g alcance +-%.0f'
              % (ext, esc, alcance))
        print('     %d vertices  %s' % (n, 'BATE com o declarado'
                                        if n == declarado else
                                        '(declarado: %d)' % declarado))
        # A prova fisica: overflow e valor cru batendo no trilho do s16. Se o
        # cru nao chega perto de +-32767, nao houve estouro - e isso independe
        # de quem esta certo sobre qual fluxo e posicao.
        rail = max(abs(cl), abs(ch))
        print('     s16 cru: %d a %d   (o trilho e -32768 a 32767; usa %.1f%% dele)'
              % (cl, ch, 100.0 * rail / 32767.0))
        print('     estourou: %s'
              % ('SIM - o cru bate no trilho' if rail > 32000 else
                 'nao - sobra %.0f%% de margem' % (100.0 - 100.0 * rail / 32767.0)))
        print()
    print('  fluxos encontrados no arquivo:')
    r = le(pck, 'B')
    if r:
        for k, v in sorted(r[3].items()):
            print('     %-22s %d' % (k, v))
    print()
    print('  Os dois numeros vem dos MESMOS bytes. A unica diferenca e se o')
    print('  V3-8 mascarado em 0x0A0/0x1C7 conta como posicao ou como normal.')


def todos(pasta):
    """A varredura. O sinal que importa NAO e a extensao - e o uso do trilho.

    Um modelo longe da origem tem valor cru enorme e extensao pequena: ele nao e
    grande, so esta longe. Medir extensao faz todos parecerem seguros. O que
    diz se ha risco de estouro e quanto do intervalo de s16 o valor cru ja
    gasta, porque acima do trilho ele da a volta em silencio.
    """
    arqs = sorted(glob.glob(os.path.join(pasta, '*.pck')))
    if not arqs:
        print('nenhum .pck em %s' % pasta)
        return 1
    linhas = []
    exato = 0
    for f in arqs:
        pck = V.Pck(f)
        declarado = sum(nv for _, _, nv in V.walk_graph(pck))
        r = le(pck, 'A')
        if r is None:
            continue
        ext, esc, n, _, cl, ch = r
        if n == declarado:
            exato += 1
        linhas.append((max(abs(cl), abs(ch)) / 32767.0,
                       os.path.basename(f)[:44], ext, esc, cl, ch))
    linhas.sort(reverse=True)

    faixas = ((0.98, 'no trilho    >= 98%'),
              (0.90, 'perigoso     90-98%'),
              (0.75, 'apertado     75-90%'),
              (0.00, 'folgado       < 75%'))
    print('%d arquivos em %s, %d com a contagem de vertice batendo exato'
          % (len(arqs), pasta, exato))
    print()
    print('  USO DO TRILHO s16 - o sinal que importa:')
    ant = 1.01
    for lim, nome in faixas:
        c = sum(1 for x in linhas if lim <= x[0] < ant)
        print('     %-22s %4d' % (nome, c))
        ant = lim
    print()
    print('  os mais proximos do trilho:')
    for u, n, ext, esc, cl, ch in linhas[:8]:
        print('     %5.1f%%  %-46s cru %7d..%-7d escala %g'
              % (100 * u, n, cl, ch, esc))
    print()
    print('  Extensao, para comparar - e por que ela ENGANA aqui:')
    print('     acima de 2000: %d' % sum(1 for x in linhas if x[2] > 2000))
    print('     Um modelo longe da origem tem cru grande e extensao pequena.')
    print('     Ele nao e grande, so esta longe - e e exatamente esse que corre')
    print('     risco de estourar.')
    return 0


def cidade(caminho):
    """Uso do trilho dentro de um .pck de CIDADE (tipo 0x43).

    Uma cidade nao tem raiz de malha em corpo+0, entao aqui a varredura de
    cabecalho e legitima em vez de preguicosa: cada SUB-LOTE tem o seu proprio
    'UNPACK S-32 x2' com a escala inversa, e foi por isso que o hotel_01 tinha
    sete deles num pacote so. Achando os cabecalhos eu acho os sub-lotes, e a
    escala vem junto - que e tudo que a medida de trilho precisa.

    O float da escala e o filtro contra falso positivo: tem que ser potencia de
    dois em (0, 1].
    """
    pck = V.Pck(caminho)
    print('%s  tipo 0x%02X  %d bytes de corpo'
          % (os.path.basename(caminho), pck.type, pck.body))
    cabecalhos = V.find_chains(pck)
    print('  %d sub-lotes encontrados' % len(cabecalhos))
    if not cabecalhos:
        return 1

    escalas = collections.Counter()
    pior = 0
    pior_off = 0
    nv = 0
    usos = []
    for off, esc in cabecalhos:
        escalas[esc] += 1
        cru = 0
        for o, w, t in V.walk_chain(pck, off):
            cmd = (w >> 24) & 0xFF
            if not (0x60 <= cmd <= 0x7F):
                continue
            addr = w & 0x3FF
            if classifica(addr) != 'pos':
                continue
            if ((cmd & ~0x10) & 0x0C) != 0x08:
                continue
            cnt = (w >> 16) & 0xFF
            b = pck.off + o + 4
            bits = V.unpack_bits(cmd)
            if bits != 16:
                continue          # o delta e relativo; o trilho e do absoluto
            for i in range(cnt * 3):
                v = abs(V._s16(struct.unpack_from('<H', pck.data,
                                                  b + i * 2)[0]))
                if v > cru:
                    cru = v
                nv += 1
        if cru:
            usos.append(cru / 32767.0)
            if cru > pior:
                pior, pior_off = cru, off

    print('  %d componentes de posicao lidos' % nv)
    print()
    print('  USO DO TRILHO s16, por sub-lote:')
    ant = 1.01
    for lim, nome in ((0.98, 'no trilho    >= 98%'), (0.90, 'perigoso     90-98%'),
                      (0.75, 'apertado     75-90%'), (0.00, 'folgado       < 75%')):
        c = sum(1 for u in usos if lim <= u < ant)
        print('     %-22s %5d   %5.1f%%' % (nome, c, 100.0 * c / max(1, len(usos))))
        ant = lim
    print()
    print('  pior valor cru: %d de 32767 (%.1f%%), no sub-lote em corpo+%06X'
          % (pior, 100.0 * pior / 32767.0, pior_off))
    print()
    print('  escalas em uso:')
    for e, c in escalas.most_common(6):
        print('     %-12g %5d sub-lotes   alcance +-%.0f' % (e, c, 32767 * e))
    return 0


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    if argv[1] == '--todos':
        return todos(argv[2])
    if argv[1] == '--cidade':
        return cidade(argv[2])
    um(argv[1])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
