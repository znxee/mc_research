"""MC3-0008 Gate 6: the sun shadow's captures side by side.

  python -I sun_views.py <substring of capture dir names> <out.png> [scale]

Per capture: the frame before the pass, after it, and where it darkened (amplified), one row each.
"""

import os
from __future__ import annotations

from pathlib import Path
import re
import sys

from PIL import Image, ImageChops, ImageDraw

CAPTURES = Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/xbox_recomp/xboxxberecomp_eval/templates/game/gpu_captures'))


def main() -> int:
    key, out = sys.argv[1], Path(sys.argv[2])
    scale = float(sys.argv[3]) if len(sys.argv) > 3 else 0.4
    rows = []
    for d in sorted(CAPTURES.iterdir()):
        if not d.is_dir() or key not in d.name:
            continue
        pre = [p for p in d.glob("*.bmp") if re.fullmatch(r"\d{4}_sun_pre_\w+\.bmp", p.name)]
        post = [p for p in d.glob("*.bmp") if re.fullmatch(r"\d{4}_sun_(blended|overlay)\.bmp", p.name)]
        if not pre or not post:
            continue
        a, b = Image.open(pre[0]).convert("RGB"), Image.open(post[0]).convert("RGB")
        diff = ImageChops.difference(a, b).convert("L").point(lambda v: min(255, v * 4))
        w, h = int(a.size[0] * scale), int(a.size[1] * scale)
        row = Image.new("RGB", (w * 3, h + 18), (20, 20, 20))
        for i, im in enumerate([a, b, diff.convert("RGB")]):
            row.paste(im.resize((w, h)), (i * w, 18))
        ImageDraw.Draw(row).text((4, 3), d.name[:6] + " " + pre[0].name, fill=(255, 255, 0))
        rows.append(row)
    if not rows:
        print("no captures")
        return 1
    sheet = Image.new("RGB", (max(r.size[0] for r in rows), sum(r.size[1] for r in rows)))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.size[1]
    sheet.save(out)
    print(out, sheet.size)
    return 0


if __name__ == "__main__":
    sys.exit(main())
