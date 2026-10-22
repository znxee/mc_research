import json
cap = json.load(open("ida_flat/capture.json", encoding="utf-8"))
lines = []
for fn in cap["functions"]:
    if not fn.get("pseudocode"):
        lines.append(f"{fn['address']} {fn['end']} {fn['symbol']} -> {fn.get('decompile_error')}")
open("err.txt", "w", encoding="utf-8").write(f"Total: {len(cap['functions'])}, Missing: {len(lines)}\n" + "\n".join(lines))
