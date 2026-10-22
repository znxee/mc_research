"""Extract files from an Xbox / Xbox 360 disc image (XDVDFS), for local research only.

  python -I xiso_extract.py <image.iso> <out dir> [--list] [--only REGEX]

Finds the game partition (offset 0, XGD1 0x18300000, XGD2 0xFD90000, XGD3 0x2080000), then walks the directory tree
(binary trees of entries: left, right in dwords, start sector, size, attributes, name).
"""

from __future__ import annotations

import argparse
import os
import re
import struct

SECTOR = 2048
MAGIC = b"MICROSOFT*XBOX*MEDIA"
OFFSETS = [0, 0x2080000, 0xFD90000, 0x18300000]


def find_partition(f):
    for off in OFFSETS:
        f.seek(off + 32 * SECTOR)
        if f.read(len(MAGIC)) == MAGIC:
            root, size = struct.unpack("<II", f.read(8))
            return off, root, size
    raise SystemExit("no XDVDFS partition found")


def walk(f, base, sector, size, path, out):
    f.seek(base + sector * SECTOR)
    data = f.read(size)
    seen = set()

    def node(off):
        if off in seen or off * 4 + 14 > len(data):
            return
        seen.add(off)
        p = off * 4
        left, right, start, length, attr, nlen = struct.unpack_from("<HHIIBB", data, p)
        if left == 0xFFFF and right == 0xFFFF and start == 0xFFFFFFFF:
            return
        name = data[p + 14:p + 14 + nlen].decode("ascii", "replace")
        if left:
            node(left)
        full = path + "/" + name if path else name
        if attr & 0x10:
            if length:
                walk(f, base, start, length, full, out)
        else:
            out.append((full, base + start * SECTOR, length))
        if right:
            node(right)

    node(0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("iso")
    ap.add_argument("out")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    with open(a.iso, "rb") as f:
        base, root, size = find_partition(f)
        print(f"partition at 0x{base:X}, root sector {root}, {size} bytes")
        files = []
        walk(f, base, root, size, "", files)
        pat = re.compile(a.only, re.I) if a.only else None
        total = 0
        for name, off, length in files:
            if pat and not pat.search(name):
                continue
            total += length
            if a.list:
                print(f"{length:>12} {name}")
                continue
            dst = os.path.join(a.out, name.replace("/", os.sep))
            os.makedirs(os.path.dirname(dst) or a.out, exist_ok=True)
            f.seek(off)
            left = length
            with open(dst, "wb") as o:
                while left:
                    chunk = f.read(min(left, 1 << 24))
                    if not chunk:
                        raise SystemExit(f"short read in {name}")
                    o.write(chunk)
                    left -= len(chunk)
            print(f"{length:>12} {name}")
        print(f"{len(files)} files, {total} bytes selected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
