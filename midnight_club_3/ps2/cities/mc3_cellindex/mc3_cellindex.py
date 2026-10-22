"""mc3_cellindex.py - reconstruir o indice por celula em MapRoot+0x1C

ESTE E O CULLING DA CIDADE. Nao a esfera, nao a tile box: a tile box e so a
ENTRADA. O que o jogo percorre e uma tabela por celula, e ela vem PRONTA no
`.pck`. Trocar a geometria sem refazer a tabela deixa Los Angeles fora de todas
as listas - carrega, roda, e quase nada aparece.

Medido no `atl_la_shader.pck`, o build que entrou em jogo mostrando so o asfalto:
o indice guardava 10087 uniques e 9794 instancias (os numeros do atlanta de
varejo, intactos) enquanto as tile boxes reais pediam 18026 e 7347.

ESTRUTURA, com o objeto apontado por `MapRoot+0x1C`:

    +0x00 u32  numero de componentes unique   (651 no atlanta)
    +0x04 u32  numero de instancias           (3608)
    +0x08 ptr  u32[+0x00]  ponteiro para cada UniqueComponent
    +0x0C ptr  u32[+0x04]  ponteiro para cada Instance
    +0x10 ptr  registro[cell_count] de 12 bytes:
                 +0 s16 quantos uniques cobrem esta celula
                 +2 s16 quantas instancias cobrem
                 +4 ptr u16[n0]  indices no array de +0x08
                 +8 ptr u16[n1]  indices no array de +0x0C
    +0x14 ptr  u32[cell_count]   uma lista extra por celula (ver abaixo)

`cell_count` e `MapRoot+0x268`, e o indice da celula e `rel_z * W + rel_x` com
W em `+0x26C` - o mesmo endereco que `mcCity::CellIndexFromPos` (0x257BE8)
calcula. E POR ISSO QUE A GRADE NAO E UM PARAMETRO LIVRE: o fixup em 0x25BAE8
percorre `cell_count` registros de 12 bytes e 0x25BB40 percorre `cell_count`
ponteiros, os dois em arrays que vieram do arquivo. Aumentar `+0x268` sem
refazer os arrays faz o laco andar alem do fim - foi assim que 91x82 travou o
carregamento com um arquivo cujos arrays tinham 3968 entradas.

A REGRA FOI VALIDADA CONTRA O VAREJO, nao deduzida: reconstruindo o indice do
atlanta a partir das proprias tile boxes dele, as 3968 celulas saem IDENTICAS,
e as somas batem nas tres cidades medidas (atlanta 10087/9794, tokyo
15913/16485, detroit 14484/11308). As listas vem em ordem DECRESCENTE de indice
- 2316 de 2316 listas com mais de uma entrada.

SOBRE `+0x14`: e outra lista por celula, com indices de 14 bits mais dois bits
de flag, e nao esta decifrada (parece PVS). Aqui ela e reemitida com TODAS as
entradas nulas, que e um estado que o varejo ja exercita em 1810 das 3968
celulas do atlanta. Nulo desenha mais, nao menos - que e o lado certo pra errar
enquanto a cidade esta sendo portada.
"""
import struct
import collections


def _objeto(p):
    """(offset do objeto, [offsets dos uniques], [offsets das instancias])."""
    r = 0x80
    o = p.F(p.U(r + 0x1C))
    if not p.inside(o):
        return None
    nu, ni = struct.unpack_from('<2I', p.data, o)
    if not (0 < nu <= 20000 and 0 < ni <= 60000):
        return None
    a08, a0c = p.F(p.U(o + 8)), p.F(p.U(o + 0x0C))
    if not (p.inside(a08) and p.inside(a0c)):
        return None
    us = [p.F(p.U(a08 + 4 * k)) for k in range(nu)]
    ins = [p.F(p.U(a0c + 4 * k)) for k in range(ni)]
    return o, us, ins


def _por_celula(p, objs, w, h):
    """{indice de celula: [indices de objeto, decrescente]}."""
    m = collections.defaultdict(list)
    for i, off in enumerate(objs):
        if not p.inside(off + 0x18):
            continue
        x0, x1, z0, z1 = p.data[off + 0x14:off + 0x18]
        for z in range(max(0, z0), min(h - 1, z1) + 1):
            base = z * w
            for x in range(max(0, x0), min(w - 1, x1) + 1):
                m[base + x].append(i)
    for k in m:
        m[k].reverse()          # o varejo guarda decrescente
    return m


def confere(p):
    """(celulas iguais, total) entre o indice gravado e as tile boxes.

    Serve pros dois lados: valida a regra num arquivo de varejo e denuncia um
    indice velho num arquivo portado.
    """
    r = 0x80
    cc, w, h = struct.unpack_from('<3i', p.data, r + 0x268)
    got = _objeto(p)
    if not got:
        return 0, 0
    o, us, ins = got
    a10 = p.F(p.U(o + 0x10))
    if not p.inside(a10):
        return 0, cc
    mu, mi = _por_celula(p, us, w, h), _por_celula(p, ins, w, h)
    iguais = 0
    for k in range(cc):
        c0, c1 = struct.unpack_from('<2h', p.data, a10 + 12 * k)
        pa, pb = struct.unpack_from('<2I', p.data, a10 + 12 * k + 4)
        lidos = []
        for cnt, ptr in ((c0, pa), (c1, pb)):
            if cnt > 0 and ptr and p.inside(p.F(ptr)):
                lidos.append(list(struct.unpack_from('<%dH' % cnt, p.data, p.F(ptr))))
            else:
                lidos.append([])
        if lidos == [mu.get(k, []), mi.get(k, [])]:
            iguais += 1
    return iguais, cc


def reconstroi(p):
    """Reescreve +0x10 e +0x14 do objeto de MapRoot+0x1C. Devolve um resumo."""
    r = 0x80
    cc, w, h = struct.unpack_from('<3i', p.data, r + 0x268)
    got = _objeto(p)
    if not got or cc <= 0 or cc != w * h:
        return None
    o, us, ins = got
    mu, mi = _por_celula(p, us, w, h), _por_celula(p, ins, w, h)

    # As listas ficam logo depois dos registros, coladas e alinhadas a 2 bytes,
    # que e como o varejo as guarda (celula 51 em ...CE0 e a 52 em ...CE2).
    regs = bytearray(12 * cc)
    listas = bytearray()
    n_u = n_i = 0
    for k in range(cc):
        lu, li = mu.get(k, ()), mi.get(k, ())
        struct.pack_into('<2h', regs, 12 * k, len(lu), len(li))
        for col, seq in ((4, lu), (8, li)):
            if not seq:
                continue
            struct.pack_into('<I', regs, 12 * k + col, len(listas))   # provisorio
            listas += struct.pack('<%dH' % len(seq), *seq)
        n_u += len(lu)
        n_i += len(li)

    ptrs = bytearray(4 * cc)                 # +0x14, tudo nulo de proposito
    bloco = bytes(regs) + bytes(listas)
    if len(bloco) % 4:
        bloco += b'\0' * (4 - len(bloco) % 4)
    desloc_ptrs = len(bloco)
    bloco += bytes(ptrs)

    off = p.append(bloco)
    base_listas = off + 12 * cc
    # agora que se sabe onde caiu, os offsets provisorios viram VA
    for k in range(cc):
        c0, c1 = struct.unpack_from('<2h', p.data, off + 12 * k)
        for col, cnt in ((4, c0), (8, c1)):
            if cnt <= 0:
                continue
            rel = struct.unpack_from('<I', p.data, off + 12 * k + col)[0]
            struct.pack_into('<I', p.data, off + 12 * k + col,
                             p.V(base_listas + rel))

    struct.pack_into('<I', p.data, o + 0x10, p.V(off))
    struct.pack_into('<I', p.data, o + 0x14, p.V(off + desloc_ptrs))
    return {'celulas': cc, 'grade': (w, h), 'uniques': n_u, 'instancias': n_i,
            'bytes': len(bloco), 'ocupadas': sum(1 for k in range(cc)
                                                 if mu.get(k) or mi.get(k))}
