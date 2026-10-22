import os
exec(open(os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/city_research/garageprop.py')).read().split("for o")[0]);u=lambda o:struct.unpack_from('<I',d,o)[0];off=lambda v:v-u(0)+128
for p in [0xbc900,0xbcce0,0xbc750]:
 print('OBJECT',hex(p))
 for o in range(p,p+224,16):print(hex(o-p),' '.join('%08x'%v for v in struct.unpack_from('<4I',d,o)))
