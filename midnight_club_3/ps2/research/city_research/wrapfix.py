import os
from pathlib import Path
p=Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'src/city/geometry.cpp'));s=p.read_text().replace('Vec3 place(const Matrix& m', 'std::int32_t wrapped_add(std::int32_t a,std::int32_t b){\n    const auto bits=std::uint32_t(a)+std::uint32_t(b);std::int32_t result;std::memcpy(&result,&bits,4);return result;\n}\nVec3 place(const Matrix& m');s=s.replace('v+=row[k];row[k]=v;','v=wrapped_add(v,row[k]);row[k]=v;');p.write_text(s)
