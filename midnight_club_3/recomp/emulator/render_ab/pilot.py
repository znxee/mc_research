"""Drive one MC3RemixXBE process by hand, a command at a time (for mapping menu paths into a runner).

  python pilot.py launch [game args...]   start the game (MC3 only: no MC3_MC2_DIR), remember its pid
  python pilot.py pad NAME [COUNT]        up/down/left/right/start/a/b through the shared-memory pad
  python pilot.py drive SECONDS [STEER]   right trigger held, left stick x -1..1
  python pilot.py wait SECONDS
  python pilot.py shot NAME               PrintWindow of the game into pilot/NAME.png
  python pilot.py state                   the MC3_GAME_STATE snapshot
  python pilot.py f3 NAME                 F3 capture; prints its folder
  python pilot.py kill
"""

from __future__ import annotations

import ctypes
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "mc2_career_test"))
from mc2_conditional_controller import MC2ConditionalController  # noqa: E402
from run_mc2_headless import capture_window, find_game_window  # noqa: E402

GAME_DIR = Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/xbox_recomp/xboxxberecomp_eval/templates/game'))
EXE = GAME_DIR / "MC3RemixXBE.exe"
CAPTURES = GAME_DIR / "gpu_captures"
PID = HERE / "pilot.pid"
OUT = HERE / "pilot"
u = ctypes.windll.user32


def pid() -> int:
    return int(PID.read_text()) if PID.exists() else 0


def ctl() -> MC2ConditionalController:
    c = MC2ConditionalController(find_game_window(pid()))
    c.connect(timeout=10)
    return c


def f3(name: str) -> Path | None:
    hwnd = find_game_window(pid())
    before = {p.name for p in CAPTURES.iterdir()}
    capture_window(hwnd, OUT / f"{name}_presented.png")
    u.PostMessageW(hwnd, 0x0100, 0x72, 0)
    time.sleep(0.05)
    u.PostMessageW(hwnd, 0x0101, 0x72, 0)
    end = time.monotonic() + 40
    while time.monotonic() < end:
        for p in CAPTURES.iterdir():
            if p.name not in before and p.is_dir() and (p / "final.bmp").exists():
                time.sleep(1.5)
                return p
        time.sleep(0.2)
    return None


def main() -> int:
    OUT.mkdir(exist_ok=True)
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "launch":
        env = dict(os.environ)
        env.pop("MC3_MC2_DIR", None)
        log = open(OUT / "game.stderr.log", "w")
        p = subprocess.Popen([str(EXE), *args], cwd=GAME_DIR, env=env, stdout=log, stderr=log,
                             creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | 0x00000008)  # DETACHED_PROCESS
        PID.write_text(str(p.pid))
        end = time.monotonic() + 30
        while time.monotonic() < end and not find_game_window(p.pid):
            time.sleep(0.2)
        print("pid", p.pid, "window", find_game_window(p.pid))
    elif cmd == "pad":
        c = ctl()
        for _ in range(int(args[1]) if len(args) > 1 else 1):
            c.send_pad(args[0], frames=1000, settle=0.15)
            time.sleep(0.35)
        print(json.dumps(c.poll_state()))
    elif cmd == "drive":
        # throttle for SECONDS, optionally steering (-1..1)
        c = ctl()
        steer = float(args[1]) if len(args) > 1 else 0.0
        c.inject_report(rt=255, lx=int(steer * 32767), frames=100000)
        time.sleep(float(args[0]))
        c.release_report()
    elif cmd == "wait":
        time.sleep(float(args[0]))
    elif cmd == "shot":
        print(capture_window(find_game_window(pid()), OUT / f"{args[0]}.png"))
    elif cmd == "state":
        print(json.dumps(ctl().poll_state()))
    elif cmd == "f3":
        print(f3(args[0]))
    elif cmd == "kill":
        subprocess.run(["taskkill", "/PID", str(pid()), "/F"], capture_output=True)
        PID.unlink(missing_ok=True)
        print("killed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
