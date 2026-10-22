"""Read-only instruction differential for the reconstructed Remix submodels.

Runs actual unmodified SLUS_213.55 instructions with IEEE float32 scalars.
This bounded interpreter is an oracle for operation order/branches, not an EE
hardware emulator: denormals, EE FPU rounding and hardware timing are excluded.
Usage: python verify_retail.py probe.csv [--out differential.json]
"""
import os
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

sys.path.insert(0, os.environ.get('MC_RESEARCH_ROOT', ''))
import mc3_elfpatch

ELF = Path(os.path.join(os.environ.get('MC_WORK_DIR', ''), 'slus_213.55'))
PCK = Path(os.path.join(os.environ.get('MC3_ALPHA_HOSTFS', ''), 'ASSETS/resources/vehicle/vp_350z_04/vp_350z_04.pck'))
MASK = (1 << 64) - 1

def bits(x):
    return struct.unpack('<I', struct.pack('<f', x))[0]

def f32(x):
    return struct.unpack('<f', struct.pack('<f', x))[0]

def floating(x):
    return struct.unpack('<f', struct.pack('<I', x & 0xffffffff))[0]

def signed(x, width):
    return x - (1 << width) if x & (1 << (width - 1)) else x

class Machine:
    def __init__(self, elf):
        self.elf = elf
        self.segments = mc3_elfpatch.segmentos(elf)
        self.memory = {}
        self.r = [0] * 32
        self.f = [0] * 32
        self.condition = False
        self.instructions = 0

    def write(self, address, data):
        for i, byte in enumerate(data):
            self.memory[address + i] = byte

    def integer(self, address, size=4):
        if address in self.memory:
            return int.from_bytes(bytes(self.memory.get(address+i, 0) for i in range(size)), 'little')
        for base, offset, length in self.segments:
            if base <= address and address + size <= base + length:
                return int.from_bytes(self.elf[offset+address-base:offset+address-base+size], 'little')
        raise RuntimeError(f'unmapped read {address:08x}/{size}')

    def put(self, address, value, size=4):
        self.write(address, int(value & ((1 << (size*8))-1)).to_bytes(size, 'little'))

    def putf(self, address, value):
        self.put(address, bits(value))

    def execute(self, pc):
        w = self.integer(pc)
        op, rs, rt, rd, sh, fn = w >> 26, (w >> 21) & 31, (w >> 16) & 31, (w >> 11) & 31, (w >> 6) & 31, w & 63
        imm = signed(w & 65535, 16)
        address = (self.r[rs] + imm) & MASK
        self.instructions += 1
        branch = None
        if op == 0:
            if fn == 0: self.r[rd] = (self.r[rt] << sh) & 0xffffffff
            elif fn in (0x21, 0x2d): self.r[rd] = (self.r[rs] + self.r[rt]) & MASK
            elif fn == 0x25: self.r[rd] = self.r[rs] | self.r[rt]
            elif fn == 8: branch = (self.r[rs], True, False)
            else: raise RuntimeError(f'unsupported SPECIAL {w:08x} at {pc:08x}')
        elif op in (2, 3):
            if op == 3: self.r[31] = pc + 8
            branch = ((pc & 0xf0000000) | ((w & 0x3ffffff) << 2), True, False)
        elif op in (4, 5):
            same = self.r[rs] == self.r[rt]
            branch = (pc + 4 + imm * 4, same if op == 4 else not same, False)
        elif op == 9: self.r[rt] = (self.r[rs] + imm) & MASK
        elif op == 12: self.r[rt] = self.r[rs] & (w & 65535)
        elif op == 13: self.r[rt] = self.r[rs] | (w & 65535)
        elif op == 15: self.r[rt] = (w & 65535) << 16
        elif op == 35: self.r[rt] = self.integer(address)
        elif op == 36: self.r[rt] = self.integer(address, 1)
        elif op == 55: self.r[rt] = self.integer(address, 8)
        elif op == 43: self.put(address, self.r[rt])
        elif op == 63: self.put(address, self.r[rt], 8)
        elif op == 49: self.f[rt] = self.integer(address)
        elif op == 57: self.put(address, self.f[rt])
        elif op == 17:
            if rs == 0: self.r[rt] = self.f[rd]
            elif rs == 4: self.f[rd] = self.r[rt] & 0xffffffff
            elif rs == 8: branch = (pc + 4 + imm * 4, self.condition == bool(rt & 1), bool(rt & 2))
            elif rs == 20 and fn == 32: self.f[sh] = bits(signed(self.f[rd], 32))
            elif rs == 16:
                a, b = floating(self.f[rd]), floating(self.f[rt])
                if fn == 0: self.f[sh] = bits(a+b)
                elif fn == 1: self.f[sh] = bits(a-b)
                elif fn == 2: self.f[sh] = bits(a*b)
                elif fn == 3: self.f[sh] = bits(a/b)
                elif fn == 4: self.f[sh] = bits(math.sqrt(a))
                elif fn == 5: self.f[sh] = bits(abs(a))
                elif fn == 6: self.f[sh] = self.f[rd]
                elif fn == 7: self.f[sh] = bits(-a)
                elif fn == 36: self.f[sh] = int(a) & 0xffffffff
                elif fn == 50: self.condition = a == b
                elif fn == 52: self.condition = a < b
                elif fn == 54: self.condition = a <= b
                else: raise RuntimeError(f'unsupported COP1 {w:08x} at {pc:08x}')
            else: raise RuntimeError(f'unsupported COP1 fmt {w:08x} at {pc:08x}')
        else: raise RuntimeError(f'unsupported {w:08x} at {pc:08x}')
        self.r[0] = 0
        return branch

    def run(self, entry, speed=0, stop=0x0fff0000):
        self.r[4], self.r[29], self.r[31] = 0x10000000, 0x10010000, stop
        # Mapped stack, with strict unmapped asset/code access elsewhere.
        self.write(0x1000f000, bytes(4096))
        self.f[12] = bits(speed)
        pc = entry
        for _ in range(10000):
            if pc == stop: return floating(self.f[0])
            branch = self.execute(pc)
            if branch is None: pc += 4
            else:
                destination, taken, likely = branch
                if taken or not likely:
                    if self.execute(pc + 4) is not None:
                        raise RuntimeError('branch in delay slot')
                pc = destination if taken else pc + 8
        raise RuntimeError('instruction budget exhausted')

def setup(elf, pck, profile):
    m = Machine(elf)
    base = struct.unpack_from('<I', pck)[0]
    pointer = lambda offset: struct.unpack_from('<I', pck, offset)[0] - base + 128
    sim = pointer(0xb8 if profile else 0xb4)
    tune = pointer(sim + 0x5c)
    input_tune = pointer(0x98)
    obj, eng, trans, input_mem, sim_mem = 0x10000000, 0x10001000, 0x10002000, 0x10003000, 0x10004000
    m.write(obj, bytes(256)); m.write(trans, bytes(256))
    m.write(eng, pck[tune:tune+40]);m.write(input_mem, pck[input_tune:input_tune+64]);m.write(sim_mem, pck[sim:sim+160])
    # Constructor's two sqrt(5) roots, executed through the original instructions.
    m.run(0x2625f8, stop=0x262690)
    m.put(obj+4, eng);m.put(obj+0x38, trans);m.put(obj+0x30, input_mem);m.put(obj+0xb4, sim_mem)
    m.putf(obj+0x20, 1)
    m.run(0x2626d8)
    return m

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('probe', type=Path)
    parser.add_argument('--out', type=Path, default=Path('research/vehicle_dynamics/differential.json'))
    args = parser.parse_args()
    elf, pck = ELF.read_bytes(), PCK.read_bytes()
    assert hashlib.md5(elf).hexdigest() == '3e1413150ed5038d12cbfeccacd2044c'
    machines = [setup(elf, pck, n) for n in range(2)]
    entries = {'full':0x262960,'zero':0x262a60,'hp':0x2628f8,'input':0x59db10,'simulation':0x2dd760}
    comparisons, mismatches, golden = {}, [], []
    with args.probe.open(newline='') as stream:
        for row in csv.DictReader(stream):
            kind, profile = row['kind'], int(row['profile'])
            m = machines[profile]
            x, remaining, disabled, scale = float(row['x']), float(row['remaining']), int(row['disabled']), float(row['scale'])
            m.putf(0x10000008, x);m.putf(0x1000001c, remaining);m.putf(0x10000020, scale);m.put(0x10002020, disabled, 1)
            expected = m.run(entries[kind], x)
            actual = float(row['result'])
            delta = abs(bits(expected) - bits(actual))
            item = comparisons.setdefault(kind, {'samples':0,'different_bits':0,'max_ulps':0})
            item['samples'] += 1;item['different_bits'] += delta != 0;item['max_ulps'] = max(item['max_ulps'], delta)
            if delta:
                mismatches.append(dict(row, expected=expected, expected_bits=hex(bits(expected)), actual_bits=hex(bits(actual)), ulps=delta))
            if len(golden)<30 and (kind not in ('full','zero') or (remaining==0 and scale==1 and profile==0)):
                golden.append(dict(row, expected=expected, expected_bits=hex(bits(expected))))
    out = {'elf':str(ELF),'elf_md5':hashlib.md5(elf).hexdigest(),'package':str(PCK),'package_sha256':hashlib.sha256(pck).hexdigest(),
           'oracle':'Actual retail instructions, bounded IEEE float32 interpreter; cvt.w.s truncation; excludes EE FPU hardware quirks',
           'comparisons':comparisons,'total_instructions':sum(m.instructions for m in machines),
           'mismatch_count':len(mismatches),'first_mismatches':mismatches[:20],'golden':golden}
    args.out.write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('golden','first_mismatches')},indent=2))
    if mismatches: sys.exit(1)

if __name__ == '__main__': main()
