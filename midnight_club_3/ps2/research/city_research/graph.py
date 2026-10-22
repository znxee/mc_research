import os
import sys, struct, json, pathlib, collections, math
sys.path.insert(0,os.environ.get('MC_RESEARCH_ROOT', ''))
import mc3_vifpos, mc3_view, mc3_bound
root=pathlib.Path(os.path.join(os.environ.get('MC3_ALPHA_HOSTFS', ''), 'ASSETS'))
p=root/'resources/city/sd_midnight_clear.pck';d=p.read_bytes();u=lambda o:struct.unpack_from('<I',d,o)[0];h=lambda o:struct.unpack_from('<H',d,o)[0];f=lambda o:struct.unpack_from('<f',d,o)[0];base=u(0)-128;off=lambda v:v-base
center=(358,0,-42); radius=200
selected=[]; cmds=collections.Counter(); shg=set(); files=collections.Counter(); triangles=0
hp=off(u(128+24));nh=u(128+20)
for hi in range(nh):
 e=hp+hi*20
 for cnt,arr,stride,inst in [(u(e+4),u(e+8),28,False),(u(e+12),u(e+16),96,True)]:
  for i in range(cnt):
   co=off(arr)+i*stride;cd=off(u(co+12));name=d[cd+112:cd+132].split(b'\0')[0].decode('ascii','replace')
   mat=struct.unpack_from('<12f',d,co+32) if inst else (1,0,0,0,1,0,0,0,1,*struct.unpack_from('<3f',d,cd+44))
   rr=f(cd+56);distance=math.hypot(mat[9]-center[0],mat[11]-center[2])
   if distance>radius+rr:continue
   meshes=[u(cd+60+4*j) for j in range(10)]; mesh=next((v for v in meshes if v),0)
   if not mesh:continue
   mo=off(mesh);grp=d[co+10];shg.add(grp);sg=off(u(128+12))+grp*16;sa=off(u(sg+4))
   selected.append(dict(name=name,component=co,data=cd,mesh=mo,group=grp,inst=inst,center=mat[9:],radius=rr))
   mt=off(u(mo+12));gt=off(u(mo+16))
   for g in range(h(mo+8)):
    material=h(mt+2*g);s=off(u(sa+4*material)) if u(sa+4*material) else None
    if s and u(s+8):
     tex=off(u(s+8))
     if d[tex+4]==2:tex=off(u(tex+12))
     if d[tex+4]==0:
      for l in range(d[tex+134]):
       ptr,po,pw=struct.unpack_from('<3I',d,tex+72+12*l);files[(ptr!=0,pw>>23)]+=1
    bl=off(u(gt+8*g));n=h(gt+8*g+4)
    for b in range(n):
     bp,qw,nv=struct.unpack_from('<IHH',d,bl+8*b);data=d[off(bp):off(bp)+qw*16]
     for c in mc3_vifpos._commands(data):cmds[(c['cmd'],c['mode'],c['imm'])]+=1
     positions=mc3_vifpos.decode_batches(data)
     triangles+=sum(max(0,len(ps)-2) for ps in positions)
print('selected',len(selected),'tri_beforeADC',triangles,'shadergroups',shg,'files',files)
print('commands',cmds)
print('selectedfirst',selected[:20])
pathlib.Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/city_research/native_graph.json')).write_text(json.dumps(dict(source=str(p),center=center,radius=radius,selected=selected,commands={str(k):v for k,v in cmds.items()},stream_files={str(k):v for k,v in files.items()}),indent=2))
