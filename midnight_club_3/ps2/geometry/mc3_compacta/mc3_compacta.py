"""
mc3_compacta.py - reclaim the dead geometry a hood fill leaves behind

`mc3_hood_fill.troca()` writes the replacement geometry at the END of the file
and repoints the mesh at it. Nothing moves, which is what makes the swap safe -
and the geometry that was there before stays in the file as dead weight. For one
neighbourhood that costs a few hundred kilobytes. For a whole city it nearly
doubles the file, and a city `.pck` has a size ceiling: measured in game,
12.08 MB loads and 13.88 MB hangs before the file ever reaches RAM.

So the dead bytes have to go. This does it in the narrowest way that is safe:

  * only the PACKETS of the meshes that were actually replaced are dropped, and
    their ranges are recorded from the old block list BEFORE the swap, so
    nothing is guessed and nothing unknown is discarded;
  * everything else keeps its bytes, in order;
  * every pointer is translated through a shift map.

The pointer pass is the part that has to be careful. Vertex data constantly
forms u32 that fall inside the VA window, so a blind scan would corrupt
geometry. The scan therefore SKIPS the packet regions that survive - the same
rule the rest of the toolkit uses.

    import mc3_compacta
    mortas = []
    for mesh in ...:
        mortas += mc3_compacta.pacotes_do_mesh(p, mesh)   # ANTES de trocar
    ...
    mc3_compacta.compacta(p, mortas)
"""

import struct


def _lista_de_blocos(p, mesh):
    """[(offset do pacote, tamanho)] que este mesh referencia agora.

    `mesh+0x10` aponta pra tabela de grupos: `ngrp` entradas de 8 bytes, cada
    uma `[ponteiro pra lista][u16 contagem][u16]`. Cada lista tem `contagem`
    entradas de 8 bytes `[VA do pacote][u16 qwc][u16 nv]`, e o qwc da o tamanho:
    o pacote tem `qwc * 16` bytes.
    """
    fora = []
    ngrp = struct.unpack_from('<H', p.data, mesh + 8)[0]
    if not (1 <= ngrp <= 64):
        return fora
    gt = p.F(p.U(mesh + 0x10))
    if not p.inside(gt):
        return fora
    for g in range(ngrp):
        e = gt + 8 * g
        if not p.inside(e + 8):
            break
        lista = p.F(p.U(e))
        n = struct.unpack_from('<H', p.data, e + 4)[0]
        if not p.inside(lista) or n > 4096:
            continue
        for k in range(n):
            o = lista + 8 * k
            if not p.inside(o + 8):
                break
            va, qwc, _nv = struct.unpack_from('<IHH', p.data, o)
            po = p.F(va)
            if p.inside(po) and 0 < qwc <= 4096:
                fora.append((po, qwc * 16))
    return fora


def pacotes_do_mesh(p, mesh):
    """As regioes de pacote que ficarao ORFAS ao trocar este mesh.

    Chamar ANTES da troca: depois, `mesh+0x10` ja aponta pra geometria nova e a
    antiga nao tem mais quem a nomeie.
    """
    return _lista_de_blocos(p, mesh)


def _payloads_do_mesh(p, mesh):
    """As regioes de PAYLOAD por bloco de `mesh+0x14`.

    Sao um byte por vertice, alta entropia, e formam u32 na janela de VA o tempo
    todo - a mesma armadilha dos pacotes. Sem pular estas, o scan de ponteiro
    "traduz" dado e corrompe o arquivo: no tokyo isso trocou a contagem do grupo
    de shader de 1720 para 55112.

        mesh+0x14 -> [nslot ponteiros]
          cada slot -> ngrp entradas de 8: [ptrA][ptrB]
             ptrA -> [u32 count][u32 verts por bloco] + payloads colados
             ptrB -> array de count ponteiros
    """
    fora = []
    ngrp = struct.unpack_from('<H', p.data, mesh + 8)[0]
    nslot = struct.unpack_from('<H', p.data, mesh + 0x0A)[0]
    if not (1 <= ngrp <= 64) or not (1 <= nslot <= 64):
        return fora
    t14 = p.F(p.U(mesh + 0x14))
    if not p.inside(t14):
        return fora
    for s in range(nslot):
        base = p.F(p.U(t14 + 4 * s))
        if not p.inside(base):
            continue
        for g in range(ngrp):
            e = base + 8 * g
            if not p.inside(e + 8):
                break
            for campo in (0, 4):
                a = p.F(p.U(e + campo))
                if not p.inside(a):
                    continue
                n = struct.unpack_from('<I', p.data, a)[0] if campo == 0 else 0
                if campo == 0 and 0 < n <= 4096:
                    verts = struct.unpack_from('<%dI' % n, p.data, a + 4)
                    tam = 4 + 4 * n + sum((v + 15) & ~15 for v in verts)
                    fora.append((a, tam))
                elif campo == 4:
                    fora.append((a, 4 * max(1, ngrp)))
    return fora


def _vivos(p):
    """Todas as regioes de pacote ainda referenciadas, para o scan pular."""
    hb = p.F(p.U(0x80 + 0x18))
    vivos = []
    vistos = set()

    def do_cd(cd):
        for lod in range(10):
            mp = p.U(cd + 0x3C + 4 * lod)
            m = p.F(mp)
            if p.inside(m) and m not in vistos:
                vistos.add(m)
                vivos.extend(_lista_de_blocos(p, m))
                try:
                    vivos.extend(_payloads_do_mesh(p, m))
                except Exception:
                    pass

    for h in range(p.U(0x80 + 0x14)):
        e = hb + 20 * h
        nu, au = p.U(e + 4), p.F(p.U(e + 8))
        ni, ai = p.U(e + 0x0C), p.F(p.U(e + 0x10))
        if p.inside(au):
            for k in range(nu):
                cd = p.F(p.U(au + 28 * k + 0x0C))
                if p.inside(cd):
                    do_cd(cd)
        if p.inside(ai):
            for k in range(ni):
                cd = p.F(p.U(ai + 96 * k + 0x0C))
                if p.inside(cd):
                    do_cd(cd)
    return vivos


def _funde(ranges):
    """Ordena e junta faixas que se tocam."""
    if not ranges:
        return []
    r = sorted((a, a + n) for a, n in ranges)
    saida = [list(r[0])]
    for a, b in r[1:]:
        if a <= saida[-1][1]:
            saida[-1][1] = max(saida[-1][1], b)
        else:
            saida.append([a, b])
    return [(a, b) for a, b in saida]


def compacta(p, mortas, base_va=0x06800000):
    """Remove as faixas mortas e conserta todos os ponteiros. Devolve (antes, depois)."""
    antes = len(p.data)
    mortas = [(a, n) for a, n in mortas if a >= 0x80 and n > 0]
    faixas = _funde(mortas)
    if not faixas:
        return antes, antes

    # nao remover nada que ainda esteja referenciado
    vivos = set()
    for a, n in _vivos(p):
        vivos.add(a)
    faixas = [(a, b) for a, b in faixas if a not in vivos]
    if not faixas:
        return antes, antes

    # mapa de deslocamento: quantos bytes desaparecem antes de cada offset
    inicios = [a for a, _b in faixas]
    acum = []
    t = 0
    for a, b in faixas:
        acum.append(t)
        t += b - a

    import bisect

    def novo(off):
        i = bisect.bisect_right(inicios, off) - 1
        if i < 0:
            return off
        a, b = faixas[i]
        if off < b:                      # dentro de uma faixa morta
            return None
        return off - (acum[i] + (b - a))

    # o scan de ponteiro pula os pacotes vivos: dado de vertice forma u32 que
    # cai na janela de VA e um scan cego corromperia a geometria
    pular = _funde(_vivos(p))
    ini_p = [a for a, _b in pular]

    def em_pacote(off):
        i = bisect.bisect_right(ini_p, off) - 1
        return i >= 0 and off < pular[i][1]

    lim = base_va + antes
    d = p.data
    corrigidos = perdidos = 0
    for off in range(0x80, antes - 4, 4):
        if em_pacote(off):
            continue
        v = struct.unpack_from('<I', d, off)[0]
        if not (base_va <= v < lim):
            continue
        alvo = v - base_va + 0x80
        n = novo(alvo)
        if n is None:
            perdidos += 1
            continue
        struct.pack_into('<I', d, off, n - 0x80 + base_va)
        corrigidos += 1

    # remove de tras pra frente para nao invalidar os offsets
    for a, b in reversed(faixas):
        del d[a:b]

    struct.pack_into('<I', d, 0x0C, len(d) - 0x80)
    return antes, len(d), corrigidos, perdidos


def regiao_do_mesh(p, mesh):
    """TODO o espaco que este mesh ocupa hoje, em faixas fundidas.

    `emit_mesh_region` grava a substituicao como UMA regiao contigua - tabelas,
    listas, pacotes e payloads juntos - e pede esse tamanho de uma vez. Liberar
    so os pacotes nao adianta, porque cada um sozinho e menor que a regiao nova:
    o pool tinha 5.25 MB e devolvia 0.6 MB de arquivo. Fundindo tudo o que o
    mesh ocupa, a faixa livre passa a ter a ordem de grandeza certa.

    Entram: a tabela de grupos, as listas de bloco, os pacotes, o array de
    ponteiros de `+0x14`, as entradas por grupo e os payloads por bloco.
    """
    fora = list(_lista_de_blocos(p, mesh))
    try:
        fora += _payloads_do_mesh(p, mesh)
    except Exception:
        pass
    ngrp = struct.unpack_from('<H', p.data, mesh + 8)[0]
    nslot = struct.unpack_from('<H', p.data, mesh + 0x0A)[0]
    if 1 <= ngrp <= 64:
        gt = p.F(p.U(mesh + 0x10))
        if p.inside(gt):
            fora.append((gt, 8 * ngrp))
            for g in range(ngrp):
                e = gt + 8 * g
                if not p.inside(e + 8):
                    break
                lista = p.F(p.U(e))
                n = struct.unpack_from('<H', p.data, e + 4)[0]
                if p.inside(lista) and n <= 4096:
                    fora.append((lista, 8 * n))
        if 1 <= nslot <= 64:
            t14 = p.F(p.U(mesh + 0x14))
            if p.inside(t14):
                fora.append((t14, 4 * nslot))
                for s in range(nslot):
                    base = p.F(p.U(t14 + 4 * s))
                    if p.inside(base):
                        fora.append((base, 8 * ngrp))
    return [(a, b - a) for a, b in _funde(fora)]
