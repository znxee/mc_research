#!/usr/bin/env python3
"""Give the converted MC2 races their MC2 names in MC3's string tables.

mc2_races_to_mc3.py and mc2_race_modes.py name a race after its file
(lamauro_moses_checkpoint_one -> "Moses Checkpoint One"). MC2 has the real
names in its own text table, assets_p/fonts/mcstrings.txt (UTF-16, tab
separated): HS_short_<race> is the short name ("Initiation"), CM_<race> the
long one ("Race: Initiation"). MC3's Arcade shows plain names, so:

  - race (any mode, also the Frenzy/Tag/Paint variants made from it):
    HS_short_<race>, the MC2 short name;
  - battle map (ctf/detonate/tag/paint): "<MC2 map> Map", the style of MC3's
    own CTF maps ("Buckhead Map") - lamarc_battle_modes_la_ctf_ghetto is
    "Watts Map", *_full "Full Map";
  - the arcade cruises keep "Arcade Cruise": MC2's text for them is the
    start point ("Startpoint One"), not a name.

Every CM_<type>\\mc2\\<race> key of mcstrings01.strtbl is rewritten, in
mcstrings01, mcstrings01_pal and mcloadstrings (the loading screen), all
languages, through mc2_races_to_mc3.add_strings (backup .before_mc2 once).

    python mc2_race_names.py --mc2-strings MC2/assets_p/fonts/mcstrings.txt \\
        --fonts HOSTFS/ASSETS/fonts [--dry-run]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

import mc2_races_to_mc3 as conv

VARIANTS = ('_frenzy', '_tag', '_paint')
BATTLE = ('ctf', 'detonate', 'tag', 'paint')


def mc2_names(path):
    """{lower-case identifier: English text} from MC2's mcstrings.txt."""
    raw = open(path, 'rb').read()
    text = raw.decode('utf-16') if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else raw.decode('utf-8-sig')
    out = {}
    for line in text.splitlines():
        f = line.split('\t')
        if len(f) > 3 and f[2] == 'en':
            out[f[0].lower()] = f[3].strip()
    return out


def mc2_race_keys(fonts, strtbl_tool):
    """{CM_ key: current text} of the MC2 races in mcstrings01.strtbl."""
    work = tempfile.mkdtemp()
    try:
        shutil.copy2(os.path.join(fonts, 'mcstrings01.strtbl'), work)
        subprocess.run([sys.executable, strtbl_tool, 'dec', 'mcstrings01.strtbl'], cwd=work,
                       check=True, stdout=subprocess.DEVNULL)
        data = json.load(open(os.path.join(work, 'mcstrings01.json'), encoding='utf-8'))['data']
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return {k: v['Language 00']['text'] for k, v in data.items()
            if k.startswith('CM_') and '\\mc2\\' in k}


def proper_name(key, names):
    """MC2 name for CM_<type>\\mc2\\<race>, or None."""
    mode, _, race = key[3:].split('\\')
    if mode == 'cruise':
        return None
    for suffix in VARIANTS:
        if race.endswith(suffix):
            race = race[:-len(suffix)]
    short = names.get('hs_short_' + race)
    if not short:
        return None
    if mode in BATTLE:
        return short if short.endswith(' Map') else short + ' Map'
    return short


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--mc2-strings', required=True, help="MC2's assets_p/fonts/mcstrings.txt")
    ap.add_argument('--fonts', required=True, help='ASSETS/fonts of the MC3 install')
    ap.add_argument('--strtbl', default=os.environ.get('MC3_STRTBL', 'strtbl.py'),
                    help='Edness strtbl.py (env MC3_STRTBL)')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    names = mc2_names(a.mc2_strings)
    current = mc2_race_keys(a.fonts, a.strtbl)
    entries = []
    for key in sorted(current):
        name = proper_name(key, names)
        if name is None:
            print('  keep     %-62s %s' % (key[3:], current[key]))
            continue
        if name != current[key]:
            entries.append((key, name))
        print('  %-8s %-62s %-32s -> %s' % ('rename' if name != current[key] else 'same',
                                             key[3:], current[key], name))
    print('%d MC2 races, %d renamed' % (len(current), len(entries)))
    if entries and not a.dry_run:
        conv.add_strings(a.fonts, a.strtbl, entries)


if __name__ == '__main__':
    main()
