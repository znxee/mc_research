"""Read-only integration checks for staged opponent traffic artifacts."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import unittest

import mc3_traffic_opponents as build
import mc3_traffic_mlod as mlod
import mc3_traffic_wheels as wheels
import tempfile

ROOT = Path(__file__).resolve().parent
MANIFEST = Path(os.environ.get("MC3_TRAFFIC_TEST_MANIFEST",
                              ROOT / "output/traffic_opponents/manifest.json"))


class TrafficOpponents(unittest.TestCase):
    def test_reject_invalid_ppf(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'bad.ppf';path.write_bytes(b'bad!'+bytes(16))
            with self.assertRaisesRegex(ValueError,'pf05'):wheels.ppf_model(path,'rim')

    def test_reject_original_overwrite(self):
        with self.assertRaisesRegex(ValueError, "original"):
            build.build("same.pck", ".", "same.pck")

    def test_reject_unbound_atlas(self):
        with self.assertRaisesRegex(ValueError, "only valid"):
            mlod.insert("absent.pck", "absent_o.pck", "va_tacoma_sh", "out.pck",
                        uv_profile="civic-share")
        with self.assertRaisesRegex(ValueError, "body_atlas requires"):
            mlod.insert("absent.pck", "absent_o.pck", "va_tacoma_sh", "out.pck",
                        uv_profile="civic-share", body_atlas="unrelated")

    def test_module_hook(self):
        d=(ROOT/"output/traffic_opponents/traffic_opponents.mod").read_bytes()
        magic,version,entry,size,nrel,base,hooks,nhooks=struct.unpack_from("<8I",d)
        self.assertEqual((magic,version,nhooks),(0x4D43334D,2,1))
        self.assertLess(entry,size)
        self.assertEqual(struct.unpack_from("<I",d,32+hooks)[0],0x21E04C)
        self.assertEqual(len(d),32+size+12*nrel)

    def test_artifacts(self):
        reports=json.loads(MANIFEST.read_text())
        self.assertTrue(reports)
        for report in reports:
            with self.subTest(city=report["source"]):
                src=Path(report["source"]);out=Path(report["output"])
                a=mlod.traffic.TrafficPck(str(src)); b=mlod.traffic.TrafficPck(str(out))
                self.assertEqual(build.sha(src),report["source_sha256"])
                self.assertEqual(build.sha(out),report["sha256"])
                self.assertEqual(b.pck.U(4),60)
                self.assertEqual(b.pck.U(0xC),len(b.data)-0x80)
                self.assertEqual(len(b.data)%16,0)
                self.assertEqual(a.roots(),b.roots())
                roles={r["vehicle"] for r in report["replacements"]}
                wheel_slots={w['slot'] for r in report['replacements'] if r.get('stock_wheels')
                             for w in r['stock_wheels']['wheels']}
                wheel_bones={r['vehicle']:{w['bone'] for w in r['stock_wheels']['wheels']}
                             for r in report['replacements'] if r.get('stock_wheels')}
                for (an,ans),(bn,bns) in zip(a.skeletons(),b.skeletons()):
                    self.assertEqual(an,bn);self.assertEqual(len(ans),len(bns))
                    for old,new in zip(ans,bns):
                        if old['bone'] in wheel_bones.get(an,set()):
                            new=dict(new);new['anchor']=old['anchor']
                        self.assertEqual(old,new)
                for off,(vehicle,slot,index,bone) in a.vehicles().items():
                    if (vehicle in roles and a.pck.U16(off+6)==0) or slot in wheel_slots:
                        self.assertGreaterEqual(b.pck.F(b.pck.U(slot)),len(a.data))
                    else:
                        self.assertEqual(a.pck.U(slot),b.pck.U(slot))
                # Only header length, body slots and per-vehicle group owners
                # may differ in the original byte range. No raw VA-range fixup.
                allowed=set(range(12,16))
                for _,(vehicle,slot,_,_) in a.vehicles().items():
                    if vehicle in roles and a.pck.U16(a.pck.F(a.pck.U(slot))+6)==0:
                        allowed.update(range(slot,slot+4))
                for vehicle,root in a.roots():
                    if vehicle not in roles: continue
                    allowed.update(range(root+8,root+12))
                for r in report['replacements']:
                    wr=r.get('stock_wheels')
                    if not wr:continue
                    donor=mlod.embed.Pck(r['donor'])
                    dobj=donor.F(donor.U(0x88));darr=donor.F(donor.U(dobj+0x3810))
                    donor_nodes={n[2]:n for n in donor.skel_nodes()}
                    for w in wr['wheels']:
                        dbone=donor.U(darr+28*w['ordinal']+8)
                        self.assertEqual(list(donor_nodes[dbone][6]),w['anchor'])
                    for item in (wr['rim'],wr['tire']):
                        self.assertEqual(build.sha(item['library']),item['sha256'])
                    for key in ('config','catalog'):
                        self.assertEqual(build.sha(wr[key]),wr[key+'_sha256'])
                    allowed.update(wr['changed_prefix_offsets'])
                    self.assertEqual(len(wr['wheels']),4)
                    _,typed=wheels.mount_fields(a,r['vehicle'])
                    for original,w in zip(typed,wr['wheels']):
                        self.assertEqual(original['position_fields'],w['position_fields'])
                        self.assertEqual(original['slot'],w['slot'])
                        self.assertEqual(b.pck.U(w['slot']),w['new_va'])
                        off=b.pck.F(w['new_va'])
                        self.assertEqual(b.pck.U(off),mlod.traffic.RUNTIME_MESH_VTABLE)
                        self.assertEqual(b.pck.U16(off+6),w['bone'])
                        self.assertGreater(w['stats'][3],20)
                        for field in w['position_fields']:
                            actual=struct.unpack_from('<3f',b.data,field)
                            for x,y in zip(actual,w['anchor']):self.assertAlmostEqual(x,y,places=5)
                        mesh=mlod._read_piece(mlod._standalone_piece(b.pck,w['new_va']))
                        self.assertEqual(mesh.stats()[3],w['stats'][3])
                        self.assertTrue(all(abs(c*mesh.scale)<1 for gr in mesh.groups
                                            for st in gr['strips'] for v in st for c in v.pos))
                unexpected=[i for i,(x,y) in enumerate(zip(a.data,b.data)) if x!=y and i not in allowed]
                self.assertFalse(unexpected,unexpected[:10])
                atlas_resources=[]
                for r in report["replacements"]:
                    self.assertTrue(r["donor"].endswith("_o.pck"))
                    self.assertGreater(r["stats"][3],0)
                    self.assertTrue(r["parts"])
                    for resource in r["atlas_bindings"].values():
                        self.assertGreaterEqual(b.pck.F(resource),len(a.data))
                        atlas_resources.append(resource)
                self.assertEqual(len(atlas_resources),len(set(atlas_resources)),
                                 "ambient Place must never relocate one shared resource twice")
                self.assertLess(len(b.data)-len(a.data),512*1024)


if __name__=="__main__":
    unittest.main()
