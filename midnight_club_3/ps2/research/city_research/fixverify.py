import os
from pathlib import Path
p=Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/city_research/verify.py'));s=p.read_text();a=s.index('      # Constant maskednormal');e=s.index('      break',a);s=s[:a]+'''      adc=[bool(d[data+(3 if (cmd&0x6f)==0x6a else 4)*i]&1) for i in range(n)]
'''+s[e:];p.write_text(s)
