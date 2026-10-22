"""MC3-0008: the dubshop garage and San Diego free roam, native MC3 (no MC2 career, no MC3_MC2_DIR).

Boots MC3RemixXBE.exe with one renderer profile, loads profile Player 1 (a San Diego career), opens
Career > Go to Garage, takes F3 captures there, leaves the garage, continues the career into San Diego
and takes F3 captures standing and driving. Every step leaves a screenshot in the run folder.

  python -I run_render_native.py --profile legacy
  python -I run_render_native.py --profile hybrid --feature post,contact-shadow
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "mc2_career_test"))
from PIL import Image  # noqa: E402
from mc2_conditional_controller import MC2ConditionalController  # noqa: E402
from run_mc2_headless import capture_window, find_game_window  # noqa: E402

GAME_DIR = Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/xbox_recomp/xboxxberecomp_eval/templates/game'))
EXE = GAME_DIR / "MC3RemixXBE.exe"
CAPTURES = GAME_DIR / "gpu_captures"
LOG = GAME_DIR / "logs" / "mc3_xbe.log"
TITLE = "MC3 title: update"
# the profile list's rows (1080p screenshot): Player 1-4, Create Profile
PROFILE_ROWS = [475, 518, 562, 608, 650]
u = ctypes.windll.user32


def say(m: str) -> None:
    print(m, flush=True)


def orange_rows(img: Path, rows: list[int], x0=560, x1=1360, half=16) -> list[int]:
    """Orange (highlighted) text pixels in each row band."""
    im = Image.open(img).convert("RGB")
    out = []
    for y in rows:
        n = 0
        for yy in range(y - half, y + half, 2):
            for xx in range(x0, x1, 3):
                r, g, b = im.getpixel((xx, yy))
                # highlighted text is warm (red over blue by 50-80), plain text near grey (about 20)
                n += r > 130 and r - b > 45
        out.append(n)
    return out


class Native:
    def __init__(self, args: list[str], out: Path):
        self.args, self.out = args, out
        self.ctl = MC2ConditionalController()
        self.result: dict = {"args": args, "steps": [], "captures": {}}
        self.step_n = 0

    def alive(self):
        if self.proc.poll() is not None:
            raise RuntimeError(f"game exited with {self.proc.returncode}")

    def log(self) -> str:
        try:
            return (self.out / "game.stderr.log").read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return ""

    def shot(self, name: str) -> Path:
        self.step_n += 1
        p = self.out / f"{self.step_n:02d}_{name}.png"
        capture_window(self.hwnd, p)
        st = self.ctl.poll_state()
        self.result["steps"].append({"name": name, "shot": str(p), "state": st})
        return p

    def pad(self, name: str, n: int = 1, gap: float = 0.35):
        for _ in range(n):
            self.ctl.send_pad(name, frames=1000, settle=0.15)
            time.sleep(gap)

    def wait_state(self, want, timeout: float, during=None) -> dict:
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            self.alive()
            st = self.ctl.poll_state()
            if st and want(st):
                return st
            if during:
                during(st)
            time.sleep(0.25)
        raise TimeoutError(f"state not reached: {self.ctl.poll_state()}")

    def f3(self, name: str) -> dict:
        before = {p.name for p in CAPTURES.iterdir()}
        shot = self.shot(name)
        u.PostMessageW(self.hwnd, 0x0100, 0x72, 0)
        time.sleep(0.05)
        u.PostMessageW(self.hwnd, 0x0101, 0x72, 0)
        cap = None
        end = time.monotonic() + 40
        while time.monotonic() < end and not cap:
            for p in CAPTURES.iterdir():
                if p.name not in before and p.is_dir() and (p / "final.bmp").exists():
                    cap = p
            time.sleep(0.2)
        info = {"presented": str(shot), "capture": str(cap) if cap else None}
        if cap:
            time.sleep(1.5)
            txt = (cap / "frame.txt").read_text(encoding="utf-8", errors="ignore")
            info["lines"] = [ln[:200] for ln in txt.splitlines() if re.match(r"^\d{4} (post|shadow|vshadow) ", ln)]
        self.result["captures"][name] = info
        say(f"[f3] {name}: {cap} {info.get('lines', [])[:2]}")
        return info

    def execute(self, drive: float) -> dict:
        self.out.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ)
        env.pop("MC3_MC2_DIR", None)
        cmd = [str(EXE), *self.args]
        self.result["command"] = subprocess.list2cmdline(cmd)
        self.result["exe_sha256"] = hashlib.sha256(EXE.read_bytes()).hexdigest()
        se = (self.out / "game.stderr.log").open("w", encoding="utf-8")
        self.proc = subprocess.Popen(cmd, cwd=GAME_DIR, env=env, stdout=se, stderr=se)
        try:
            end = time.monotonic() + 30
            self.hwnd = None
            while time.monotonic() < end and not self.hwnd:
                self.alive()
                self.hwnd = find_game_window(self.proc.pid)
                time.sleep(0.1)
            self.ctl.hwnd = self.hwnd
            if not self.ctl.connect(timeout=30):
                raise RuntimeError("no MC3_GAME_STATE")

            # boot: skip the movies while they play, until the title updates
            end = time.monotonic() + 150
            while TITLE not in self.log():
                self.alive()
                if time.monotonic() > end:
                    raise TimeoutError("title not reached")
                st = self.ctl.poll_state()
                if st and st["is_fmv"]:
                    self.pad("start", 1, 0.2)
                    self.pad("a", 1, 0.2)
                elif st and st["state"] == 7 and not st["menu_active"]:
                    self.pad("a", 1, 0.2)
                time.sleep(0.8)
            time.sleep(2.5)
            self.shot("title")
            self.pad("start")

            # the profile list: walk the highlight to Player 1 by its colour
            self.wait_state(lambda s: s["cursor_ready"] and s["menu_active"], 30)
            time.sleep(1.0)
            for _ in range(6):
                rows = orange_rows(self.shot("profiles"), PROFILE_ROWS)
                at = max(range(len(rows)), key=lambda i: rows[i])
                say(f"[profiles] highlight on row {at} {rows}")
                if rows[at] < 20:
                    raise RuntimeError(f"profile list highlight not found: {rows}")
                if at == 0:
                    break
                self.pad("up")
                time.sleep(0.6)
            else:
                raise RuntimeError("Player 1 not reached")
            self.pad("a")

            # main menu: the cursor starts on Career; Career's own menu starts on Continue Career
            self.wait_state(lambda s: s["cursor_ready"] and s["menu_active"], 40)
            time.sleep(1.5)
            self.shot("main_menu")
            self.pad("a")
            self.wait_state(lambda s: s["cursor_ready"] and s["menu_active"], 20)
            time.sleep(1.0)
            self.shot("career_menu")
            self.pad("down")
            time.sleep(0.6)
            self.shot("career_garage_selected")
            self.pad("a")
            time.sleep(2.0)
            st = self.ctl.poll_state()
            if st and st["state"] == 7:
                # "your current progress will be lost": nothing was played, Yes is one row up
                self.shot("garage_confirm")
                self.pad("up")
                self.pad("a")
            self.wait_state(lambda s: s["state"] == 5, 60)
            time.sleep(6.0)
            self.f3("garage_front")
            self.pad("left")
            time.sleep(2.5)
            self.f3("garage_turned")

            # leave the garage, continue the career into San Diego
            self.pad("b")
            time.sleep(1.5)
            self.shot("exit_garage")
            self.pad("up")
            self.pad("a")

            def into_city(st):
                if st and st["state"] == 7 and st["cursor_ready"] and st["menu_active"]:
                    self.shot("menu_after_garage")
                    self.pad("a")
                    time.sleep(2.0)

            self.wait_state(lambda s: s["state"] == 2, 120, into_city)
            time.sleep(8.0)
            self.f3("sd_still")
            # the career starts facing a garage door: turn away from it, then drive
            self.ctl.inject_report(rt=255, lx=32767, frames=100000)
            time.sleep(2.5)
            self.ctl.inject_report(rt=255, frames=100000)
            time.sleep(3.0)
            self.f3("sd_drive1")
            self.ctl.inject_report(rt=255, lx=13000, frames=100000)
            time.sleep(5.0)
            self.f3("sd_drive2")
            self.ctl.inject_report(rt=255, frames=100000)
            time.sleep(drive)
            self.ctl.release_report()
            self.result["passed"] = True
        except Exception as e:  # noqa: BLE001
            self.result["passed"] = False
            self.result["error"] = str(e)
            say(f"[FAIL] {e}")
            try:
                self.shot("failure")
            except Exception:  # noqa: BLE001
                pass
        finally:
            try:
                self.ctl.release_report()
            except Exception:  # noqa: BLE001
                pass
            self.proc.terminate()
            try:
                self.proc.wait(10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            se.close()
            text = LOG.read_text(encoding="utf-8", errors="ignore") if LOG.exists() else ""
            (self.out / "mc3_xbe.log").write_text(text, encoding="utf-8")
            self.result["mc3render"] = [ln.split("] ", 1)[-1] for ln in text.splitlines() if "MC3RENDER" in ln]
            (self.out / "result.json").write_text(json.dumps(self.result, indent=2), encoding="utf-8")
            say(f"[result] {self.out / 'result.json'}")
        return self.result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="legacy")
    ap.add_argument("--feature", default="")
    ap.add_argument("--tag", default="")
    ap.add_argument("--drive", type=float, default=15.0, help="seconds of throttle with timing after the captures")
    ap.add_argument("--extra", action="append", default=[])
    a = ap.parse_args()
    stamp = time.strftime("%Y%m%d-%H%M%S")
    name = f"native_{a.profile}" + (f"_{a.feature.replace(',', '+')}" if a.feature else "") + (f"_{a.tag}" if a.tag else "")
    args = [f"--mc3-render-profile={a.profile}", f"--mc3-render-capture-ab={stamp}-{name}"]
    if a.feature:
        args.append(f"--mc3-render-feature={a.feature}")
    args += a.extra
    r = Native(args, HERE / "runs" / f"{stamp}_{name}").execute(a.drive)
    return 0 if r.get("passed") else 1


if __name__ == "__main__":
    sys.exit(main())
