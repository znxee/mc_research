import os
import sys,struct,json
from pathlib import Path
sys.path.insert(0,os.environ.get('MC_RESEARCH_ROOT', ''))
import mc3_traffic_wheels as w
s=w.stock_setup(os.path.join(os.environ.get('MC3_ALPHA_HOSTFS', ''), 'ASSETS/resources/vehicle/vp_350z_04/vp_350z_04.pck'),os.path.join(os.environ.get('MC3_ALPHA_HOSTFS', ''), 'ASSETS/resources/vehicle'),os.path.join(os.environ.get('MC3_ALPHA_HOSTFS', ''), 'ASSETS/tune/vehicle'))
Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/assembly_research/350z_wheels.json')).write_text(json.dumps(s['report'],indent=2))
print(json.dumps(s['report'],indent=2))
for key in ('rim','tire'):
 print(key,'strips',len(s[key]),'vertices',sum(len(x[2]) for x in s[key]))
