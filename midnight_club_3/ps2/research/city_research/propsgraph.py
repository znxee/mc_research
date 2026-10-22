import os
exec(open(os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/city_research/garageprop.py')).read().split("for o")[0]);u=lambda o:struct.unpack_from('<I',d,o)[0];off=lambda v:v-u(0)+128
for cl in range(29):
 n=u(0x90+cl*4)
 if not n:continue
 a=off(u(0x104+4*cl));print('class',cl,'count',n,'array',hex(a))
 for i in range(n):
  o=off(u(a+4*i));t=off(u(o+12));m=off(u(t+156));print('obj',hex(o),'type',hex(t),'model',hex(m),'eulerpos',struct.unpack_from('<6f',d,o+20),'objhead',d[o:o+20].hex(),'modelhead',d[m:m+32].hex(),'typename',d[t+56:t+76])
