import os
exec(open(os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/city_research/garageprop.py')).read().split("for o")[0]);u=lambda o:struct.unpack_from('<I',d,o)[0];h=lambda o:struct.unpack_from('<H',d,o)[0];off=lambda v:v-u(0)+128
for t in [0xbcce0,0xd23d0]:
 mo=off(u(t+180));gt=off(u(mo+16));bl=off(u(gt));bp,qw,nv=struct.unpack_from('<IHH',d,bl);b=off(bp);print(hex(mo),hex(b),qw,nv,d[b:b+32].hex())
