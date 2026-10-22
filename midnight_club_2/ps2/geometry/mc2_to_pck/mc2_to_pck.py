"""mc2_to_pck.py - Midnight Club 2 (PS2) city geometry -> MC3 `.mesh.pck`

Closes the last gap between `mc2_rsc.py`, which decodes MC2's `PMD0`, and
`mc3_mesh_convert.py`, which writes MC3 packets. Everything it needs was
measured, not guessed:

  * a `PMD0` batch IS one triangle strip with ADC flags, and `Batch.triangles()`
    uses the same parity rule as `tris_of_strip` here -- (k-2,k-1,k) on even k,
    (k-1,k-2,k) on odd -- so the topology maps across untouched.
  * MC3's packets are written with `--keep-strips` (restrip=False), which cuts
    only the strips longer than a packet. Measured over the 294 baked Los
    Angeles components: 6370 packets against 39709 the re-stripifying way, and
    3.27 MB against 5.34 MB, with triangles AND winding identical in 294 of 294.

What does NOT come across, and why:

  * The VIF chain itself. MC2 unpacks position as V3-16u at base+4 and decodes
    it as 131072 + raw/64 - bias, with the base coming from `itop`; MC3 unpacks
    at the fixed VU address 0x00EE and multiplies by a scale. Different
    addresses, formats and microprogram, so the geometry crosses as DATA and is
    re-emitted in MC3's own packet.
  * The material index. A `.mesh.pck` stores a u16 slot per group, not a name,
    and the slot belongs to a shader group that lives outside the mesh. The MC2
    texture NAME is written to the manifest so it can be mapped; without
    `--materials` every group gets slot 0.
  * Per-vertex colour. MC2 keeps it in `<hour>_cpvs.rsc` as a palette index, not
    in the geometry, so the meshes come out with the default diffuse.

Usage:

    python mc2_to_pck.py <city.rsc>                   # everything, to output/
    python mc2_to_pck.py <city.rsc> --filtro rd_23    # just the ones matching
    python mc2_to_pck.py <city.rsc> --materials m.tsv # texture name -> slot
    python mc2_to_pck.py <city.rsc> --so-manifesto    # tables only, no .pck

Writes into the output folder: one `.mesh.pck` per model, a
`<city>_place.tsv` in the same column layout `mc3_city_build.py --place`
reads, and a `<city>_materials.tsv` pairing each group with the MC2 texture
name it draws with.
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mc2_rsc as R
import mc3_mesh_convert as M
import mc3_saida


IDENT = (1, 0, 0, 0, 1, 0, 0, 0, 1)


def batches_of(rsc, model, lod=None):
    got = []
    for h in R.model_blocks(model, lod):
        r = rsc.resolve(h)
        if r is not None:
            got.extend(R.read_pmd(rsc, r[1])[0])
    return got


def mesh_from_batches(rsc, batches):
    """One MC3 Mesh, one group per MC2 texture, one strip per batch.

    The fixed-point exponent is fitted to the model's own extent, the way
    rmcModelGeom::Load fits it when the game loads text: a city piece in world
    coordinates would saturate s16 at the converter's default 1/4096.
    """
    allpos = [p for b in batches for p in b.pos]
    if not allpos:
        return None, []
    scale = M._fit_scale(allpos)
    inv = 1.0 / scale
    by = collections.OrderedDict()
    for b in batches:
        by.setdefault(b.texture, []).append(b)
    mesh = M.Mesh()
    mesh.scale = scale
    mesh.source = 'mc2-pmd0'
    texturas = []
    for handle, bs in by.items():
        strips = []
        for b in bs:
            st = []
            for k, p in enumerate(b.pos):
                uv = b.uv[k] if k < len(b.uv) else (0.0, 0.0)
                # MC2's 0x80 is the GS ADC bit, which is exactly what Vtx.skip
                # means here: do not close a triangle on this vertex.
                skip = bool(k < len(b.adc) and (b.adc[k] & 0x80))
                st.append(M.Vtx(tuple(M._clampi(c * inv, -32768, 32767) for c in p),
                                uv, (0.0, 0.0, 1.0), skip))
            if len(st) >= 3:
                strips.append(st)
        if strips:
            mesh.groups.append({'material': 0, 'strips': strips})
            texturas.append(rsc.texture_name(handle) or 'none')
    if not mesh.groups:
        return None, []
    # MC2 ships no normals; without these every surface exports flat with a zero
    # normal, and the normal stream is also where MC3 carries the ADC bit.
    M._recompute_normals(mesh)
    return mesh, texturas


def le_extents(pasta, cidade, comps, insts):
    """extents do `<cidade>.lvl`, caindo para a caixa dos dados se nao houver."""
    lvl = os.path.join(pasta, cidade + '.lvl')
    if os.path.isfile(lvl):
        txt = open(lvl, 'r', errors='replace').read()
        got = {}
        for chave in ('extents_min', 'extents_max'):
            m = re.search(chave + r'\s*\{([^}]*)\}', txt)
            if m:
                got[chave] = [float(x) for x in m.group(1).split()][:3]
        if len(got) == 2:
            return got['extents_min'], got['extents_max']
    caixas = [c.emin for c in comps] + [i.emin for i in insts]
    altas = [c.emax for c in comps] + [i.emax for i in insts]
    if not caixas:
        return [0.0] * 3, [0.0] * 3
    return ([min(v[k] for v in caixas) for k in range(3)],
            [max(v[k] for v in altas) for k in range(3)])


def nome_de_arquivo(nome):
    return re.sub(r'[^A-Za-z0-9_.#-]', '_', nome)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('arquivo')
    ap.add_argument('--out')
    ap.add_argument('--filtro')
    ap.add_argument('--lod', type=int)
    ap.add_argument('--materials', help='TSV com "nome_da_textura<TAB>slot"')
    ap.add_argument('--limite', type=int)
    ap.add_argument('--so-manifesto', action='store_true')
    a = ap.parse_args()

    rsc = R.Rsc(a.arquivo)
    cidade = os.path.splitext(os.path.basename(rsc.path))[0]
    out = a.out or os.path.join(mc3_saida.pasta(), 'mc2_pck', cidade)
    if not os.path.isdir(out):
        os.makedirs(out)

    mapa = {}
    if a.materials:
        for l in open(a.materials, 'r', errors='replace'):
            p = l.split('#')[0].split('\t')
            if len(p) >= 2 and p[0].strip():
                mapa[p[0].strip().lower()] = int(p[1], 0)

    pasta_cidade = R.city_folder(rsc.path)
    comps, insts = R.read_hoods(pasta_cidade)
    porTipo = collections.defaultdict(list)
    for i in insts:
        porTipo[i.type.lower()].append(i)
    # The .lvl's own extents, not the bounding box of the data: the cell grid
    # is derived from them, and they are round numbers the data does not quite
    # reach (LA declares -2000..1600 while the geometry stops at -1989.7).
    emin, emax = le_extents(pasta_cidade, cidade, comps, insts)

    linhas = []
    mats = []
    n_pck = n_grupo = n_tri = 0
    bytes_pck = 0
    modelos = R.read_models(rsc)
    if a.filtro:
        modelos = [m for m in modelos if a.filtro in m.name]
    if a.limite:
        modelos = modelos[:a.limite]

    for mo in modelos:
        bs = batches_of(rsc, mo, a.lod)
        if not bs:
            continue
        mesh, texturas = mesh_from_batches(rsc, bs)
        if mesh is None:
            continue
        for gi, tex in enumerate(texturas):
            slot = mapa.get(os.path.basename(tex.replace('\\', '/')).lower(), 0)
            mesh.groups[gi]['material'] = slot
            mats.append((mo.name, gi, tex, slot))
        arq = nome_de_arquivo(mo.name) + '.mesh.pck'
        if not a.so_manifesto:
            bytes_pck += M.write_pck(mesh, os.path.join(out, arq), restrip=False)
        n_pck += 1
        n_grupo += len(mesh.groups)
        n_tri += mesh.stats()[3]

        chave = mo.name.lower()
        if chave in porTipo:
            for i in porTipo[chave]:
                linhas.append(('inst', mo.name,
                               [i.rot[0][0], i.rot[0][1], i.rot[0][2],
                                i.rot[1][0], i.rot[1][1], i.rot[1][2],
                                i.rot[2][0], i.rot[2][1], i.rot[2][2]],
                               i.pos, i.emin, i.emax, i.hood))
        else:
            c = next((c for c in comps if c.name.lower() == chave), None)
            linhas.append(('comp', mo.name, list(IDENT), (0.0, 0.0, 0.0),
                           c.emin if c else (0, 0, 0), c.emax if c else (0, 0, 0),
                           c.hood if c else '-'))

    place = os.path.join(out, cidade + '_place.tsv')
    with open(place, 'w') as f:
        f.write('# %s: gerado por mc2_to_pck.py a partir de %s\n'
                % (cidade, os.path.basename(rsc.path)))
        f.write('# extents_min\t%f\t%f\t%f\n' % tuple(emin))
        f.write('# extents_max\t%f\t%f\t%f\n' % tuple(emax))
        f.write('\t'.join(['kind', 'name', 'lod', 'part',
                           'm00', 'm01', 'm02', 'm10', 'm11', 'm12',
                           'm20', 'm21', 'm22', 'tx', 'ty', 'tz',
                           'eminx', 'eminy', 'eminz', 'emaxx', 'emaxy', 'emaxz',
                           'hood']) + '\n')
        for kind, nome, rot, pos, mn, mx, hood in linhas:
            f.write('%s\t%s\t0\tmain\t%s\t%s\t%s\t%s\t%s\n'
                    % (kind, nome,
                       '\t'.join('%f' % x for x in rot),
                       '\t'.join('%f' % x for x in pos),
                       '\t'.join('%f' % x for x in mn),
                       '\t'.join('%f' % x for x in mx),
                       # sem a extensao, que e como o place.tsv do mc2_port
                       # ja nomeava o hood
                       os.path.splitext(hood)[0]))

    tabela = os.path.join(out, cidade + '_materials.tsv')
    with open(tabela, 'w') as f:
        f.write('# modelo\tgrupo\ttextura_mc2\tslot\n')
        for nome, gi, tex, slot in mats:
            f.write('%s\t%d\t%s\t%d\n' % (nome, gi, tex, slot))

    distintas = len({t for _, _, t, _ in mats})
    print('%s' % out)
    print('  %d modelos -> .mesh.pck  (%d grupos, %d triangulos, %d bytes)'
          % (n_pck, n_grupo, n_tri, bytes_pck))
    print('  %s  %d linhas (%d comp, %d inst)'
          % (os.path.basename(place), len(linhas),
             sum(1 for l in linhas if l[0] == 'comp'),
             sum(1 for l in linhas if l[0] == 'inst')))
    print('  %s  %d grupos, %d texturas distintas, %d mapeadas para slot != 0'
          % (os.path.basename(tabela), len(mats), distintas,
             sum(1 for _, _, _, s in mats if s)))
    if not mapa:
        print('  AVISO: sem --materials, todo grupo saiu com slot 0. O nome da')
        print('  textura esta no _materials.tsv para voces mapearem.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
