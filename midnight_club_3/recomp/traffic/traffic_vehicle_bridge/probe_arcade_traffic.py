"""Boot native MC3 and capture the Arcade flow used by the full-vp traffic bridge.

This is deliberately a UI probe rather than a headless assertion: the shared
cursor field does not represent the main menu's visible row.  Screens at each
transition make the chosen route reviewable and the resulting game log proves
whether aiAmbientVehicle::Init ran.
"""

from __future__ import annotations

import os
import argparse
import ctypes
import json
import re
import struct
import hashlib
from datetime import datetime
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/xbox_recomp'))
GAME = ROOT / "xboxxberecomp_eval" / "templates" / "game"
OUT = ROOT / "traffic_vehicle_bridge" / "arcade_probe"
sys.path.insert(0, str(ROOT / "mc2_career_test"))
sys.path.insert(0, str(ROOT / "render_ab"))

from mc2_conditional_controller import MC2ConditionalController  # noqa: E402
from run_mc2_headless import capture_window, find_game_window  # noqa: E402
from run_render_native import orange_rows, PROFILE_ROWS  # noqa: E402


FATAL_MARKERS = ("exception ", "KeBugCheck ", "MC3TRAFFIC heap BAD",
                 "MC3TRAFFIC physics BAD", "MC3TRAFFIC invalid physics removal")


def fail_on_fatal_log(log_text: str, phase: str) -> None:
    for marker in FATAL_MARKERS:
        if marker in log_text:
            raise RuntimeError(f"{phase}: game log contains {marker.strip()}")


def pause_highlights(path: Path) -> list[int]:
    # Enhanced's pause blur darkens the gold fill to RGB ~119,69,0.
    # Profile-screen orange_rows uses r>130 and would miss this native menu.
    from PIL import Image
    im = Image.open(path).convert("RGB")
    sx, sy = im.width / 1920, im.height / 1080
    return [sum(1 for y in range(int((row - 15)*sy), int((row + 15)*sy), 2)
                for x in range(int(1080*sx), int(1570*sx), 3)
                if (lambda c: c[0] > 80 and c[1] > 35 and
                    c[0] - c[2] > 50 and c[0] - c[1] > 25)(im.getpixel((x, y))))
            for row in [353, 402, 452, 502, 552, 602, 652]]


def pause_go_to_menus_row(path: Path, mode: str) -> int:
    # Career Cruise has five rows; Arcade Cruise has six. Race may have six
    # or seven depending on replay availability. The car roof behind Career's
    # overlay is bright enough to fool a generic last-white-row detector.
    if mode == "career":
        return 4
    if mode == "cruise":
        return 5
    from PIL import Image
    im = Image.open(path).convert("RGB")
    sx, sy = im.width / 1920, im.height / 1080
    white = sum(1 for y in range(int(637*sy), int(667*sy), 2)
                for x in range(int(1080*sx), int(1570*sx), 3)
                if min(im.getpixel((x, y))) > 155)
    return 6 if white > 20 else 5


def dump_actors(pid: int, log_text: str, out: Path) -> None:
    """Read actual guest poses/components for independent runtime inspection."""
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.ReadProcessMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                                         ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel.OpenProcess(0x1010, False, pid)
    if not handle:
        raise RuntimeError("cannot inspect traffic actor memory")
    def raw(address: int, size: int) -> bytes:
        buf = ctypes.create_string_buffer(size)
        count = ctypes.c_size_t()
        if not kernel.ReadProcessMemory(handle, address, buf, size, ctypes.byref(count)):
            raise OSError(ctypes.get_last_error(), f"read actor memory {address:X}")
        return buf.raw
    try:
        guest_base = None
        for candidate in (0x100000000, 0x200000000, 0x300000000):
            try:
                if raw(candidate + 0x1299F, 4) == bytes.fromhex("558bec83"):
                    guest_base = candidate
                    break
            except OSError:
                pass
        # Validate the original entry bytes from the installed XBE rather than
        # assuming the exact instruction prefix across executables.
        if guest_base is None:
            for candidate in (0x100000000, 0x200000000, 0x300000000):
                try:
                    state = struct.unpack("<I", raw(candidate + 0x557ED0, 4))[0]
                    if 0x80000000 <= state < 0x84000000 and struct.unpack("<I", raw(candidate + state + 4, 4))[0] == 2:
                        guest_base = candidate
                        break
                except OSError:
                    pass
        if guest_base is None:
            raise RuntimeError("guest address base not found")
        actors = []
        active = {}
        for line in log_text.splitlines():
            match = re.search(r"full-vp built ambient=([0-9A-F]+).*?owner=([0-9A-F]+) entity=([0-9A-F]+) vehCar=([0-9A-F]+)", line)
            retired = re.search(r"MC3TRAFFIC retired owner=([0-9A-F]+)", line)
            if match:
                active[match[2]] = match
            elif retired:
                active.pop(retired[1], None)
        for match in active.values():
            ambient, owner, entity, car = (int(x, 16) for x in match.groups())
            data = raw(guest_base + entity, 0x3138)
            (out / f"actor_{owner:08X}.bin").write_bytes(data)
            (out / f"owner_{owner:08X}.bin").write_bytes(raw(guest_base + owner, 0x43c))
            (out / f"ambient_{ambient:08X}.bin").write_bytes(raw(guest_base + ambient, 0x21c))
            def word(address): return struct.unpack("<I", raw(guest_base + address, 4))[0]
            vt = word(entity)
            sim = word(entity + 8)
            inp = word(entity + 4)
            for label, address, size in (("sim", sim, 0x200), ("input", inp, 0x160), ("car", car, 0x44)):
                if address:
                    (out / f"{label}_{owner:08X}.bin").write_bytes(raw(guest_base + address, size))
            actors.append({"ambient": hex(ambient), "owner": hex(owner), "entity": hex(entity),
                           "car": hex(car), "vtable": hex(vt), "sim": hex(sim), "input": hex(inp),
                           "entity_vtable": [hex(v) for v in struct.unpack("<8I", raw(guest_base + vt, 32))],
                           "car_pose": struct.unpack("<12f", raw(guest_base + car + 0x10, 48)),
                           "ambient_pose": struct.unpack("<12f", raw(guest_base + ambient + 0x34, 48))})
        (out / "actors.json").write_text(json.dumps(actors, indent=2), encoding="utf-8")
        templates = []
        for match in re.finditer(r"MC3TRAFFIC init capture owner=([0-9A-F]+) slot=(\d+) start=([0-9A-F]+)", log_text):
            owner, slot, start = int(match[1], 16), int(match[2]), int(match[3], 16)
            data = raw(guest_base + start, 0x88)
            config = struct.unpack_from("<I", data, 0x64)[0]
            (out / f"template_start_{slot}.bin").write_bytes(data)
            config_data = raw(guest_base + config, 0x108)
            (out / f"template_config_{slot}.bin").write_bytes(config_data)
            templates.append({"owner": hex(owner), "slot": slot, "start": hex(start),
                              "config": hex(config), "vehicle": config_data[0xe3:0xf9].split(b"\0")[0].decode("ascii", errors="replace")})
        (out / "templates.json").write_text(json.dumps(templates, indent=2), encoding="utf-8")
        level = struct.unpack("<I", raw(guest_base + 0x5580f0, 4))[0]
        vt = struct.unpack("<I", raw(guest_base + level, 4))[0]
        (out / "physics_level.json").write_text(json.dumps({
            "level": hex(level), "vtable": hex(vt),
            "functions": [hex(v) for v in struct.unpack("<40I", raw(guest_base + vt, 160))],
        }, indent=2), encoding="utf-8")
    finally:
        kernel.CloseHandle(handle)


def measure_routes(log_text: str) -> dict:
    """Measure travel, including loops that end near their starting point."""
    samples = re.findall(
        r"MC3TRAFFIC actor owner=([0-9A-F]+).*?pos=([-\d.]+),([-\d.]+),([-\d.]+)"
        r".*?target=([-\d.]+),([-\d.]+),([-\d.]+).*?error=([-\d.]+)", log_text)
    metrics = {}
    for owner in sorted({row[0] for row in samples}):
        rows = [[float(v) for v in row[1:]] for row in samples if row[0] == owner]
        if len(rows) < 2:
            continue
        def distance(a, b, offset):
            return ((b[offset] - a[offset]) ** 2 + (b[offset + 2] - a[offset + 2]) ** 2) ** .5
        def path_length(offset):
            # Ignore sub-10 cm resting jitter; position telemetry is rounded
            # to centimeters. A closed traffic loop still counts as movement.
            return sum(step for a, b in zip(rows, rows[1:])
                       if (step := distance(a, b, offset)) > .1)
        metrics[owner] = {
            "samples": len(rows), "actor_displacement": distance(rows[0], rows[-1], 0),
            "oracle_displacement": distance(rows[0], rows[-1], 3),
            "actor_path_length": path_length(0), "oracle_path_length": path_length(3),
            "max_tracking_error": max(row[6] for row in rows),
        }
    return metrics


def read_pause_flag(pid: int) -> bool:
    """Read the native gGameState+9 simulation pause flag."""
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.ReadProcessMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                                         ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel.OpenProcess(0x1010, False, pid)
    try:
        for base in (0x100000000, 0x200000000, 0x300000000):
            state = ctypes.c_uint32()
            if not kernel.ReadProcessMemory(handle, base + 0x557ed0, ctypes.byref(state), 4, None):
                continue
            if not 0x80000000 <= state.value < 0x84000000:
                continue
            flag = ctypes.c_uint8()
            if kernel.ReadProcessMemory(handle, base + state.value + 9, ctypes.byref(flag), 1, None):
                return bool(flag.value)
        raise RuntimeError("cannot inspect native pause flag")
    finally:
        kernel.CloseHandle(handle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--soak-seconds", type=float, default=10.0)
    parser.add_argument("--render-profile", choices=("legacy", "enhanced"), default="enhanced")
    parser.add_argument("--arcade-mode", choices=("race", "cruise", "career"), default="race")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--allocation-probe", action="store_true",
                        help="expensive per-allocation heap walk during native traffic Init")
    parser.add_argument("--resource-probe", action="store_true",
                        help="log native car resource paths without changing asset loading")
    parser.add_argument("--raw-open-probe", action="store_true",
                        help="opt-in native Open test for two _o paths during player car load")
    parser.add_argument("--cruise-pilot", action="store_true",
                        help="opt-in one-car independent Cruise construction experiment")
    parser.add_argument("--traffic-vp-bridge", action="store_true",
                        help="opt in to experimental full vp_* ambient traffic")
    parser.add_argument("--cruise-preload-probe", action="store_true",
                        help="opt-in native asynchronous _o preload before Cruise construction")
    parser.add_argument("--require-bridge", action="store_true")
    parser.add_argument("--require-route", action="store_true",
                        help="require a moving lane oracle and bounded physical tracking error")
    parser.add_argument("--pause-seconds", type=float, default=0,
                        help="pause after the soak for interactive lifecycle inspection")
    parser.add_argument("--exit-to-menu", action="store_true",
                        help="exercise native Pause / Go to Menus / Yes and require owner cleanup")
    args = parser.parse_args()
    global OUT
    OUT = args.out or OUT.parent / "runs" / datetime.now().strftime("%Y%m%d-%H%M%S")
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"[output] {OUT}", flush=True)
    with (GAME / "MC3RemixXBE.exe").open("rb") as binary:
        binary_sha256 = hashlib.file_digest(binary, "sha256").hexdigest()
    (OUT / "binary.json").write_text(json.dumps({
        "exe": str(GAME / "MC3RemixXBE.exe"), "sha256": binary_sha256,
    }, indent=2), encoding="utf-8")
    env = dict(os.environ)
    env.pop("MC3_MC2_DIR", None)
    log = (OUT / "game.log").open("w", encoding="utf-8")
    command = [str(GAME / "MC3RemixXBE.exe"), f"--mc3-render-profile={args.render_profile}"]
    if args.allocation_probe:
        command.append("--mc3-traffic-check-allocations")
    if args.resource_probe:
        command.append("--mc3-traffic-resource-probe")
    if args.raw_open_probe:
        command.append("--mc3-traffic-raw-open-probe")
    if args.cruise_pilot:
        command.append("--mc3-traffic-cruise-pilot")
    if args.traffic_vp_bridge or args.require_bridge or args.cruise_pilot:
        command.append("--mc3-traffic-vp-bridge")
    if args.cruise_preload_probe:
        command.append("--mc3-traffic-cruise-preload-probe")
    p = subprocess.Popen(
        command,
        cwd=GAME, env=env, stdout=log, stderr=log,
    )
    ctl = MC2ConditionalController()
    try:
        hwnd = None
        end = time.monotonic() + 30
        while time.monotonic() < end and not hwnd:
            hwnd = find_game_window(p.pid)
            time.sleep(.1)
        ctl.hwnd = hwnd
        if not hwnd or not ctl.connect(30):
            raise RuntimeError("game window/shared state not available")

        # Skip movies/legal until the game's own title-update marker.  A state
        # 7 menu alone is not sufficient: legal/profile screens share it.
        end = time.monotonic() + 120
        while time.monotonic() < end and "MC3 title: update" not in (OUT / "game.log").read_text(encoding="utf-8", errors="ignore"):
            st = ctl.poll_state()
            if st and st["is_fmv"]:
                ctl.send_pad("start", settle=.1)
                ctl.send_pad("a", settle=.1)
            elif st and st["state"] == 7 and not st["menu_active"]:
                ctl.send_pad("a", settle=.1)
            time.sleep(.25)
        time.sleep(3)
        ctl.send_pad("start")
        time.sleep(4)
        capture_window(hwnd, OUT / "01_profiles.png")
        # Find the highlighted profile row by its orange text, as the visible
        # profile list and shared cursor can briefly disagree during animation.
        for _ in range(6):
            rows = orange_rows(OUT / "01_profiles.png", PROFILE_ROWS)
            at = max(range(len(rows)), key=lambda i: rows[i])
            if rows[at] >= 20 and at == 0:
                break
            if rows[at] < 20:
                time.sleep(1)
                capture_window(hwnd, OUT / "01_profiles.png")
                continue
            ctl.send_pad("up", settle=.08)
            capture_window(hwnd, OUT / "01_profiles.png")
        ctl.send_pad("a")
        time.sleep(5)
        capture_window(hwnd, OUT / "02_main_menu.png")

        # Main menu starts on Career; Arcade is the fourth visible row (after
        # Tokyo Challenge and the injected MC2 Career entry).
        if args.arcade_mode != "career":
            for _ in range(3):
                ctl.send_window_key("down", hold=.05)
                time.sleep(.35)
        capture_window(hwnd, OUT / "03_arcade_selected.png")
        ctl.send_window_key("enter", hold=.05)
        time.sleep(2)
        capture_window(hwnd, OUT / "04_arcade_menu.png")

        # Race supplies native opponents for the bridge; Cruise exercises the
        # zero-opponent manager path and its independent-pool requirement.
        if args.arcade_mode == "race":
            ctl.send_window_key("down", hold=.05)
            time.sleep(.25)
            ctl.send_window_key("right", hold=.05)
            time.sleep(.5)
        capture_window(hwnd, OUT / "04b_race_mode.png")

        # Accept the initial Arcade choice and subsequent defaults.  Stop once
        # gameplay begins; each intermediate screen is retained for auditing.
        for step in range(12):
            st = ctl.poll_state()
            capture_window(hwnd, OUT / f"{5 + step:02d}_step_{step}.png")
            if st and st["state"] == 2:
                end = time.monotonic() + args.soak_seconds
                initial_frame = st["frame"]
                while time.monotonic() < end:
                    time.sleep(.5)
                    current_log = (OUT / "game.log").read_text(encoding="utf-8", errors="replace")
                    fail_on_fatal_log(current_log, "traffic soak")
                    if p.poll() is not None:
                        raise RuntimeError(f"game exited during soak: {p.returncode}")
                final_state = ctl.poll_state()
                if not final_state or final_state["state"] != 2 or final_state["frame"] - initial_frame < args.soak_seconds * 3:
                    raise RuntimeError(f"simulation did not progress: {final_state}")
                current_log = (OUT / "game.log").read_text(encoding="utf-8", errors="replace")
                built = len(re.findall(r"MC3TRAFFIC full-vp built", current_log))
                if args.require_bridge and not built:
                    raise RuntimeError("gameplay reached, but no complete traffic vehicle was built")
                capture_window(hwnd, OUT / "20_gameplay.png")
                dump_actors(p.pid, current_log, OUT)
                route_metrics = measure_routes(current_log)
                (OUT / "route_metrics.json").write_text(json.dumps(route_metrics, indent=2), encoding="utf-8")
                if args.pause_seconds or args.exit_to_menu:
                    for _ in range(10):
                        if read_pause_flag(p.pid):
                            break
                        ctl.send_window_key("space", hold=.1)
                        time.sleep(1)
                    if not read_pause_flag(p.pid):
                        raise RuntimeError("native pause did not engage; no menu navigation attempted")
                    time.sleep(2)
                    capture_window(hwnd, OUT / "21_pause.png")
                    print(f"[pause] pid={p.pid} inspection_seconds={args.pause_seconds}", flush=True)
                    if args.exit_to_menu:
                        # Native pause animations can consume an early key.
                        # Verify the visible Go to Menus highlight, not a count
                        # of key presses or the unrelated shared cursor field.
                        for attempt in range(12):
                            capture_window(hwnd, OUT / "23_go_to_menus.png")
                            rows = pause_highlights(OUT / "23_go_to_menus.png")
                            at = max(range(len(rows)), key=lambda i: rows[i])
                            go_to_menus_row = pause_go_to_menus_row(OUT / "23_go_to_menus.png", args.arcade_mode)
                            if rows[at] >= 20 and at == go_to_menus_row:
                                break
                            if rows[at] < 20:
                                time.sleep(.5)
                                continue
                            ctl.send_window_key("down", hold=.1)
                            time.sleep(.4)
                        else:
                            raise RuntimeError(f"Go to Menus highlight not found: {rows}")
                        ctl.send_window_key("enter", hold=.05)
                        time.sleep(2)
                        capture_window(hwnd, OUT / "24_confirm_exit.png")
                        ctl.send_window_key("up", hold=.05)
                        time.sleep(.3)
                        ctl.send_window_key("enter", hold=.05)
                        deadline = time.monotonic() + 25
                        while time.monotonic() < deadline:
                            time.sleep(.5)
                            current_log = (OUT / "game.log").read_text(encoding="utf-8", errors="replace")
                            fail_on_fatal_log(current_log, "leaving the race")
                            if p.poll() is not None:
                                raise RuntimeError("process exited while leaving the race")
                            state = ctl.poll_state()
                            if state and state["state"] == 7:
                                break
                        else:
                            raise RuntimeError("native Go to Menus did not return to the frontend")
                        # State 7 precedes the frontend's blur/menu entrance
                        # animation. Retain a visibly settled menu capture.
                        time.sleep(8)
                        current_log = (OUT / "game.log").read_text(encoding="utf-8", errors="replace")
                        fail_on_fatal_log(current_log, "frontend settling")
                        if p.poll() is not None:
                            raise RuntimeError("process exited during frontend settling")
                        capture_window(hwnd, OUT / "25_back_to_menus.png")
                        if built and "MC3TRAFFIC released " not in current_log:
                            raise RuntimeError("frontend reached without releasing traffic owners")
                    end = time.monotonic() + args.pause_seconds
                    while time.monotonic() < end:
                        time.sleep(.5)
                        current_log = (OUT / "game.log").read_text(encoding="utf-8", errors="replace")
                        fail_on_fatal_log(current_log, "lifecycle inspection")
                        if p.poll() is not None:
                            raise RuntimeError("process exited during lifecycle inspection")
                    capture_window(hwnd, OUT / "22_after_pause.png")
                    (OUT / "after_pause_state.json").write_text(json.dumps(ctl.poll_state(), indent=2), encoding="utf-8")
                if args.require_route and (not route_metrics or any(
                    row["actor_path_length"] < 10 or row["oracle_path_length"] < 10 or
                    row["max_tracking_error"] > 100 for row in route_metrics.values())):
                    raise RuntimeError(f"traffic route validation failed: {route_metrics}")
                (OUT / "result.json").write_text(json.dumps({
                    "result": "PASS", "profile": args.render_profile,
                    "arcade_mode": args.arcade_mode,
                    "soak_seconds": args.soak_seconds, "built": built,
                    "initial_frame": initial_frame, "final_state": final_state,
                    "route_metrics": route_metrics,
                    "exit_to_menu": args.exit_to_menu,
                    "after_exit_state": ctl.poll_state() if args.exit_to_menu else None,
                    "native_removed": len(re.findall(r"MC3TRAFFIC removed full-vp", current_log)),
                    "redundant_ambient_removals": len(re.findall(r"MC3TRAFFIC already detached", current_log)),
                    "frontend_observation_seconds": 8 + args.pause_seconds if args.exit_to_menu else 0,
                    "allocation_probe": args.allocation_probe,
                    "resource_probe": args.resource_probe,
                    "raw_open_probe": args.raw_open_probe,
                    "cruise_pilot": args.cruise_pilot,
                }, indent=2), encoding="utf-8")
                return 0
            if st and st["is_fmv"]:
                ctl.send_pad("start", settle=.1)
            else:
                ctl.send_pad("a")
            time.sleep(2)
        raise RuntimeError(f"gameplay not reached: {ctl.poll_state()}")
    except Exception as exc:
        try:
            failure = OUT / "failure_memory"
            failure.mkdir(exist_ok=True)
            dump_actors(p.pid, (OUT / "game.log").read_text(encoding="utf-8", errors="replace"), failure)
        except Exception as dump_error:
            (OUT / "failure_dump_error.txt").write_text(str(dump_error), encoding="utf-8")
        (OUT / "result.json").write_text(json.dumps({
            "result": "FAIL", "error": str(exc), "profile": args.render_profile,
            "arcade_mode": args.arcade_mode,
            "soak_seconds": args.soak_seconds,
        }, indent=2), encoding="utf-8")
        raise
    finally:
        try:
            ctl.release_report()
        except Exception:
            pass
        p.terminate()
        try:
            p.wait(10)
        except subprocess.TimeoutExpired:
            p.kill()
        log.close()


if __name__ == "__main__":
    raise SystemExit(main())
