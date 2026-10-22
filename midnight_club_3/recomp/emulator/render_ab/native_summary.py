"""MC3-0008: summary of run_render_native.py runs (garage + San Diego).

  python -I native_summary.py <substring of run dir names> ...

Per run: passed, the last timing windows (the drive), the passes' own GPU cost; per capture: where the
post and shadow passes ran and how many pixels each changed (before/after of the same frame).
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import statistics as st
import sys

from PIL import Image, ImageChops

RUNS = Path(__file__).parent / "runs"
TIMING = re.compile(r"cpu_ms avg=([\d.]+) p95=([\d.]+) p99=([\d.]+) gpu_ms avg=([\d.]+) p95=([\d.]+) p99=([\d.]+)")


def changed(cap: Path, kind: str) -> str:
    pre = [p for p in cap.glob("*.bmp") if re.fullmatch(rf"\d{{4}}_{kind}_pre_\w+\.bmp", p.name)]
    post = [p for p in cap.glob("*.bmp") if re.fullmatch(rf"\d{{4}}_{kind}_(overlay|present|blended)\.bmp", p.name)]
    if not pre or not post:
        return "-"
    a, b = Image.open(pre[0]).convert("RGB"), Image.open(post[0]).convert("RGB")
    h = ImageChops.difference(a, b).convert("L").histogram()
    return f"{(sum(h[1:]) / (a.size[0] * a.size[1])) * 100:.1f}%"


def main() -> int:
    for run in sorted(RUNS.iterdir()):
        if not run.name[16:].startswith("native") or not any(k in run.name for k in sys.argv[1:]):
            continue
        if not (run / "result.json").exists():
            continue
        r = json.loads((run / "result.json").read_text(encoding="utf-8"))
        m = r.get("mc3render", [])
        rows = [[float(x) for x in t.groups()] for ln in m if (t := TIMING.search(ln))]
        last = rows[-3:]
        cols = list(zip(*last)) if last else None
        def cost(key):
            v = [float(x.group(1)) for ln in m if (x := re.search(key + r" avg=([\d.]+)", ln))]
            return f"{st.mean(v[-3:]):.3f}" if v else "-"
        print(f"== {run.name[16:]} passed={r.get('passed')} {r.get('error', '')}")
        if cols:
            print(f"   drive: cpu avg {st.mean(cols[0]):.2f} p99 {st.mean(cols[2]):.2f} | gpu avg {st.mean(cols[3]):.3f} "
                  f"p99 {st.mean(cols[5]):.3f} | post_ms {cost('post_pass_ms')} shadow_ms {cost('contact_shadow_ms')} "
                  f"vshadow_ms {cost('vehicle_shadow_ms')} sun_ms {cost('sun_shadow_ms')}")
        for name, c in r.get("captures", {}).items():
            if not c.get("capture"):
                print(f"   {name:14} no capture")
                continue
            cap = Path(c["capture"])
            lines = c.get("lines", [])
            where = " ".join(ln[:4] + ":" + ln.split()[1] for ln in lines) or "none"
            print(f"   {name:14} passes {where:34} post {changed(cap, 'post'):6} shadow {changed(cap, 'shadow'):6} "
                  f"vshadow {changed(cap, 'vshadow'):6} sun {changed(cap, 'sun'):6}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
