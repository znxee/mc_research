import os
from pathlib import Path
p=Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'tests/verify_city_geometry.py'));s=p.read_text().replace('expected.append(triangle)','expected.append((triangle,normals is not None))').replace('for et,gt in zip(expected,got):','for (et,has_source_normal),gt in zip(expected,got):').replace("if label!='normal' or normals is not None:","if label!='normal' or has_source_normal:");p.write_text(s)
