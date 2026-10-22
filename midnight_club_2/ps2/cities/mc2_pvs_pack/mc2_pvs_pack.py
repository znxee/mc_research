#!/usr/bin/env python3
"""Pack MC2's per-cell PVS into a file small enough for the city renderer.

MC2 keeps, for every 40-unit cell, the components and instances that can be
seen from there (mc2_pvs.py has the format). The block is 728-849 KB per city
and the city .rsc / .pvc are deflated inside MC2.DAT, so the renderer can
neither keep it (the race heap has ~0.3-1 MB) nor seek into it mid-race.

This writes the same information, coarser and smaller (~85-105 KB at the
default 4x4):

  - one byte per FINE cell: 0 = MC2 has no list there (the renderer keeps its
    distance path, as MC2 does), else floor(height) + 32 clamped to 1..255 -
    MC2 uses the list while the camera is below height + 5.0 (sub_26A858;
    the 5.0 at +12 and the "skip above" flag at +16 = 1 are set by its PVS
    constructor sub_26A180); floor() here, so it errs on drawing more;
  - for each COARSE cell (factor x factor fine cells) the UNION of the visible
    sets of its fine cells that have a list - a superset, so nothing MC2 would
    show from any of them is hidden;
  - each coarse row stored as XOR differences against the previous coarse cell
    of the row, as runs over the object numbering (components 0..nc-1, then
    instances nc..nc+ni-1, the game's order: hoods in .lvl order, records in
    .hood order - the renderer numbers its instances the same way).

Measured (median, objects kept inside 600 m among the fine cells that have a
list): 1x1 15-19 %, 2x2 22-27 %, 4x4 32-38 %.

FILE (little-endian)
    +0  'MPV1'
    +4  u16 W, u16 H          fine grid (as MC2's PVS0)
    +8  s16 ox, s16 oz        origin in cells = floor(.lvl extents_min / 40)
    +12 u16 factor, u16 CW, u16 CH
    +18 u16 ncomp, u16 ninst, u16 0
    +24 u32 rows_at, u32 data_at, u32 data_bytes
    +36 u8  code[W*H]
    rows_at: u32 row[CH + 1]  offsets into data (row[CH] = data_bytes)
    data:    per coarse row, entries {u8 cx, varint nruns, nruns x
             (varint gap from the previous run's end, varint length - 1)};
             start of row = empty set, each entry XORs into it and is then
             the set of coarse cell (cx, row).

    python mc2_pvs_pack.py losangeles [--factor 4] [--out FILE] [--root MC2_ASSETS]

Default output: $MC3_HOSTFS/ASSETS/resources/city/mc2_pvs_<city>.txt (the
.txt name only so the asset pipelines that already carry mc2_*.txt take it;
the content is binary).
"""
import argparse
import os
import struct
import sys

import mc2_pvs as P


def varint(v):
    out = bytearray()
    while v >= 0x80:
        out.append((v & 0x7F) | 0x80)
        v >>= 7
    out.append(v)
    return bytes(out)


def runs(ids):
    out = []
    for i in sorted(ids):
        if out and out[-1][0] + out[-1][1] == i:
            out[-1][1] += 1
        else:
            out.append([i, 1])
    return out


def pack(pv, factor):
    nc, ni = len(pv.comps), len(pv.insts)
    W, H = pv.W, pv.H
    CW, CH = (W + factor - 1) // factor, (H + factor - 1) // factor
    code = bytearray(W * H)
    coarse = {}
    for cell in range(W * H):
        v = pv.visible(cell)
        if not v or (not v[1] and not v[2]):
            continue
        h = int(v[0] // 1) + 32
        code[cell] = max(1, min(255, h))
        x, z = cell % W, cell // W
        coarse.setdefault((z // factor, x // factor), set()).update(
            set(v[1]) | set(nc + i for i in v[2]))
    data = bytearray()
    rows = []
    for cz in range(CH):
        rows.append(len(data))
        prev = set()
        for cx in range(CW):
            ids = coarse.get((cz, cx))
            if ids is None:
                continue
            rr = runs(ids ^ prev)
            data += bytes([cx]) + varint(len(rr))
            end = 0
            for s, n in rr:
                data += varint(s - end) + varint(n - 1)
                end = s + n
            prev = ids
    rows.append(len(data))
    head = b'MPV1' + struct.pack('<HHhhHHHHHH', W, H, pv.ox, pv.oz, factor, CW, CH, nc, ni, 0)
    rows_at = 36 + W * H
    rows_at += (-rows_at) & 3
    data_at = rows_at + 4 * (CH + 1)
    out = bytearray(head + struct.pack('<III', rows_at, data_at, len(data)))
    out += code
    out += bytes(rows_at - len(out))
    out += struct.pack('<%dI' % (CH + 1), *rows)
    out += data
    return bytes(out), coarse


def decode(blob, cx, cz):
    """The set of coarse cell (cx, cz), as the renderer computes it."""
    W, H, ox, oz, f, CW, CH, nc, ni, _ = struct.unpack_from('<HHhhHHHHHH', blob, 4)
    rows_at, data_at, nbytes = struct.unpack_from('<III', blob, 24)
    a, b = struct.unpack_from('<II', blob, rows_at + 4 * cz)
    p, end = data_at + a, data_at + b
    s = set()

    def rv():
        nonlocal p
        v, sh = 0, 0
        while True:
            c = blob[p]
            p += 1
            v |= (c & 0x7F) << sh
            sh += 7
            if c < 0x80:
                return v

    while p < end:
        x = blob[p]
        p += 1
        n = rv()
        e = 0
        for _ in range(n):
            st = e + rv()
            ln = rv() + 1
            s ^= set(range(st, st + ln))
            e = st + ln
        if x == cx:
            return s
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('city', choices=P.CITIES)
    ap.add_argument('--factor', type=int, default=4)
    ap.add_argument('--root', default=P.ROOT, help="MC2 PS2 assets folder (city/, resource/)")
    ap.add_argument('--out')
    a = ap.parse_args(argv)
    pv = P.Pvs(a.city, a.root)
    blob, coarse = pack(pv, a.factor)
    # self-check: every coarse cell decodes to its union
    for (cz, cx), ids in coarse.items():
        assert decode(blob, cx, cz) == ids, (cx, cz)
    out = a.out
    if not out:
        host = os.environ.get('MC3_HOSTFS', os.environ.get('MC3_ALPHA_HOSTFS', ''))
        out = os.path.join(host, 'ASSETS', 'resources', 'city', 'mc2_pvs_%s.txt' % a.city)
    with open(out, 'wb') as f:
        f.write(blob)
    print('%s: %d bytes, %dx%d cells of %d m, %d coarse cells with a list, %d comps, %d instances -> %s'
          % (a.city, len(blob), pv.W, pv.H, 40 * a.factor, len(coarse), len(pv.comps), len(pv.insts), out))


if __name__ == '__main__':
    main()
