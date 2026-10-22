"""MC3-0008 gate 0: the same scenes under each renderer profile, compared.

Each run boots MC3RemixXBE.exe with one profile, waits for the title and the main
menu, presses F3 at each (the backend's frame capture, tagged with the profile
through --mc3-render-capture-ab) and keeps a PrintWindow of the presented output.
A second legacy run is the control: whatever differs between two legacy runs is
the scene's own nondeterminism, not a profile.

  python -I run_render_ab.py                 # legacy, legacy, hybrid, enhanced
  python -I run_render_ab.py --gpu-pair      # also legacy on --mc3-gpu-index=1
"""

import os
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "mc2_career_test"))
from PIL import Image, ImageChops, ImageStat  # noqa: E402
from mc2_conditional_controller import MC2ConditionalController  # noqa: E402
from run_mc2_headless import capture_window, find_game_window  # noqa: E402

import ctypes  # noqa: E402

GAME_DIR = Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/xbox_recomp/xboxxberecomp_eval/templates/game'))
EXE = GAME_DIR / "MC3RemixXBE.exe"
CAPTURES = GAME_DIR / "gpu_captures"
LOG = GAME_DIR / "logs" / "mc3_xbe.log"
WM_KEYDOWN, WM_KEYUP, VK_F3 = 0x0100, 0x0101, 0x72
TITLE_MARKER = "MC3 title: update"
MENU_MARKER = "injected 'MC2 CAREER' below 'TOKYO CHALLENGE'"
u = ctypes.windll.user32


def say(m: str) -> None:
    print(m, flush=True)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class Run:
    def __init__(self, name: str, args: list[str], out: Path, tag: str, legal: float = 0.0, exe: Path = EXE):
        self.name, self.args, self.out, self.tag, self.legal, self.exe = name, args, out, tag, legal, exe
        self.proc = None
        self.hwnd = None
        self.ctl = MC2ConditionalController()
        self.result: dict = {"name": name, "args": args, "scenes": {}}

    def log(self) -> str:
        try:
            return self.out.joinpath("game.stderr.log").read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return ""

    def game_log(self) -> str:
        try:
            return LOG.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return ""

    def seen(self, marker: str) -> bool:
        return marker in self.log() or marker in self.game_log()

    def alive(self):
        if self.proc.poll() is not None:
            raise RuntimeError(f"game exited with {self.proc.returncode}")

    def skip_boot(self):
        st = self.ctl.poll_state()
        if st and st["is_fmv"]:
            self.ctl.send_pad("start", frames=1000, settle=0.08)
            self.ctl.send_pad("a", frames=1000, settle=0.08)
        elif st and st["state"] == 7 and not st["menu_active"]:
            self.ctl.send_pad("a", frames=1000, settle=0.08)

    def wait(self, marker: str, timeout: float, during=None, every=1.2) -> bool:
        end = time.monotonic() + timeout
        nxt = 0.0
        while time.monotonic() < end:
            self.alive()
            if self.seen(marker):
                return True
            if during and time.monotonic() >= nxt:
                during()
                nxt = time.monotonic() + every
            time.sleep(0.12)
        return self.seen(marker)

    def f3(self, scene: str) -> dict:
        before = {p.name for p in CAPTURES.iterdir()} if CAPTURES.exists() else set()
        shot = capture_window(self.hwnd, self.out / f"{scene}_presented.png")
        u.PostMessageW(self.hwnd, WM_KEYDOWN, VK_F3, 0)
        time.sleep(0.05)
        u.PostMessageW(self.hwnd, WM_KEYUP, VK_F3, 0)
        end = time.monotonic() + 30
        cap = None
        while time.monotonic() < end and not cap:
            self.alive()
            for p in CAPTURES.iterdir():
                if p.name not in before and p.is_dir() and (p / "final.bmp").exists():
                    cap = p
            time.sleep(0.2)
        info = {"presented": str(shot) if shot else None, "capture": str(cap) if cap else None}
        if cap:
            time.sleep(1.0)  # textures after final.bmp
            info["final_sha256"] = sha256(cap / "final.bmp")
        say(f"[{self.name}] {scene}: {info}")
        return info

    def execute(self, idle: float) -> dict:
        self.out.mkdir(parents=True, exist_ok=True)
        args = [str(self.exe), *self.args, f"--mc3-render-capture-ab={self.tag}"]
        self.result["command"] = subprocess.list2cmdline(args)
        self.result["exe_sha256"] = sha256(self.exe)
        so = self.out.joinpath("game.stdout.log").open("w", encoding="utf-8")
        se = self.out.joinpath("game.stderr.log").open("w", encoding="utf-8")
        self.proc = subprocess.Popen(args, cwd=GAME_DIR, stdout=so, stderr=se)
        try:
            end = time.monotonic() + 30
            while time.monotonic() < end and not self.hwnd:
                self.alive()
                self.hwnd = find_game_window(self.proc.pid)
                time.sleep(0.1)
            self.ctl.hwnd = self.hwnd
            if not self.ctl.connect(timeout=30):
                raise RuntimeError("no MC3_GAME_STATE")
            if self.legal:
                # the legal Flash screen is static: the one scene two runs can match pixel for pixel
                end = time.monotonic() + 120
                fmv_done = False
                while time.monotonic() < end:
                    self.alive()
                    st = self.ctl.poll_state()
                    if st and st["is_fmv"] and not fmv_done:
                        # Bink: never touched by the post pass, never white
                        time.sleep(2.0)
                        self.result["scenes"]["fmv"] = self.f3("fmv")
                        fmv_done = True
                    elif st and st["is_fmv"]:
                        self.ctl.send_pad("start", frames=1000, settle=0.08)
                        self.ctl.send_pad("a", frames=1000, settle=0.08)
                        time.sleep(1.0)
                    elif st and st["state"] == 7 and not st["menu_active"]:
                        time.sleep(self.legal)
                        self.result["scenes"]["legal"] = self.f3("legal")
                        break
                    time.sleep(0.1)
            if not self.wait(TITLE_MARKER, 150, self.skip_boot):
                raise TimeoutError("title not reached")
            time.sleep(3.0)
            self.result["scenes"]["title"] = self.f3("title")
            self.ctl.send_pad("start", frames=1000, settle=0.2)

            def profile():
                st = self.ctl.poll_state()
                if st and st["is_fmv"]:
                    self.ctl.send_pad("start", frames=1000, settle=0.08)
                elif st and st["cursor_ready"]:
                    self.ctl.send_pad("a", frames=1000, settle=0.12)

            if not self.wait(MENU_MARKER, 75, profile, every=1.8):
                raise TimeoutError("main menu not reached")
            end = time.monotonic() + 25
            while time.monotonic() < end:
                st = self.ctl.poll_state()
                if st and st["cursor_ready"]:
                    break
                time.sleep(0.1)
            time.sleep(3.0)
            self.result["scenes"]["menu"] = self.f3("menu")
            time.sleep(idle)  # timing windows of 600 frames
            self.result["passed"] = True
        except Exception as e:  # noqa: BLE001
            self.result["passed"] = False
            self.result["error"] = str(e)
            say(f"[{self.name}] FAIL {e}")
        finally:
            self.proc.terminate()
            try:
                self.proc.wait(10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            so.close()
            se.close()
            try:
                (self.out / "mc3_xbe.log").write_text(self.game_log(), encoding="utf-8")
            except OSError:
                pass
            eff = GAME_DIR / "logs" / "render_effective_config.txt"
            if eff.exists():
                (self.out / "render_effective_config.txt").write_text(eff.read_text(encoding="utf-8"), encoding="utf-8")
        text = self.game_log()
        self.result["mc3render"] = [ln.split("] ", 1)[-1] for ln in text.splitlines() if "MC3RENDER" in ln]
        return self.result


DRAW = re.compile(r"^\d{4} (draw|clear|copy)\b(.*)$")


def structure(frame: Path) -> list[str]:
    """frame.txt draw/clear/copy lines without the leading index and the floating constants."""
    out = []
    for ln in frame.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = DRAW.match(ln)
        if not m:
            continue
        body = m.group(2)
        body = body.split(" c0 ")[0]
        out.append(m.group(1) + body)
    return out


def image_stats(p: Path) -> dict:
    im = Image.open(p).convert("RGB")
    st = ImageStat.Stat(im)
    return {"size": im.size, "mean": [round(x, 3) for x in st.mean], "stddev": [round(x, 3) for x in st.stddev]}


def diff(a: Path, b: Path) -> dict:
    ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    if ia.size != ib.size:
        return {"same_size": False}
    d = ImageChops.difference(ia, ib)
    px = d.getdata()
    changed = sum(1 for p in px if p != (0, 0, 0))
    return {"same_size": True, "changed_pixels": changed, "changed_ratio": round(changed / (ia.size[0] * ia.size[1]), 6),
            "mean_abs": round(sum(ImageStat.Stat(d).mean) / 3, 4)}


def post_report(results: list[dict]) -> dict:
    """Inside one capture: the scene before and after the post pass, the same frame."""
    out = {}
    for r in results:
        for scene, info in r["scenes"].items():
            cap = info.get("capture")
            if not cap:
                continue
            cap = Path(cap)
            lines = [ln for ln in (cap / "frame.txt").read_text(encoding="utf-8", errors="ignore").splitlines()
                     if re.match(r"^\d{4} post ", ln)]
            entry = {"post_lines": lines}
            pre = sorted(p for p in cap.glob("*.bmp") if re.fullmatch(r"\d{4}_post_pre_(overlay|present)\.bmp", p.name))
            post = sorted(p for p in cap.glob("*.bmp") if re.fullmatch(r"\d{4}_post_(overlay|present)\.bmp", p.name))
            if pre and post:
                entry["pre"], entry["post"] = str(pre[0]), str(post[0])
                entry["diff"] = diff(pre[0], post[0])
            fin = cap / "final.bmp"
            if fin.exists():
                entry["final_stats"] = image_stats(fin)
            out[f"{r['name']}/{scene}"] = entry
    return out


def compare(results: list[dict]) -> dict:
    ref = results[0]
    rep = {"reference": ref["name"], "pairs": {}}
    for r in results:
        pair = {}
        for scene in ("fmv", "legal", "title", "menu"):
            a, b = ref["scenes"].get(scene, {}), r["scenes"].get(scene, {})
            if not a.get("capture") or not b.get("capture"):
                pair[scene] = {"missing": True}
                continue
            ca, cb = Path(a["capture"]), Path(b["capture"])
            sa, sb = structure(ca / "frame.txt"), structure(cb / "frame.txt")
            sh_a = sorted(p.name for p in ca.glob("*.hlsl"))
            sh_b = sorted(p.name for p in cb.glob("*.hlsl"))
            first = next((i for i, (x, y) in enumerate(zip(sa, sb)) if x != y), None)
            if first is None and len(sa) != len(sb):
                first = min(len(sa), len(sb))
            pair[scene] = {
                "final_identical": a.get("final_sha256") == b.get("final_sha256"),
                "final_diff": diff(ca / "final.bmp", cb / "final.bmp"),
                "final_stats": image_stats(cb / "final.bmp"),
                "commands": [len(sa), len(sb)],
                "command_sequence_identical": sa == sb,
                "first_divergent_command": first,
                "first_divergent_text": [sa[first] if first is not None and first < len(sa) else None,
                                         sb[first] if first is not None and first < len(sb) else None],
                "shaders_identical": sh_a == sh_b,
                "shaders": [len(sh_a), len(sh_b)],
                "targets": sorted({t for t in re.findall(r" rt ([0-9A-F]{8})", "\n".join(sb))}),
            }
            if a.get("presented") and b.get("presented"):
                pair[scene]["presented_diff"] = diff(Path(a["presented"]), Path(b["presented"]))
        rep["pairs"][r["name"]] = pair
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--idle", type=float, default=20.0, help="seconds in the main menu for timing lines")
    ap.add_argument("--gpu-pair", action="store_true", help="also run legacy on --mc3-gpu-index=1")
    ap.add_argument("--only", nargs="*", help="run names to run")
    ap.add_argument("--legal", type=float, default=0.0, help="also capture the legal screen this many seconds in")
    a = ap.parse_args()
    stamp = time.strftime("%Y%m%d-%H%M%S")
    root = HERE / "runs" / stamp
    old = GAME_DIR / "MC3RemixXBE.before_render_profiles.exe"
    runs = [
        ("legacy", ["--mc3-render-profile=legacy", "--mc3-render-timing"]),
        ("pre_profiles_exe", []),
        ("legacy_control", ["--mc3-render-profile=legacy", "--mc3-render-timing"]),
        ("hybrid_empty", ["--mc3-render-profile=hybrid", "--mc3-render-timing"]),
        ("enhanced_empty", ["--mc3-render-profile=enhanced", "--mc3-render-timing"]),
        ("hybrid_post", ["--mc3-render-profile=hybrid", "--mc3-render-feature=post", "--mc3-render-timing"]),
        ("hybrid_post_neutral", ["--mc3-render-profile=hybrid", "--mc3-render-feature=post", "--mc3-post=fxaa=0",
                                 "--mc3-render-timing"]),
        ("legacy_post_ignored", ["--mc3-render-profile=legacy", "--mc3-render-feature=post", "--mc3-render-timing"]),
    ]
    if a.gpu_pair:
        runs.append(("legacy_gpu1", ["--mc3-render-profile=legacy", "--mc3-gpu-index=1", "--mc3-render-timing"]))
    if a.only:
        runs = [r for r in runs if r[0] in a.only]
    results = []
    for name, args in runs:
        say(f"=== {name} {args}")
        exe = old if name == "pre_profiles_exe" else EXE
        results.append(Run(name, args, root / name, f"gate0-{stamp}-{name}", a.legal, exe).execute(a.idle))
        time.sleep(2)
    report = {"stamp": stamp, "runs": results, "comparison": compare(results), "post": post_report(results)}
    (root / "result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    say(f"[result] {root / 'result.json'}")
    return 0 if all(r.get("passed") for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
