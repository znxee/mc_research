import json
from match_mc2_mc3_symbols import XbeImage, index_xbe, build_func_metadata, load_mc3_symbols, MC2_XBE_PATH

img2 = XbeImage(MC2_XBE_PATH)
idx2 = index_xbe(img2, "mc2_x86idx.pkl")
meta2 = build_func_metadata(img2, idx2)

ps2_sym, ps2_to_mc3x, mc3x_sym = load_mc3_symbols()

with open('mc2_to_mc3_symbols.json', 'r', encoding='utf-8') as f:
    matched = json.load(f)
matched_by_mc2 = {int(m['mc2_xbox_va'], 16): m for m in matched}

out_lines = []

# 1. List all MC3 PS2/Xbox symbols related to Progress, Unlock, Career, Hookman, CityData, RaceMgr, etc.
out_lines.append("=== A. MC3 SYMBOLS FOR CAREER / PROGRESS / UNLOCK / HOOKMAN / RACE ===")
mc3_career_kws = [
    'progress', 'unlock', 'career', 'hookman', 'citydata', 'raceconfig',
    'racemgr', 'racebase', 'racecheckpoint', 'racefollow', 'follow',
    'roam', 'opponent', 'tournament', 'club', 'pinkslip', 'wager', 'cruis'
]
for ps2_va, name in sorted(ps2_sym.items(), key=lambda x: x[1]):
    nl = name.lower()
    if any(k in nl for k in mc3_career_kws):
        v = ps2_to_mc3x.get(ps2_va)
        xva = v[0] if isinstance(v, (tuple, list)) else v
        x_str = f"MC3_XBOX:0x{xva:06X}" if xva else "PS2_ONLY"
        out_lines.append(f"  PS2:0x{ps2_va:06X} | {x_str:18s} | {name}")

# 2. Inspect MC2 Xbox Cluster 1: 0x14D800 .. 0x153000 (mcProgressManager, mcRaceConfig, mcCityData, mcUnlocking, mcLocalPlayerOptions)
out_lines.append("\n=== B. MC2 CLUSTER 1: 0x14D800 .. 0x153000 (ProgressManager, RaceConfig, CityData::LoadLoc, mcUnlocking) ===")
for fva in meta2['funcs']:
    if 0x14D800 <= fva <= 0x153000:
        sz = meta2['fsize'](fva)
        m = matched_by_mc2.get(fva)
        m_str = f"-> MC3 {m['mc3_xbox_va'] or m['mc3_ps2_va']} ({m['symbol']})" if m else "-> UNMATCHED"
        strs = meta2['strings'].get(fva, [])
        callees = [f"0x{c:06X}" for c in meta2['callees'].get(fva, [])[:6]]
        callers = [f"0x{c:06X}" for c in sorted(meta2['callers'].get(fva, []))[:6]]
        out_lines.append(f"  MC2 0x{fva:06X} ({sz:4d}B) {m_str}")
        if strs:
            out_lines.append(f"      strings: {strs[:8]}")
        out_lines.append(f"      callees: {callees} | callers: {callers}")

# 3. Inspect MC2 Xbox Cluster 2: 0x096000 .. 0x0B0800 (Race Over, Career Unlocks, Hookman Cruise/Roam, RaceBase, Checkpoints, Follow, Ambient)
out_lines.append("\n=== C. MC2 CLUSTER 2: 0x096000 .. 0x0B0800 (RaceMgr, Hookman Roam/Follow, RaceBase, Unlocks in-game) ===")
for fva in meta2['funcs']:
    if 0x096000 <= fva <= 0x0B0800:
        sz = meta2['fsize'](fva)
        m = matched_by_mc2.get(fva)
        strs = meta2['strings'].get(fva, [])
        if m or strs or sz >= 120:
            m_str = f"-> MC3 {m['mc3_xbox_va'] or m['mc3_ps2_va']} ({m['symbol']})" if m else "-> UNMATCHED"
            out_lines.append(f"  MC2 0x{fva:06X} ({sz:4d}B) {m_str} | strs={strs[:6]}")

open("career_clusters_report.txt", "w", encoding="utf-8").write("\n".join(out_lines))
print(f"Wrote {len(out_lines)} lines to career_clusters_report.txt")
