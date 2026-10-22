"""
mc3_hood_fill.py - replace every unique mesh of ONE hood of an MC3 PS2 city

Step towards importing a whole neighbourhood. A city is seven hoods and the hood
table hangs off MapRoot+0x14 (count) and +0x18 (pointer); each 20-byte entry is

    +00 -> a 176-byte record whose first bytes are the hood NAME, inline
    +04  unique count      +08 -> unique component array (28 bytes each)
    +0C  instance count    +10 -> instance array (96 bytes each)

and the name matches the prefix on that hood's meshes exactly. In atlanta:

    hood 0 bh (51 uniq)   1 dt (183)   2 fwy (75)   3 lf (90)
    hood 4 mt (155)       5 ug (43)    6 we (54)

`ug` is the smallest and it is underground, so a failed experiment does not
disturb anything the player can see. That is the one to start with.

Every replacement reuses `mc2_to_mc3.py`: nothing already in the file moves, the
new geometry and block tables are APPENDED and only the target mesh's two
pointers are rewritten. The group COUNT of each mesh is preserved - the material
table carries one shader index per group, and collapsing the groups makes the
game read past the end of it and hang.

Do this in steps and boot between them. `--limite N` stops after N meshes, so a
black screen can be bisected instead of guessed at: the loader fails silently and
the main thread spins on a `while(1);` left over from a stripped assert, which
looks exactly like a frozen emulator.

    python mc3_hood_fill.py CIDADE.pck --hood ug --xmod M.xmod --limite 1 --saida out.pck
    python mc3_hood_fill.py CIDADE.pck --hood ug --xmod M.xmod --saida out.pck
"""

import argparse
import importlib.util
import io
import os
import struct
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))
_SPEC = importlib.util.spec_from_file_location(
    'mc2_to_mc3', os.path.join(_AQUI, 'experimental', 'mc2_to_mc3.py'))
mc2 = importlib.util.module_from_spec(_SPEC)
sys.modules['mc2_to_mc3'] = mc2
_SPEC.loader.exec_module(mc2)
_VP_SPEC = importlib.util.spec_from_file_location(
    'mc3_vifpos', os.path.join(_AQUI, 'mc3_vifpos.py'))
vifpos = importlib.util.module_from_spec(_VP_SPEC)
_VP_SPEC.loader.exec_module(vifpos)


def hoods(p):
    """[(name, uniq_count, uniq_array, inst_count, inst_array)] in file order."""
    nh, hp = p.U(0x80 + 0x14), p.U(0x80 + 0x18)
    hb = p.F(hp)
    out = []
    for h in range(nh):
        e = hb + 20 * h
        rec = p.F(p.U(e))
        nome = bytes(p.data[rec:rec + 32]).split(b'\0')[0].decode('latin1', 'ignore')
        out.append((nome,) + struct.unpack_from('<4I', p.data, e + 4))
    return out


def uniques_do_hood(p, idx):
    """[(name, model_offset)] of the meshes owned by that hood's unique array.

    The unique components are the hood's OWN geometry; the instance array is
    mostly `a_inst_*` props shared with every other hood, so filling those would
    change the whole city instead of one neighbourhood.
    """
    _nome, nu, au, _ni, _ai = hoods(p)[idx]
    if not p.inside(p.F(au)):        # inside() takes a FILE offset, not a VA
        return []
    ab = p.F(au)
    out, visto = [], set()
    for k in range(nu):
        comp = ab + 28 * k
        dp = p.U(comp + 0x0C)
        if not p.inside(p.F(dp)):
            continue
        cd = p.F(dp)
        nm = bytes(p.data[cd + 0x70:cd + 0xB0]).split(b'\0')[0].decode('latin1', 'ignore')
        # Go to the mesh through the component, NOT by name. The name here
        # carries a `#geomN` suffix (`a_ug_underground_01x#geom1`) while the
        # model object stores it without one, so a name lookup finds nothing.
        #
        # And read ALL TEN slots of `buffers[2][5]` at +0x3C, not just the first.
        # They hold the LOD variants and they are separate meshes: of the 43
        # unique components of atlanta's `ug`, 20 have more than one slot filled
        # (13 have two, 6 have three, one has five), and some - `#geom23`,
        # `#geom28` - have NOTHING in slot 0. Replacing only slot 0 leaves those
        # components completely untouched and leaves every other component's
        # distant LOD showing the ORIGINAL geometry at the ORIGINAL place, which
        # in game looks like pieces of the old location following you around.
        meshes = []
        for slot in range(10):
            mp = p.U(cd + 0x3C + 4 * slot)
            if not p.inside(p.F(mp)):
                continue
            mesh = p.F(mp)
            if mesh not in visto:
                visto.add(mesh)
                meshes.append(mesh)
        if meshes:
            out.append((nm or 'comp@%06X' % comp, meshes, comp, cd))
    return out


def le_hood_mc2(path):
    """[(name, emin, emax)] of the unique components of an MC2 .hood.

    The file is plain text and the parser in the game (`sub_5248D0` of the
    unprotected `testapp.exe`, the twin of the packed `mc2.exe`) reads exactly
    three things per unique component: `name:`, `emin`, `emax`. No parent, no
    transform, no chain - so there IS no hierarchy, and the geometry is already
    in world coordinates. Verified: the wfargo .xmod spans 640.000..800.000 in x,
    byte for byte the emin/emax the .hood declares.

    That is what makes a coherent port possible: the models already know where
    they stand relative to each other, so the whole set can move as one rigid
    block instead of each mesh being placed on its own.
    """
    out = []
    atual = None
    with io.open(path, encoding='latin1') as f:
        for line in f:
            t = line.split()
            if not t:
                continue
            if t[0] == 'unique_component':
                atual = {}
            elif atual is None:
                continue
            elif t[0] == 'name:' and len(t) >= 2:
                atual['name'] = t[1]
            elif t[0] in ('emin', 'emax') and len(t) >= 4:
                atual[t[0]] = tuple(float(x) for x in t[1:4])
            elif t[0] == '}':
                if atual.get('name') and 'emin' in atual and 'emax' in atual:
                    out.append((atual['name'], atual['emin'], atual['emax']))
                atual = None
    return out


def le_cc(nome, pasta):
    """The component's `.cc` manifest: (passes of lod 0, bounding sphere).

    Next to every `.xmod` sits a small ASCII manifest that says which passes each
    LOD actually draws, plus the sphere in world coordinates:

        inst_cpv: 1
        bounding_sphere: 720.000000 97.649986 122.500000 136.610764
        lod 0 {
            main
            refl
        }
        lod 1 {
        }

    This is the authority on what a component is made of. Guessing `_main` works
    for buildings and silently loses every road: `l_downtown_rd_01` has no main
    at all, its lod 0 is `refl` alone, because in MC2 the road IS the reflective
    surface. Nine of downtown's thirty-four components are roads and junctions.
    """
    p = os.path.join(pasta, nome + '.cc')
    if not os.path.isfile(p):
        return None, None
    passes, esfera, dentro = [], None, False
    for linha in io.open(p, encoding='latin1'):
        t = linha.strip()
        if t.startswith('bounding_sphere:'):
            try:
                esfera = tuple(float(x) for x in t.split(':', 1)[1].split())
            except ValueError:
                pass
        elif t.startswith('lod '):
            dentro = t.split()[1] == '0'
        elif t.startswith('}'):
            dentro = False
        elif dentro and t and t != '{':
            passes.append(t)
    return passes, esfera


def xmod_de(nome, pasta):
    """The .xmod that holds a .hood component's geometry, or None.

    The .hood names it `l_downtown_rd_38_x#geom` while the file on disk is
    `l_downtown_rd_38_x#geom_0_main.xmod`. Which suffix carries the geometry is
    not fixed - the `.cc` manifest decides - so ask it first and only fall back
    to the `_main` guess when there is no manifest.
    """
    passes, _esf = le_cc(nome, pasta)
    for nome_passe in (passes or ()):
        for i in range(3):
            p = os.path.join(pasta, '%s_%d_%s.xmod' % (nome, i, nome_passe))
            if os.path.isfile(p):
                return p
    # O export do MC2 usa `.mod` e o do MC3 `.xmod`, mesmo formato de texto
    # (o proprio log registra que o leitor do jogo e o mesmo). Aceitar os dois.
    for suf in ('_0_main.xmod', '_1_main.xmod', '_2_main.xmod',
                '_0_main.mod', '_1_main.mod', '_2_main.mod'):
        p = os.path.join(pasta, nome + suf)
        if os.path.isfile(p):
            return p
    return None


def raio_xmod(path):
    """Bounding radius of an .xmod, read cheaply.

    Only the `v` lines are parsed - no adjuncts, no strips. Converting all 815
    models of the MC2 city just to measure them takes minutes; this takes a
    second, and the full conversion then runs on the handful actually chosen.
    """
    lo = [1e30, 1e30, 1e30]
    hi = [-1e30, -1e30, -1e30]
    with io.open(path, encoding='latin1') as f:
        for line in f:
            # the lines are indented, so match the TOKEN and not the raw prefix
            q = line.split()
            if q and q[0] == 'v' and len(q) >= 4:
                try:
                    v = (float(q[1]), float(q[2]), float(q[3]))
                except ValueError:
                    continue
                for a in range(3):
                    lo[a] = min(lo[a], v[a])
                    hi[a] = max(hi[a], v[a])
    if lo[0] > hi[0]:
        return 0.0
    # Measure from the SAME anchor the converter uses - centre in x/z, base in
    # y - or the number is not comparable with what comes out the other end.
    # Measuring from the model's own origin made a 164-radius target get a model
    # that converted to 94.
    anc = ((lo[0] + hi[0]) / 2.0, lo[1], (lo[2] + hi[2]) / 2.0)
    return max(((x - anc[0]) ** 2 + (y - anc[1]) ** 2 + (z - anc[2]) ** 2) ** 0.5
               for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2]))


def catalogo(pasta):
    """[(radius, path)] of the `_main` models, sorted by radius.

    `_refl` and `_emissive` are companion passes of the same object, not
    standalone geometry, so only `_main` is offered.
    """
    out = []
    for f in sorted(os.listdir(pasta)):
        if f.endswith(('.xmod', '.mod')) and '_main' in f:
            r = raio_xmod(os.path.join(pasta, f))
            if r > 0.1:
                out.append((r, os.path.join(pasta, f)))
    out.sort()
    return out


def caixa_de_celulas(grid, xw, zw, raio):
    """Os 4 bytes da tile box, presos DENTRO da grade que o arquivo declara.

    Prender em 0..255 nao basta, e essa foi a diferenca entre "some as vezes" e
    "some sempre". `mcCity::CellIndexFromPos` (0x257BE8) devolve -1 para
    qualquer celula com `rel_x < 0`, `rel_x >= MapRoot+0x26C`, `rel_z < 0` ou
    `rel_z >= MapRoot+0x270`, e quem chama - `CellGrid::Insert` (0x259658) -
    volta sem inserir. Fora da grade nao e culling agressivo: e invisivel, sem
    crash e sem aviso.

    O varejo nunca cai nesse caso. Medido no atlanta, tokyo e detroit, W e H
    saem exatamente dos extents e ZERO objetos tem tile box fora deles. Um
    objeto que escape por pouco fica melhor preso na borda do que perdido.
    """
    cx, ox, cz, oz = grid[:4]
    w = (grid[4] if len(grid) > 4 and grid[4] else 256)
    h = (grid[5] if len(grid) > 5 and grid[5] else 256)

    def faixa(v0, v1, base, passo, n):
        a = int((v0 - base) // passo)
        b = int((v1 - base) // passo)
        return max(0, min(n - 1, a)), max(0, min(n - 1, b))

    x0, x1 = faixa(xw - raio, xw + raio, ox, cx, w)
    z0, z1 = faixa(zw - raio, zw + raio, oz, cz, h)
    return bytes((x0, x1, z0, z1))


def reposiciona(p, comp, cd, raio, grid):
    """Resize the culling of a unique component after its geometry changed.

    A unique component has no transform - it is 28 bytes - and what places it is
    the bound sphere on its ComponentData: **+0x2C is the centre in WORLD
    coordinates and +0x38 the radius**, while the vertices themselves are local
    and centred on the origin. Verified on atlanta's `ug` hood: geom1 sits at
    (-324.74, 32.84, 783.94) with radius 52.45, and 52.45 is exactly the extent
    of its own local vertices.

    The centre is left ALONE - that is the placement, and the point of a hood
    fill is to change what is drawn, not where. Only the radius and the tile box
    move, and they have to: a tunnel piece is 52 units across, a replacement
    building is 195 tall, and leaving the old radius means the culling drops it
    before the camera ever gets close. That is why the first fill loaded
    perfectly and showed nothing.
    """
    cxw, cyw, czw = struct.unpack_from('<3f', p.data, cd + 0x2C)
    struct.pack_into('<f', p.data, cd + 0x38, raio)      # ComponentData radius
    struct.pack_into('<f', p.data, comp + 0x18, raio)    # the component's own
    if grid:
        p.data[comp + 0x14:comp + 0x18] = caixa_de_celulas(grid, cxw, czw, raio)
    return (cxw, cyw, czw)


def aabb_local(p, mesh):
    """(lo, hi) from the packet header-selected VIF position stream."""
    ngrp = struct.unpack_from('<H', p.data, mesh + 8)[0]
    if not p.inside(p.F(p.U(mesh + 0x10))):
        return None
    gt = p.F(p.U(mesh + 0x10))
    lo = [1e30, 1e30, 1e30]
    hi = [-1e30, -1e30, -1e30]
    for gi in range(ngrp):
        lp, cnt, _ = struct.unpack_from('<IHH', p.data, gt + 8 * gi)
        if not p.inside(p.F(lp)) or cnt > 4096:
            break
        for bi in range(cnt):
            bp, qw, nv = struct.unpack_from('<IHH', p.data, p.F(lp) + 8 * bi)
            if not p.inside(p.F(bp)) or not (3 <= nv <= 256):
                continue
            b = p.F(bp)
            try:
                pts = vifpos.decode_positions(bytes(p.data[b:b + 16 * qw]))
            except ValueError:
                continue
            if len(pts) != nv:
                continue
            for xyz in pts:
                for a, v in enumerate(xyz):
                    lo[a] = min(lo[a], v)
                    hi[a] = max(hi[a], v)
    return (lo, hi) if lo[0] < hi[0] else None


def centra_na_origem(blocos):
    """Re-anchor the model on its own AABB centre, and say where that centre was.

    This sidesteps an ambiguity instead of resolving it. `cd+0x2C` is either the
    translation of the model origin (A) or the centre of the bound sphere (B),
    and the two readings differ by exactly the local AABB centre. Vanilla city
    meshes are mostly built centred on their own origin, which is why both
    readings fit the stock data equally well - a tile-box test over all 479
    unique meshes scores A at 2.65 units of error and B at 2.43, far too close to
    call.

    Centre the imported model the same way and the local centre becomes zero, so
    A and B COINCIDE and the question stops mattering. It also removes the big
    error: anchoring base-at-y=0, as the converter does, puts the local centre at
    half the model height - 97 units on the wfargo tower - and that is what one
    of the two readings would be off by.
    """
    pts = [c for pos, _u, _nr, _o in blocos for c in pos]
    lo = [min(q[a] for q in pts) for a in range(3)]
    hi = [max(q[a] for q in pts) for a in range(3)]
    cen = [(lo[a] + hi[a]) / 2.0 for a in range(3)]
    fora = [([(q[0] - cen[0], q[1] - cen[1], q[2] - cen[2]) for q in pos], u, nr, o)
            for pos, u, nr, o in blocos]
    return fora, cen


def alinha(blocos, alvo):
    """Shift the new geometry onto the footprint the old geometry occupied.

    `cd+0x2C` is where the model's ORIGIN goes - confirmed because the stored
    radius matches the distance from the origin to the furthest vertex, not from
    the local AABB centre (geom21: radius 90.3, origin 90.3, centre 80.0). But
    the old geometry was not centred on that origin: `#geom22` sits 81 units away
    in z and `#geom24` 45 in x. The converter anchors the imported model centred
    in x/z with its base at y=0, so dropping it in unshifted lands it on the old
    ORIGIN instead of where the old building actually stood - off by up to about
    fifty units, which is what shows up in game as "close but not right".

    So the new model is moved to put its footprint centre over the old footprint
    centre, and its base at the old base.
    """
    lo, hi = alvo
    dx = (lo[0] + hi[0]) / 2.0
    dy = lo[1]
    dz = (lo[2] + hi[2]) / 2.0
    if abs(dx) < 0.05 and abs(dy) < 0.05 and abs(dz) < 0.05:
        return blocos, (0.0, 0.0, 0.0)
    fora = [([(q[0] + dx, q[1] + dy, q[2] + dz) for q in pos], u, nr, o)
            for pos, u, nr, o in blocos]
    return fora, (dx, dy, dz)


def recentra_esfera(p, cd, alvo_antigo, novo_lo, novo_hi):
    """Rewrite cd+0x2C under the OTHER reading of what that field means.

    Two readings survive the evidence and they disagree once the geometry is
    replaced:

    A. `cd+0x2C` is the TRANSLATION of the model origin. Then replacing geometry
       needs no change there, and the new model just has to be shifted onto the
       old footprint - that is what `alinha()` does.
    B. `cd+0x2C` is the CENTRE OF THE BOUND SPHERE, i.e. translation plus the
       local AABB centre. Then it has to be rewritten whenever the geometry
       changes shape, or the object is drawn off by the difference between the
       old and new local centres.

    They are indistinguishable on stock data because most city meshes are built
    centred on their own origin, so the two coincide. The radius almost decides
    it - it matches the distance from the ORIGIN on most meshes, which argues for
    A - but not on all of them (`#geom22` stores 148 against 133 from the origin,
    `a_bh_blk_04x#geom` stores 108 against 73), so it is not conclusive.

    Under B: translation = old_centre - old_local_centre, and the new centre is
    that translation plus the new local centre.
    """
    lo, hi = alvo_antigo
    velho_cen = [(lo[a] + hi[a]) / 2.0 for a in range(3)]
    novo_cen = [(novo_lo[a] + novo_hi[a]) / 2.0 for a in range(3)]
    c = list(struct.unpack_from('<3f', p.data, cd + 0x2C))
    novo = [c[a] - velho_cen[a] + novo_cen[a] for a in range(3)]
    struct.pack_into('<3f', p.data, cd + 0x2C, *novo)
    return tuple(novo[a] - c[a] for a in range(3))


def uniformiza_material(p, mesh, indice):
    """Point every group of a mesh at ONE material index.

    Not the same thing as "an untextured shader", and that distinction matters:
    there is no untextured shader to point at. The city names only four -
    road_reflector, water, city_specular and moon - and across every .pck the
    whole vocabulary is 24 names, none of them flat/unlit/vertex-colour; ordinary
    city geometry goes through an unnamed default path, and the named ones are
    MORE specialised, not less.

    What this does instead is make the look uniform. A replaced mesh inherits the
    original's per-group material list, so a 13-group tunnel piece renders the
    imported model in 13 different materials at once, which is unreadable.
    Forcing one index - combined with a constant UV - gives one material and one
    texel everywhere, which is flat enough to judge shape by.

    The index must be one the file already uses. 3 is the most common in
    atlanta's own geometry (109 groups), so it is a safe pick.
    """
    ngrp = struct.unpack_from('<H', p.data, mesh + 8)[0]
    mt = p.U(mesh + 0x0C)
    if not p.inside(p.F(mt)):
        return 0
    mo = p.F(mt)
    for gi in range(ngrp):
        struct.pack_into('<H', p.data, mo + 2 * gi, indice)
    return ngrp


def troca(p, mesh, blocos):
    """Swap one mesh's geometry. Returns (blocks written, groups) or None.

    A geometria nova e APENDADA e o mesh e reapontado - nada se move, que e o
    que torna a troca segura. O preco e que a antiga fica no arquivo. As faixas
    dela sao anotadas em `p._mortas` ANTES da troca, para o mc3_compacta poder
    devolver esses bytes depois; sem isso, portar a cidade inteira quase dobra o
    arquivo e estoura o teto de tamanho do .pck de cidade.
    """
    ngrp = struct.unpack_from('<H', p.data, mesh + 8)[0]
    if not (1 <= ngrp <= 64):
        return None
    # as faixas do que este mesh ja tinha viram espaco LIVRE para os proximos.
    # Nada e liberado antes da propria troca ler o payload de exemplo em +0x14.
    # A REGIAO INTEIRA do mesh (tabelas, listas, pacotes e payloads) vira
    # espaco livre para os PROXIMOS - nunca antes da propria troca, porque o
    # emit_mesh_region le a amostra de payload da cadeia de +0x14 deste mesmo
    # mesh. Liberar so os pacotes nao serve: o emit pede UMA regiao contigua do
    # tamanho todo, e pacote solto e sempre menor que ela.
    mortas = []
    try:
        import mc3_compacta
        mortas = mc3_compacta.regiao_do_mesh(p, mesh)
    except Exception:
        pass
    n, r = divmod(len(blocos), ngrp)
    corte, k = [], 0
    for i in range(ngrp):
        m = max(1, n + (1 if i < r else 0))
        corte.append(blocos[k:k + m] or [blocos[0]])
        k += m
    if k < len(blocos):
        corte[-1] += blocos[k:]
    sc = mc2.pick_scale([b for g in corte for b in g])
    blobs = [[mc2.make_block(pos, uv, nr, sc, j % 2 == 1)
              for j, (pos, uv, nr, _o) in enumerate(g)] for g in corte]
    grp_at, t14_at = mc2.emit_mesh_region(p, mesh, corte, blobs)
    # REAPROVEITAMENTO DE ESPACO DESLIGADO. As faixas que `regiao_do_mesh`
    # devolve nao sao confiaveis: alguma delas engole estrutura viva, e o
    # alocador escreve por cima. O sintoma foi mesh com `+0x08` valendo 0xCDCD
    # (52685 "grupos") e tabela de material apontando pra fora do arquivo - ou
    # seja, objeto de mesh sobrescrito por padding.
    #
    # O ganho era pequeno de qualquer jeito (13.88 -> 13.02 MB); o que resolve o
    # tamanho e nao escrever a peca inteira em todos os slots de LOD.
    if False and mortas:
        if not hasattr(p, 'livres'):
            p.livres = []
        p.livres += mortas
        p.livres.sort(key=lambda x: -x[1])
    struct.pack_into('<I', p.data, mesh + mc2.MESH_BLOCKS, p.V(grp_at))
    struct.pack_into('<I', p.data, mesh + mc2.MESH_PERBLOCK, p.V(t14_at))
    return sum(len(g) for g in corte), ngrp


CATEGORIAS = ('rua', 'predio', 'muro', 'vegetacao', 'poste', 'interior', 'outro')


def categoria(nome):
    """A que tipo de superficie um nome de mesh pertence.

    Os dois jogos nomeiam a cidade da mesma familia de jeitos (`_rd_`, `fwy`,
    `blk`, `_inst_alpha_`, `wall`), entao a mesma regra classifica o nome de
    origem do MC2 e o de destino do MC3 - que e o que permite MEDIR no destino
    qual indice cada categoria usa em vez de escolher no palpite.
    """
    n = nome.lower()
    # NAO "CONSERTAR" ESTA REGRA SEM LER O QUE VEM ABAIXO.
    #
    # Los Angeles nomeia os cruzamentos `l_inst_2lane_3wayint_g_x`, e o teste
    # `int_` casa dentro de "3wayint_g", entao 97 pedacos de asfalto caem em
    # 'interior'. Isso e feio e eu tentei arrumar - mandando lane/wayint pra
    # 'rua' e exigindo `_int_` em interior. O jogo travou no loading.
    #
    # O motivo e indireto e vale guardar: com os cruzamentos fora, a categoria
    # 'interior' fica quase sem malha nenhuma, perde o indice dominante dela
    # (154) e cai num indice sobrando - saiu 0. Ai `completa_slots_semanticos`
    # foi clonar shader para dentro dos 7 slots 0 nulos, e o slot 0 e da classe
    # INSTANCE, que o clonador copia com 16 bytes. Loading infinito.
    #
    # A classificacao errada e cosmetica: cruzamento com material de interior
    # continua desenhando. O caminho de shader nao perdoa. Se um dia isso for
    # mexido, medir ANTES o conjunto de lacunas com /tmp/cmp.py e conferir que
    # nenhuma classe nova entrou.
    if '_rd_' in n or 'fwy' in n or 'road' in n or 'ramp' in n:
        return 'rua'
    if 'wall' in n or 'fence' in n or 'barrier' in n or 'irongate' in n:
        return 'muro'
    if ('alpha' in n or 'tree' in n or 'bush' in n or 'shrub' in n
            or 'palm' in n or 'planter' in n):
        return 'vegetacao'
    if ('light' in n or 'lamp' in n or 'pole' in n or 'sign' in n
            or 'meter' in n or 'hydrant' in n):
        return 'poste'
    if 'blk' in n or 'bld' in n or 'building' in n or 'house' in n:
        return 'predio'
    if 'int_' in n or 'interior' in n:
        return 'interior'
    return 'outro'


def slots_seguros(p):
    """Indices de material preenchidos em TODOS os grupos de shader.

    `rmcModel::FixupShaders` (0x2A8A18) desreferencia `array[indice]` e chama o
    virtual de +24 sem checar nulo. Um slot vazio no grupo que for usado leva a
    chamada em ponteiro nulo - foi o que travou quando eu escolhi o indice 1002,
    que no atlanta existe em 2 dos 18 grupos.

    O varejo NAO segue essa regra - 1041 dos 1046 indices que o atlanta usa
    estao vazios em algum grupo -, porque a malha original participa so dos
    passes onde seu material existe. Como aqui o material e trocado por baixo, a
    unica escolha comprovadamente segura e a que vale em qualquer grupo. Sao 5
    no atlanta (1, 150, 631, 684, 685) e 15 no tokyo.
    """
    r = 0x80
    ng = p.U(r + 8)
    base = p.F(p.U(r + 0x0C))
    if not ng or not p.inside(base):
        return []
    n0 = struct.unpack_from('<H', p.data, base + 8)[0]
    cheio = [0] * n0
    for g in range(ng):
        dados = p.F(p.U(base + 16 * g + 4))
        if not p.inside(dados):
            continue
        for i in range(n0):
            if p.U(dados + 4 * i):
                cheio[i] += 1
    return [i for i, c in enumerate(cheio) if c == ng]


def materiais_por_categoria(p, somente_seguros=True):
    """{categoria: indice de material}, medido no destino.

    Cada categoria fica com o indice que o destino mais usa naquela categoria
    ENTRE OS QUE EXISTEM EM TODOS OS GRUPOS, por padrao. `somente_seguros=False`
    recupera a preferencia semantica original do varejo; ela e usada por
    `completa_slots_semanticos` para saber QUAIS lacunas vale a pena preencher.

    Com poucos slots seguros varias categorias acabam compartilhando indice -
    no atlanta sao 5 - e isso e melhor do que um indice unico para a cidade toda
    e muito melhor do que um indice que trava.
    """
    import collections
    permitidos = set(slots_seguros(p)) if somente_seguros else None
    tab = collections.defaultdict(collections.Counter)

    def conta(nome, meshes):
        c = categoria(nome)
        for m in meshes:
            n = struct.unpack_from('<H', p.data, m + 8)[0]
            mt = p.F(p.U(m + 0x0C))
            if not p.inside(mt):
                continue
            for k in range(n):
                v = struct.unpack_from('<H', p.data, mt + 2 * k)[0]
                if permitidos is None or v in permitidos:
                    tab[c][v] += 1

    for i in range(len(hoods(p))):
        for nm, meshes, _c, _cd in uniques_do_hood(p, i):
            conta(nm, meshes)
    _slots, tipos = tipos_de_instancia(p)
    for _va, (nm, _cd, meshes) in tipos.items():
        conta(nm, meshes)

    candidatos = (permitidos if permitidos is not None else
                  set(v for c in tab.values() for v in c))
    if not candidatos:
        return {}
    geral = collections.Counter()
    for c in tab:
        geral.update(tab[c])
    padrao = geral.most_common(1)[0][0] if geral else sorted(seguros)[0]

    # Categoria diferente, indice diferente sempre que houver slot seguro
    # sobrando: no atlanta ha 5, e usa-los todos separa rua, predio, muro,
    # vegetacao e poste na tela. Sem isso as categorias sem indice dominante
    # proprio caem todas no mesmo numero e a cidade volta a ser um bloco so.
    fora = {}
    usados = set()
    for c in CATEGORIAS:
        for v, _n in tab[c].most_common():
            if v not in usados:
                fora[c] = v
                usados.add(v)
                break
    # CATEGORIA SEM MEDICAO NAO GANHA INDICE INVENTADO QUANDO O RESULTADO VAI
    # GUIAR CLONAGEM DE SHADER.
    #
    # Com `somente_seguros=True` isto e a tabela final: toda categoria precisa
    # de ALGUM indice, entao sobra vale. Com `somente_seguros=False` quem
    # chama e `completa_slots_semanticos`, que vai CLONAR shader para dentro
    # dos slots nulos do indice devolvido - e um indice tirado da sobra nao
    # representa nada. Foi assim que 'interior' virou 0, o clonador foi
    # preencher 7 slots 0 da classe INSTANCE com 16 bytes, e o loading travou.
    if somente_seguros:
        livres = [v for v in sorted(candidatos) if v not in usados]
        for c in CATEGORIAS:
            if c in fora:
                continue
            fora[c] = livres.pop(0) if livres else padrao
    return fora


# Tokens logicos do perfil Atlanta. O Tokyo usa os mesmos tokens com +0x488.
_VT_BASIC = 0x007A1EF8
_VT_NAMED = 0x007A1F58
_VT_INSTANCE = 0x007A1FC8
_VT_TEXTURE_NODE = 0x007A20E0
_VT_TEXTURE_INFO = 0x007A2320
_VT_OWNER_16 = 0x007B2318
_VT_OWNER_17 = 0x007B22B8
_SHADER_TOKENS = {_VT_BASIC, _VT_NAMED, _VT_INSTANCE,
                  _VT_OWNER_16, _VT_OWNER_17,
                  _VT_TEXTURE_NODE, _VT_TEXTURE_INFO}


def _token_shader(v):
    """Normaliza um token Atlanta/Tokyo para o valor logico Atlanta."""
    for desloca in (0, 0x488):
        if v - desloca in _SHADER_TOKENS:
            return v - desloca
    return None


def _tamanho_shader_clonavel(p, src):
    """Bytes pertencentes ao shader, incluindo recursos inline alcancaveis.

    Nao se pode copiar um tamanho fixo. `rmcShaderBasic` pode ser so um header
    de 12 bytes apontando para fora ou 0xB0 bytes com TextureInfo inline. O
    owner-placed 17 usado pelo material 154 do Atlanta tem header, TextureInfo
    de 0xA0 e TextureNode de 0x10, totalizando 0xD0. Copiar apenas os 0x40 bytes
    da classe deixa o ponteiro interno mirando dados que nao foram clonados.
    """
    if not p.inside(src + 8):
        raise ValueError('shader fora do arquivo em %#x' % src)
    vt = _token_shader(p.U(src))
    sub = p.F(p.U(src + 8))
    delta = sub - src if p.inside(sub) else None
    if vt == _VT_BASIC:
        tamanho = 0xB0 if delta == 0x10 else 0x0C
    elif vt == _VT_INSTANCE:
        tamanho = 0x20 if delta == 0x10 else 0x30 if delta == 0x20 else 0x10
    elif vt in (_VT_OWNER_16, _VT_OWNER_17):
        tamanho = 0x40
        # Estes dois campos sao os donos dos recursos inline dessa familia.
        # Recursos externos continuam compartilhados e nao entram na copia.
        for rel in (8, 0x0C):
            alvo = p.F(p.U(src + rel))
            if not p.inside(alvo) or not src <= alvo < src + 0x400:
                continue
            tipo = _token_shader(p.U(alvo))
            if tipo == _VT_TEXTURE_INFO:
                tamanho = max(tamanho, alvo - src + 0xA0)
            elif tipo == _VT_TEXTURE_NODE:
                tamanho = max(tamanho, alvo - src + 0x10)
    elif vt == _VT_NAMED:
        tamanho = 0x30
    else:
        raise ValueError('classe de shader desconhecida em %#x: %#x'
                         % (src, p.U(src)))
    if src + tamanho > len(p.data):
        raise ValueError('shader truncado em %#x (tamanho %#x)' % (src, tamanho))
    return tamanho


def _clona_shader(p, src):
    """Copia um shader retail e reloca somente seus ponteiros internos."""
    tamanho = _tamanho_shader_clonavel(p, src)
    dst = p.append(bytes(p.data[src:src + tamanho]), 16)
    for rel in range(0, tamanho, 4):
        valor = p.U(dst + rel)
        alvo = p.F(valor)
        if src <= alvo < src + tamanho:
            struct.pack_into('<I', p.data, dst + rel,
                             p.V(dst + (alvo - src)))
    return dst, tamanho


def completa_slots_semanticos(p):
    """Torna seguros os materiais preferidos de TODAS as sete categorias.

    Primeiro mede a escolha semantica no arquivo ainda retail, sem filtrar os
    slots nulos. Para cada indice escolhido, preserva todo shader que ja existe
    e preenche somente os grupos ausentes com uma COPIA INDEPENDENTE do shader
    retail mais proximo do mesmo indice. Nao ha alias de ponteiro entre slots,
    nao se move nenhum byte existente e o crescimento e de poucos KiB.

    No Atlanta isso completa 30 lacunas / 5344 bytes, leva os slots universais
    de 5 para 11 e libera exatamente:
      rua=164, predio=1, muro=698, vegetacao=45,
      poste=1002, interior=154, outro=3.
    """
    escolhidos = materiais_por_categoria(p, somente_seguros=False)
    if not escolhidos:
        return {}
    antes = set(slots_seguros(p))
    r = 0x80
    ng = p.U(r + 8)
    base = p.F(p.U(r + 0x0C))
    if not ng or not p.inside(base):
        raise ValueError('tabela de grupos de shader invalida')
    descr = []
    for g in range(ng):
        d = base + 16 * g
        arr = p.F(p.U(d + 4))
        n = struct.unpack_from('<H', p.data, d + 8)[0]
        if not p.inside(arr) or arr + 4 * n > len(p.data):
            raise ValueError('array de shader invalido no grupo %d' % g)
        descr.append((arr, n))

    copias = bytes_novos = 0
    por_indice = {}
    for indice in sorted(set(escolhidos.values())):
        if any(indice >= n for _arr, n in descr):
            raise ValueError('material semantico %d fora da tabela' % indice)
        origens = []
        faltam = []
        for g, (arr, _n) in enumerate(descr):
            va = p.U(arr + 4 * indice)
            if va:
                src = p.F(va)
                _tamanho_shader_clonavel(p, src)  # valida antes de escrever
                origens.append((g, src))
            else:
                faltam.append(g)
        if not origens:
            raise ValueError('material semantico %d nao tem shader doador'
                             % indice)
        por_indice[indice] = len(faltam)
        for g in faltam:
            _sg, src = min(origens, key=lambda q: abs(q[0] - g))
            dst, tamanho = _clona_shader(p, src)
            struct.pack_into('<I', p.data, descr[g][0] + 4 * indice, p.V(dst))
            copias += 1
            bytes_novos += tamanho

    depois = set(slots_seguros(p))
    perdidos = set(escolhidos.values()) - depois
    if perdidos:
        raise ValueError('slots continuaram inseguros: %s'
                         % ', '.join(map(str, sorted(perdidos))))
    print('  shaders semanticos: %d lacunas clonadas, +%d bytes; '
          'slots seguros %d -> %d'
          % (copias, bytes_novos, len(antes), len(depois)))
    print('  materiais liberados: %s'
          % ', '.join('%s=%d' % (c, escolhidos[c]) for c in CATEGORIAS))
    return {'materiais': escolhidos, 'lacunas': por_indice,
            'copias': copias, 'bytes': bytes_novos,
            'seguros_antes': sorted(antes), 'seguros_depois': sorted(depois)}


def tipos_de_instancia(p):
    """(slots, tipos) do alvo: os registros de 96 bytes e os ComponentData que
    eles apontam.

    Uma instancia NAO carrega geometria: `+0x0C` aponta pro ComponentData do
    TIPO, e o tipo e que tem os dez slots de LOD em `+0x3C`. No atlanta sao 3608
    instancias para 231 tipos, e nenhum desses tipos esta entre os 651
    componentes unique - sao objetos separados.
    """
    slots, tipos = [], {}
    hb = p.F(p.U(0x80 + 0x18))
    for h in range(p.U(0x80 + 0x14)):
        e = hb + 20 * h
        cnt, arr = p.U(e + 0x0C), p.F(p.U(e + 0x10))
        if not p.inside(arr):
            continue
        for k in range(cnt):
            o = arr + 96 * k
            slots.append(o)
            va = p.U(o + 0x0C)
            if va in tipos or not p.inside(p.F(va)):
                continue
            cd = p.F(va)
            meshes = []
            for lod in range(10):
                mp = p.U(cd + 0x3C + 4 * lod)
                if p.inside(p.F(mp)):
                    meshes.append(p.F(mp))
            nome = bytes(p.data[cd + 0x70:cd + 0xB0]).split(b'\0')[0]
            tipos[va] = (nome.decode('latin1', 'ignore'), cd, meshes)
    return slots, tipos


def libera_alvos(p, meshes):
    """Poe no pool de espaco livre os pacotes de TODOS os meshes que serao
    trocados, ANTES da primeira alocacao.

    Liberar so depois de cada troca quase nao adianta: as malhas de Los Angeles
    sao maiores que as do doador, entao uma faixa recem-liberada raramente cabe
    a proxima alocacao e o arquivo cresce assim mesmo (13.88 -> 13.67 MB).
    Com o pool inteiro disponivel desde o inicio, o encaixe melhora muito.

    E seguro: `pacotes_do_mesh` le a LISTA de blocos, nao o conteudo, e o
    `emit_mesh_region` tira sua amostra de payload da cadeia de `+0x14`, que nao
    entra no pool. Um mesh pode ficar apontando para bytes ja reescritos entre a
    liberacao e a sua propria troca, mas ele vai ser trocado de qualquer jeito.
    """
    try:
        import mc3_compacta
    except Exception:
        return 0
    if not hasattr(p, 'livres'):
        p.livres = []
    visto = set()
    for m in meshes:
        if m in visto:
            continue
        visto.add(m)
        p.livres += mc3_compacta.regiao_do_mesh(p, m)
    # maior primeiro: encaixa as malhas grandes antes de fatiar o pool
    p.livres.sort(key=lambda x: -x[1])
    return sum(t for _a, t in p.livres)


def porta_instancias(p, place, pasta, converte, grid, material=None):
    """Preenche os slots de INSTANCIA do alvo com as instancias do MC2.

    AS INSTANCIAS SAO ENCADEADAS POR TIPO, e ignorar isso trava o jogo. Medido
    no atlanta: dos 3608 registros, 3377 tem `+0x00` apontando para outra
    instancia DO MESMO TIPO e nenhum aponta para tipo diferente; sao 231
    cadeias, uma por tipo, cada uma com `+0x04 == 0` na cabeca. `+0x00` e o
    proximo e `+0x04` o anterior.

    A primeira versao disto reapontava `+0x0C` livremente, tratando os 3608
    slots como um banco unico - as cadeias passaram a misturar tipos e o jogo
    ficou em loading infinito. Aqui cada CADEIA inteira recebe um unico tipo do
    MC2, entao o encadeamento continua verdadeiro.
    """
    import collections
    import mc3_city_build as cb
    linhas, _ext = cb.le_place(place)
    insts = [l for l in linhas if l['kind'] == 'inst']
    if not insts:
        return 0

    tabela_mat = None if material is not None else materiais_por_categoria(p)
    slots, tipos = tipos_de_instancia(p)
    por_tipo_alvo = collections.defaultdict(list)
    for o in slots:
        por_tipo_alvo[p.U(o + 0x0C)].append(o)
    alvos = [(len(v), va) for va, v in por_tipo_alvo.items() if tipos.get(va, (0, 0, []))[2]]
    alvos.sort(reverse=True)
    print('  instancias: %d slots em %d cadeias de tipo' % (len(slots), len(alvos)))

    fonte = collections.Counter(l['name'] for l in insts)
    por_nome = collections.defaultdict(list)
    for l in insts:
        por_nome[l['name']].append(l)
    ordem = [n for n, _c in fonte.most_common()]

    postos = usados = 0
    teto = getattr(p, 'teto_bytes', 0)
    cortados = 0
    for i, (n_slots, va) in enumerate(alvos):
        if i >= len(ordem):
            break
        # ORCAMENTO DE TAMANHO. O .pck de cidade tem teto - 12.08 MB carrega,
        # 13.88 trava - e cada TIPO de instancia novo custa uma copia da malha.
        # Os tipos vem ordenados por quantas instancias usam cada um, entao
        # cortar no fim do orcamento e cortar o que menos aparece.
        if teto and len(p.data) > teto:
            cortados += 1
            # o tipo cortado fica com a geometria do doador; se as instancias
            # dele ficarem onde estao, a cidade antiga reaparece no meio da
            # nova. Entao elas sao estacionadas fora do mundo, com raio
            # minusculo - a malha continua valida, so nunca e vista.
            for o in por_tipo_alvo[va]:
                struct.pack_into('<12f', p.data, o + 0x20,
                                 1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0,
                                 0.0, -100000.0, 0.0)
                struct.pack_into('<f', p.data, o + 0x18, 0.01)
                struct.pack_into('<3f', p.data, o + 0x50, 0.0, -100000.0, 0.0)
            continue
        nome = ordem[i]
        l0 = por_nome[nome][0]
        arq = ('%s_%s.mod' % (nome, l0['lod'])) if l0['part'] == '-' else               ('%s_%s_%s.mod' % (nome, l0['lod'], l0['part']))
        cam = os.path.join(pasta, arq)
        if not os.path.isfile(cam):
            continue
        got = converte(cam)
        if not got:
            continue
        blocos, _r = got
        blocos, _c = centra_na_origem(blocos)
        _nm, cd, meshes = tipos[va]
        mat = material if material is not None else             (tabela_mat.get(categoria(nome)) if tabela_mat else None)
        ok = False
        for j, mm in enumerate(meshes):
            if troca(p, mm, blocos if j == 0 else blocos[:1]):
                if j == 0:
                    ok = True
            if mat is not None:
                uniformiza_material(p, mm, mat)
        if not ok:
            continue
        pts = [q for pos, _u, _n, _o in blocos for q in pos]
        raio = max((q[0] ** 2 + q[1] ** 2 + q[2] ** 2) ** 0.5 for q in pts)
        struct.pack_into('<f', p.data, cd + 0x38, raio)
        usados += 1

        # espalhados pela cidade, nao os primeiros: uma cadeia com 20 vagas para
        # 629 arbustos so mostraria um canto do mapa
        fila = por_nome[nome]
        alvo_slots = por_tipo_alvo[va]
        if len(fila) > len(alvo_slots):
            passo = len(fila) / float(len(alvo_slots))
            fila = [fila[int(k * passo)] for k in range(len(alvo_slots))]
        for k, o in enumerate(alvo_slots):
            if k < len(fila):
                l = fila[k]
                m = [float(l[c]) for c in ('m00', 'm01', 'm02', 'm10', 'm11',
                                           'm12', 'm20', 'm21', 'm22',
                                           'tx', 'ty', 'tz')]
                centro = tuple((float(l['emin' + e]) + float(l['emax' + e])) / 2.0
                               for e in 'xyz')
                postos += 1
            else:
                # vaga que sobrou: parcada longe, com raio minusculo, para o
                # culling nunca alcancar. Zerar a matriz nao serve - linha de
                # norma zero e matriz degenerada.
                m = [1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0, 0.0, -100000.0, 0.0]
                centro = (0.0, -100000.0, 0.0)
            struct.pack_into('<12f', p.data, o + 0x20, *m)
            struct.pack_into('<f', p.data, o + 0x18,
                             raio if k < len(fila) else 0.01)
            struct.pack_into('<3f', p.data, o + 0x50, *centro)
            struct.pack_into('<I', p.data, o + 0x1C, k)
            if grid:
                rr = raio if k < len(fila) else 0.0
                p.data[o + 0x14:o + 0x18] = caixa_de_celulas(
                    grid, centro[0], centro[2], rr)
    print('  %d cadeias de tipo remapeadas, %d instancias colocadas%s'
          % (usados, postos,
             ', %d tipos cortados pelo orcamento' % cortados if cortados else ''))
    return postos


def porta_cidade(p, place, pasta, converte, material=None, limite=None,
                 instancias=False, completar_shaders=True,
                 grade_do_doador=False):
    """Fill EVERY hood of the target with a whole MC2 city, in TRUE coordinates.

    `porta_hood` maps one MC2 hood onto one target hood and rescales it to that
    hood's footprint. That is right for one neighbourhood and wrong for a city:
    each hood would get its own scale and the layout would come apart.

    Here nothing is rescaled. Every component goes to its own world position
    from the table, the world extents of the target are rewritten to the
    source's, and the culling grid is recomputed from those extents - MC2's
    `.lvl` says `dimensions 90 81` for Los Angeles and 90 * 40 = 3600 is exactly
    its x extent, so both games tile the world at 40 units and the grid carries
    over unchanged.

    Slots are consumed hood by hood; what is left over is emptied. The hood a
    component lands in does not decide its culling - the tile box at
    `component+0x14` does, and that is computed from the real position.
    """
    import mc3_city_build as cb
    linhas, ext = cb.le_place(place)
    comps = [l for l in linhas if l['kind'] == 'comp']
    if limite:
        comps = comps[:limite]

    if material is None and completar_shaders:
        completa_slots_semanticos(p)
    tabela_mat = None if material is not None else materiais_por_categoria(p)
    if tabela_mat:
        print('  material por semantica, medido no destino: %s'
              % ', '.join('%s=%d' % (c, tabela_mat[c]) for c in CATEGORIAS))
    hs = hoods(p)
    slots = []
    for i in range(len(hs)):
        for nm, meshes, comp, cd in uniques_do_hood(p, i):
            slots.append((i, nm, meshes, comp, cd))
    print('  alvo: %d hood(s), %d slots; fonte: %d componentes'
          % (len(hs), len(slots), len(comps)))

    r = 0x80
    antes_n, antes_w, antes_h = struct.unpack_from('<3i', p.data, r + 0x268)
    if ext.get('extents_min') and ext.get('extents_max'):
        for off, chave in ((0x238, 'extents_min'), (0x244, 'extents_max')):
            for j, v in enumerate(ext[chave][:3]):
                struct.pack_into('<f', p.data, r + off + 4 * j, v)
        # A ORIGEM DA GRADE DE CULLING VIVE EM MapRoot+0x274/+0x278, em CELULAS,
        # e reescrever so os extents deixa as duas em desacordo.
        #
        # Lido do ELF: `mcCity::CalcAbsCellXZ` (0x257CC8) e `floor(x / 40)` e
        # `floor(z / 40)`, sem origem nenhuma; quem tira a origem e
        # `CalcRelCellXZ` (0x257C60), subtraindo `mcCity+0x274` e `+0x278`.
        # Confirmado nas quatro cidades de varejo, 8 de 8 valores:
        # +0x274 == floor(extents_min.x / 40) e +0x278 == floor(min.z / 40).
        #
        # O arquivo anterior tinha os extents de Los Angeles e a origem do
        # atlanta: -33/-34 no lugar de -50/-43, ou seja o culling inteiro
        # deslocado 17 celulas em x e 9 em z - 680 e 360 unidades de mundo.
        import math
        cx0 = int(math.floor(ext['extents_min'][0] / 40.0))
        cz0 = int(math.floor(ext['extents_min'][2] / 40.0))
        struct.pack_into('<2i', p.data, r + 0x274, cx0, cz0)
        # O TAMANHO DA GRADE ANDA JUNTO COM OS EXTENTS, e escrever so a origem
        # deixava a cidade metade invisivel.
        #
        # `MapRoot+0x26C` e `+0x270` sao os limites de `rel_x` e `rel_z`, e
        # `+0x268` e a contagem de celulas que o jogo aloca (0x2594D0 faz
        # `malloc(+0x268 * 4)`; outro consumidor em 0x25B090 usa 12 bytes por
        # celula). `mcCity::CellIndexFromPos` (0x257BE8) devolve
        # `rel_z * W + rel_x` e -1 fora disso - e o objeto nao entra na grade.
        #
        # A invariante do varejo, conferida no atlanta (64x62), tokyo (90x69) e
        # detroit (96x75): W e H saem exatamente dos extents e ZERO objetos
        # ficam de fora. O arquivo anterior tinha os extents de Los Angeles
        # (91x82 celulas) com a grade do atlanta (64x62): tudo que caia em
        # x >= 64 ou z >= 62 era descartado sem aviso.
        gw = int(math.floor(ext['extents_max'][0] / 40.0)) - cx0 + 1
        gh = int(math.floor(ext['extents_max'][2] / 40.0)) - cz0 + 1
        gw = max(1, min(256, gw))
        gh = max(1, min(256, gh))
        if grade_do_doador:
            gw, gh = antes_w, antes_h
        else:
            struct.pack_into('<3i', p.data, r + 0x268, gw * gh, gw, gh)
        grid = (40.0, cx0 * 40.0, 40.0, cz0 * 40.0, gw, gh)
        print('  extents reescritos para x %.0f..%.0f  z %.0f..%.0f;'
              ' origem de celula +0x274/+0x278 = %d, %d'
              % (ext['extents_min'][0], ext['extents_max'][0],
                 ext['extents_min'][2], ext['extents_max'][2], cx0, cz0))
        print('  grade de celulas %d x %d = %d (era %d x %d = %d)'
              % (gw, gh, gw * gh, antes_w, antes_h, antes_n))
    else:
        grid = mc2.tile_grid(p)

    feitos = usados = 0
    for l in comps:
        if usados >= len(slots):
            break
        if l['part'] == '-':
            arq = '%s_%s.mod' % (l['name'], l['lod'])
        else:
            arq = '%s_%s_%s.mod' % (l['name'], l['lod'], l['part'])
        cam = os.path.join(pasta, arq)
        if not os.path.isfile(cam):
            continue
        got = converte(cam)
        if not got:
            continue
        blocos, _r = got
        blocos, _c = centra_na_origem(blocos)
        _i, _nm, meshes, comp, cd = slots[usados]
        usados += 1
        # SO O PRIMEIRO SLOT DE LOD. O atlanta tem 1076 meshes para 651
        # componentes: dar a mesma geometria de LA a cada slot escreve a peca
        # inteira ate dez vezes e e o que estoura o teto de tamanho. Os outros
        # slots ficam com contagem de grupo zero - nao desenham, e o LOD longe
        # simplesmente nao aparece.
        mat = material if material is not None else             (tabela_mat.get(categoria(l['name'])) if tabela_mat else None)
        ok = False
        for j, mm in enumerate(meshes):
            # LOD 0 leva a peca inteira; os outros slots levam UM bloco.
            #
            # Dar a geometria completa a todos os dez slots e o que estourava o
            # teto de tamanho. Mas ZERAR a contagem de grupo dos outros nao
            # serve: o LOD vazio faz o PCSX2 abortar com
            # "FQC = 0 on VIF FIFO READ" - alguem escolhe esse LOD e acaba lendo
            # uma FIFO que ninguem encheu. Um bloco e barato e continua sendo
            # mesh de verdade.
            if troca(p, mm, blocos if j == 0 else blocos[:1]):
                if j == 0:
                    ok = True
            if mat is not None:
                uniformiza_material(p, mm, mat)
        if not ok:
            continue
        mundo = tuple((float(l['emin' + e]) + float(l['emax' + e])) / 2.0
                      for e in 'xyz')
        struct.pack_into('<3f', p.data, cd + 0x2C, *mundo)
        pts = [q for pos, _u, _n, _o in blocos for q in pos]
        raio = max((q[0] ** 2 + q[1] ** 2 + q[2] ** 2) ** 0.5 for q in pts)
        reposiciona(p, comp, cd, raio, grid)
        feitos += 1

    if instancias:
        porta_instancias(p, place, pasta, converte, grid, material)

    vazios = 0
    for _i, _nm, meshes, _c, _cd in slots[usados:]:
        for mm in meshes:
            struct.pack_into('<H', p.data, mm + 8, 0)
        vazios += 1
    print('  %d componentes portados, %d slots esvaziados' % (feitos, vazios))

    # POR ULTIMO, depois que toda tile box esta no lugar: o indice por celula.
    # Sem isto a cidade carrega e nao aparece - o jogo percorre a tabela de
    # MapRoot+0x1C, que continua listando os objetos do doador nas celulas do
    # doador. Ver mc3_cellindex.
    try:
        import mc3_cellindex
        res = mc3_cellindex.reconstroi(p)
    except Exception as e:
        print('  AVISO: indice por celula nao reconstruido (%s)' % e)
        res = None
    if res:
        print('  indice por celula refeito: %d celulas (%d ocupadas), '
              '%d unique + %d instancia listados, +%d bytes'
              % (res['celulas'], res['ocupadas'], res['uniques'],
                 res['instancias'], res['bytes']))
    return feitos


def porta_hood(p, alvos, fonte, pasta, converte, grid, escala_pedida,
               material, sem_esfera):
    """Move a whole MC2 hood in as one rigid block.

    Matching mesh-by-mesh on size, which is what the catalogue mode does, cannot
    produce a neighbourhood: it drops unrelated buildings onto unrelated
    footprints. Here the SET moves together - each component keeps its position
    relative to its neighbours, because MC2 stores geometry in world coordinates
    and the .hood declares each component's world box.

    The two sides never have the same number of slots (LA downtown offers 25
    usable uniques, atlanta's `ug` has 43), so components are assigned to the
    nearest free slot by mapped position, and **whatever is left over is
    emptied** - otherwise the original geometry stays behind and mixes with the
    import, which is exactly the mess the LOD bug produced.
    """
    lo = [min(a[k] for _n, a, _b in fonte) for k in range(3)]
    hi = [max(b[k] for _n, _a, b in fonte) for k in range(3)]
    cen_src = [(lo[k] + hi[k]) / 2.0 for k in range(3)]

    pos_alvo = [struct.unpack_from('<3f', p.data, cd + 0x2C) for _n, _m, _c, cd in alvos]
    tlo = [min(q[k] for q in pos_alvo) for k in range(3)]
    thi = [max(q[k] for q in pos_alvo) for k in range(3)]
    cen_dst = [(tlo[k] + thi[k]) / 2.0 for k in range(3)]

    # HEIGHT. Y is not part of the tile mapping - `mcCity::CalcAbsCellXZ` is
    # `floor(x/40)` and `floor(z/40)` and never reads Y - so height decides
    # nothing about where a model is filed, only whether it looks buried.
    #
    # Seating each component on the base of the slot it replaces was wrong for
    # anything FLAT. A road is 73 x 0.1 x 103, so its base is its top, and the
    # slot it lands in is a tunnel piece whose lowest point is the foot of a
    # wall, well under the floor - every road went under the ground and none of
    # them was ever visible. It also threw away the neighbourhood's own vertical
    # structure: street below, building above, freeway overhead.
    #
    # So the hood moves as one rigid block in Y too. Each component keeps its
    # own height relative to the MC2 ground, scaled by the same factor, and the
    # whole set is offset once so that MC2's street level lands on the target's.
    chao_alvo = []
    for j, (_n, meshes, _c, cd) in enumerate(alvos):
        base = None
        for mm in meshes:
            ab = aabb_local(p, mm)
            if ab:
                base = pos_alvo[j][1] + ab[0][1]
                break
        if base is None:      # mesh ilegivel: cai pro raio da esfera
            base = pos_alvo[j][1] - struct.unpack_from('<f', p.data, cd + 0x38)[0]
        chao_alvo.append(base)
    ordenado = sorted(chao_alvo)
    chao_dst = ordenado[len(ordenado) // 2]      # mediana: robusta a um poco fundo
    chao_src = min(a[1] for _n, a, _b in fonte)
    print('  chao: MC2 %.1f -> alvo %.1f (mediana de %d slots)'
          % (chao_src, chao_dst, len(chao_alvo)))

    if escala_pedida:
        esc = escala_pedida
    else:
        esc = min((thi[k] - tlo[k]) / (hi[k] - lo[k])
                  for k in (0, 2) if hi[k] - lo[k] > 1) or 1.0
    print('  fonte %.0f x %.0f, alvo %.0f x %.0f  ->  escala %.3f'
          % (hi[0] - lo[0], hi[2] - lo[2], thi[0] - tlo[0], thi[2] - tlo[2], esc))

    livres = list(range(len(alvos)))
    feitos = 0
    for nome, emin, emax in fonte:
        cam = xmod_de(nome, pasta)
        if not cam:
            continue
        got = converte(cam, esc)
        if not got:
            continue
        blocos, _r = got
        blocos, _c = centra_na_origem(blocos)
        c_src = [(emin[k] + emax[k]) / 2.0 for k in range(3)]
        destino = [cen_dst[k] + (c_src[k] - cen_src[k]) * esc if k != 1 else 0.0
                   for k in range(3)]
        if not livres:
            break
        j = min(livres, key=lambda i: sum((pos_alvo[i][k] - destino[k]) ** 2
                                          for k in (0, 2)))
        livres.remove(j)
        _nm, meshes, comp, cd = alvos[j]
        pts = [c for pos, _u, _nr, _o in blocos for c in pos]
        raio = max((q[0] ** 2 + q[1] ** 2 + q[2] ** 2) ** 0.5 for q in pts)
        # base na altura que a peca tinha no MC2, medida do chao de la e escalada;
        # os blocos ja estao centrados, entao o centro fica meia altura acima
        alto = max(q[1] for q in pts) - min(q[1] for q in pts)
        destino[1] = chao_dst + (emin[1] - chao_src) * esc + alto / 2.0
        ok = False
        for mm in meshes:
            if troca(p, mm, blocos):
                ok = True
            if material is not None:
                uniformiza_material(p, mm, material)
        if not ok:
            continue
        struct.pack_into('<3f', p.data, cd + 0x2C, *destino)
        if not sem_esfera:
            reposiciona(p, comp, cd, raio, grid)
        feitos += 1
        print('   ok %-40s -> (%7.0f %6.0f %7.0f)  raio %.0f'
              % (nome[:40], destino[0], destino[1], destino[2], raio))

    # o que sobrou tem que sumir, senao a cidade antiga fica por baixo
    for i in livres:
        _nm, meshes, _c, _cd = alvos[i]
        for mm in meshes:
            struct.pack_into('<H', p.data, mm + 8, 0)
    print('  %d componentes portados; %d slots do alvo esvaziados'
          % (feitos, len(livres)))
    return feitos


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pck')
    ap.add_argument('--hood', required=True, help='hood name (bh, dt, fwy, lf, mt, ug, we)')
    ap.add_argument('--xmod', default=mc2.XMOD)
    ap.add_argument('--xmoddir', help='a directory of .xmod; each target mesh gets '
                                      'the model whose radius is closest to its own')
    ap.add_argument('--sem-compactar', action='store_true',
                    help='nao devolver os bytes da geometria substituida')
    ap.add_argument('--teto-mb', type=float, default=11.8,
                    help='para de acrescentar tipo de instancia quando o '
                         'arquivo passa deste tamanho')
    ap.add_argument('--com-instancias', action='store_true',
                    help='preenche tambem os slots de instancia do alvo')
    ap.add_argument('--mc2cidade', metavar='PLACE.tsv',
                    help='porta a CIDADE inteira em coordenada real, usando '
                         'todos os hoods do alvo; reescreve os extents')
    ap.add_argument('--mc2hood', metavar='ARQ.hood',
                    help='porta um hood INTEIRO do MC2 preservando o layout'
                         ' relativo, e esvazia os slots que sobrarem')
    ap.add_argument('--escala', type=float, default=1.0)
    ap.add_argument('--limite', type=int, default=0, help='stop after N meshes')
    ap.add_argument('--luz', type=int, default=mc2.LUZ)
    ap.add_argument('--normais', action='store_true')
    ap.add_argument('--empilhar', metavar='X,Y,Z',
                    help='EXPERIMENTO: poe o MESMO cd+0x2C em todos os meshes. Se'
                         ' esse campo e a colocacao, os objetos empilham nesse'
                         ' ponto; se nao empilharem, a colocacao esta noutro lugar')
    ap.add_argument('--centrado', action='store_true',
                    help='ancora o modelo no proprio centro (como a maioria dos'
                         ' meshes vanilla). Faz as duas leituras de cd+0x2C'
                         ' coincidirem, entao a ambiguidade deixa de importar')
    ap.add_argument('--centro-esfera', action='store_true',
                    help='trata cd+0x2C como CENTRO DA ESFERA e o reescreve, em'
                         ' vez de tratar como translacao da origem. Implica'
                         ' --sem-alinhar: sao leituras alternativas, nao somam')
    ap.add_argument('--sem-alinhar', action='store_true',
                    help='nao desloca o modelo novo pra pegada do antigo; use'
                         ' pra comparar com o comportamento anterior')
    ap.add_argument('--material', type=int,
                    help='forca UM indice de material em todos os grupos (3 e o'
                         ' mais usado do atlanta). Junto com --uvfixo da'
                         ' superficie chapada e uniforme entre meshes')
    ap.add_argument('--grade-do-doador', action='store_true',
                    help='nao aumentar a grade de celulas: mantem W/H/contagem '
                         'do doador e so refaz o indice por celula dentro dela. '
                         'Serve para separar as duas variaveis num teste.')
    ap.add_argument('--sem-completar-shaders', action='store_true',
                    help='na importacao de cidade inteira, mantem so os slots'
                         ' de material que ja existem nos 18 grupos; por padrao'
                         ' os sete materiais semanticos sao completados com'
                         ' clones retail independentes')
    ap.add_argument('--uvfixo', metavar='U,V',
                    help='trava o UV de tudo num valor so -> superficie chapada')
    ap.add_argument('--uvdebug', action='store_true',
                    help='um UV constante DIFERENTE por mesh: cada objeto sai de'
                         ' uma cor chapada distinta, o que separa um do outro na'
                         ' tela sem depender da textura estar certa')
    ap.add_argument('--manter-esfera', action='store_true',
                    help='nao mexe no raio nem na AABB de tile (o culling vai '
                         'esconder modelo maior que o original)')
    ap.add_argument('--saida')
    a = ap.parse_args()
    globals()['LUZ'] = a.luz
    mc2.LUZ = max(0, min(255, a.luz))
    mc2.NORMAIS = bool(a.normais)
    if a.uvfixo:
        mc2.UV_FIXO = tuple(float(x) for x in a.uvfixo.split(','))

    p = mc2.Pck(a.pck)
    hs = hoods(p)
    print('%s: %d hoods' % (os.path.basename(a.pck), len(hs)))
    for i, (nome, nu, _au, ni, _ai) in enumerate(hs):
        print('   %d %-5s %4d unique  %4d instance%s'
              % (i, nome, nu, ni, '   <- alvo' if nome == a.hood else ''))
    idx = next((i for i, h in enumerate(hs) if h[0] == a.hood), None)
    if idx is None:
        raise SystemExit('no hood named %r' % a.hood)

    cache = {}

    def converte(caminho, esc=None):
        """(blocks, radius) for one .xmod, converted once and reused.

        The cache is keyed on the UV too: with `--uvdebug` the same model is
        converted again per mesh with a different constant UV, so caching on the
        path alone would hand every mesh the first colour.
        """
        fator = a.escala if esc is None else esc
        chave = (caminho, mc2.UV_FIXO, fator)
        if chave in cache:
            return cache[chave]
        v, t1, adj, strips = mc2.read_xmod(caminho)
        bl, _c = mc2.strips_to_blocks(v, t1, adj, strips)
        if fator != 1.0 and bl:
            bl = [([tuple(c * fator for c in q) for q in pos], u, nr, o)
                  for pos, u, nr, o in bl]
        if not bl or len(bl) > mc2.MAX_BLOCKS:
            cache[chave] = None              # retail never exceeds 88 blocks
            return None
        pts = [c for pos, _u, _nr, _o in bl for c in pos]
        r = max((q[0] ** 2 + q[1] ** 2 + q[2] ** 2) ** 0.5 for q in pts)
        cache[chave] = (bl, r)
        return cache[chave]

    if a.mc2cidade:
        pasta = a.xmoddir or os.path.join(os.path.dirname(a.mc2cidade), 'model')
        if a.teto_mb:
            p.teto_bytes = int(a.teto_mb * 1048576)
        porta_cidade(p, a.mc2cidade, pasta, converte, a.material, a.limite,
                     a.com_instancias, not a.sem_completar_shaders,
                     a.grade_do_doador)
        out = a.saida or (os.path.splitext(a.pck)[0] + '_cidade.pck')
        if not a.sem_compactar:
            import mc3_compacta
            r = mc3_compacta.compacta(p, getattr(p, '_mortas', []))
            if len(r) == 4:
                print('  compactado: %.2f MB -> %.2f MB (%d ponteiros movidos, %d perdidos)'
                      % (r[0]/1048576.0, r[1]/1048576.0, r[2], r[3]))
        p.save(out)
        print('gravado %s (%d bytes)' % (out, len(p.data)))
        raise SystemExit(0)

    cat = []
    if a.xmoddir:
        cat = catalogo(a.xmoddir)
        if not cat:
            raise SystemExit('no usable `_main` .xmod/.mod in %s' % a.xmoddir)
        print()
        print('catalogo: %d modelos `_main`, raio de %.0f a %.0f'
              % (len(cat), cat[0][0], cat[-1][0]))
    else:
        r = converte(a.xmod)
        if not r:
            raise SystemExit('%s nao converte dentro do limite de %d blocos'
                             % (a.xmod, mc2.MAX_BLOCKS))
        print()
        print('modelo unico: %d blocos, %d triangulos, raio %.1f'
              % (len(r[0]), sum(len(x[0]) - 2 for x in r[0]), r[1]))
    grid = mc2.tile_grid(p)
    print('grade de tile: %s'
          % ('celula %.1f x %.1f' % (grid[0], grid[2]) if grid else 'nao ajustou'))

    def escolhe(alvo_raio):
        """The catalogue entry whose radius is closest to what it replaces.

        Matching by size keeps the swap sane: a tunnel piece of radius 52 gets a
        model of about that size instead of a 217-unit tower, so the culling, the
        collision and the general look of the block stay in proportion. Entries
        that fail to convert are dropped and the next closest is tried.
        """
        for _d, caminho in sorted(((abs(r - alvo_raio), c) for r, c in cat))[:12]:
            got = converte(caminho)
            if got:
                return caminho, got
        return None, None

    nomes = uniques_do_hood(p, idx)
    if a.mc2hood:
        fonte = le_hood_mc2(a.mc2hood)
        pasta = a.xmoddir or os.path.join(os.path.dirname(a.mc2hood), 'models')
        print()
        print('MC2 %s: %d unique_component' % (os.path.basename(a.mc2hood), len(fonte)))
        porta_hood(p, nomes, fonte, pasta, converte, grid,
                   a.escala if a.escala != 1.0 else None,
                   a.material, a.manter_esfera)
        out = a.saida or (os.path.splitext(a.pck)[0] + '_hood.pck')
        p.save(out)
        print('gravado %s (%d bytes)' % (out, len(p.data)))
        return
    if a.limite:
        nomes = nomes[:a.limite]
    antes = len(p.data)
    feitos = falhos = 0
    desl = (0.0, 0.0, 0.0)
    for i_alvo, (nm, meshes, comp, cd) in enumerate(nomes):
        if a.uvdebug:
            # spread the constant UV over the atlas so consecutive meshes land on
            # different texels and therefore come out different flat colours
            mc2.UV_FIXO = (0.08 + 0.16 * (i_alvo % 6), 0.08 + 0.16 * ((i_alvo // 6) % 6))
        antes_raio = struct.unpack_from('<f', p.data, cd + 0x38)[0]
        if cat:
            caminho, got = escolhe(antes_raio)
            if not got:
                falhos += 1
                print('   -- %-30s nada no catalogo converteu' % nm[:30])
                continue
            blocos, raio = got
            de = os.path.basename(caminho).split('#')[0]
        else:
            blocos, raio = converte(a.xmod)
            de = os.path.basename(a.xmod).split('#')[0]
        alvo = aabb_local(p, meshes[0])
        if a.empilhar:
            q = tuple(float(x) for x in a.empilhar.split(','))
            blocos, _cen = centra_na_origem(blocos)
            struct.pack_into('<3f', p.data, cd + 0x2C, *q)
            desl = q
        elif a.centrado:
            # o modelo passa a ser centrado na origem; cd+0x2C recebe o centro
            # de mundo que a geometria antiga ocupava, que sob a leitura A e
            # `cd2C + centro_local_antigo` e sob a B e o proprio `cd2C` -- a
            # diferenca entre as duas cai para o centro local antigo, cuja
            # mediana e 0 em x/z e 6.4 em y, em vez dos ~97 de antes
            blocos, _cen = centra_na_origem(blocos)
            if alvo:
                velho = [(alvo[0][k] + alvo[1][k]) / 2.0 for k in range(3)]
                c0 = struct.unpack_from('<3f', p.data, cd + 0x2C)
                novo = [c0[k] + velho[k] for k in range(3)]
                struct.pack_into('<3f', p.data, cd + 0x2C, *novo)
                desl = tuple(novo[k] - c0[k] for k in range(3))
        elif a.centro_esfera:
            if alvo:
                pts = [c for pos, _u, _nr, _o in blocos for c in pos]
                nlo = [min(q[a2] for q in pts) for a2 in range(3)]
                nhi = [max(q[a2] for q in pts) for a2 in range(3)]
                desl = recentra_esfera(p, cd, alvo, nlo, nhi)
        elif not a.sem_alinhar:
            if alvo:
                blocos, desl = alinha(blocos, alvo)
        # every LOD of this component gets the same geometry, or the distant
        # ones keep drawing what used to be there
        rs = [troca(p, mm, blocos) for mm in meshes]
        r = next((x for x in rs if x), None)
        if r is None:
            falhos += 1
            print('   -- %-30s nenhum dos %d LODs tinha grupo usavel' % (nm, len(meshes)))
            continue
        r = (sum(x[0] for x in rs if x), r[1])
        if a.material is not None:
            for mm in meshes:
                uniformiza_material(p, mm, a.material)
        c = reposiciona(p, comp, cd, raio, grid) if not a.manter_esfera else None
        feitos += 1
        print('   ok %-22s <- %-26s %d LOD %3d bl  raio %.0f->%.0f  desl (%.0f %.0f %.0f)'
              % (nm[:22], de[:26], len(meshes), r[0], antes_raio,
                 raio if c else antes_raio, *desl))

    print()
    print('%d meshes trocados, %d pulados; arquivo %d -> %d bytes (+%.1f MB)'
          % (feitos, falhos, antes, len(p.data), (len(p.data) - antes) / 1048576.0))
    out = a.saida or (os.path.splitext(a.pck)[0] + '_hood.pck')
    p.save(out)
    print('gravado %s' % out)


if __name__ == '__main__':
    main()
