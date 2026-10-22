#!/usr/bin/env python3
"""Benchmark the game under PCSX2: host frames per second, with the frame
limiter off, and how much of each frame the EE really works.

    python mc3_perf_bench.py --name base
    python mc3_perf_bench.py --name mtvu_off --pcsx2 EmuCore/Speedhacks:vuThread=false
    python mc3_perf_bench.py --name no60 --patch "60 FPS/1 - Destravar para 60 fps=1"
    python mc3_perf_bench.py --name atl --boot city=atlanta

What it does, per run:
  * copies mc3boot.ini and PCSX2.ini, and puts both back at the end (also on
    error or Ctrl+C);
  * [Framerate] NominalScalar = 10 (the maximum PCSX2 accepts: the limiter
    no longer holds the game back, so speed = what the host can do);
  * loads perf_probe.mod (shim) and boots straight into the city ([boot]
    nofe = 1, racetype roam, the player car parked at its spawn: a steady,
    repeatable scene);
  * waits for perf_probe's "PRF0 <addr>" line in the PCSX2 log, lets the
    scene settle for --warmup seconds, then reads the record through PINE
    every --every seconds for --seconds.

Figures (per sample and the median of the samples):
  host fps     game frames per real second        <- what the player gets
  speed        emulated seconds per real second   (1.0 = full speed)
  game fps     frames per EMULATED second         (30 or 60 with the patch)
  EE busy      frame time the game thread is not blocked in BeginFrame
  EE ms        EE work per frame, emulated milliseconds

With the limiter off, "game fps" can stay at 30 while "host fps" goes to 90:
the game still paces itself on vblanks, the emulator just delivers them faster.
Host fps above 30 (or 60) is HEADROOM - the margin a real-time run has.
"""
import argparse
import os
import re
import shutil
import statistics
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mc3_pckbuild import Pine, PineNotReady  # noqa: E402
import mc3_pcsx2_shots as SHOTS  # noqa: E402

PCSX2 = os.environ.get('MC3_PCSX2', os.path.join(os.environ.get('MC3_PCSX2_DIR', ''), 'pcsx2-qt.exe'))
PCSX2_INI = os.environ.get('MC3_PCSX2_INI', os.path.join(os.environ.get('MC3_PCSX2_DATA', ''), 'inis/PCSX2.ini'))
HOSTFS = os.environ.get('MC3_HOSTFS', os.environ.get('MC3_HOSTFS', ''))
INI = os.path.join(HOSTFS, 'mc3boot.ini')
ELF = os.path.join(HOSTFS, 'mc3boot.elf')
LOG = os.path.join(os.environ.get('MC3_PCSX2_DATA', ''), 'logs/cli_perf.txt')
EE_HZ = 294912000.0
# 28011 is usually taken by the ReShade telemetry add-on, which holds PINE's
# only connection; the bench moves PCSX2 to its own slot.
PINE_PORT = 28012
HERE = os.path.dirname(os.path.abspath(__file__))


def set_key(text, section, key, value):
    """Set key = value inside [section] of an ini text (added if missing)."""
    nl = '\r\n' if '\r\n' in text else '\n'
    lines = text.split(nl)
    start = None
    for i, l in enumerate(lines):
        if l.strip() == '[%s]' % section:
            start = i
            break
    if start is None:
        lines += ['', '[%s]' % section, '%s = %s' % (key, value)]
        return nl.join(lines)
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith('['):
            end = i
            break
    for i in range(start + 1, end):
        m = re.match(r'\s*([^=;#]+?)\s*=', lines[i])
        if m and m.group(1) == key:
            lines[i] = '%s = %s' % (key, value)
            return nl.join(lines)
    ins = end
    while ins > start + 1 and not lines[ins - 1].strip():
        ins -= 1
    lines.insert(ins, '%s = %s' % (key, value))
    return nl.join(lines)


def read_rec(p, base):
    return [p.read32(base + 4 * i) for i in range(10)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument('--name', required=True)
    ap.add_argument('--root', default=None,
                    help='HostFS folder to boot (default $MC3_HOSTFS or Y:/MC3HostFS), e.g. '
                         'Y:/mc3.2_alpha_hostfs; perf_probe.mod is copied there if missing')
    ap.add_argument('--out', default=os.path.join(HERE, 'output', 'perf'))
    ap.add_argument('--pcsx2', action='append', default=[],
                    help='Section:key=value for PCSX2.ini (repeatable)')
    ap.add_argument('--mod', action='append', default=[],
                    help='name.mod=value for [mods] of mc3boot.ini (repeatable)')
    ap.add_argument('--patch', action='append', default=[],
                    help='"patch name=0|1" for [patches] of mc3boot.ini (repeatable)')
    ap.add_argument('--boot', action='append', default=[],
                    help='key=value for [boot] (repeatable), on top of the scene defaults')
    ap.add_argument('--warmup', type=float, default=20.0)
    ap.add_argument('--seconds', type=float, default=40.0)
    ap.add_argument('--every', type=float, default=5.0)
    ap.add_argument('--timeout', type=float, default=240.0,
                    help='give up if the first frame has not come by then')
    ap.add_argument('--no-limit', dest='limit', action='store_false', default=True)
    ap.add_argument('--states', type=int, default=0,
                    help='also take N savestates (F1) after sampling, to read the EE PC from; the slot-1 '
                         'file is backed up first and put back afterwards')
    ap.add_argument('--keep-limiter', action='store_true',
                    help='leave the frame limiter on (measures real-time behaviour instead)')
    a = ap.parse_args()

    global INI, ELF
    if a.root:
        a.root = os.path.normpath(a.root)   # PCSX2 refuses mixed slashes
        INI = os.path.join(a.root, 'mc3boot.ini')
        ELF = os.path.join(a.root, 'mc3boot.elf')
        probe = os.path.join(a.root, 'perf_probe.mod')
        if not os.path.exists(probe):
            shutil.copy2(os.path.join(HOSTFS, 'perf_probe.mod'), probe)
            print('  copied perf_probe.mod to %s' % a.root)
    os.makedirs(a.out, exist_ok=True)
    # Backups on disk too: a run killed from outside cannot reach `finally`,
    # and the next run puts the originals back before doing anything else.
    for f in (INI, PCSX2_INI):
        if os.path.exists(f + '.perf_backup'):
            shutil.copy2(f + '.perf_backup', f)
            os.remove(f + '.perf_backup')
            print('  restored %s from an interrupted run' % f)
        shutil.copy2(f, f + '.perf_backup')
    ini_orig = open(INI, 'rb').read()
    pcsx2_orig = open(PCSX2_INI, 'rb').read()
    try:
        # --- mc3boot.ini
        t = ini_orig.decode('latin1')
        t = set_key(t, 'mods', 'perf_probe.mod', 'shim')
        boot = [('nofe', '1'), ('racetype', 'roam'), ('city', 'losangeles'),
                ('time', 'midnight'), ('weather', 'clear'), ('garage', '0'), ('mc2s', '0'), ('rnam', '')]
        for kv in a.boot:
            k, v = kv.split('=', 1)
            boot = [(x, y) for x, y in boot if x != k] + [(k, v)]
        for k, v in boot:
            if v == '':
                continue
            t = set_key(t, 'boot', k, v)
        for kv in a.mod:
            k, v = kv.split('=', 1)
            t = set_key(t, 'mods', k, v)
        for kv in a.patch:
            k, v = kv.rsplit('=', 1)
            t = set_key(t, 'patches', k, v)
        open(INI, 'wb').write(t.encode('latin1'))
        # --- PCSX2.ini
        t = pcsx2_orig.decode('utf-8')
        if not a.keep_limiter:
            t = set_key(t, 'Framerate', 'NominalScalar', '10')
        t = set_key(t, 'EmuCore', 'PINESlot', str(PINE_PORT))
        t = set_key(t, 'EmuCore', 'EnablePINE', 'true')
        for kv in a.pcsx2:
            sk, v = kv.split('=', 1)
            s, k = sk.split(':', 1)
            t = set_key(t, s, k, v)
        open(PCSX2_INI, 'wb').write(t.encode('utf-8'))

        if os.path.exists(LOG):
            os.remove(LOG)
        cmd = [PCSX2, '-batch', '-nogui', '-logfile', LOG, '--', ELF]
        t0 = time.time()
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        base = None
        try:
            while base is None:
                if proc.poll() is not None:
                    sys.exit('PCSX2 exited before the first frame')
                if time.time() - t0 > a.timeout:
                    sys.exit('no PRF0 line in %.0fs' % a.timeout)
                time.sleep(1.0)
                if os.path.exists(LOG):
                    m = re.search(r'PRF0 ([0-9A-F]{8})', open(LOG, encoding='latin1', errors='replace').read())
                    if m:
                        base = int(m.group(1), 16)
            print('  first frame at %.1fs, record %08X' % (time.time() - t0, base), flush=True)
            # ONE socket: PINE serves one client at a time, so dropping a live
            # socket after an IPC_FAIL and opening another leaves the server
            # stuck on the first one (see mc3_pckbuild.Pine).
            p = None
            deadline = time.time() + 60
            while True:
                if time.time() > deadline:
                    sys.exit('PINE never answered')
                try:
                    if p is None:
                        p = Pine(port=PINE_PORT)
                    read_rec(p, base)
                    break
                except PineNotReady:
                    time.sleep(1.0)
                except OSError:
                    if p is not None:
                        p.close()
                    p = None
                    time.sleep(1.0)
            print('  PINE connected', flush=True)
            time.sleep(a.warmup)
            samples = []
            prev = (time.time(), read_rec(p, base))
            end = time.time() + a.seconds
            while time.time() < end:
                time.sleep(a.every)
                now = (time.time(), read_rec(p, base))
                wall = now[0] - prev[0]
                r0, r1 = prev[1], now[1]
                fr = (r1[1] - r0[1]) & 0xFFFFFFFF
                tot = ((r1[2] - r0[2]) & 0xFFFFFFFF) * 256.0
                wd = ((r1[3] - r0[3]) & 0xFFFFFFFF) * 256.0
                wv = ((r1[4] - r0[4]) & 0xFFFFFFFF) * 256.0
                emu = tot / EE_HZ
                s = dict(host_fps=fr / wall if wall else 0, speed=emu / wall if wall else 0,
                         game_fps=fr / emu if emu else 0,
                         busy=100.0 * (1 - (wd + wv) / tot) if tot else 0,
                         ee_ms=1000.0 * (tot - wd - wv) / EE_HZ / fr if fr else 0,
                         wait_done_ms=1000.0 * wd / EE_HZ / fr if fr else 0,
                         max_ms=1000.0 * r1[9] * 256 / EE_HZ)
                samples.append(s)
                print('   host %6.1f fps  speed %5.2fx  game %5.1f fps  EE busy %5.1f%%  EE %5.2f ms/frame'
                      '  (render wait %5.2f)' % (s['host_fps'], s['speed'], s['game_fps'], s['busy'],
                                                  s['ee_ms'], s['wait_done_ms']), flush=True)
                prev = now
            if a.states:
                slot = None
                for k in range(a.states):
                    got = SHOTS.save_state(proc.pid)
                    if os.path.exists(got):
                        if slot is None:
                            slot = got
                        dst = os.path.join(a.out, '%s_state%d.p2s' % (a.name, k))
                        shutil.copy2(got, dst)
                        print('  savestate -> %s' % dst, flush=True)
                    time.sleep(1.3)
            try:
                print('  screenshot: %s' % SHOTS.shoot(proc.pid, os.path.join(a.out, a.name + '.png')))
            except Exception as e:  # a missing picture must not lose the numbers
                print('  screenshot failed: %s' % e)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
        med = {k: statistics.median(x[k] for x in samples) for k in samples[0]} if samples else {}
        line = ('%-24s host %6.1f fps  speed %5.2fx  game %5.1f fps  EE busy %5.1f%%  EE %5.2f ms  render-wait %5.2f ms'
                % (a.name, med.get('host_fps', 0), med.get('speed', 0), med.get('game_fps', 0),
                   med.get('busy', 0), med.get('ee_ms', 0), med.get('wait_done_ms', 0)))
        print(line)
        with open(os.path.join(a.out, 'results.txt'), 'a') as fh:
            fh.write('%s  %s  pcsx2=%s mods=%s patches=%s boot=%s\n' % (
                time.strftime('%Y-%m-%d %H:%M'), line, a.pcsx2, a.mod, a.patch, a.boot))
        if os.path.exists(LOG):
            shutil.copy2(LOG, os.path.join(a.out, a.name + '.log'))
    finally:
        open(INI, 'wb').write(ini_orig)
        open(PCSX2_INI, 'wb').write(pcsx2_orig)
        for f in (INI, PCSX2_INI):
            if os.path.exists(f + '.perf_backup'):
                os.remove(f + '.perf_backup')


if __name__ == '__main__':
    main()
