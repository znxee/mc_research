import os
import pathlib,struct,re
p=pathlib.Path(os.path.join(os.environ.get('MC3_ALPHA_HOSTFS', ''), 'ASSETS/resources/prop/sd_midnight_clear_garage_props.pck'));d=p.read_bytes();print('Header',struct.unpack_from('<4I',d,0))
for o in range(128,384,16):print(hex(o),' '.join('%08x'%v for v in struct.unpack_from('<4I',d,o)))
print('Strings',[(hex(m.start()),m.group().decode()) for m in re.finditer(rb'[a-z][a-z0-9_#]{5,}',d)][:30])
