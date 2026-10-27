"""mc3_xbe_regdeps: check an Xbox function before you hook it or replace it with your own code.

MC3's Xbox build was compiled by MSVC 7.1 with whole-program optimisation (LTCG), which ignores the calling
convention where it can see both sides of a call:

  callers   a caller may keep a value in a register the convention lets the callee destroy (ecx, edx, xmm0-7)
            when it knows the callee leaves it alone. Replace the callee with code compiled today and that
            caller breaks. This lists every direct call site that reads such a register after the call before
            writing it.
  callee    a function may read a register on entry that its callers happen to set up (a pointer in edx, a 0 or
            1 in an xmm register). Call it from your own code and that register holds garbage. This lists the
            registers the function reads before writing them, besides ecx (this, or the first fastcall
            argument).

Both follow the code's branches for a limited number of instructions; treat a hit as "read this code", not as
proof.

    mc3_xbe_regdeps.py callers 35da80 2c9aa0
    mc3_xbe_regdeps.py callers --rewritten mine.txt 35da80     ignore call sites in functions you replaced too
    mc3_xbe_regdeps.py callee 2ca890

Environment variables this tool reads (set them, do not edit the code):
    MC3_XBOX_XBE    the game's default.xbe
    MC3_XBOX_NAMES  optional name files (see mc3_xbe)

Origin: the MC3 Xbox C++ decompilation's callerdeps.py and calleedeps.py, written for mc_research by
SaltySasha.
"""
import argparse

import capstone
from capstone import x86

import mc3_xbe

VOLATILE = {f'xmm{i}' for i in range(8)} | {'ecx', 'edx'}
GENERAL = {f'xmm{i}' for i in range(8)} | {'eax', 'ebx', 'ecx', 'edx', 'esi', 'edi'}
FAMILY = {'ax': 'eax', 'al': 'eax', 'ah': 'eax', 'bx': 'ebx', 'bl': 'ebx', 'bh': 'ebx', 'cx': 'ecx', 'cl': 'ecx',
          'ch': 'ecx', 'dx': 'edx', 'dl': 'edx', 'dh': 'edx', 'si': 'esi', 'di': 'edi'}
WRITE_ONLY = ('movss', 'movaps', 'movups', 'movd', 'cvtsi2ss', 'mov', 'movzx', 'movsx', 'lea')


def reg(cs, r):
    n = cs.reg_name(r)
    return FAMILY.get(n, n)


def accesses(cs, ins, watch):
    """(reads, writes) of the watched registers, with the idioms that only write taken out."""
    try:
        rd, wr = ins.regs_access()
    except capstone.CsError:
        return None
    reads = {reg(cs, r) for r in rd} & watch
    writes = {reg(cs, r) for r in wr} & watch
    ops = ins.operands
    if ins.mnemonic in ('xorps', 'xorpd', 'pxor', 'xor', 'sub') and len(ops) == 2 and \
            ops[0].type == x86.X86_OP_REG and ops[1].type == x86.X86_OP_REG and ops[0].reg == ops[1].reg:
        reads = set()
    # "or r, -1" and "and r, 0" set the register whatever it held
    if ins.mnemonic in ('or', 'and') and len(ops) == 2 and ops[0].type == x86.X86_OP_REG and \
            ops[1].type == x86.X86_OP_IMM and ops[1].imm & 0xffffffff == (0xffffffff if ins.mnemonic == 'or' else 0):
        reads -= {reg(cs, ops[0].reg)}
    if ins.mnemonic in WRITE_ONLY and ops and ops[0].type == x86.X86_OP_REG:
        reads -= {reg(cs, ops[0].reg)}
    return reads, writes


def walk(xbe, cs, start, watch, limit, after_call):
    """Registers of `watch` read before written, following both arms of each branch: {register: first read}."""
    deps = {}
    seen = set()
    work = [(start, frozenset())]
    while work:
        a, written = work.pop()
        steps = 0
        while steps < limit:
            if (a, written) in seen:
                break
            seen.add((a, written))
            ins = next(cs.disasm(xbe.read(a, 16), a), None)
            if ins is None:
                break
            if after_call and steps == 0:
                if ins.mnemonic != 'call':
                    break   # a tail call: nothing runs after it in this function
                a += ins.size
                steps += 1
                continue
            got = accesses(cs, ins, watch)
            if got is None:
                break
            reads, writes = got
            if ins.mnemonic == 'push':
                # saving a callee-saved register, or MSVC reserving a stack slot with "push ecx"
                reads = set() if not after_call else reads - {'ecx', 'edx'}
            for r in reads - written:
                deps.setdefault(r, ins.address)
            written = written | writes
            if ins.mnemonic == 'ret' or ins.mnemonic == 'jmp' and not ins.op_str.startswith('0x'):
                break
            if ins.mnemonic == 'call':
                if after_call:
                    break
                written = written | {'eax', 'ecx', 'edx'} | {f'xmm{i}' for i in range(8)}
            elif ins.mnemonic.startswith('j') and ins.op_str.startswith('0x'):
                t = int(ins.op_str, 16)
                if ins.mnemonic == 'jmp':
                    a = t
                    steps += 1
                    continue
                work.append((t, written))
            a += ins.size
            steps += 1
    return deps


def read_addresses(path):
    out = set()
    for line in open(path, encoding='utf-8', errors='replace'):
        q = line.split()
        if q and not line.startswith('#'):
            try:
                out.add(int(q[0], 16))
            except ValueError:
                pass
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('mode', choices=('callers', 'callee'))
    ap.add_argument('addresses', nargs='+', help='hex addresses of functions')
    ap.add_argument('--rewritten', help='a file of function addresses (first column) whose original code no '
                                        'longer runs: call sites inside them are skipped')
    ap.add_argument('--xbe', help='default.xbe (default: MC3_XBOX_XBE)')
    a = ap.parse_args()
    xbe = mc3_xbe.open_xbe(a.xbe)
    cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    cs.detail = True
    targets = [mc3_xbe.parse_address(t) for t in a.addresses]
    if a.mode == 'callee':
        for t in targets:
            deps = walk(xbe, cs, t, GENERAL, 400, False)
            deps.pop('ecx', None)
            shown = ', '.join(f'{r} (first read at {at:08x})' for r, at in sorted(deps.items()))
            print(f'{t:08x} {xbe.name(t, "?")}: {shown or "nothing beyond its arguments"}')
        return
    rewritten = read_addresses(a.rewritten) if a.rewritten else set()
    bad = 0
    for t in targets:
        for site, kind in sorted(xbe.branch_sites().get(t, [])):
            if kind != 'call':
                continue
            near = xbe.nearest_name(site)
            if near and near[0] in rewritten:
                continue
            deps = walk(xbe, cs, site, VOLATILE, 60, True)
            if deps:
                bad += 1
                where = f'{near[1]}+{site - near[0]:#x}' if near else ''
                print(f'{t:08x} {xbe.name(t, "?")}: the call at {site:08x} {where} relies on '
                      f'{" ".join(sorted(deps))} afterwards')
    print(f'{bad} call site(s) rely on registers across calls to {len(targets)} function(s)')


if __name__ == '__main__':
    main()
