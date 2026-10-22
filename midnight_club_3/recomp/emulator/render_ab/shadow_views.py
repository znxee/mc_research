"""MC3-0008: the contact shadow in one in-game run, before and after its pass in each F3 capture.

  python -I shadow_views.py <run dir> [out.png]

Prints the changed pixels per capture and writes a grid: before | after, one row per capture.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

from PIL import Image, ImageChops

SCENES = ["race_start", "driving", "freecam_above", "freecam_side", "freecam_low"]


def pair(cap: Path):
    pre = [p for p in cap.glob("*.bmp") if re.fullmatch(r"\d{4}_shadow_pre_\w+\.bmp", p.name)]
    post = [p for p in cap.glob("*.bmp") if re.fullmatch(r"\d{4}_shadow_(blended|overlay)\.bmp", p.name)]
    if not pre or not post:
        return None
    return Image.open(pre[0]).convert("RGB"), Image.open(post[0]).convert("RGB")


def main() -> int:
    run = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else run / "shadow_views.png"
    r = json.loads((run / "result.json").read_text(encoding="utf-8"))
    rows = []
    for k in SCENES:
        if k not in r or not r[k].get("capture"):
            continue
        cap = Path(r[k]["capture"])
        p = pair(cap)
        line = next((ln for ln in r[k].get("post_lines", []) if " shadow " in ln[:12]), "")
        if not p:
            print(k, "no shadow pair", line[:120])
            continue
        h = ImageChops.difference(*p).convert("L").histogram()
        print(f"{k:14} changed={sum(h[1:]):6} max={max(i for i, c in enumerate(h) if c):3} {line[:110]}")
        rows.append(p)
    if rows:
        w, hgt = rows[0][0].size
        grid = Image.new("RGB", (w * 2, hgt * len(rows)))
        for i, (a, b) in enumerate(rows):
            grid.paste(a, (0, i * hgt))
            grid.paste(b, (w, i * hgt))
        grid.save(out)
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
