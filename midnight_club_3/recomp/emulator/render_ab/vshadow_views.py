"""MC3-0008: the vehicle shadow in one run, before and after its pass, and its depth map (debug=2 corner).

  python -I vshadow_views.py <run dir> <out prefix>

Writes <prefix>_pairs.png (before | after per capture), <prefix>_map.png (the corners, enlarged) and
<prefix>_zoom.png (the ground behind the car, enlarged); prints the vshadow line and changed pixels.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

from PIL import Image, ImageChops


def main() -> int:
    run, prefix = Path(sys.argv[1]), sys.argv[2]
    r = json.loads((run / "result.json").read_text(encoding="utf-8"))
    pairs = []
    for k in ["race_start", "driving", "freecam_above", "freecam_side", "freecam_low", "garage_front", "sd_still", "sd_drive1"]:
        caps = r.get("captures", {})
        info = r.get(k) or caps.get(k)
        if not info or not info.get("capture"):
            continue
        cap = Path(info["capture"])
        pre = [p for p in cap.glob("*.bmp") if re.fullmatch(r"\d{4}_vshadow_pre_\w+\.bmp", p.name)]
        post = [p for p in cap.glob("*.bmp") if re.fullmatch(r"\d{4}_vshadow_(blended|overlay)\.bmp", p.name)]
        line = next((ln for ln in (cap / "frame.txt").read_text(encoding="utf-8", errors="ignore").splitlines()
                     if re.match(r"^\d{4} vshadow", ln)), "no vshadow line")
        if not pre or not post:
            print(f"{k:14} {line[:120]}")
            continue
        a, b = Image.open(pre[0]).convert("RGB"), Image.open(post[0]).convert("RGB")
        h = ImageChops.difference(a, b).convert("L").histogram()
        print(f"{k:14} changed={sum(h[1:]):6} {line[:140]}")
        pairs.append((k, a, b))
    if not pairs:
        return 1
    w, hgt = pairs[0][1].size
    grid = Image.new("RGB", (w * 2, hgt * len(pairs)))
    maps = Image.new("RGB", (420 * len(pairs), 420))
    zoom = Image.new("RGB", (720, 400 * len(pairs)))
    for i, (_, a, b) in enumerate(pairs):
        grid.paste(a, (0, i * hgt))
        grid.paste(b, (w, i * hgt))
        maps.paste(b.crop((0, 0, 140, 140)).resize((420, 420), Image.NEAREST), (i * 420, 0))
        box = (200, 300, 520, 480)
        zoom.paste(Image.new("RGB", (720, 400)), (0, i * 400))
        zoom.paste(a.crop(box).resize((360, 200), Image.NEAREST), (0, i * 400))
        zoom.paste(b.crop(box).resize((360, 200), Image.NEAREST), (360, i * 400))
        zoom.paste(b.crop(box).resize((720, 400), Image.NEAREST).crop((0, 200, 720, 400)), (0, i * 400 + 200))
    grid.save(prefix + "_pairs.png")
    maps.save(prefix + "_map.png")
    zoom.save(prefix + "_zoom.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
