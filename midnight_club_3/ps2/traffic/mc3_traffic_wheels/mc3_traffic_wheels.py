"""Stock VP wheel geometry and mounting points for optional ambient packs.

Read the named drwShaderModel chunks in rim/tire.ppf, not a guessed page
number and not the VP body LOD table. Bake their MLOD into the four existing
ambient wheel slots. Keep ambient rotation/steering, bone IDs and hierarchy.
Only the wheel positions/caches change; collision bounds and tuning stay VA.
Finishes are neutral Civic-atlas swatches, NOT player chrome/tire shaders.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
import re
import struct
import tempfile

import mc3_traffic_mlod as mlod

# Retail SLUS-21355: mcCarConfig::CalcTireWidth 4AF890 -> 4AFB00,
# GetRimScale 4AFAB0. The diameter of a default tire is twice the wheel
# record's mounting Y (mcCarCustom::GetDefaultTireDiameter 2CA780).
WIDTHS = (.195, .215, .235, .255, .275, .295, .315, .335, .355)
RIM_RATIOS = (.415532, .47585, .538852, .6, .66, .725, .782, .83)


def ppf_model(path, name, preferred_page=None):
    """Extract one named model as a synthetic PCK; texture chunks stay opaque."""
    data = Path(path).read_bytes()
    if data[:4] != b"pf05":
        raise ValueError("expected PS2 pf05 library: %s" % path)
    count, = struct.unpack_from("<I", data, 4)
    if not 0 < count <= (len(data)-12)//4:
        raise ValueError("invalid PPF descriptor count")
    needle = re.compile(re.escape(name.encode("ascii")) + rb"_[hHmMlL](?:_|\x00)")
    found = []
    for page_id in range(count):
        entry, = struct.unpack_from("<I", data, 12 + 4*page_id)
        base, size = (entry & 0x7FFFF)*0x800, (entry >> 19)*0x400
        if not size or base+size > len(data):
            raise ValueError("invalid PPF page %d" % page_id)
        page = data[base:base+size]
        if not needle.search(page):
            continue
        off = 0
        while off+32 <= len(page):
            va, _, _, n, _, kind, _, _ = struct.unpack_from("<8I", page, off)
            if not n:
                break
            if n < 32 or off+n > len(page):
                raise ValueError("invalid PPF chunk in page %d" % page_id)
            if kind == 0xFFFF0000 and needle.search(page[off+32:off+n]):
                header = bytearray(128)
                struct.pack_into("<4I", header, 0, va, 22, 1, n-32)
                found.append((bytes(header)+page[off+32:off+n], page_id))
            off += n
    if len(found)>1 and preferred_page is not None:
        found=[item for item in found if item[1]==preferred_page]
    if len(found) != 1:
        raise ValueError("expected one model %s in %s, found %d" % (name,path,len(found)))
    blob, page_id = found[0]
    return blob, dict(library=str(path), sha256=hashlib.sha256(data).hexdigest(),
                      model=name, page=page_id)


def model_geometry(blob, tire=False):
    """Read both MLOD submeshes; omit animated floating-poly blur cards."""
    out = []
    with tempfile.TemporaryDirectory(prefix="mc3_wheel_read_") as tmp:
        path = Path(tmp)/"model.pck"
        path.write_bytes(blob)
        p = mlod.embed.Pck(str(path))
        group = p.F(p.U(0x94))  # drwShaderModel +14 = MLOD
        if not p.inside(group+12):
            raise ValueError("wheel model has no MLOD")
        count, arr = p.U16(group+2), p.F(p.U(group+8))
        if not 0 < count <= 32 or not p.inside(arr+4*count-1):
            raise ValueError("invalid wheel MLOD table")
        view = mlod.shader_transplant.Pck(p)
        shaders = mlod.shader_transplant.read_shader_group(view,view.pointer(0x88))
        for k in range(count):
            mesh = mlod._read_piece(mlod._standalone_piece(p,p.U(arr+4*k)))
            for gr in mesh.groups:
                entry = shaders.entries[gr['material']]
                name = entry.name if entry else "unnamed_wheel"
                if name == "wheel_floating_poly.shadert":
                    continue
                dark = tire or name == "wheel_inner.shadert"
                for strip in gr['strips']:
                    out.append((dark, mesh.scale, strip))
    if not out:
        raise ValueError("empty static MLOD wheel")
    return out


def stock_setup(vp_path, vehicle_dir, tune_dir):
    """Resolve stock model names from customwheels + carcfg, anchors from VP."""
    vp_path, vehicle_dir, tune_dir = map(Path,(vp_path,vehicle_dir,tune_dir))
    name = vp_path.stem.removesuffix("_o")
    cfg_path = tune_dir/"customdata"/(name+".carcfg")
    cfg = {k:int(v) for k,v in re.findall(r"^\s*(\w+)\s+(-?\d+)\s*$",
                                            cfg_path.read_text(), re.M)}
    catalog_path = tune_dir/"customdata/customwheels.txt"
    catalog = re.sub(r';[^\n]*', '', catalog_path.read_text())
    def choice(section, index):
        match = re.search(r"\b"+section+r"\s*\{([^}]+)\}", catalog)
        if not match: raise ValueError("missing wheel catalog section "+section)
        names = re.findall(r"\bwhld?_\w+",match[1])
        if not 0 <= index < len(names): raise ValueError("wheel catalog index out of range")
        return names[index]
    rim_name = choice("rims",cfg['RimMdlIdx'])
    tire_name = choice("tires",cfg['TireMdlIdx'])
    rim_blob, rim_report = ppf_model(vehicle_dir/"rim.ppf",rim_name)
    # Several tire pages reuse the black tire geometry's H/b1/b2 names;
    # page zero is the black BFG tire, not eight independently named models.
    tire_blob, tire_report = ppf_model(vehicle_dir/"tire.ppf",tire_name,
                                      0 if tire_name=='whl_tir_bfghrch_blk' else None)
    p = mlod.embed.Pck(str(vp_path))
    obj = p.F(p.U(0x88))
    count, arr = p.U(obj+0x3814),p.F(p.U(obj+0x3810))
    if count != 4 or not p.inside(arr+28*count-1):
        raise ValueError("only four-wheel VP cars supported")
    bones = {n[2]:n for n in p.skel_nodes()}
    anchors = []
    for k in range(count):
        ordinal, _, bone, _, x,y,z = struct.unpack_from('<4I3f',p.data,arr+28*k)
        if ordinal != k or bone not in bones:
            raise ValueError("invalid VP wheel record")
        anchor = bones[bone][6]
        if max(abs(a-b) for a,b in zip(anchor,(x,y,z))) > 1e-4 or anchor[1] <= 0:
            raise ValueError("wheel record and VP skeleton disagree")
        anchors.append(anchor)
    wi=[cfg['TireWidth%d'%a] for a in range(2)]
    ri=[cfg['TireProfile%d'%a] for a in range(2)]
    if any(not 0<=v<len(WIDTHS) for v in wi) or any(not 0<=v<len(RIM_RATIOS) for v in ri):
        raise ValueError('unsupported wheel width/profile; automatic profile -1 is not baked')
    widths = [WIDTHS[v] for v in wi]
    ratios = [RIM_RATIOS[v] for v in ri]
    return dict(anchors=anchors,widths=widths,ratios=ratios,
                rim=model_geometry(rim_blob),tire=model_geometry(tire_blob,True),
                report=dict(rim=rim_report,tire=tire_report,config=str(cfg_path),
                            config_sha256=hashlib.sha256(cfg_path.read_bytes()).hexdigest(),
                            catalog=str(catalog_path),catalog_sha256=hashlib.sha256(catalog_path.read_bytes()).hexdigest(),
                            widths=widths,rim_ratios=ratios,anchors=anchors,
                            finish="neutral ambient swatches; no player wheel shader",
                            diameter="twice donor stock mounting Y; stock-size approximation"))


def wheel_mesh(setup, ordinal, material):
    """Bake scale + side orientation, keeping the rotation pivot at local zero."""
    mesh = mlod.convert.Mesh()
    mesh.scale = 1/32768
    axle = ordinal//2
    diameter = 2*setup['anchors'][ordinal][1]
    ratio, width = setup['ratios'][axle],setup['widths'][axle]
    groups = {True:[],False:[]}
    for is_tire, items in ((False,setup['rim']),(True,setup['tire'])):
        for dark, scale, strip in items:
            dst=[]
            for v in strip:
                x,y,z = [c*scale for c in v.pos]
                sx, sr = 2*width, diameter*(1 if is_tire else ratio)
                if is_tire:
                    # PPF base profile is RIM_RATIOS[0]; its sidewall's inner
                    # ring must meet this car's rim, not leave a large gap.
                    radius=math.hypot(y,z)
                    if abs(radius-RIM_RATIOS[0]/2) < .0001:
                        sr *= ratio/RIM_RATIOS[0]
                side = -1 if ordinal%2 else 1
                pos = (x*sx*side,y*sr,z*sr*side) # right = rotate Y by pi, NOT reflect
                raw = tuple(round(c/mesh.scale) for c in pos)
                if any(c < -32768 or c > 32767 for c in raw):
                    raise ValueError("wheel coordinate overflows s16")
                nx,ny,nz=v.nrm
                normal=(nx/sx*side,ny/sr,nz/sr*side)
                norm=math.sqrt(sum(c*c for c in normal)) or 1
                uv=mlod._civic_share_uv('rubber.shadert' if dark else 'chrome.shadert')
                dst.append(mlod.convert.Vtx(raw,uv,tuple(c/norm for c in normal),v.skip,cpv=v.cpv))
            groups[dark].append(dst)
    mesh.groups=[dict(material=material,strips=strips) for strips in groups.values() if strips]
    return mesh


def mount_fields(tp, vehicle):
    """Typed position fields only; never search/replace coincident float bytes."""
    p=tp.pck;root=dict(tp.roots())[vehicle]
    objects=p.F(p.U(0xB0));matches=[]
    for k in range(p.U16(0xB4)):
        obj=p.F(p.U(objects+4*k))
        if p.inside(obj+676) and p.U(obj+676)==p.V(root):matches.append(obj)
    if len(matches)!=1:raise ValueError("ambient vehicle object is ambiguous")
    obj=matches[0];rec=p.F(p.U(obj+816));count=p.U(obj+820)
    if count!=4:raise ValueError("expected four ambient wheel records")
    skel=p.F(p.U(obj+680));live=p.F(p.U(skel+4));matrices=p.F(p.U(skel+8))
    nodes={n['bone']:n for name,ns in tp.skeletons() if name==vehicle for n in ns}
    pieces={pc['piece_id']:pc for pc in tp.pieces() if pc['vehicle']==vehicle}
    fields=[]
    for k in range(count):
        ordinal,_,bone,_=struct.unpack_from('<4I',p.data,rec+28*k)
        if ordinal!=k or bone not in nodes or bone not in pieces:
            raise ValueError("ambient wheel record lacks bone/mesh")
        node=nodes[bone];idx=node['index'];a=node['off']
        fields.append(dict(ordinal=k,bone=bone,slot=pieces[bone]['slot'],
                           piece_index=pieces[bone]['index'],
                           position_fields=[a,a+0x20,live+64*idx+36,
                                            matrices+48*idx+36,rec+28*k+16,obj+876+12*k]))
    if len({f['bone'] for f in fields})!=4:raise ValueError("duplicate wheel bone")
    return obj, fields


def insert(tp, vehicle, setup):
    root=dict(tp.roots())[vehicle]
    view=mlod.shader_transplant.Pck(tp.pck)
    group=mlod.shader_transplant.read_shader_group(view,view.pointer(root+8))
    body=[e.index for e in group.entries if e and e.name=='ambient_body.shadert']
    if len(body)!=1:raise ValueError("wheel swatches need exactly one bound ambient_body")
    obj,fields=mount_fields(tp,vehicle)
    report=dict(setup['report']);report['wheels']=fields
    allowed=[]
    with tempfile.TemporaryDirectory(prefix='mc3_wheel_write_') as tmp:
        for f in fields:
            ordinal=f['ordinal'];anchor=setup['anchors'][ordinal]
            for off in f['position_fields']:
                if not tp.pck.inside(off+11):raise ValueError("wheel position leaves pack")
                old=struct.unpack_from('<3f',tp.data,off)
                # All six caches must already be coherent; Matrix34 differs
                # by a few float32 ULPs. Fail rather than modify an unknown layout.
                base=struct.unpack_from('<3f',tp.data,f['position_fields'][0])
                if max(abs(a-b) for a,b in zip(old,base))>.0001:
                    raise ValueError("incoherent ambient wheel cache at %#x"%off)
                allowed.extend(range(off,off+12))
            mesh=wheel_mesh(setup,ordinal,body[0]);path=Path(tmp)/'wheel.pck'
            mlod.convert.write_pck(mesh,str(path),block_style='traffic',restrip=False)
            # Appending invalidates pieces() and its scan order can change.
            # The serialized slot, unlike the transient list index, is stable.
            candidates=[pc for pc in tp.pieces() if pc.get('slot')==f['slot']]
            if len(candidates)!=1:raise ValueError("wheel slot disappeared")
            va,_,n=tp.replace(candidates[0]['index'],str(path),material=None)
            f.update(new_va=va,stats=mesh.stats(),appended_bytes=n,anchor=anchor)
            # Preserve IDs/parents/tags: only translation components change.
            for off in f['position_fields']:struct.pack_into('<3f',tp.data,off,*anchor)
            allowed.extend(range(f['slot'],f['slot']+4))
    # Cached visual rolling/radius and axle/track measures, derived by native
    # aiAmbientType::LoadAndInitialization 21F9D8. No bounds/tunes replaced.
    anchors=setup['anchors']
    for rel,value in [(632,128/(anchors[0][1]*2*math.pi)),
                      (664,-anchors[0][2]),
                      (996,1/(abs(anchors[0][0])+abs(anchors[1][0])))]:
        struct.pack_into('<f',tp.data,obj+rel,value);allowed.extend(range(obj+rel,obj+rel+4))
    report['changed_prefix_offsets']=sorted(set(allowed))
    return report
