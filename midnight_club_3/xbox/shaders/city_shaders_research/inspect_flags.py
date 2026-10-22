import os
from pathlib import Path
import struct, json, collections
elf=Path(os.path.join(os.environ.get('MC_WORK_DIR', ''), 'slus_213.55')).read_bytes()
for pattern in [b'city_window.shadert',b'city_facade.shadert',b'inputs',b'alpharef 45',b'texture %0']:
    hits=[];p=0
    while (p:=elf.find(pattern,p))>=0: hits.append(p);p+=1
    print(pattern,hits[:35],len(hits))
for source in [os.path.join(os.environ.get('MC3_ALPHA_HOSTFS', ''), 'ASSETS/resources/city/sd_midnight_clear.pck'),os.path.join(os.environ.get('MC3_ALPHA_HOSTFS', ''), 'ASSETS/resources/prop/sd_midnight_clear_garage_props.pck')]:
    b=Path(source).read_bytes();u32=lambda p:struct.unpack_from('<I',b,p)[0];u16=lambda p:struct.unpack_from('<H',b,p)[0];ptr=lambda p:u32(p)-u32(0)+128
    groups=[ptr(0x8c)+16*i for i in range(u32(0x88))] if u32(4)==67 else [ptr(0x8c)]
    seen={};counts=collections.Counter()
    for g in groups:
        a=ptr(g+4)
        for i in range(u16(g+8)):
            if not u32(a+4*i):continue
            s=ptr(a+4*i);flags=u32(s+4);tag=flags&127;reg=(flags>>15)&127;n=(flags>>22)&7;mask=flags>>25;bucket=(flags>>7)&31
            seen[s]={'offset':s,'flags':flags,'tag':tag,'registry':reg,'count':n,'texture_mask':mask,'bucket':bucket,'words':[u32(s+8+4*j) for j in range(n)]}
    for row in seen.values():counts[(row['tag'],row['registry'],row['count'],row['texture_mask'],row['bucket'])]+=1
    print(source,len(seen),dict(counts))
    Path('research/city_shaders/'+('sd_flags.json' if u32(4)==67 else 'garage_flags.json')).write_text(json.dumps(list(seen.values()),indent=2))
