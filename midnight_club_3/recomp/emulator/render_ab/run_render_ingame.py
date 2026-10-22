"""MC3-0008: in-game scenes (HUD, minimap, gauges, MC2 Los Angeles) under one renderer profile.

Drives the MC2 career headless path (run_mc2_headless.CareerRun) to a running race,
then presses F3 twice while driving and keeps PrintWindow shots, all tagged with
the profile. One process per profile; compare inside each capture (post_pre vs
post) and across profiles by metadata.

  python -I run_render_ingame.py --profile legacy
  python -I run_render_ingame.py --profile hybrid --feature post
"""

from __future__ import annotations

import argparse
import ctypes
import json
import re
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "mc2_career_test"))
import run_mc2_headless as H  # noqa: E402
from run_render_ab import CAPTURES, diff, image_stats, sha256  # noqa: E402

u = ctypes.windll.user32
WM_KEYDOWN, WM_KEYUP, VK_F3 = 0x0100, 0x0101, 0x72


def hold(keys: list[int], seconds: float) -> None:
    """Keys held down system wide: the freecam reads GetAsyncKeyState."""
    for k in keys:
        u.keybd_event(k, 0, 0, 0)
    time.sleep(seconds)
    for k in reversed(keys):
        u.keybd_event(k, 0, 2, 0)
    time.sleep(0.1)


def freecam_views(run: H.CareerRun, result: dict) -> None:
    """F7 freecam around the player's car: from above, from the side, back level and low."""
    VK_F7, VK_CONTROL, VK_DOWN, VK_UP = 0x76, 0x11, 0x28, 0x26
    run.controller.release_report()
    time.sleep(1.5)  # let the car roll to a stop under the chase camera
    hold([VK_F7], 0.1)
    hold([VK_CONTROL, ord("R")], 0.5)   # 3 m up at the slow speed
    hold([VK_UP], 0.55)                 # look down about 0.9 rad (MC3's view looks along -z: the keys come out swapped)
    result["freecam_above"] = f3(run, "freecam_above")
    hold([VK_CONTROL, ord("D")], 1.0)   # 6 m to the side
    result["freecam_side"] = f3(run, "freecam_side")
    hold([VK_DOWN], 0.4)                # flatter, the shadow's edge against the road
    hold([VK_CONTROL, ord("F")], 0.35)
    result["freecam_low"] = f3(run, "freecam_low")
    hold([VK_F7], 0.1)


def f3(run: H.CareerRun, name: str) -> dict:
    before = {p.name for p in CAPTURES.iterdir()}
    shot = H.capture_window(run.hwnd, run.output_dir / f"{name}_presented.png")
    u.PostMessageW(run.hwnd, WM_KEYDOWN, VK_F3, 0)
    time.sleep(0.05)
    u.PostMessageW(run.hwnd, WM_KEYUP, VK_F3, 0)
    end = time.monotonic() + 40
    cap = None
    while time.monotonic() < end and not cap:
        for p in CAPTURES.iterdir():
            if p.name not in before and p.is_dir() and (p / "final.bmp").exists():
                cap = p
        time.sleep(0.2)
    info = {"presented": str(shot) if shot else None, "capture": str(cap) if cap else None}
    if cap:
        time.sleep(1.5)
        info["final_sha256"] = sha256(cap / "final.bmp")
        info["final_stats"] = image_stats(cap / "final.bmp")
        lines = [ln for ln in (cap / "frame.txt").read_text(encoding="utf-8", errors="ignore").splitlines()
                 if re.match(r"^\d{4} (post|shadow) ", ln)]
        info["post_lines"] = lines
        pre = sorted(p for p in cap.glob("*.bmp") if re.fullmatch(r"\d{4}_post_pre_(overlay|present)\.bmp", p.name))
        post = sorted(p for p in cap.glob("*.bmp") if re.fullmatch(r"\d{4}_post_(overlay|present)\.bmp", p.name))
        if pre and post:
            info["post_diff"] = diff(pre[0], post[0])
    H.say(f"[{name}] {json.dumps(info)[:400]}")
    return info


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="legacy")
    ap.add_argument("--feature", default="")
    ap.add_argument("--post", default="")
    ap.add_argument("--shadow", default="")
    ap.add_argument("--tag", default="")
    ap.add_argument("--freecam", action="store_true", help="F7 views of the car after driving")
    ap.add_argument("--extra", action="append", default=[], help="another game argument, e.g. --extra=--mc3-gpu-index=1")
    ap.add_argument("--city", default="la")
    ap.add_argument("--stage", type=int, default=1)
    ap.add_argument("--drive", type=float, default=20.0, help="seconds of throttle with timing after the captures")
    a = ap.parse_args()
    stamp = time.strftime("%Y%m%d-%H%M%S")
    name = f"ingame_{a.profile}" + (f"_{a.feature.replace(',', '+')}" if a.feature else "") + (f"_{a.tag}" if a.tag else "")
    out = HERE / "runs" / f"{stamp}_{name}"
    args = [f"--mc3-mc2-city={a.city}", f"--mc3-mc2-stage={a.stage}", "--mc3-mc2-car=0",
            f"--mc3-render-profile={a.profile}", f"--mc3-render-capture-ab={stamp}-{name}"]
    if a.feature:
        args.append(f"--mc3-render-feature={a.feature}")
    if a.post:
        args.append(f"--mc3-post={a.post}")
    if a.shadow:
        args.append(f"--mc3-shadow={a.shadow}")
    args += a.extra
    run = H.CareerRun(out, keep_open=True, game_args=args)
    result = {"name": name, "args": args, "exe_sha256": sha256(H.EXE_PATH)}
    try:
        result["career"] = run.execute()
        result["race_start"] = f3(run, "race_start")
        run.controller.inject_report(rt=255, frames=100000)
        time.sleep(6.0)
        result["driving"] = f3(run, "driving")
        time.sleep(a.drive)
        run.controller.release_report()
        if a.freecam:
            freecam_views(run, result)
        result["passed"] = True
    except Exception as e:  # noqa: BLE001
        result["passed"] = False
        result["error"] = str(e)
        H.say(f"[FAIL] {e}")
    finally:
        run.keep_open = False
        run.close()
        log = H.GAME_DIR / "logs" / "mc3_xbe.log"
        text = log.read_text(encoding="utf-8", errors="ignore") if log.exists() else ""
        result["mc3render"] = [ln.split("] ", 1)[-1] for ln in text.splitlines() if "MC3RENDER" in ln]
        # a run whose game died is no pass: the F3 captures come back empty and the log has the exception
        faults = [ln.split("] ", 1)[-1] for ln in text.splitlines() if "error: exception " in ln]
        missing = [k for k in ("race_start", "driving") if not (result.get(k) or {}).get("capture")]
        if result.get("passed") and (faults or missing):
            result["passed"] = False
            result["error"] = (f"guest exception: {faults[0]}" if faults else "") + \
                (f" no capture for {', '.join(missing)}" if missing else "")
            H.say(f"[FAIL] {result['error']}")
        result["exceptions"] = faults[:8]
        out.mkdir(parents=True, exist_ok=True)
        (out / "mc3_xbe.log").write_text(text, encoding="utf-8")
        (out / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        H.say(f"[result] {out / 'result.json'}")
    return 0 if result.get("passed") else 1


if __name__ == "__main__":
    sys.exit(main())
