import os
import struct,pathlib
p=pathlib.Path(os.path.join(os.environ.get('MC3_ALPHA_HOSTFS', ''), 'ASSETS/resources/city/sd_midnight_clear.pck'));d=p.read_bytes();u=lambda o:struct.unpack_from('<I',d,o)[0];off=lambda v:v-u(0)+128;groups=off(u(0x8c));sg=groups+5*16;sa=off(u(sg+4));sp=off(u(sa+4*216));print('shader',hex(sp),d[sp:sp+32].hex());tx=off(u(sp+8));
if d[tx+4]==2:tx=off(u(tx+12))
print('tex',hex(tx),d[tx:tx+160].hex());tex0=struct.unpack_from('<Q',d,tx+16)[0];print('WHPSM',1<<((tex0>>26)&15),1<<((tex0>>30)&15),(tex0>>20)&63)
