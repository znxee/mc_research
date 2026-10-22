import os
from pathlib import Path
h=Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'src/city/geometry.hpp'));s=h.read_text();s=s.replace('unsigned material=0,polygon=0;','unsigned material=0,polygon=0,tree=9;');h.write_text(s)
p=Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'src/city/geometry.cpp'));s=p.read_text();a=s.index('    auto pair=b.ptr(0x8c);std::size_t node=0;');e=s.index('    if(polygons)*polygons=selected;return result;',a)
s=s[:a]+'''    auto pair=b.ptr(0x8c);std::vector<CollisionTriangle> result;unsigned selected=0;
    for(unsigned slot=0;slot<2;++slot){auto wrapper=b.ptr(pair+4*slot),inner=b.ptr(wrapper+4),node=b.ptr(inner+12);unsigned tree=b.u8(node+4);
        if(tree!=9 && tree!=10)Bytes::fail("Unknown native collision tree");unsigned nv=b.u32(node+0x4c),np=b.u32(node+0x50);if(nv>1000000 || np>1000000)Bytes::fail("City collision limits");
        auto vertices=b.ptr(node+0x68),faces=b.ptr(node+0x6c),materials=b.ptr(node+0x70);b.range(vertices,std::size_t(nv)*12);b.range(faces,std::size_t(np)*32);
        for(unsigned i=0;i<np;++i){auto face=faces+32*i;unsigned count=b.u16(face+22)==0 && b.u16(face+30)==65535?3:4;std::array<Vec3,4> p{};Vec3 lo{},hi{};
            for(unsigned k=0;k<count;++k){auto index=b.u16(face+16+2*k);if(index>=nv)Bytes::fail("Collision vertex outside table");p[k]=b.vec(vertices+12*index);if(k==0)lo=hi=p[k];else for(unsigned a=0;a<3;++a){lo[a]=std::min(lo[a],p[k][a]);hi[a]=std::max(hi[a],p[k][a]);}}
            if(!intersects(lo,hi,center,radius))continue;auto n=b.vec(face);auto material=b.u32(materials+4*b.u8(face+12));++selected;
            result.push_back({{p[0],p[1],p[2]},n,material,i,tree});if(count==4)result.push_back({{p[0],p[2],p[3]},n,material,i,tree});
        }
    }
''' + s[e:];s=s.replace('GroundSample{y,t.normal,t.material,t.polygon}','GroundSample{y,t.normal,t.material,t.polygon,t.tree}')
p.write_text(s)
