import os
from pathlib import Path
p=Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'tests/city_collision_test.cpp'));s=p.read_text().replace('std::filesystem::remove(path);std::cout', '''{std::ofstream out(path);out<<"2\\n1 2 3 40 Origin\\n20 .25 -80 270 Garage\\n";}
        auto spawn=mc3::city::read_reset_spawn(path);require(spawn.position==std::array<float,3>{20,.25f,-80} && spawn.heading_degrees==270,"Pack reset position and heading preserved");
        {std::ofstream out(path);out<<"2\\n20 0 -80 270 Garage\\n";}
        rejected=false;try{mc3::city::read_reset_spawn(path);}catch(const std::exception&){rejected=true;}require(rejected,"Truncated city reset rejected");
        std::filesystem::remove(path);std::cout''');p.write_text(s)
