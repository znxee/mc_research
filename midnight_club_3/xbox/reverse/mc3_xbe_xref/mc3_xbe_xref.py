"""mc3_xbe_xref: who references an address in MC3's Xbox default.xbe.

Lists the direct call, jmp and conditional jump sites that reach the address (each checked by disassembling
the site), and every 32-bit word in the image that holds it: vtable slots, function-pointer tables, pointers
to a global, or an instruction operand. A data word inside the code is shown with the instruction it belongs to
when one decodes there.

    mc3_xbe_xref.py 35da80            what calls vehAutoMgr::Update, and the vtable slot that holds it
    mc3_xbe_xref.py 5580f0 4b2d70     who reads these globals (operand words in the code)

Environment variables this tool reads (set them, do not edit the code):
    MC3_XBOX_XBE    the game's default.xbe
    MC3_XBOX_NAMES  optional name files (see mc3_xbe)

Origin: the MC3 Xbox C++ decompilation's xref.py, written for mc_research by SaltySasha.
"""
import argparse

import capstone

import mc3_xbe


def where(xbe, va):
    near = xbe.nearest_name(va)
    return f'{near[1]}+{va - near[0]:#x}' if near else ''


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('addresses', nargs='+', help='hex addresses')
    ap.add_argument('--xbe', help='default.xbe (default: MC3_XBOX_XBE)')
    a = ap.parse_args()
    xbe = mc3_xbe.open_xbe(a.xbe)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    for text in a.addresses:
        target = mc3_xbe.parse_address(text)
        print(f'== {target:08x} {xbe.name(target, "")}')
        for site, kind in sorted(xbe.branch_sites().get(target, [])):
            insn = next(md.disasm(xbe.read(site, 16), site), None)
            if insn is None or not insn.op_str.startswith('0x') or int(insn.op_str, 16) != target:
                continue
            print(f'  {kind:5s} {site:08x}  {where(xbe, site)}')
        for ref in xbe.data_refs(target):
            if xbe.is_code(ref):
                # an operand: disassemble from the enclosing function's start (or a little before, where x86
                # falls into step) to find the instruction that holds it
                near = xbe.nearest_name(ref)
                start = near[0] if near and ref - near[0] < 0x4000 else ref - 64
                insn = next((i for i in md.disasm(xbe.read(start, ref + 16 - start), start)
                             if i.address <= ref < i.address + i.size), None)
                if insn and insn.address + insn.size >= ref + 4:
                    print(f'  code  {insn.address:08x}  {insn.mnemonic} {insn.op_str}    ; {where(xbe, insn.address)}')
                else:
                    print(f'  word  {ref:08x}  (in code, not an operand)')
            else:
                s = xbe.section_of(ref)
                print(f'  data  {ref:08x}  {s["name"] if s else ""} {xbe.name(ref, "")}'.rstrip())


if __name__ == '__main__':
    main()
