import json
from match_mc2_mc3_symbols import XbeImage, index_xbe, build_func_metadata, load_mc3_symbols, MC3_XBE_PATH

img3 = XbeImage(MC3_XBE_PATH)
idx3 = index_xbe(img3, "mc3_x86idx_full.pkl")
meta3 = build_func_metadata(img3, idx3)
ps2_sym, ps2_to_mc3x, mc3x_sym = load_mc3_symbols()

ranges = [
    ("MC3 Xbox mcRaceHookmen area (0x1E0A00..0x1E2900)", 0x1E0A00, 0x1E2900),
    ("MC3 Xbox aiBrainHookman area (0x1EB500..0x1EC500)", 0x1EB500, 0x1EC500),
    ("MC3 Xbox mcPgCareer area (0x276E00..0x278500)", 0x276E00, 0x278500),
    ("MC3 Xbox mcPgUnlockingRulesEval area (0x289C00..0x28C500)", 0x289C00, 0x28C500),
]

lines = []
for title, lo, hi in ranges:
    lines.append(f"=== {title} ===")
    for fva in meta3['funcs']:
        if lo <= fva <= hi:
            sz = meta3['fsize'](fva)
            sym = mc3x_sym.get(fva, (None, None))[0] or ""
            strs = meta3['strings'].get(fva, [])
            if sym or strs or sz >= 80:
                lines.append(f"  MC3 0x{fva:06X} ({sz:4d}B) | {sym} | strs={strs[:6]}")

open("mc3_career_areas.txt", "w", encoding="utf-8").write("\n".join(lines))
print("Wrote", len(lines), "lines")
