#!/usr/bin/env python3
"""Put the converted MC2 races of an MC3 city's .loc in MC2's own order.

MC3's Arcade lists the races of a mode in the order of the city's .loc
(checked in the game on 2026-10-11, all 9 cities). MC2's .loc lists them
hookman by hookman (the career order), then the arcade cruise and circuits,
then the battle maps. mc2_races_to_mc3.py keeps that order for the races it
converts, but the MC3-only modes made by mc2_race_modes.py come out in
another one: Tag and Paint (from the CTF maps) alphabetical, Frenzy (from
ordered races) by checkpoint count.

This sorts, in place, the Race blocks of each folder under <type>\\mc2\\ by
the MC2 position of the race they come from (the name without
_frenzy/_tag/_paint). Every other block keeps its place; a folder whose
races are already in order does not change. Only the .loc is touched.

    python mc2_race_order.py --mc2-loc MC2/assets_p/tune/race/losangeles.loc \\
        --loc HOSTFS/ASSETS/tune/race/losangeles.loc [--dry-run]
"""
import argparse
import re
import shutil
import os

SUFFIXES = ('_frenzy', '_tag', '_paint')
BLOCK = re.compile(r'Race\s*\{[^{}]*?\}\s*', re.S)
NAME = re.compile(r'^\s*Name\s+(\S+)', re.M | re.I)


def mc2_order(path):
    """{lower-case race name: position} from an MC2 .loc (Hookman blocks)."""
    text = open(path, encoding='latin1').read()
    text = text[:text.find('Movies')] if 'Movies' in text else text
    order = {}
    for line in text.splitlines():
        w = line.split()
        if len(w) >= 2 and w[0] not in ('name', 'numRaces', 'numHookmen', 'City', '{', '}'):
            order.setdefault(w[1].lower(), len(order))
    return order


def base(race):
    race = race.lower()
    for s in SUFFIXES:
        if race.endswith(s):
            return race[:-len(s)]
    return race


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--mc2-loc', required=True, help="MC2's assets_p/tune/race/<city>.loc")
    ap.add_argument('--loc', required=True, help="the MC3 city's tune/race/<city>.loc")
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    order = mc2_order(a.mc2_loc)
    text = open(a.loc, encoding='latin1', newline='').read()
    blocks = list(BLOCK.finditer(text))
    names = [NAME.search(b.group(0)).group(1) for b in blocks]
    by_folder = {}
    for i, n in enumerate(names):
        parts = n.split('\\')
        if len(parts) == 3 and parts[1].lower() == 'mc2':
            by_folder.setdefault(parts[0].lower(), []).append(i)
    new = [b.group(0) for b in blocks]
    moved = 0
    for folder, idx in by_folder.items():
        unknown = [names[i] for i in idx if base(names[i].split('\\')[2]) not in order]
        ranked = sorted(idx, key=lambda i: (order.get(base(names[i].split('\\')[2]), 1 << 30), idx.index(i)))
        if ranked != idx:
            moved += 1
            print('  %s:' % folder)
            for i in ranked:
                print('      %s' % names[i].split('\\')[2])
        for slot, i in zip(idx, ranked):
            new[slot] = blocks[i].group(0)
        for n in unknown:
            print('  %s: %s not in the MC2 .loc, kept last' % (folder, n))
    if not moved:
        print('already in MC2 order')
        return
    out, pos = [], 0
    for b, body in zip(blocks, new):
        out.append(text[pos:b.start()])
        out.append(body)
        pos = b.end()
    out.append(text[pos:])
    result = ''.join(out)
    assert sorted(BLOCK.findall(result)) == sorted(b.group(0) for b in blocks)
    if a.dry_run:
        return
    if not os.path.exists(a.loc + '.before_order'):
        shutil.copy2(a.loc, a.loc + '.before_order')
    open(a.loc, 'w', encoding='latin1', newline='').write(result)
    print('written', a.loc)


if __name__ == '__main__':
    main()
