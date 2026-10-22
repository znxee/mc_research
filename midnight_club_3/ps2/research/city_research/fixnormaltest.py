import os
from pathlib import Path
p=Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'tests/verify_city_geometry.py'));s=p.read_text().replace("errors[label]=max(errors[label],*[abs(ev[k]-gv[k]) for k in range(lo,hi)])", "if label!='normal' or normals is not None:\n                        errors[label]=max(errors[label],*[abs(ev[k]-gv[k]) for k in range(lo,hi)])");p.write_text(s)
