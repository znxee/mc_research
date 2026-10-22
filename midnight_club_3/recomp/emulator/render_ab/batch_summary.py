"""MC3-0008: one line per in-game run: steady race timing, pass costs, how often the passes ran, captures.

  python -I batch_summary.py <substring of run dir names> ...
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import statistics as st
import sys

RUNS = Path(__file__).parent / "runs"
TIMING = re.compile(r"cpu_ms avg=([\d.]+) p95=([\d.]+) p99=([\d.]+) gpu_ms avg=([\d.]+) p95=([\d.]+) p99=([\d.]+).*psos=(\d+)")


def avg(lines: list[str], key: str) -> str:
    v = [float(m.group(1)) for ln in lines if (m := re.search(key + r" avg=([\d.]+)", ln))]
    return f"{st.mean(v):.3f}" if v else "-"


def main() -> int:
    for run in sorted(RUNS.iterdir()):
        if not any(k in run.name for k in sys.argv[1:]) or not (run / "result.json").exists():
            continue
        r = json.loads((run / "result.json").read_text(encoding="utf-8"))
        m = r.get("mc3render", [])
        rows = [[float(x) for x in t.groups()] for ln in m if (t := TIMING.search(ln))]
        steady = [x for x in rows if x[6] >= 170][2:]  # race pipelines made, the first windows dropped
        cols = list(zip(*steady)) if steady else None
        adapter = next((ln.split("name=")[1].split('"')[1] for ln in m if "adapter_index=" in ln), "?")
        shadow = [ln for ln in m if "contact-shadow:" in ln and "of the last 600" in ln]
        post = [ln for ln in m if "MC3RENDER post:" in ln]
        sh_frames = [int(re.search(r": (\d+) of", ln).group(1)) for ln in shadow]
        po_frames = [int(re.search(r": (\d+) of", ln).group(1)) for ln in post]
        print(f"{run.name[16:]:40} passed={r.get('passed')} gpu={adapter[15:]:8} windows={len(steady):3} "
              + (f"cpu {st.mean(cols[0]):.2f}/{st.mean(cols[2]):.2f} gpu {st.mean(cols[3]):.3f}/{st.mean(cols[5]):.3f} "
                 if cols else "no steady windows ")
              + f"post_ms={avg(m, 'post_pass_ms')} shadow_ms={avg(m, 'contact_shadow_ms')} vshadow_ms={avg(m, 'vehicle_shadow_ms')} "
              + f"shadow_frames(max)={max(sh_frames) if sh_frames else '-'} post_frames(max)={max(po_frames) if po_frames else '-'} "
              + f"error={r.get('error', '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
