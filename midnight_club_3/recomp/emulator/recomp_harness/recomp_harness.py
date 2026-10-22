"""Drive the XboxXBERecomp build of Midnight Club 3 on Windows: start it, press keys,
take screenshots, and run a scripted race for regression checks.

Environment:
    MC3_RECOMP_DIR   folder that holds MC3RemixXBE.exe and settings.toml (required)
    MC_OUTPUT_DIR    where screenshots, logs and run files go (default: ./recomp_runs)

Commands:
    start [--fps-cap N] [--vsync 0|1] [--size WxH]    launch the game with those settings
    keys NAME[:HOLD] ...                              press keys; sleepN waits N seconds
    shot NAME                                         screenshot of the game window
    drive SECONDS NAME                                hold accelerate for SECONDS, then screenshot
    kill                                              stop the game
    scenario arcade-race NAME [--fps-cap N] [--vsync 0|1] [--size WxH]
                                                      menu route to San Diego cruise, a short drive,
                                                      screenshots, log copied to MC_OUTPUT_DIR

The settings.toml of the game is backed up before any change and restored afterwards.
Windows only: keyboard input goes through user32 and captures through PIL.
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

GAME_DIR = Path(os.environ.get("MC3_RECOMP_DIR", ""))
OUT = Path(os.environ.get("MC_OUTPUT_DIR", "recomp_runs"))
EXE = "MC3RemixXBE.exe"
SETTINGS_KEYS = ("fps_cap", "vsync", "width", "height", "render_percent")
VK = {"space": 0x20, "enter": 0x0D, "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
      "esc": 0x1B, "rshift": 0xA1, "f3": 0x72, "f6": 0x75}
user32 = ctypes.windll.user32


def need_game_dir():
    if not GAME_DIR or not (GAME_DIR / EXE).exists():
        sys.exit(f"set MC3_RECOMP_DIR to the folder that holds {EXE} (now: {GAME_DIR!s})")


def pid_file():
    return OUT / "run.pid"


def find_window():
    pid = int(pid_file().read_text())
    found = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        owner = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value == pid and user32.IsWindowVisible(hwnd):
            found.append(hwnd)
        return True

    user32.EnumWindows(cb, 0)
    if not found:
        sys.exit("no visible window for the game; is it running? (start first)")
    return found[0]


def set_settings(fps_cap=None, vsync=None, size=None):
    path = GAME_DIR / "settings.toml"
    text = path.read_text(encoding="utf-8")
    values = {"fps_cap": fps_cap, "vsync": vsync}
    if size:
        w, h = size.lower().split("x")
        values.update({"width": w, "height": h, "render_percent": "200"})
    for key, value in values.items():
        if value is None:
            continue
        text = re.sub(rf"^{key} = .*$", f"{key} = {value}", text, flags=re.M)
    path.write_text(text, encoding="utf-8")


def backup_settings():
    src = GAME_DIR / "settings.toml"
    dst = OUT / "settings.toml.backup"
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def restore_settings(backup):
    shutil.copy2(backup, GAME_DIR / "settings.toml")


def press(name, hold=0.15):
    hwnd = find_window()
    user32.ShowWindow(hwnd, 9)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.15)
    vk = VK[name]
    user32.keybd_event(vk, 0, 0, 0)
    time.sleep(hold)
    user32.keybd_event(vk, 0, 2, 0)
    time.sleep(0.3)


def shot(name):
    from PIL import ImageGrab
    hwnd = find_window()
    rect = wt.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    user32.ShowWindow(hwnd, 9)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.4)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.png"
    ImageGrab.grab((rect.left, rect.top, rect.right, rect.bottom), all_screens=True).save(path)
    return path


def start(fps_cap=None, vsync=None, size=None):
    need_game_dir()
    OUT.mkdir(parents=True, exist_ok=True)
    set_settings(fps_cap, vsync, size)
    env = dict(os.environ, XBE_CAPTURE_DIR=str(OUT / "gpu_captures"))
    proc = subprocess.Popen([str(GAME_DIR / EXE)], cwd=GAME_DIR, env=env,
                            stdout=open(OUT / "run.out", "w"), stderr=open(OUT / "run.err", "w"))
    pid_file().write_text(str(proc.pid))
    time.sleep(22)  # the game takes about this long to reach the intro


def kill():
    """Stop the game if it is still running; a game that already exited is not an error."""
    if pid_file().exists():
        subprocess.call(["taskkill", "/PID", pid_file().read_text(), "/F"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pid_file().unlink()


def run_keys(tokens):
    for tok in tokens:
        if tok.startswith("sleep"):
            time.sleep(float(tok[5:]))
            continue
        name, _, hold = tok.partition(":")
        press(name, float(hold) if hold else 0.15)


def scenario_arcade_race(name, fps_cap, vsync, size):
    """Intro, profile, Arcade, San Diego cruise, race; one screenshot per stage."""
    backup = backup_settings()
    try:
        start(fps_cap, vsync, size)
        run_keys(["enter", "sleep3", "enter", "sleep3", "enter", "sleep8", "space", "sleep8",
                  "down", "sleep1.2", "down", "sleep1.2", "enter", "sleep6", "space", "sleep5",
                  "enter", "sleep5", "enter", "sleep45"])
        shot(f"{name}_race")
        press("rshift", 1.5)
        shot(f"{name}_after_throttle")
        kill()
        log = GAME_DIR / "logs" / "mc3_xbe.log"
        if log.exists():
            shutil.copy2(log, OUT / f"{name}.log")
        print(f"scenario done: {OUT / name}*.png and {OUT / (name + '.log')}")
    finally:
        kill()
        restore_settings(backup)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("--fps-cap", type=int)
    s.add_argument("--vsync", type=int, choices=(0, 1))
    s.add_argument("--size")
    k = sub.add_parser("keys")
    k.add_argument("tokens", nargs="+")
    sh = sub.add_parser("shot")
    sh.add_argument("name")
    d = sub.add_parser("drive")
    d.add_argument("seconds", type=float)
    d.add_argument("name")
    sub.add_parser("kill")
    sc = sub.add_parser("scenario")
    sc.add_argument("which", choices=["arcade-race"])
    sc.add_argument("name")
    sc.add_argument("--fps-cap", type=int, default=30)
    sc.add_argument("--vsync", type=int, default=1, choices=(0, 1))
    sc.add_argument("--size", default="1280x960")
    a = ap.parse_args(argv)
    if a.cmd == "start":
        start(a.fps_cap, a.vsync, a.size)
    elif a.cmd == "keys":
        run_keys(a.tokens)
    elif a.cmd == "shot":
        print(shot(a.name))
    elif a.cmd == "drive":
        hwnd = find_window()
        user32.ShowWindow(hwnd, 9)
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.3)
        user32.keybd_event(VK["rshift"], 0, 0, 0)
        time.sleep(a.seconds)
        print(shot(a.name))
        user32.keybd_event(VK["rshift"], 0, 2, 0)
    elif a.cmd == "kill":
        kill()
    elif a.cmd == "scenario":
        need_game_dir()
        scenario_arcade_race(a.name, a.fps_cap, a.vsync, a.size)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
