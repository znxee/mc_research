import os
from pathlib import Path
import json,struct,collections,sys,hashlib
sys.path.insert(0,os.environ.get('MC_RESEARCH_ROOT', ''))
import mc3_shader_diff as canonical
source=Path(os.path.join(os.environ.get('MC3_ALPHA_HOSTFS', ''), 'ASSETS/resources/city/sd_midnight_clear.pck'))
p=canonical.Pck(str(source));slots=canonical.all_slots(p)
catalog={}
for slot in slots:
    f=p.u32(slot.off+4);n=(f>>22)&7
    catalog[(f,tuple(p.u32(slot.off+8+4*i) for i in range(n)))]=slot
manifest=json.loads(Path('research/city_shaders/scene/materials/materials.json').read_text())
counts=collections.Counter();checked=0;numeric=0;texture_params=0
for m in manifest['materials']:
    if m['registry_id'] is None: continue
    key=(m['flags'],tuple(v['raw'] for v in m['parameters']))
    assert key in catalog,m['name']
    slot=catalog[key];flags=p.u32(slot.off+4)
    assert m['type']==slot.tag and m['registry_id']==((flags>>15)&127) and m['draw_bucket']==((flags>>7)&31)
    linked={info['off'] for _,info in canonical.linked_infos(p,slot)}
    for i,parameter in enumerate(m['parameters']):
        assert parameter['is_texture']==bool((flags>>(25+i))&1)
        if parameter['is_texture']:
            t=manifest['textures'][parameter['texture']]
            offset=int(t['name'].removeprefix('native_texture_'))
            assert offset in linked,(slot,offset,linked)
            texture_params+=1
        else:
            expected=struct.unpack('<f',struct.pack('<I',parameter['raw']))[0]
            assert abs(parameter['value']-expected)<1e-7
            numeric+=1
    if m['registry_id']==4:
        assert len(m['passes'])==2
        assert m['passes'][1]['texture']==m['parameters'][1]['texture']
        assert m['passes'][1]['uv_scale']==[v['value'] for v in m['parameters'][2:4]]
        assert m['passes'][0]['gs_alpha']==10 and m['passes'][1]['gs_alpha']==68
        assert m['passes'][1]['write_alpha'] is False
    checked+=1;counts[m['template']]+=1
report={'canonical_reader':'mc3_shader_diff.all_slots/linked_infos','original_unique_shaders':len({s.off for s in slots}),'loaded_registered_materials':checked,'texture_parameters':texture_params,'numeric_parameters':numeric,'different_words':0,'templates':dict(counts)}
Path('research/city_shaders/parameter_diff.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
