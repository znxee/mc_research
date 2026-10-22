import os
exec(open(os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/city_research/garageprop.py')).read().split("for o")[0]);u=lambda o:struct.unpack_from('<I',d,o)[0];off=lambda v:v-u(0)+128
for p in [0xbcce0,0xd23d0,0xbc900]:
 m=off(u(p+180));print('TYPE',hex(p),'MODEL',hex(m),'group',hex(u(p+184)))
 for o in range(m,m+96,16):print(hex(o-m),' '.join('%08x'%v for v in struct.unpack_from('<4I',d,o)))
