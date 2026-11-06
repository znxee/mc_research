import os
import sys, json, struct, collections, pathlib
sys.path.insert(0,os.environ.get('MC_RESEARCH_ROOT', ''))
import mc3_bound
p=pathlib.Path(os.path.join(os.environ.get('MC3_ALPHA_HOSTFS', ''), 'ASSETS/resources/city/sd_bnd.pck'))
b=mc3_bound.Bound(p)
print(b.trees)
for kind,node in b.trees.items():
 print(kind,b.aabb(node),b.u32(node+0x4c),b.u32(node+0x50),b.materials(node))
 verts, polys = b.geometry(node)
 print(type(polys),polys[:2])
