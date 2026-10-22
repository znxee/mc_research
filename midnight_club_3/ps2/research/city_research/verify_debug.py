"""Compare a native city dump against existing canonical PS2 toolkit contracts.

Read-only external assets; generated dumps stay outside source control.
"""
import os
import argparse, collections, importlib.util, json, math, pathlib, struct, sys


def verify(package, dump, toolkit, center=(358, 0, -42), radius=200):
    sys.path.insert(0, str(toolkit))
    import mc3_vifpos
    import mc3_view
    d = pathlib.Path(package).read_bytes()
    u = lambda p: struct.unpack_from('<I', d, p)[0]
    h = lambda p: struct.unpack_from('<H', d, p)[0]
    vec = lambda p: struct.unpack_from('<3f', d, p)
    off = lambda va: va-u(0)+128
    native = json.loads(pathlib.Path(dump).read_text())
    palette = [tuple(math.floor(max(0, min(1, v))*128+.5) for v in struct.unpack_from('<4f',d,off(u(128+44))+16*i)) for i in range(256)]
    selected = []
    hoods = off(u(128+24))
    for hi in range(u(128+20)):
        e = hoods+20*hi
        for count, array, stride, inst in ((u(e+4),u(e+8),28,False),(u(e+12),u(e+16),96,True)):
            for i in range(count):
                co = off(array)+i*stride
                cd = off(u(co+12))
                matrix = struct.unpack_from('<12f',d,co+32) if inst else (1,0,0,0,1,0,0,0,1,*vec(cd+44))
                rr = struct.unpack_from('<f',d,cd+56)[0]
                if math.hypot(matrix[9]-center[0],matrix[11]-center[2]) > radius+rr:
                    continue
                mesh = next((u(cd+60+4*j) for j in range(10) if u(cd+60+4*j)),0)
                if mesh:
                    selected.append((co,cd,off(mesh),matrix))
    assert len(selected)==len(native['pieces'])
    errors = collections.defaultdict(float)
    totals = collections.Counter()
    for (co,cd,mo,matrix), piece in zip(selected,native['pieces']):
        groups = off(u(mo+16))
        cpvgroups = off(u(off(u(mo+20)))) if h(mo+10) and u(mo+20) else None
        expected=[]
        for gi in range(h(mo+8)):
            blocklist=off(u(groups+8*gi))
            colorvectors=off(u(cpvgroups+8*gi+4)) if cpvgroups else None
            for bi in range(h(groups+8*gi+4)):
                bp,qw,nv=struct.unpack_from('<IHH',d,blocklist+8*bi)
                start=off(bp)
                packet=d[start:start+qw*16]
                positions=mc3_vifpos.decode_batches(packet)
                walked=mc3_view._vif_walk(d,start,qw*16)
                commands=list(mc3_vifpos._commands(packet))
                cpv=off(u(colorvectors+4*bi)) if colorvectors else None
                vertex_offset=0
                for batchindex, local in enumerate(positions):
                    count=len(local)
                    normals=None
                    uv=None
                    for rel,cmd,data,n in walked[batchindex]:
                        if rel==2 and (cmd&0x6f) in (0x6a,0x6e):
                            step=3 if (cmd&0x6f)==0x6a else 4
                            normals=[struct.unpack_from('<3b',d,data+step*j) for j in range(n)]
                        if rel==50:
                            basic=cmd&0x6f
                            if basic in (0x65,0x6d):
                                step=4 if basic==0x65 else 8
                                uv=[tuple(v/4096 for v in struct.unpack_from('<2h',d,data+step*j)) for j in range(n)]
                            elif basic==0x66:
                                state=next(c for c in commands if c['payload']==data-start)
                                row=list(state['row'])
                                uv=[]
                                for j in range(n):
                                    raw=struct.unpack_from('<2b',d,data+2*j)
                                    if state['mode']==2:
                                        raw=tuple(raw[k]+row[k] for k in range(2))
                                        row[:2]=raw
                                    uv.append(tuple(v/4096 for v in raw))
                    assert uv is not None and len(uv)==count
                    world=[[matrix[9+k]+p[0]*matrix[k]+p[1]*matrix[3+k]+p[2]*matrix[6+k] for k in range(3)] for p in local]
                    for i in range(2,count):
                        if normals and normals[i][0]&1:
                            continue
                        a,b,c=(i-2,i-1,i) if i%2==0 else (i-1,i-2,i)
                        if world[a]==world[b] or world[b]==world[c] or world[a]==world[c]:
                            continue
                        face=mc3_view._cross([world[b][k]-world[a][k] for k in range(3)], [world[c][k]-world[a][k] for k in range(3)])
                        length=math.sqrt(sum(v*v for v in face))
                        face=tuple(v/length for v in face) if length else (0,0,0)
                        triangle=[]
                        for index in (a,b,c):
                            normal=tuple(sum(normals[index][j]/127*matrix[3*j+k] for j in range(3)) for k in range(3)) if normals else face
                            color=palette[d[cpv+vertex_offset+index]] if cpv else (128,128,128,128)
                            triangle.append([*world[index],*normal,*uv[index],*color])
                        expected.append(triangle)
                    vertex_offset+=count
                    totals['packets']+=1
                    totals['source_vertices']+=count
        got=native['triangles'][piece['first_triangle']:piece['first_triangle']+piece['triangle_count']]
        assert len(expected)==len(got),(piece['name'],len(expected),len(got))
        for et,gt in zip(expected,got):
            for ev,gv in zip(et,gt['vertices']):
                for label,lo,hi in (('position',0,3),('normal',3,6),('uv',6,8),('color',8,12)):
                    
                    error=max(abs(ev[k]-gv[k]) for k in range(lo,hi))
                    if label=='normal' and error>.01 and totals['bad_normals']<10:print(piece['name'],ev,gv);totals['bad_normals']+=1
                    errors[label]=max(errors[label],error)
        totals['triangles']+=len(got)
    assert totals['triangles']==len(native['triangles'])
    assert errors['position']<.0002 and errors['normal']<.01 and errors['uv']<1e-7 and errors['color']==0,errors
    return {'components':len(selected),**totals,'maximum_errors':dict(errors)}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package',type=pathlib.Path)
    parser.add_argument('dump',type=pathlib.Path)
    parser.add_argument('--toolkit',type=pathlib.Path,default=pathlib.Path(os.environ.get('MC_RESEARCH_ROOT', '')))
    parser.add_argument('--out',type=pathlib.Path)
    args=parser.parse_args()
    result=verify(args.package,args.dump,args.toolkit)
    print(json.dumps(result,indent=2))
    if args.out:
        args.out.write_text(json.dumps(result,indent=2)+'\n')
