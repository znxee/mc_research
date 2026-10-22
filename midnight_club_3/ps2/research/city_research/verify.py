import os
import sys,json,struct,math,pathlib,collections
sys.path.insert(0,os.environ.get('MC_RESEARCH_ROOT', ''));import mc3_vifpos,mc3_view,mc3_bound
rd=pathlib.Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/city_research'));meta=json.loads((rd/'native_graph.json').read_text());d=pathlib.Path(meta['source']).read_bytes();u=lambda o:struct.unpack_from('<I',d,o)[0];h=lambda o:struct.unpack_from('<H',d,o)[0];off=lambda v:v-u(0)+128
native=json.loads((rd/'city_geometry.json').read_text());triangles=native['triangles'];pieces=native['pieces'];cursor=0;maxerr=0.;counts=[];issues=[]
for comp,piece in zip(meta['selected'],pieces):
 co=comp['component'];cd=comp['data'];mo=comp['mesh'];M=struct.unpack_from('<12f',d,co+32) if comp['inst'] else (1,0,0,0,1,0,0,0,1,*struct.unpack_from('<3f',d,cd+44))
 gt=off(u(mo+16));expected=[]
 for gi in range(h(mo+8)):
  bl=off(u(gt+8*gi))
  for bi in range(h(gt+8*gi+4)):
   bp,qw,nv=struct.unpack_from('<IHH',d,bl+8*bi);b=off(bp);pos=mc3_vifpos.decode_batches(d[b:b+qw*16]);walked=mc3_view._vif_walk(d,b,qw*16)
   for li,positions in enumerate(pos):
    adc=None
    for rel,cmd,data,n in walked[li]:
     if rel==2 and (cmd&0x6f) in (0x6a,0x6e):
      adc=[bool(d[data+(3 if (cmd&0x6f)==0x6a else 4)*i]&1) for i in range(n)]
      break
    world=[[M[9+k]+p[0]*M[k]+p[1]*M[3+k]+p[2]*M[6+k] for k in range(3)] for p in positions]
    for i in range(2,len(world)):
     if adc and adc[i]:continue
     a,bb,c=(i-2,i-1,i) if i%2==0 else (i-1,i-2,i)
     if world[a]==world[bb] or world[bb]==world[c] or world[a]==world[c]:continue
     expected.append([world[a],world[bb],world[c]])
 got=triangles[piece['first_triangle']:piece['first_triangle']+piece['triangle_count']]
 if len(expected)!=len(got):issues.append([comp['name'],len(expected),len(got)]);continue
 for et,gt in zip(expected,got):
  for ev,gv in zip(et,gt['vertices']):maxerr=max(maxerr,*[abs(ev[k]-gv[k]) for k in range(3)])
 counts.append(len(got));cursor+=len(got)
print('compared',len(counts),'triangles',cursor,'maxworlderror',maxerr,'issues',issues)
b=mc3_bound.Bound(pathlib.Path(meta['source']).parent/'sd_bnd.pck');cn=json.loads((rd/'collision.json').read_text());print('collisiontriangles',len(cn))
report=dict(components=len(counts),triangles=cursor,maximum_world_coordinate_error=maxerr,issues=issues,collision_triangles=len(cn))
(rd/'differential.json').write_text(json.dumps(report,indent=2))
assert not issues and maxerr<.0002
