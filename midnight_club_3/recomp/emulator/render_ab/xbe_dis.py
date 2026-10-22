"""MC3-0008: disassemble the MC3 XBE around an address (local analysis only).

  python -I xbe_dis.py <va> [--func] [--callers] [-n N]

--func disassembles the whole function holding va (disasm/functions.json); --callers lists who calls it.
"""

from __future__ import annotations

import argparse
import bisect
import json
from pathlib import Path
import struct

import capstone

HERE = Path(__file__).resolve().parent
XBE = HERE.parent / "xboxxberecomp_eval" / "templates" / "game" / "assets" / "default.xbe"
FUNCS = HERE.parent / "disasm" / "functions.json"


def sections(data: bytes):
    base = struct.unpack_from("<I", data, 0x104)[0]
    n = struct.unpack_from("<I", data, 0x11C)[0]
    hdr = struct.unpack_from("<I", data, 0x120)[0] - base
    out = []
    for i in range(n):
        flags, va, vsize, raw, rsize = struct.unpack_from("<IIIII", data, hdr + i * 56)
        out.append((va, vsize, raw, rsize))
    return out


def read(data, secs, va, n):
    for sva, vsize, raw, rsize in secs:
        if sva <= va < sva + vsize:
            off = va - sva
            return data[raw + off: raw + min(off + n, rsize)]
    return b""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("va")
    ap.add_argument("--func", action="store_true")
    ap.add_argument("--callers", action="store_true")
    ap.add_argument("-n", type=int, default=40)
    ap.add_argument("--before", type=int, default=0, help="bytes before va to start from")
    a = ap.parse_args()
    va = int(a.va, 16)
    data = XBE.read_bytes()
    secs = sections(data)
    funcs = json.loads(FUNCS.read_text())
    starts = [int(f["start"], 16) for f in funcs]
    i = bisect.bisect_right(starts, va) - 1
    f = funcs[i] if i >= 0 else None
    if f:
        print(f"in {f['name']} {f['start']}..{f['end']} called by {len(f['called_by'])}: {' '.join(f['called_by'][:12])}")
    if a.callers:
        return 0
    start = int(f["start"], 16) if a.func and f else va - a.before
    end = int(f["end"], 16) + 1 if a.func and f else None
    code = read(data, secs, start, (end - start) if end else a.n * 8)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    k = 0
    for ins in md.disasm(code, start):
        mark = " <==" if ins.address <= va < ins.address + ins.size else ""
        print(f"{ins.address:08X}  {ins.mnemonic:8} {ins.op_str}{mark}")
        k += 1
        if not end and k >= a.n:
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
