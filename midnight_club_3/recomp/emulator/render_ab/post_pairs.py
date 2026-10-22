"""MC3-0008: every post pass pair in the tagged F3 captures, measured on the right files.

For each capture with a `NNNN post <why>` line: the scene before (NNNN_post_pre_<why>.bmp) and after
(NNNN_post_<why>.bmp) the pass, the same frame; the HUD region of final.bmp is reported for reference.

  python -I post_pairs.py [capture dir substring ...]
"""

import os
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

from PIL import Image, ImageChops

CAPTURES = Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/xbox_recomp/xboxxberecomp_eval/templates/game/gpu_captures'))


def pair(cap: Path) -> dict | None:
    txt = (cap / "frame.txt").read_text(encoding="utf-8", errors="ignore")
    lines = [ln for ln in txt.splitlines() if re.match(r"^\d{4} post ", ln)]
    if not lines:
        return None
    idx, why = re.match(r"^(\d{4}) post (\w+)", lines[0]).groups()
    pre, post = cap / f"{idx}_post_pre_{why}.bmp", cap / f"{idx}_post_{why}.bmp"
    if not pre.exists() or not post.exists():
        return {"line": lines[0], "missing": True}
    a, b = Image.open(pre).convert("RGB"), Image.open(post).convert("RGB")
    d = ImageChops.difference(a, b).convert("L")
    h = d.histogram()
    n = a.size[0] * a.size[1]
    changed = n - h[0]
    return {
        "line": lines[0][:120],
        "size": a.size,
        "changed_ratio": round(changed / n, 6),
        "changed_over_8": round(sum(h[9:]) / n, 6),
        "max_delta": max(i for i, c in enumerate(h) if c),
        "bbox": d.getbbox(),
    }


def main() -> int:
    keys = sys.argv[1:] or ["post"]
    out = {}
    for cap in sorted(p for p in CAPTURES.iterdir() if p.is_dir()):
        if not any(k in cap.name for k in keys) or not (cap / "frame.txt").exists():
            continue
        r = pair(cap)
        if r:
            out[cap.name] = r
            print(cap.name[:70], json.dumps(r))
    (Path(__file__).parent / "post_pairs.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
