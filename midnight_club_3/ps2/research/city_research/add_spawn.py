import os
from pathlib import Path
h=Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'src/city/geometry.hpp'));s=h.read_text().replace('struct GroundSample {','struct SpawnPoint {std::array<float,3> position{};float heading_degrees=0;};\nSpawnPoint read_reset_spawn(const std::filesystem::path& reset_file,const std::string& name="Garage");\nstruct GroundSample {');s=s.replace('std::array<float,3> center={358,0,-42},float radius=200,','std::array<float,3> center,float radius=200,');s=s.replace('std::vector<CollisionTriangle> load_collision','// Default city entry comes from the pack\'s named Garage reset record.\nScene load_scene(const std::filesystem::path& assets_root,float radius=200,bool load_textures=true);\nstd::vector<CollisionTriangle> load_collision');h.write_text(s)
p=Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'src/city/geometry.cpp'));s=p.read_text().replace('#include <set>','#include <set>\n#include <sstream>\n#include <locale>');a=s.index('std::vector<CollisionTriangle> load_collision(');s=s[:a]+'''SpawnPoint read_reset_spawn(const std::filesystem::path& path,const std::string& name){
    std::ifstream in(path);if(!in)throw std::runtime_error("Cannot open city reset source: "+path.string());in.imbue(std::locale::classic());
    unsigned count=0;if(!(in>>count) || !count || count>10000)Bytes::fail("Invalid city reset count");std::optional<SpawnPoint> result;
    for(unsigned i=0;i<count;++i){SpawnPoint p;std::string key;if(!(in>>p.position[0]>>p.position[1]>>p.position[2]>>p.heading_degrees>>key))Bytes::fail("Incomplete city reset record");
        for(auto x:p.position)if(!std::isfinite(x))Bytes::fail("Nonfinite city reset position");if(!std::isfinite(p.heading_degrees))Bytes::fail("Nonfinite city reset heading");
        if(key==name){if(result)Bytes::fail("Duplicate named city reset");result=p;}
    }
    if(!result)throw std::runtime_error("Named city reset not found: "+name);return *result;
}
''' + s[a:];s=s.replace('    Bytes b(path);if(b.u32(4)!=9)', '    if(!std::isfinite(radius) || radius<=0 || radius>10000)Bytes::fail("Invalid collision radius");for(auto x:center)if(!std::isfinite(x))Bytes::fail("Invalid collision center");\n    Bytes b(path);if(b.u32(4)!=9)');a=s.index('std::optional<GroundSample> sample_ground(');s=s[:a]+'''Scene load_scene(const std::filesystem::path& assets,float radius,bool textures){
    auto spawn=read_reset_spawn(assets/"tune"/"city"/"sd.reset");auto result=load_scene(assets,spawn.position,radius,textures);result.heading_degrees=spawn.heading_degrees;return result;
}
''' + s[a:];p.write_text(s)
