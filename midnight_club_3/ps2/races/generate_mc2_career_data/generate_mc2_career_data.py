#!/usr/bin/env python3
"""generate_mc2_career_data.py — Generate mc2_career_data.h and mc2_career_data.cpp from manifest."""

import json
import os
import sys

MANIFEST_PATH = os.path.join(os.environ.get('MC_RESEARCH_ROOT', ''), 'mc2_career_manifest.json')
GAME_SRC_DIR = os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/xbox_recomp/xboxxberecomp_eval/templates/game/src/game')

HEADER_FILE = os.path.join(GAME_SRC_DIR, "mc2_career_data.h")
CPP_FILE = os.path.join(GAME_SRC_DIR, "mc2_career_data.cpp")


def generate():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    cities = data["cities"]
    rules = data["unlocking_rules"]
    veh_map = data["vehicle_reward_mapping"]

    # 1. Generate Header
    header_content = """#pragma once
#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>

namespace mc2 {

enum class CityId : int {
    LosAngeles = 0,
    Paris = 1,
    Tokyo = 2,
    Count = 3
};

enum class MovieType : int {
    PreCity,
    PreRace,
    PostRace,
    AltPostRace
};

enum class ConditionType : int {
    RaceBeaten,         // R
    HookmanBeaten,      // H
    HookmanBeatenIter,  // HTCIO
    CityAvailable,      // C
    InRace,             // IR
    VehicleAvailable    // V
};

enum class RewardType : int {
    Vehicle,            // V
    Hookman,            // H
    City,               // C
    Nitro,              // NITRO
    SlipstreamTurbo,    // SST / TEMP_SST
    Burnout,            // BO / TEMP_BO
    TwoWheelDrive,      // 2WD / TEMP_2WD
    InAirControl,       // IAC / TEMP_IAC
};

struct RaceDef {
    const char* name;
    const char* type;
    const char* tod;
    const char* weather;
    float ambient_density;
    float ped_density;
    const char* forced_vehicle; // nullptr if none
    bool is_supported;          // supported by current MC3 race converter
    int city_idx;
    int hookman_idx;
    int race_index_in_hookman;
};

struct FollowDef {
    const char* follow_race;
    const char* target_race;
    int target_race_index;
};

struct HookmanDef {
    const char* name;
    int city_idx;
    int global_hookman_idx;
    const char* cruise_route;
    int race_count;
    const RaceDef* races;
    int follow_count;
    const FollowDef* follows;
};

struct MovieDef {
    MovieType type;
    const char* target_race;    // nullptr for PreCity
    const char* pss_file;
    const char* bik_file;       // relative path to video folder
};

struct UnlockCondition {
    ConditionType type;
    const char* item_id;
};

struct UnlockRule {
    RewardType reward_type;
    const char* reward_id;
    bool is_temporary;
    int condition_count;
    const UnlockCondition* conditions;
};

struct VehicleRewardMapping {
    const char* mc2_veh;
    const char* mc3_veh;
    int tier;
    const char* veh_class;
    const char* display_name;
};

// Career Data API
int GetTotalHookmenCount();
int GetHookmenCount(CityId city);
const HookmanDef* GetHookman(CityId city, int index);
const HookmanDef* GetHookmanByGlobalIndex(int global_idx);
const HookmanDef* FindHookman(std::string_view name);

int GetTotalRacesCount();
const RaceDef* FindRace(std::string_view name);
const FollowDef* FindFollow(std::string_view follow_race_name);

int GetTotalMoviesCount();
const MovieDef* FindMovie(MovieType type, std::string_view target_race);
const MovieDef* GetPreCityMovie(CityId city);

std::span<const UnlockRule> GetUnlockRules();
const VehicleRewardMapping* FindVehicleReward(std::string_view mc2_veh);

} // namespace mc2
"""

    with open(HEADER_FILE, "w", encoding="utf-8") as f:
        f.write(header_content)

    # 2. Generate CPP
    lines = []
    lines.append('#include "mc2_career_data.h"')
    lines.append('#include <cstring>')
    lines.append('#include <algorithm>')
    lines.append('#include <string>')
    lines.append('')
    lines.append('namespace mc2 {')
    lines.append('')

    # Vehicle rewards table
    lines.append('static constexpr VehicleRewardMapping kVehicleRewards[] = {')
    for k, v in veh_map.items():
        lines.append(f'    {{"{k}", "{v["mc3_car"]}", {v["tier"]}, "{v["class"]}", "{v["name"]}"}},')
    lines.append('};')
    lines.append('')

    # City Hookmen definitions
    city_names = ["losangeles", "paris", "tokyo"]
    global_hm_counter = 0
    all_hm_ptrs = []

    for city_idx, cname in enumerate(city_names):
        hm_list = cities[cname]["hookmen"]
        for hm_idx, hm in enumerate(hm_list):
            var_base = f"k_{cname}_{hm['name']}"
            # Races
            lines.append(f"static constexpr RaceDef {var_base}_races[] = {{")
            for r_idx, r in enumerate(hm["races"]):
                forced_str = f'"{r["forced_vehicle"]}"' if r["forced_vehicle"] else "nullptr"
                supp_str = "true" if r["type"] not in ["lose_the_cops", "destroy", "cp_unordered_time_global"] else "false"
                lines.append(f'    {{"{r["name"]}", "{r["type"]}", "{r["tod"]}", "{r["weather"]}", {r["ambient_density"]}f, {r["ped_density"]}f, {forced_str}, {supp_str}, {city_idx}, {hm_idx}, {r_idx}}},')
            lines.append("};")

            # Follows
            lines.append(f"static constexpr FollowDef {var_base}_follows[] = {{")
            for f_idx, f in enumerate(hm["follows"]):
                # find target index
                target_idx = -1
                for r_idx, r in enumerate(hm["races"]):
                    if r["name"].lower() == f["target_race"].lower():
                        target_idx = r_idx
                        break
                lines.append(f'    {{"{f["follow_race"]}", "{f["target_race"]}", {target_idx}}},')
            lines.append("};")

            cruise_str = f'"{hm["cruise"]}"' if hm["cruise"] else "nullptr"
            races_ptr = f"{var_base}_races" if len(hm["races"]) > 0 else "nullptr"
            follows_ptr = f"{var_base}_follows" if len(hm["follows"]) > 0 else "nullptr"

            lines.append(f"static constexpr HookmanDef {var_base}_def = {{")
            lines.append(f'    "{hm["name"]}", {city_idx}, {global_hm_counter}, {cruise_str},')
            lines.append(f'    int(sizeof({var_base}_races)/sizeof({var_base}_races[0])), {races_ptr},')
            lines.append(f'    int(sizeof({var_base}_follows)/sizeof({var_base}_follows[0])), {follows_ptr}')
            lines.append("};")
            lines.append("")
            all_hm_ptrs.append(f"&{var_base}_def")
            global_hm_counter += 1

    # Hookmen by city arrays
    lines.append("static const HookmanDef* const kLaHookmen[] = {")
    for ptr in all_hm_ptrs[0:8]:
        lines.append(f"    {ptr},")
    lines.append("};")
    lines.append("")

    lines.append("static const HookmanDef* const kParisHookmen[] = {")
    for ptr in all_hm_ptrs[8:16]:
        lines.append(f"    {ptr},")
    lines.append("};")
    lines.append("")

    lines.append("static const HookmanDef* const kTokyoHookmen[] = {")
    for ptr in all_hm_ptrs[16:24]:
        lines.append(f"    {ptr},")
    lines.append("};")
    lines.append("")

    lines.append("static const HookmanDef* const kAllHookmen[24] = {")
    for ptr in all_hm_ptrs:
        lines.append(f"    {ptr},")
    lines.append("};")
    lines.append("")

    # Movies
    lines.append("static constexpr MovieDef kAllMovies[] = {")
    for cname in city_names:
        for mv in cities[cname]["movies"]:
            m_type_enum = {
                "pre_city": "MovieType::PreCity",
                "pre_race": "MovieType::PreRace",
                "post_race": "MovieType::PostRace",
                "alt_post_race": "MovieType::AltPostRace",
            }[mv["type"]]
            target_str = f'"{mv["race"]}"' if mv["race"] else "nullptr"
            pss_file = mv["file"]
            bik_file = pss_file.replace(".pss", ".bik").replace("/", "\\\\")
            lines.append(f'    {{{m_type_enum}, {target_str}, "{pss_file}", "{bik_file}"}},')
    lines.append("};")
    lines.append("")

    # Rules
    cond_counter = 0
    rule_defs = []
    for r_idx, r in enumerate(rules):
        cond_var = f"kRule_{r_idx}_conds"
        lines.append(f"static constexpr UnlockCondition {cond_var}[] = {{")
        for c in r["conditions"]:
            c_enum = {
                "R": "ConditionType::RaceBeaten",
                "H": "ConditionType::HookmanBeaten",
                "HTCIO": "ConditionType::HookmanBeatenIter",
                "C": "ConditionType::CityAvailable",
                "IR": "ConditionType::InRace",
                "V": "ConditionType::VehicleAvailable",
            }[c["type"]]
            lines.append(f'    {{{c_enum}, "{c["id"]}"}},')
        lines.append("};")

        raw_rtype = r["reward_type"]
        is_temp = "true" if raw_rtype.startswith("TEMP_") else "false"
        clean_rtype = raw_rtype.replace("TEMP_", "")
        r_enum = {
            "V": "RewardType::Vehicle",
            "H": "RewardType::Hookman",
            "C": "RewardType::City",
            "NITRO": "RewardType::Nitro",
            "SST": "RewardType::SlipstreamTurbo",
            "BO": "RewardType::Burnout",
            "2WD": "RewardType::TwoWheelDrive",
            "IAC": "RewardType::InAirControl",
        }[clean_rtype]

        rule_defs.append(f'    {{{r_enum}, "{r["reward_id"]}", {is_temp}, int(sizeof({cond_var})/sizeof({cond_var}[0])), {cond_var}}},')

    lines.append("static constexpr UnlockRule kAllUnlockRules[] = {")
    for rd in rule_defs:
        lines.append(rd)
    lines.append("};")
    lines.append("")

    # API Implementations
    api_impl = """
int GetTotalHookmenCount() { return 24; }

int GetHookmenCount(CityId city) {
    return 8;
}

const HookmanDef* GetHookman(CityId city, int index) {
    if (index < 0 || index >= 8) return nullptr;
    switch (city) {
        case CityId::LosAngeles: return kLaHookmen[index];
        case CityId::Paris: return kParisHookmen[index];
        case CityId::Tokyo: return kTokyoHookmen[index];
        default: return nullptr;
    }
}

const HookmanDef* GetHookmanByGlobalIndex(int global_idx) {
    if (global_idx < 0 || global_idx >= 24) return nullptr;
    return kAllHookmen[global_idx];
}

static bool StrEqualsCaseInsensitive(std::string_view a, std::string_view b) {
    if (a.size() != b.size()) return false;
    for (size_t i = 0; i < a.size(); ++i) {
        if (std::tolower((unsigned char)a[i]) != std::tolower((unsigned char)b[i])) return false;
    }
    return true;
}

const HookmanDef* FindHookman(std::string_view name) {
    for (const auto* hm : kAllHookmen) {
        if (StrEqualsCaseInsensitive(hm->name, name)) return hm;
    }
    return nullptr;
}

int GetTotalRacesCount() { return 56; }

const RaceDef* FindRace(std::string_view name) {
    for (const auto* hm : kAllHookmen) {
        for (int i = 0; i < hm->race_count; ++i) {
            if (StrEqualsCaseInsensitive(hm->races[i].name, name)) {
                return &hm->races[i];
            }
        }
    }
    return nullptr;
}

const FollowDef* FindFollow(std::string_view follow_race_name) {
    for (const auto* hm : kAllHookmen) {
        for (int i = 0; i < hm->follow_count; ++i) {
            if (StrEqualsCaseInsensitive(hm->follows[i].follow_race, follow_race_name)) {
                return &hm->follows[i];
            }
        }
    }
    return nullptr;
}

int GetTotalMoviesCount() { return int(sizeof(kAllMovies)/sizeof(kAllMovies[0])); }

const MovieDef* FindMovie(MovieType type, std::string_view target_race) {
    for (const auto& mv : kAllMovies) {
        if (mv.type == type) {
            if (mv.target_race == nullptr && target_race.empty()) return &mv;
            if (mv.target_race != nullptr && StrEqualsCaseInsensitive(mv.target_race, target_race)) {
                return &mv;
            }
        }
    }
    return nullptr;
}

const MovieDef* GetPreCityMovie(CityId city) {
    if (city == CityId::LosAngeles) {
        for (const auto& mv : kAllMovies) {
            if (mv.type == MovieType::PreCity) return &mv;
        }
    }
    return nullptr;
}

std::span<const UnlockRule> GetUnlockRules() {
    return kAllUnlockRules;
}

const VehicleRewardMapping* FindVehicleReward(std::string_view mc2_veh) {
    for (const auto& vr : kVehicleRewards) {
        if (StrEqualsCaseInsensitive(vr.mc2_veh, mc2_veh)) return &vr;
    }
    return nullptr;
}

} // namespace mc2
"""
    lines.append(api_impl)

    with open(CPP_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Generated {HEADER_FILE}")
    print(f"Generated {CPP_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(generate())
