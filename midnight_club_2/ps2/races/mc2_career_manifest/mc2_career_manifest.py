#!/usr/bin/env python3
"""mc2_career_manifest.py — Parse MC2 career data, validate graph rules and generate deterministic manifest."""

import os
import sys
import json
import re

MC2_ASSETS_DIR = os.path.join(os.environ.get('MC2_PC_RESEARCH', ''), 'assets_p')
TUNE_DIR = os.path.join(MC2_ASSETS_DIR, "tune")
RACE_DIR = os.path.join(TUNE_DIR, "race")
CSV_PATH = os.path.join(TUNE_DIR, "unlockingrules.csv")
VIDEO_DIR = os.path.join(os.environ.get('MC2_PC_RESEARCH', ''), 'video')

CITIES = ["losangeles", "paris", "tokyo"]

# The 5 race types accepted by the old converter; others require an adapter
SUPPORTED_TYPES_MC3_CONVERTER = {
    "cp_ordered",
    "cp_ordered_time_global",
    "cp_ordered_time_local",
    "cp_unordered",
    "roam",
}

# MC2 vehicle reward mapping to MC3 playable vehicles, preserving class and progression
VEHICLE_REWARD_MAP = {
    # Los Angeles (Tier 1-2)
    "vp_civica": {"mc3_car": "vp_eclipse_04", "tier": 1, "class": "tuner", "name": "1998 Dodge Neon / 2004 Eclipse"},
    "vp_jetta": {"mc3_car": "vp_jetta_03", "tier": 1, "class": "sedan", "name": "VW Jetta / 1995 Golf"},
    "vp_integraa": {"mc3_car": "vp_golfr32_04", "tier": 1, "class": "tuner", "name": "1995 VW Golf R32"},
    "vp_civicb": {"mc3_car": "vp_lancer_04", "tier": 2, "class": "tuner", "name": "2004 Mitsubishi Lancer Evo"},
    "vp_s2000": {"mc3_car": "vp_elise_04", "tier": 2, "class": "sport", "name": "Lotus Elise / 350Z"},
    "vp_gto": {"mc3_car": "vp_gto_70", "tier": 2, "class": "muscle", "name": "1970 Pontiac GTO / El Camino"},
    "vp_rx7": {"mc3_car": "vp_supra_98", "tier": 2, "class": "tuner", "name": "1998 Toyota Supra"},
    "vp_viper": {"mc3_car": "vp_viper_03", "tier": 3, "class": "exotic", "name": "2003 Dodge Viper / Corvette"},
    "vp_cbr929a": {"mc3_car": "vp_ninja_03", "tier": 2, "class": "motorcycle", "name": "2004 Ducati 999R"},
    # Paris (Tier 2-3)
    "vp_puma": {"mc3_car": "vp_golfr32_04", "tier": 2, "class": "tuner", "name": "VW Golf R32"},
    "vp_cosworth": {"mc3_car": "vp_lancer_04", "tier": 2, "class": "tuner", "name": "2004 Mitsubishi Lancer Evo"},
    "vp_m5": {"mc3_car": "vp_is300_04", "tier": 2, "class": "sedan", "name": "Lexus IS300 / 350Z"},
    "vp_elise": {"mc3_car": "vp_elise_04", "tier": 2, "class": "sport", "name": "Lotus Elise"},
    "vp_golfa": {"mc3_car": "vp_golfr32_04", "tier": 2, "class": "tuner", "name": "VW Golf R32"},
    "vp_clio": {"mc3_car": "vp_eclipse_04", "tier": 2, "class": "tuner", "name": "2004 Mitsubishi Eclipse"},
    "vp_911": {"mc3_car": "vp_corvette_03", "tier": 3, "class": "exotic", "name": "2003 Corvette Z06"},
    "vp_ducati": {"mc3_car": "vp_ninja_03", "tier": 3, "class": "motorcycle", "name": "2004 Ducati 999R"},
    "vp_vanquish": {"mc3_car": "vp_corvette_03", "tier": 3, "class": "exotic", "name": "Corvette Z06 / Viper"},
    "vp_pariscop": {"mc3_car": "vp_impalass_cop_s_96", "tier": 2, "class": "cop", "name": "Police Impala"},
    # Tokyo (Tier 3-4)
    "vp_mr2": {"mc3_car": "vp_elise_04", "tier": 3, "class": "sport", "name": "Lotus Elise / 350Z"},
    "vp_nissanz": {"mc3_car": "vp_350z_04", "tier": 3, "class": "sport", "name": "2004 Nissan 350Z"},
    "vp_supraa": {"mc3_car": "vp_supra_98", "tier": 3, "class": "tuner", "name": "1998 Toyota Supra"},
    "vp_suprab": {"mc3_car": "vp_supra_98", "tier": 3, "class": "tuner", "name": "1998 Toyota Supra Spec B"},
    "vp_lexus": {"mc3_car": "vp_is300_04", "tier": 3, "class": "sedan", "name": "Lexus IS300"},
    "vp_yamaha": {"mc3_car": "vp_ninja_03", "tier": 3, "class": "motorcycle", "name": "2004 Ducati 999R"},
    "vp_lancer": {"mc3_car": "vp_lancer_04", "tier": 3, "class": "tuner", "name": "2004 Mitsubishi Lancer Evo"},
    "vp_skylinea": {"mc3_car": "vp_skyline_02", "tier": 4, "class": "tuner", "name": "2002 Nissan Skyline GT-R"},
    "vp_tokyocop": {"mc3_car": "vp_d_tokyo_cop_01", "tier": 3, "class": "cop", "name": "Tokyo Police"},
    "vp_cop_l": {"mc3_car": "vp_impalass_cop_s_96", "tier": 2, "class": "cop", "name": "LA Police Impala"},
    "vp_saleen": {"mc3_car": "vp_saleens7_04", "tier": 4, "class": "exotic", "name": "2004 Saleen S7"},
    "vp_slf450x": {"mc3_car": "vp_saleens7_04", "tier": 4, "class": "special", "name": "2004 Saleen S7 (Special)"},
}


def parse_loc(path):
    text = open(path, encoding="latin1").read()
    m_idx = text.find("Movies")
    h_text = text[:m_idx] if m_idx != -1 else text
    m_text = text[m_idx:] if m_idx != -1 else ""

    hookmen = []
    for b in re.findall(r"Hookman\s*\{(.*?)\}", h_text, re.S):
        name_m = re.search(r"name\s+(\S+)", b)
        if not name_m:
            continue
        name = name_m.group(1)
        if name in ("Arcade", "Battle_modes"):
            continue

        cruise = None
        races = []
        follows = []
        for line in b.splitlines():
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            parts = line.split()
            cmd = parts[0].lower()
            if cmd == "hookman_cruise":
                cruise = parts[1]
            elif cmd == "follow":
                follows.append({"follow_race": parts[1], "target_race": parts[2]})
            elif cmd in (
                "cp_ordered",
                "cp_ordered_time_global",
                "cp_ordered_time_local",
                "cp_unordered",
                "cp_unordered_time_global",
                "lose_the_cops",
                "destroy",
            ):
                races.append({"type": cmd, "name": parts[1]})
        hookmen.append(
            {
                "name": name,
                "cruise": cruise,
                "races": races,
                "follows": follows,
            }
        )

    movies = []
    if m_text:
        m_lines = [
            l.strip()
            for l in m_text.splitlines()
            if l.strip() and not l.strip().startswith("//")
        ]
        for l in m_lines:
            parts = l.split()
            if parts[0].lower() == "nummovies" or parts[0] in ("Movies", "{", "}"):
                continue
            m_type = parts[0].lower()
            if m_type == "pre_city":
                movies.append({"type": m_type, "race": None, "file": parts[1]})
            elif m_type in ("pre_race", "post_race", "alt_post_race"):
                movies.append({"type": m_type, "race": parts[1], "file": parts[2]})
            else:
                raise ValueError(f"Unknown movie declaration: {l}")
    return hookmen, movies


def parse_locinf(path):
    text = open(path, encoding="latin1").read()
    blocks = {}
    for m in re.finditer(r"(\S+)\s*\{(.*?)\}", text, re.S):
        name = m.group(1)
        body = m.group(2).strip()
        lines = [l.strip() for l in body.splitlines() if l.strip()]
        tod = lines[0] if len(lines) > 0 else "midnight"
        weather = lines[1] if len(lines) > 1 else "clear"
        rtype = lines[2] if len(lines) > 2 else "cp_ordered"
        amb = 1.0
        ped = 10.0
        forced_veh = None
        for l in lines:
            if "ambientdensity:" in l.lower():
                amb = float(l.split(":")[1].strip())
            elif "peddensity:" in l.lower():
                ped = float(l.split(":")[1].strip())
            elif "forcedvehicle:" in l.lower():
                forced_veh = l.split(":")[1].strip()
        blocks[name.lower()] = {
            "name": name,
            "tod": tod,
            "weather": weather,
            "rtype": rtype,
            "ambient_density": amb,
            "ped_density": ped,
            "forced_vehicle": forced_veh,
        }
    return blocks


def parse_unlockingrules(path):
    rules = []
    with open(path, "r", encoding="latin1") as f:
        for idx, line in enumerate(f):
            line = line.strip()
            if not line or line.startswith("Don't") or line.startswith('"') or line.startswith("reward"):
                continue
            parts = [p.strip() for p in line.split(",") if p.strip()]
            if len(parts) < 4:
                continue
            reward_type = parts[0]
            reward_id = parts[1]
            conds = []
            for i in range(2, len(parts), 2):
                if i + 1 < len(parts):
                    c_type = parts[i]
                    c_id = parts[i + 1]
                    conds.append({"type": c_type, "id": c_id})
            rules.append({
                "rule_index": idx + 1,
                "reward_type": reward_type,
                "reward_id": reward_id,
                "conditions": conds,
            })
    return rules


def main():
    total_hm = 0
    total_races = 0
    total_movies = 0
    all_races = {}
    all_follows = {}
    all_hookmen = {}
    unsupported_races = []
    cities_manifest = {}

    for city in CITIES:
        loc_path = os.path.join(RACE_DIR, f"{city}.loc")
        locinf_path = os.path.join(RACE_DIR, f"{city}.locinf")
        hm_list, mv_list = parse_loc(loc_path)
        locinf_map = parse_locinf(locinf_path)

        total_hm += len(hm_list)
        total_movies += len(mv_list)

        city_races_count = 0
        for hm in hm_list:
            all_hookmen[hm["name"].lower()] = {"name": hm["name"], "city": city}
            city_races_count += len(hm["races"])
            total_races += len(hm["races"])
            for r in hm["races"]:
                r_key = r["name"].lower()
                linf = locinf_map.get(r_key)
                if linf:
                    r["tod"] = linf["tod"]
                    r["weather"] = linf["weather"]
                    r["ambient_density"] = linf["ambient_density"]
                    r["ped_density"] = linf["ped_density"]
                    r["forced_vehicle"] = linf["forced_vehicle"]
                else:
                    raise KeyError(f"Missing locinf entry for race: {r['name']}")
                all_races[r_key] = {**r, "city": city, "hookman": hm["name"]}
                if r["type"] not in SUPPORTED_TYPES_MC3_CONVERTER:
                    unsupported_races.append(all_races[r_key])

            # validate follows
            race_names_in_hm = {r["name"].lower() for r in hm["races"]}
            for f in hm["follows"]:
                all_follows[f["follow_race"].lower()] = {
                    "follow_race": f["follow_race"],
                    "target_race": f["target_race"],
                    "hookman": hm["name"],
                    "city": city,
                }
                if f["target_race"].lower() not in race_names_in_hm:
                    raise ValueError(
                        f"Follow target {f['target_race']} not found in Hookman {hm['name']}"
                    )

        # resolve movies against races
        for mv in mv_list:
            if mv["race"]:
                if mv["race"].lower() not in all_races:
                    raise ValueError(f"Movie target race {mv['race']} not found in any Hookman")

        cities_manifest[city] = {
            "hookmen": hm_list,
            "movies": mv_list,
            "race_count": city_races_count,
        }

    rules = parse_unlockingrules(CSV_PATH)

    # Validate rules
    all_cities = {"losangeles", "paris", "tokyo"}
    resolved_rules = []
    for r in rules:
        rtype = r["reward_type"]
        rid = r["reward_id"]
        # Validate conditions
        for c in r["conditions"]:
            ctype = c["type"]
            cid = c["id"]
            if ctype in ("H", "HTCIO"):
                if cid.lower() not in all_hookmen:
                    raise ValueError(f"Unknown hookman condition: {cid}")
            elif ctype == "R":
                if cid.lower() not in all_races and cid.lower() not in all_follows:
                    # check if it's an arcade circuit
                    if "arcade" not in cid.lower():
                        raise ValueError(f"Unknown race condition: {cid}")
            elif ctype == "C":
                if cid.lower() not in all_cities:
                    raise ValueError(f"Unknown city condition: {cid}")
            elif ctype == "V":
                if cid.lower() not in VEHICLE_REWARD_MAP:
                    raise ValueError(f"Unknown vehicle condition: {cid}")
        resolved_rules.append(r)

    # Progression Graph Chain Verification:
    # 1. Moses -> Maria/Steven
    # 2. Steven -> Angel
    # 3. Maria -> Gina/Hector
    # 4. Angel+Gina+Hector -> Dice
    # 5. Dice -> Paris/Blog
    # 6. Blog -> Julie/Primo
    # 7. Julie -> Stephane
    # 8. Primo -> Ian
    # 9. Primo+Stephane -> Farid
    # 10. Farid+Ian -> Parfait
    # 11. Parfait -> Tokyo/Ricky/Shing
    # 12. Shing -> Haley
    # 13. Ricky -> Nikko
    # 14. Ricky+Haley -> Zen
    # 15. Haley+Nikko -> Kenichi
    # 16. Kenichi+Zen -> Makoto
    # 17. Makoto -> WorldChampTokyo -> WorldChampParis -> WorldChampLA

    def evaluate_unlocked(beaten_hookmen, beaten_races, beaten_follows):
        unlocked_h = {"Moses"}  # Moses has no rule => always unlocked at start of LA
        unlocked_c = {"losangeles"}
        for rule in rules:
            rtype = rule["reward_type"]
            rid = rule["reward_id"]
            all_met = True
            for c in rule["conditions"]:
                ctype = c["type"]
                cid = c["id"]
                if ctype in ("H", "HTCIO"):
                    if cid not in beaten_hookmen:
                        all_met = False
                        break
                elif ctype == "R":
                    if cid.lower() not in beaten_races and cid.lower() not in beaten_follows:
                        all_met = False
                        break
                elif ctype == "C":
                    if cid.lower() not in unlocked_c:
                        all_met = False
                        break
                elif ctype == "V":
                    pass
            if all_met:
                if rtype == "H":
                    unlocked_h.add(rid)
                elif rtype == "C":
                    unlocked_c.add(rid.lower())
        return unlocked_h, unlocked_c

    # Step-by-step chain assertion
    beaten_h = set()
    beaten_r = set()
    beaten_f = set()

    # Step 0: Initial
    unlocked_h, unlocked_c = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert unlocked_h == {"Moses"}, f"Initial should be Moses, got {unlocked_h}"
    assert unlocked_c == {"losangeles"}

    # Step 1: Beat Moses -> Maria and Steven unlocked
    beaten_h.add("Moses")
    unlocked_h, _ = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert "Maria" in unlocked_h and "Steven" in unlocked_h

    # Step 2: Beat Steven -> Angel unlocked
    beaten_h.add("Steven")
    unlocked_h, _ = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert "Angel" in unlocked_h

    # Step 3: Beat Maria -> Gina and Hector unlocked
    beaten_h.add("Maria")
    unlocked_h, _ = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert "Gina" in unlocked_h and "Hector" in unlocked_h
    assert "Dice" not in unlocked_h  # Dice needs Angel + Gina + Hector

    # Step 4: Beat Angel, Gina, Hector -> Dice unlocked
    beaten_h.update(["Angel", "Gina", "Hector"])
    unlocked_h, _ = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert "Dice" in unlocked_h

    # Step 5: Beat Dice -> Paris and Blog unlocked
    beaten_h.add("Dice")
    unlocked_h, unlocked_c = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert "paris" in unlocked_c
    assert "Blog" in unlocked_h

    # Step 6: Beat Blog -> Julie and Primo unlocked
    beaten_h.add("Blog")
    unlocked_h, _ = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert "Julie" in unlocked_h and "Primo" in unlocked_h

    # Step 7: Beat Julie -> Stephane unlocked
    beaten_h.add("Julie")
    unlocked_h, _ = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert "Stephane" in unlocked_h

    # Step 8: Beat Primo -> Ian unlocked
    beaten_h.add("Primo")
    unlocked_h, _ = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert "Ian" in unlocked_h
    assert "Farid" not in unlocked_h  # Needs Primo + Stephane

    # Step 9: Beat Stephane -> Farid unlocked
    beaten_h.add("Stephane")
    unlocked_h, _ = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert "Farid" in unlocked_h
    assert "Parfait" not in unlocked_h  # Needs Farid + Ian

    # Step 10: Beat Farid + Ian -> Parfait unlocked
    beaten_h.update(["Farid", "Ian"])
    unlocked_h, _ = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert "Parfait" in unlocked_h

    # Step 11: Beat Parfait -> Tokyo, Ricky and Shing unlocked
    beaten_h.add("Parfait")
    unlocked_h, unlocked_c = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert "tokyo" in unlocked_c
    assert "Ricky" in unlocked_h and "Shing" in unlocked_h

    # Step 12: Beat Shing -> Haley unlocked
    beaten_h.add("Shing")
    unlocked_h, _ = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert "Haley" in unlocked_h
    assert "Zen" not in unlocked_h  # Zen needs Ricky + Haley

    # Step 13: Beat Ricky -> Nikko unlocked
    beaten_h.add("Ricky")
    unlocked_h, _ = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert "Nikko" in unlocked_h
    assert "Zen" not in unlocked_h  # Haley not yet beaten

    # Step 14: Beat Haley -> Zen unlocked (since Ricky and Haley are both beaten)
    beaten_h.add("Haley")
    unlocked_h, _ = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert "Zen" in unlocked_h
    assert "Kenichi" not in unlocked_h  # Kenichi needs Haley + Nikko

    # Step 15: Beat Nikko -> Kenichi unlocked (since Haley and Nikko are both beaten)
    beaten_h.add("Nikko")
    unlocked_h, _ = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert "Kenichi" in unlocked_h
    assert "Makoto" not in unlocked_h  # Makoto needs Kenichi + Zen

    # Step 16: Beat Zen and Kenichi -> Makoto unlocked
    beaten_h.update(["Zen", "Kenichi"])
    unlocked_h, _ = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert "Makoto" in unlocked_h

    # Step 16: Makoto -> WorldChampTokyo -> WorldChampParis -> WorldChampLA
    beaten_h.add("Makoto")
    unlocked_h, _ = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert "WorldChampTokyo" in unlocked_h

    beaten_h.add("WorldChampTokyo")
    unlocked_h, _ = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert "WorldChampParis" in unlocked_h

    beaten_h.add("WorldChampParis")
    unlocked_h, _ = evaluate_unlocked(beaten_h, beaten_r, beaten_f)
    assert "WorldChampLA" in unlocked_h

    # Assert exact counts
    assert total_hm == 24, f"Expected 24 Hookmen, got {total_hm}"
    assert total_races == 56, f"Expected 56 races, got {total_races}"
    assert total_movies == 79, f"Expected 79 movies, got {total_movies}"
    assert len(unsupported_races) == 4, f"Expected 4 unsupported races, got {len(unsupported_races)}"

    manifest = {
        "metadata": {
            "title": "MC2 Career Manifest",
            "campaign_hookmen_count": total_hm,
            "campaign_races_count": total_races,
            "movie_declarations_count": total_movies,
            "unsupported_races_count": len(unsupported_races),
            "unsupported_races": unsupported_races,
        },
        "vehicle_reward_mapping": VEHICLE_REWARD_MAP,
        "cities": cities_manifest,
        "unlocking_rules": resolved_rules,
    }

    out_path = os.path.join(os.environ.get('MC_RESEARCH_ROOT', ''), "mc2_career_manifest.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("==================================================================")
    print("GATE 1 MANIFEST PASSED AUDIT & PROGRESSION GRAPH PROOF COMPLETED!")
    print("==================================================================")
    print(f"  [OK] Campaign Hookmen:        {total_hm}/24")
    print(f"  [OK] Campaign Races:          {total_races}/56")
    print(f"  [OK] Movie Declarations:      {total_movies}/79")
    print(f"  [OK] Progression Chain:       Moses -> ... -> WorldChampLA (17-step proof passed)")
    print(f"  [OK] Unsupported Races (4/4 reported explicitly):")
    for ur in unsupported_races:
        print(f"       * {ur['name']} ({ur['type']}) in {ur['city']} [Hookman: {ur['hookman']}, ForcedVehicle: {ur.get('forced_vehicle')}]")
    print(f"  [OK] Manifest written to:     {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
