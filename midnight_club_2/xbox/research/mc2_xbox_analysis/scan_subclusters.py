import json
from match_mc2_mc3_symbols import XbeImage, index_xbe, build_func_metadata, MC2_XBE_PATH

img2 = XbeImage(MC2_XBE_PATH)
idx2 = index_xbe(img2, "mc2_x86idx.pkl")
meta2 = build_func_metadata(img2, idx2)

with open('mc2_to_mc3_symbols.json', 'r', encoding='utf-8') as f:
    matched = json.load(f)
matched_by_mc2 = {int(m['mc2_xbox_va'], 16): m for m in matched}

ranges = [
    ("mcUnlocking & Progress tail (0x152000..0x154500)", 0x152000, 0x154500),
    ("mcRaceHookmen & Follow (0x0AD800..0x0B0000)", 0x0AD800, 0x0B0000),
    ("aiBrainHookman (0x0C7000..0x0C8000)", 0x0C7000, 0x0C8000),
]

lines = []
for title, lo, hi in ranges:
    lines.append(f"=== {title} ===")
    for fva in meta2['funcs']:
        if lo <= fva <= hi:
            sz = meta2['fsize'](fva)
            m = matched_by_mc2.get(fva)
            m_str = f"-> MC3 {m['mc3_xbox_va'] or m['mc3_ps2_va']} ({m['symbol']})" if m else "-> UNMATCHED"
            strs = meta2['strings'].get(fva, [])
            callees = [f"0x{c:06X}" for c in meta2['callees'].get(fva, [])[:8]]
            callers = [f"0x{c:06X}" for c in sorted(meta2['callers'].get(fva, []))[:8]]
            lines.append(f"  MC2 0x{fva:06X} ({sz:4d}B) {m_str}")
            if strs:
                lines.append(f"      strs: {strs[:8]}")
            lines.append(f"      callees: {callees} | callers: {callers}")

open("career_subclusters.txt", "w", encoding="utf-8").write("\n".join(lines))
print("Lines:", len(lines))
