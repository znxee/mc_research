import os
import sys,math
sys.path.insert(0,os.environ.get('MC_RESEARCH_ROOT', ''));import mc3_bound
b=mc3_bound.Bound(os.path.join(os.environ.get('MC3_ALPHA_HOSTFS', ''), 'ASSETS/resources/city/sd_bnd.pck'))
for kind,node in b.trees.items():
 verts,polys=b.geometry(node)
 for cx,cz in [(358,-42),(379.563843,-96.317802),(360,-50),(835.25,232.22),(402,700),(400,-42)]:
  out=[]
  for i,(normal,_,idx,_) in enumerate(polys):
   if normal[1]<.35:continue
   for ids in [(idx[0],idx[1],idx[2])]+([(idx[0],idx[2],idx[3])] if len(idx)==4 else []):
    a,bb,c=[verts[j] for j in ids];den=(bb[2]-c[2])*(a[0]-c[0])+(c[0]-bb[0])*(a[2]-c[2])
    if abs(den)<1e-7:continue
    u=((bb[2]-c[2])*(cx-c[0])+(c[0]-bb[0])*(cz-c[2]))/den;v=((c[2]-a[2])*(cx-c[0])+(a[0]-c[0])*(cz-c[2]))/den;w=1-u-v
    if min(u,v,w)>=-1e-4:out.append((i,round(u*a[1]+v*bb[1]+w*c[1],4),normal))
  print(kind,cx,cz,out)
