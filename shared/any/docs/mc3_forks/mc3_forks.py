"""FORKS.md - the log the parallel sessions keep for each other.

WHY

Work on this game happens in several sessions at once, each digging into a
different part. They share one filesystem, so when one of them renames a folder,
changes a file format or moves a generated artefact, the others find out by
breaking - usually much later, and usually while chasing something unrelated.

This is the channel for that, in the same spirit as `simbolos/`: a file both
sides read, with a tool that keeps the shape consistent.

Pending work, bugs, ownership, priority, acceptance criteria and regressions
belong in TASKS.md through mc3_tasks.py.  FORKS.md records changes that already
happened; it is not the work queue.

WHAT BELONGS HERE

Only what another session could trip over:

    a path or folder that moved
    a file format that changed
    a generated file that is now produced differently, or elsewhere
    a shared tool that gained or lost a flag
    a convention that changed

NOT a diary. "Investigated the flash timing" helps nobody. "The flash patch
addresses now hold different values, regenerate anything derived from them" does.
If another session would not change what it does after reading it, leave it out.
Do not add a pending task here: create or update its stable ID in TASKS.md.

USE

    python mc3_forks.py read              the last few entries
    python mc3_forks.py read --all        everything
    python mc3_forks.py since 2026-08-01  entries from a date on
    python mc3_forks.py add --fork "FORK X" --changed "..." \\
                            --affects "..." --action "..."

Read it when you start, and when something that used to work stops.
"""
import argparse
import datetime
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, 'FORKS.md')

HEAD = """# Fork log

Shared between the parallel sessions working on this game. Newest first.

Pending work, bugs, priorities, owners and regressions live in `TASKS.md` and
are maintained with `mc3_tasks.py`.

Each entry answers three questions, in this order: what changed, who it can
break, and what they should do about it. An entry that cannot answer the third
one is usually a diary entry and does not belong here - see `mc3_forks.py`.

Append with:

```
python mc3_forks.py add --fork "YOUR FORK NAME" \\
    --changed "what changed" --affects "who trips over it" --action "what to do"
```

---
"""

ENTRY = re.compile(r'^## (\d{4}-\d{2}-\d{2}) - (.+)$', re.M)


def _load():
    if not os.path.isfile(LOG):
        return HEAD, []
    txt = io.open(LOG, encoding='utf-8').read()
    corte = txt.find('\n---\n')
    if corte < 0:
        return HEAD, []
    cabeca = txt[:corte + 5]
    corpo = txt[corte + 5:].strip('\n')
    blocos = []
    if corpo:
        partes = re.split(r'\n(?=## \d{4}-\d{2}-\d{2} - )', corpo)
        blocos = [p.strip('\n') for p in partes if p.strip()]
    return cabeca, blocos


def add(fork, changed, affects, action, data=None):
    cabeca, blocos = _load()
    dia = data or datetime.date.today().isoformat()
    novo = ('## %s - %s\n\n'
            '**Changed:** %s\n\n'
            '**Affects:** %s\n\n'
            '**Action:** %s' % (dia, fork, changed, affects, action))
    # Newest first: the entry you need is almost always the most recent one, and
    # a log you have to scroll to the bottom of stops being read.
    blocos.insert(0, novo)
    io.open(LOG, 'w', encoding='utf-8', newline='\n').write(
        cabeca + '\n' + '\n\n'.join(blocos) + '\n')
    print('%s: %d entries' % (os.path.basename(LOG), len(blocos)))


def read(n=5, todos=False, desde=None):
    _cabeca, blocos = _load()
    if not blocos:
        print('%s: empty' % os.path.basename(LOG))
        return
    if desde:
        blocos = [b for b in blocos
                  if (ENTRY.search(b) or [None]) and ENTRY.search(b)
                  and ENTRY.search(b).group(1) >= desde]
        if not blocos:
            print('no entries since %s' % desde)
            return
    elif not todos:
        blocos = blocos[:n]
    for b in blocos:
        print(b)
        print()


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='acao')

    a = sub.add_parser('add', help='append an entry')
    a.add_argument('--fork', required=True)
    a.add_argument('--changed', required=True)
    a.add_argument('--affects', required=True)
    a.add_argument('--action', required=True)
    a.add_argument('--date')

    r = sub.add_parser('read', help='show recent entries')
    r.add_argument('-n', type=int, default=5)
    r.add_argument('--all', action='store_true')

    s = sub.add_parser('since', help='entries from a date on')
    s.add_argument('data')

    ns = ap.parse_args()
    if ns.acao == 'add':
        add(ns.fork, ns.changed, ns.affects, ns.action, ns.date)
    elif ns.acao == 'since':
        read(desde=ns.data)
    elif ns.acao == 'read':
        read(n=ns.n, todos=ns.all)
    else:
        read()
    return 0


if __name__ == '__main__':
    sys.exit(main())
