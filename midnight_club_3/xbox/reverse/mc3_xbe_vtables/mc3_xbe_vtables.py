"""mc3_xbe_vtables: list the vtables in a range of MC3's Xbox default.xbe.

A vtable is a run of at least two 32-bit words that all point into code. Each run is printed with its slot
numbers and the names of the functions. MSVC puts the destructor in slot 0; the PS2 build's GCC vtables have
two header words first, so PS2 slot i + 2 is Xbox slot i.

    mc3_xbe_vtables.py 4a4910 4a4980        the vtables in [lo, hi)
    mc3_xbe_vtables.py --of 4a4944          the run that starts at this address

Environment variables this tool reads (set them, do not edit the code):
    MC3_XBOX_XBE    the game's default.xbe
    MC3_XBOX_NAMES  optional name files (see mc3_xbe)

Origin: the MC3 Xbox C++ decompilation's rdvt.py, written for mc_research by SaltySasha.
"""
import argparse

import mc3_xbe


def runs(xbe, lo, hi):
    run = []
    for va in range(lo, hi + 4, 4):
        v = xbe.u32(va) if va < hi else 0
        if xbe.is_code(v):
            run.append((va, v))
            continue
        if len(run) >= 2:
            yield run
        run = []


def show(xbe, run):
    print(f'-- {run[0][0]:08x} {xbe.name(run[0][0], "")}'.rstrip())
    for i, (va, v) in enumerate(run):
        print(f'   [{i:2d}] {v:08x} {xbe.name(v, "")}')


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('range', nargs='*', help='lo hi (hex)')
    ap.add_argument('--of', help='the vtable starting at this address')
    ap.add_argument('--xbe', help='default.xbe (default: MC3_XBOX_XBE)')
    a = ap.parse_args()
    xbe = mc3_xbe.open_xbe(a.xbe)
    if a.of:
        start = mc3_xbe.parse_address(a.of)
        run = []
        va = start
        while xbe.is_code(xbe.u32(va)):
            run.append((va, xbe.u32(va)))
            va += 4
        show(xbe, run)
        return
    if len(a.range) != 2:
        ap.error('give lo and hi, or --of')
    lo, hi = (mc3_xbe.parse_address(v) for v in a.range)
    for run in runs(xbe, lo & ~3, hi):
        show(xbe, run)


if __name__ == '__main__':
    main()
