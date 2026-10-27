"""mc3_xbe_disasm: disassemble functions or address ranges of MC3's Xbox default.xbe, annotated.

Calls, jumps and data operands are labelled with names (mc3_xbox_names or your own files), kernel imports and
the strings they point at. A function's end is found by following its branches: it ends at the first return or
unconditional jump that no earlier branch jumps past. The header line lists the x87 arithmetic the function
uses: MSVC 7.1 compiled most float code to SSE, and the x87 parts round differently, which decompiler output
hides.

    mc3_xbe_disasm.py 2c9aa0 35da80          whole functions starting at these addresses (hex)
    mc3_xbe_disasm.py --range 35d500 35dd40  every instruction in [lo, hi)
    mc3_xbe_disasm.py --count 20 2ca6a8      the first 20 instructions from an address
    mc3_xbe_disasm.py --bytes 2c9aa0         also print the instruction bytes

Environment variables this tool reads (set them, do not edit the code):
    MC3_XBOX_XBE    the game's default.xbe
    MC3_XBOX_NAMES  optional name files (see mc3_xbe)

Origin: the MC3 Xbox C++ decompilation's xdis.py and asmdump.py, written for mc_research by SaltySasha.
"""
import argparse
import re

import capstone

import mc3_xbe

X87_ARITH = ('fadd', 'fsub', 'fmul', 'fdiv', 'fsqrt', 'fild', 'fist', 'fprem', 'fpatan', 'fptan', 'fyl2x',
             'fscale', 'f2xm1', 'frndint', 'fcom', 'fucom', 'fsin', 'fcos')


def annotate(xbe, insn):
    notes = []
    for m in re.finditer(r'0x[0-9a-f]+', insn.op_str):
        a = int(m.group(0), 16)
        n = xbe.name(a)
        if n:
            notes.append(n)
        elif insn.mnemonic in ('push', 'mov', 'lea') and not xbe.is_code(a):
            s = xbe.cstring(a)
            if s:
                notes.append(repr(s))
    return ('    ; ' + ', '.join(notes)) if notes else ''


def function(xbe, md, start, limit=0x4000):
    """The instructions of the function at start, following its forward branches."""
    out = []
    furthest = start
    va = start
    code = xbe.read(start, limit)
    for insn in md.disasm(code, start):
        out.append(insn)
        if insn.mnemonic.startswith('j') and insn.op_str.startswith('0x'):
            furthest = max(furthest, int(insn.op_str, 16))
        end = insn.address + insn.size
        if insn.mnemonic in ('ret', 'retf', 'int3') or insn.mnemonic == 'jmp':
            if end > furthest:
                break
        va = end
    return out


def show(xbe, insns, title, with_bytes):
    x87 = sorted({i.mnemonic for i in insns if i.mnemonic.startswith(X87_ARITH)})
    if title:
        size = insns[-1].address + insns[-1].size - insns[0].address if insns else 0
        print(f'==== {title}  ({size} bytes){"  x87: " + " ".join(x87) if x87 else ""}')
    for i in insns:
        b = f'{i.bytes.hex():20s} ' if with_bytes else ''
        print(f'{i.address:08x}  {b}{i.mnemonic} {i.op_str}{annotate(xbe, i)}')
    print()


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('addresses', nargs='*', help='hex addresses of functions')
    ap.add_argument('--range', nargs=2, metavar=('LO', 'HI'), help='disassemble [lo, hi)')
    ap.add_argument('--count', type=int, help='a fixed number of instructions from each address')
    ap.add_argument('--bytes', action='store_true', help='print the instruction bytes')
    ap.add_argument('--xbe', help='default.xbe (default: MC3_XBOX_XBE)')
    a = ap.parse_args()
    xbe = mc3_xbe.open_xbe(a.xbe)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    if a.range:
        lo, hi = (mc3_xbe.parse_address(v) for v in a.range)
        show(xbe, list(md.disasm(xbe.read(lo, hi - lo), lo)), f'{lo:08x}-{hi:08x}', a.bytes)
    for text in a.addresses:
        va = mc3_xbe.parse_address(text)
        if a.count:
            insns = list(md.disasm(xbe.read(va, a.count * 15), va))[:a.count]
        else:
            insns = function(xbe, md, va)
        show(xbe, insns, f'{va:08x} {xbe.name(va, "")}'.rstrip(), a.bytes)


if __name__ == '__main__':
    main()
