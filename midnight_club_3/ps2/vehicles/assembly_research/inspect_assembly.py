import os
import sys,json,struct
from pathlib import Path
sys.path.insert(0,os.environ.get('MC_RESEARCH_ROOT', ''))
import mc3_pck_embed as e
p=e.Pck(os.path.join(os.environ.get('MC3_ALPHA_HOSTFS', ''), 'ASSETS/resources/vehicle/vp_350z_04/vp_350z_04.pck'))
model=p.F(p.U(0x88));shader=p.F(p.U(model+0xd8));lod=p.F(p.U(shader+16))
nodes=p.skel_nodes(); byid={x[2]:x for x in nodes}
slots=p.slots(p.U(shader+16))
cats={'FrontBumperIdx':(0x2afc,0x3174),'RearBumperIdx':(0x2b5c,0x3178),'SideSkirtIdx':(0x2bbc,0x317c),'SpoilerIdx':(0x2c1c,0x3180),'HoodIdx':(0x2c7c,0x3184),'BlowerIdx':(0x2cdc,0x3188),'TaillightGeomIdx':(0x2e34,0x3190),'BodyIdx':(0x2fb4,0x31a0),'BrushGuardIdx':(0x2fd4,0x31a4),'FrontGrillIdx':(0x3034,0x31a8),'OneShotKitIdx':(0x3094,0x31ac),'WheelieBarIdx':(0x30f4,0x31b0),'Headlight':(0x2dd4,0x318c)}
report={'model_file_offset':model,'shader_file_offset':shader,'lod_file_offset':lod,'skeleton':nodes,'slots':slots,'categories':{}}
for k,(off,cnt) in cats.items():
 ids=[p.U(model+off+4*i) for i in range(p.U(model+cnt))]
 report['categories'][k]={'ids':ids,'selected_index':0,'selected_node':byid.get(ids[0]) if ids else None}
for slot in slots:
 if slot[1]:print('embedded',slot, 'node',byid.get(slot[3]))
for k,v in report['categories'].items(): print(k,v)
Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/assembly_research/350z_structure.json')).write_text(json.dumps(report,indent=2))
print('skeleton anchor1/anchor2 differences',[(x[1],x[6],struct.unpack_from('<3f',p.data,x[7]+0x20)) for x in nodes if x[6]!=struct.unpack_from('<3f',p.data,x[7]+0x20)][:20])
