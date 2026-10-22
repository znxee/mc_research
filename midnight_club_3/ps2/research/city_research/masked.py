import os
exec(open(os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/city_research/graph.py')).read().split("print('selected'")[0])
for comp in selected:
 if comp['component'] not in [3836164,3836192]:continue
 mo=comp['mesh'];gt=off(u(mo+16));print(comp)
 for gi in range(h(mo+8)):
  bl=off(u(gt+8*gi))
  for bi in range(h(gt+8*gi+4)):
   bp,qw,nv=struct.unpack_from('<IHH',d,bl+8*bi);bd=d[off(bp):off(bp)+qw*16];print('block',gi,bi,off(bp),qw,nv)
   for c in mc3_vifpos._commands(bd):
    print(c, bd[c['payload']:c['payload']+min(c['size'],16)].hex())
