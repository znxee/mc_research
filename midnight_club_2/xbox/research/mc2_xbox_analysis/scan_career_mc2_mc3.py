import json
from match_mc2_mc3_symbols import XbeImage, index_xbe, build_func_metadata, MC2_XBE_PATH

img2 = XbeImage(MC2_XBE_PATH)
idx2 = index_xbe(img2, "mc2_x86idx.pkl")
meta2 = build_func_metadata(img2, idx2)

with open('mc2_to_mc3_symbols.json', 'r') as f:
    matched = json.load(f)

matched_by_mc2 = {int(m['mc2_xbox_va'], 16): m for m in matched}

kws = [
    'unlock', 'hookman', 'career', '.loc', '.rac', '.rinf', '.srac',
    'htcio', 'follow', 'patrol', 'cp_ordered', 'cp_unordered', 'siderace',
    'worldchamp', 'moses', 'savo', 'dice', 'parfait', 'makoto', 'subtitle',
    'opponent', 'roam', 'challenge', 'flick', 'cruise', 'pinkslip', 'wager',
    'respect', 'tournament', 'club', 'garag', 'profile', 'savegame', 'numhookmen',
    'numraces', 'ambientdensity', 'peddensity', 'shortcut', 'hookmen'
]

print('=== 1. MC2 Career/Hookman/Race Strings & Referencing Functions ===')
mc2_career_funcs = {}
for fva, slist in meta2['strings'].items():
    for s in slist:
        sl = s.lower()
        if any(k in sl for k in kws):
            mc2_career_funcs.setdefault(fva, set()).add(s)

print(f'Total MC2 functions with Career/Hookman/Race strings: {len(mc2_career_funcs)}')
for fva in sorted(mc2_career_funcs):
    m = matched_by_mc2.get(fva)
    m_str = f"-> MC3 {m['mc3_xbox_va'] or m['mc3_ps2_va']} ({m['symbol']}) [{m['match_method']}]" if m else '-> UNMATCHED'
    sz = meta2['fsize'](fva)
    strs = sorted(list(mc2_career_funcs[fva]))[:6]
    print(f'  MC2 0x{fva:06X} ({sz:4d}B) {m_str} | strs={strs}')

print('\n=== 2. MC3 Matched Symbols with Career/Hookman/Race/Opponent/Unlock/Profile Names ===')
career_name_kws = [
    'career', 'hookman', 'race', 'opponent', 'unlock', 'ambient', 'follow',
    'roam', 'challenge', 'cruise', 'waypoint', 'checkpoint', 'shortcut',
    'subtitle', 'story', 'profile', 'player', 'garag', 'tourn', 'club'
]
for m in matched:
    nm = (m['symbol'] or '').lower()
    if any(k in nm for k in career_name_kws):
        v3 = m['mc3_xbox_va'] or f"ps2:{m['mc3_ps2_va']}"
        d_str = f"delta={m['size_delta']:+d}B" if m['size_delta'] is not None else "ps2-only"
        s3 = m['mc3_size'] or 0
        print(f"  MC2 {m['mc2_xbox_va']} ({m['mc2_size']:4d}B) <-> MC3 {v3} ({s3:4d}B, {d_str}) | {m['symbol']} [{m['match_method']}]")
