from match_mc2_mc3_symbols import XbeImage, index_xbe, build_func_metadata, load_mc3_symbols, MC3_XBE_PATH

img3 = XbeImage(MC3_XBE_PATH)
idx3 = index_xbe(img3, "mc3_x86idx_full.pkl")
meta3 = build_func_metadata(img3, idx3)
ps2_sym, ps2_to_mc3x, mc3x_sym = load_mc3_symbols()

kws = ['hookman', 'hookmen', 'follow', 'cruise', 'flash_lights', 'unlock', 'career', 'locinf', 'srac', 'shortcut', 'opponent']
lines = []
for fva, slist in sorted(meta3['strings'].items()):
    for s in slist:
        if any(k in s.lower() for k in kws):
            sym = mc3x_sym.get(fva, (None, None))[0] or ""
            lines.append(f"MC3 0x{fva:06X} ({meta3['fsize'](fva):4d}B) | {sym:55s} | strs={slist[:6]}")
            break

open("mc3_hookman_strings.txt", "w", encoding="utf-8").write("\n".join(lines))
print("Found", len(lines), "functions in MC3 Xbox")
