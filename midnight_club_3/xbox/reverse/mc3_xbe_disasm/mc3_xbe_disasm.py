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
    mc3_xbe_disasm.py --floats 71a10         also print the value of each float the code reads from a fixed
                                             address (as the file holds it: a global set at run time shows 0)
    mc3_xbe_disasm.py --exprs 343450         instead of the listing, each store of an SSE register as the
                                             expression it holds, operands in the code's order (see below)

--exprs is for matching float code bit for bit. addss/mulss keep their destination register's operand first, and
when both operands are NaN the first one's payload wins, so a rewrite in C that lets its compiler swap a + or *
gives other NaNs than the game. Each store prints as an expression built from the loads and ops before it
(destination first); a stack slot is named by its offset from the function's entry esp (`sp-0x10`), defined where
it is stored; a call forgets every xmm register; branches and compares print where they come, but the registers
are followed in address order, not along each path. Two limits: a callee that pops its own arguments (thiscall,
stdcall) leaves later stack slots named 4 bytes per argument too low, and loads print by address, so check the
raw listing where a value is stored and read back.

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


def float_read(xbe, insn, address):
    """The value of the 32-bit float the instruction reads from `address`, or None if it does not read one."""
    if not (insn.mnemonic.startswith('f') or insn.mnemonic.endswith('ss')):
        return None
    if f'dword ptr [{address:#x}]' not in insn.op_str:
        return None
    if insn.op_str.startswith('dword ptr') and insn.mnemonic.startswith(('movss', 'fst', 'fist')):
        return None   # a store
    return xbe.f32(address)


def annotate(xbe, insn, floats=False):
    notes = []
    for m in re.finditer(r'0x[0-9a-f]+', insn.op_str):
        a = int(m.group(0), 16)
        value = float_read(xbe, insn, a) if floats else None
        if value is not None:
            notes.append(f'{value:.9g}')
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


def show(xbe, insns, title, with_bytes, floats=False):
    x87 = sorted({i.mnemonic for i in insns if i.mnemonic.startswith(X87_ARITH)})
    if title:
        size = insns[-1].address + insns[-1].size - insns[0].address if insns else 0
        print(f'==== {title}  ({size} bytes){"  x87: " + " ".join(x87) if x87 else ""}')
    for i in insns:
        b = f'{i.bytes.hex():20s} ' if with_bytes else ''
        print(f'{i.address:08x}  {b}{i.mnemonic} {i.op_str}{annotate(xbe, i, floats)}')
    print()


SSE_OPS = {'addss': '+', 'subss': '-', 'mulss': '*', 'divss': '/'}
SSE_FUNCS = {'sqrtss': 'sqrt', 'rsqrtss': 'rsqrt', 'rcpss': 'rcp'}


def sse_exprs(xbe, insns):
    """Print each store of an xmm register as an expression in the code's operand order (see --exprs)."""
    regs = {}
    depth = 0   # bytes below the entry esp

    def slot(op):
        m = re.match(r'dword ptr \[esp(?: \+ (0x[0-9a-f]+|\d+))?\]$', op)
        return int(m.group(1), 0) - depth if m and m.group(1) else (-depth if m else None)

    def name(op):
        if op.startswith('xmm'):
            return regs.get(op, op + '?')
        k = slot(op)
        if k is not None:
            return f'sp{k:+#x}'
        m = re.match(r'dword ptr \[(.*)\]$', op)
        if not m:
            return op
        inner = m.group(1).replace(' ', '')
        if re.fullmatch(r'0x[0-9a-f]+', inner):
            a = int(inner, 16)
            return xbe.name(a) or f'{xbe.f32(a):g}@{a:x}'
        return f'[{inner}]'

    for i in insns:
        mn = i.mnemonic
        ops = [o.strip() for o in i.op_str.split(',')] if i.op_str else []
        at = f'{i.address:08x}'
        if mn == 'push':
            depth += 4
        elif mn == 'pop':
            depth -= 4
        elif mn in ('sub', 'add') and ops and ops[0] == 'esp' and re.fullmatch(r'0x[0-9a-f]+|\d+', ops[1]):
            depth += int(ops[1], 0) * (1 if mn == 'sub' else -1)
        if mn in ('movss', 'movaps', 'movups', 'movd') and len(ops) == 2:
            if ops[0].startswith('xmm'):
                regs[ops[0]] = name(ops[1])
            else:
                k = slot(ops[0])
                print(f'{at}  {f"sp{k:+#x}" if k is not None else name(ops[0])} = {regs.get(ops[1], ops[1] + "?")}')
        elif mn in SSE_OPS:
            regs[ops[0]] = f'({regs.get(ops[0], ops[0] + "?")} {SSE_OPS[mn]} {name(ops[1])})'
        elif mn in SSE_FUNCS:
            regs[ops[0]] = f'{SSE_FUNCS[mn]}({name(ops[1])})'
        elif mn in ('minss', 'maxss'):
            regs[ops[0]] = f'{mn[:3]}({regs.get(ops[0], ops[0] + "?")}, {name(ops[1])})'
        elif mn in ('xorps', 'pxor') and ops[0] == ops[1]:
            regs[ops[0]] = '0'
        elif mn in ('andps', 'orps', 'xorps', 'andnps'):
            regs[ops[0]] = f'{mn}({regs.get(ops[0], ops[0] + "?")}, {name(ops[1])})'
        elif mn in ('comiss', 'ucomiss'):
            print(f'{at}  {mn} {name(ops[0])} , {name(ops[1])}')
        elif mn == 'cvtsi2ss':
            regs[ops[0]] = f'float({ops[1]})'
        elif mn.startswith('j') or mn in ('ret', 'retn'):
            print(f'{at}  {mn} {i.op_str}')
        elif mn == 'call':
            print(f'{at}  call {i.op_str}{annotate(xbe, i)}')
            regs.clear()
        elif mn.startswith('f') and mn.startswith(X87_ARITH + ('fld', 'fst')):
            print(f'{at}  (x87) {mn} {i.op_str}')
    print()


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('addresses', nargs='*', help='hex addresses of functions')
    ap.add_argument('--range', nargs=2, metavar=('LO', 'HI'), help='disassemble [lo, hi)')
    ap.add_argument('--count', type=int, help='a fixed number of instructions from each address')
    ap.add_argument('--bytes', action='store_true', help='print the instruction bytes')
    ap.add_argument('--floats', action='store_true', help='print the value of each float read from a fixed address')
    ap.add_argument('--exprs', action='store_true', help='print SSE stores as expressions in operand order instead')
    ap.add_argument('--xbe', help='default.xbe (default: MC3_XBOX_XBE)')
    a = ap.parse_args()
    xbe = mc3_xbe.open_xbe(a.xbe)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    if a.range:
        lo, hi = (mc3_xbe.parse_address(v) for v in a.range)
        show(xbe, list(md.disasm(xbe.read(lo, hi - lo), lo)), f'{lo:08x}-{hi:08x}', a.bytes, a.floats)
    for text in a.addresses:
        va = mc3_xbe.parse_address(text)
        if a.count:
            insns = list(md.disasm(xbe.read(va, a.count * 15), va))[:a.count]
        else:
            insns = function(xbe, md, va)
        if a.exprs:
            print(f'==== {va:08x} {xbe.name(va, "")}'.rstrip())
            sse_exprs(xbe, insns)
        else:
            show(xbe, insns, f'{va:08x} {xbe.name(va, "")}'.rstrip(), a.bytes, a.floats)


if __name__ == '__main__':
    main()
