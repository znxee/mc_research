"""Extract the MC2 career routines used as an independent xboxrecomp oracle."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DISASM = ROOT / "disasm"
XBE = ROOT.parent / "disc" / "default.xbe"
SELECTED = {
    0x0C73FE: "aiBrainHookman_Update",
    0x14F300: "mcProgressManager_SetupCareerCruise",
    0x14F560: "mcProgressManager_SelectHookmanRaceFromFollow",
    0x14F8C0: "mcProgressManager_CheckAndRequestPostRaceMovie",
    0x14FAF0: "mcProgressManager_SetupNextCareerRace",
    0x14FC50: "mcProgressManager_AdvanceHookmanProgress",
    0x14FCC0: "mcProgressManager_ReportRaceResult",
}


def main() -> None:
    functions = json.loads((DISASM / "functions.json").read_text(encoding="utf-8"))
    by_start = {int(item["start"], 16): item for item in functions}
    selected = []
    ranges = []
    for address, semantic_name in SELECTED.items():
        item = by_start.get(address)
        if not item:
            owners = [
                candidate for candidate in functions
                if int(candidate["start"], 16) <= address < int(candidate["end"], 16)
            ]
            if not owners:
                raise SystemExit(f"xboxrecomp did not cover 0x{address:08X}")
            item = owners[0]
        entry = dict(item)
        entry["semantic_name"] = semantic_name
        entry["requested_start"] = f"0x{address:08X}"
        entry["detected_owner_start"] = item["start"]
        selected.append(entry)
        ranges.append((address, int(item["end"], 16), semantic_name))

    address_re = re.compile(r"^\s*0x([0-9A-Fa-f]{8})\s")
    blocks = {start: [] for start, _, _ in ranges}
    with (DISASM / "asm" / "text.asm").open("r", encoding="utf-8", errors="replace") as source:
        for line in source:
            match = address_re.match(line)
            if not match:
                continue
            address = int(match.group(1), 16)
            for start, end, _ in ranges:
                if start <= address < end:
                    blocks[start].append(line.rstrip())
                    break

    output = []
    for start, end, semantic_name in ranges:
        output.extend([
            "; ============================================================",
            f"; {semantic_name}",
            f"; xbox VA 0x{start:08X}..0x{end:08X}",
            "; ============================================================",
            *blocks[start],
            "",
        ])
    (ROOT / "selected_career_functions.asm").write_text("\n".join(output), encoding="utf-8")

    manifest = {
        "source_xbe": str(XBE),
        "source_xbe_sha256": hashlib.sha256(XBE.read_bytes()).hexdigest(),
        "tool": "sp00nznet/xboxrecomp tools.disasm",
        "function_count_full_text": len(functions),
        "selected_functions": selected,
    }
    (ROOT / "selected_career_functions.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(f"wrote {len(selected)} functions")


if __name__ == "__main__":
    main()
