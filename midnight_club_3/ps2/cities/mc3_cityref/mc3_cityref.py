"""Where the executable treats one city differently from the others.

Midnight Club 3 reaches three of its cities the same way - Career, then pick one
- and Tokyo a fourth way, its own entry called Tokyo Challenge. That is not a
different subsystem. The session object at `*(0x00619B10)` carries the city
index in its word 0, and the difference is code asking whether that word equals
a particular number.

    python mc3_cityref.py                    # the Tokyo tests (index 3)
    python mc3_cityref.py --index 4          # and so on
    python mc3_cityref.py --elf OUTRO.ELF

Written for the city-slot work: to make a sixth city reachable, something has to
treat its index the way these sites treat 3. The list is where to look.

WHAT THIS IS, HONESTLY

A lead generator, not a census. Read the count as "places worth opening", never
as "how special this city is". Two things spoil it as a measure:

  * It is BLIND TO INDEX 0. There is no `addiu rX,zero,0` in MIPS - a register
    is zeroed some other way - so index 0 can never match the pattern, and the
    empty result it prints means nothing at all.
  * SMALL INDICES ATTRACT FALSE POSITIVES. 1 and 2 are the most common literals
    in any program, so an `addiu rX,zero,1` that happens to sit near a session
    load is picked up whether or not it has anything to do with cities. Running
    it across 0..5 gives 0/18/7/11/7/1, and that spread is the proof: if the
    count measured anything real, the three cities reached the identical way
    would not score 0, 18 and 7.

So: open the addresses and read them. The one confirmed by hand is 0x0037DFA8,
where the Tokyo/Career string choice is visible instruction by instruction.
"""
import os
import argparse
import struct

ELF_PADRAO = os.path.join(os.environ.get('MC_WORK_DIR', ''), 'SLUS_213.55_EDITED - Copia.ELF')

# mcConfig's session object. Word 0 is the current city index, word 1 the
# condition (time and weather).
SESSAO_OFF = 0x9B10          # low half of 0x00619B10, as it appears in the lw
JANELA = 10                  # instructions either side; wider only adds noise

R = ['zero', 'at', 'v0', 'v1', 'a0', 'a1', 'a2', 'a3', 't0', 't1', 't2', 't3',
     't4', 't5', 't6', 't7', 's0', 's1', 's2', 's3', 's4', 's5', 's6', 's7',
     't8', 't9', 'k0', 'k1', 'gp', 'sp', 'fp', 'ra']


def carrega(caminho):
    """(bytes, file offset, vaddr, size) do unico PT_LOAD."""
    d = open(caminho, 'rb').read()
    po = struct.unpack_from('<I', d, 0x1C)[0]
    pn = struct.unpack_from('<H', d, 0x2C)[0]
    ps = struct.unpack_from('<H', d, 0x2A)[0]
    for i in range(pn):
        t, off, va, _pa, fsz, _msz, _fl, _al = struct.unpack_from(
            '<IIIIIIII', d, po + i * ps)
        if t == 1 and fsz:
            return d, off, va, fsz
    raise SystemExit('nenhum PT_LOAD em %s' % caminho)


def procura(caminho, indice):
    d, off, base, fsz = carrega(caminho)

    def w(i):
        return struct.unpack_from('<I', d, off + i)[0]

    achados = []
    for i in range(0, fsz - 4 * JANELA * 2, 4):
        x = w(i)
        if (x >> 26) != 0x23 or (x & 0xFFFF) != SESSAO_OFF:   # lw rt, off(rs)
            continue
        sess = (x >> 16) & 31

        # Follow that register to the load of its word 0 - the city index.
        idx = base_k = None
        for k in range(1, JANELA):
            y = w(i + 4 * k)
            if (y >> 26) == 0x23 and ((y >> 21) & 31) == sess and (y & 0xFFFF) == 0:
                idx, base_k = (y >> 16) & 31, k
                break
            if (y >> 26) == 0x0F and ((y >> 16) & 31) == sess:
                break                                          # rt overwritten
        if idx is None:
            continue

        # The constant is as often built BEFORE the load as after it - 0x37DFA8
        # builds it two instructions earlier - so look both ways.
        ordem = list(range(base_k + 1, base_k + JANELA)) + list(range(-JANELA, 0))
        for k in ordem:
            z = w(i + 4 * k)
            op = z >> 26
            rs, rt, imm = (z >> 21) & 31, (z >> 16) & 31, z & 0xFFFF
            va = base + i + 4 * k
            if op == 0x09 and rs == 0 and rt != 0 and imm == indice:
                achados.append((va, 'addiu %s,zero,%d  -> beq/bne com o indice'
                                % (R[rt], indice)))
                break
            if op in (0x0A, 0x0B) and rs == idx and imm == indice:
                achados.append((va, '%s %s,%s,%d'
                                % ('slti' if op == 0x0A else 'sltiu',
                                   R[rt], R[rs], indice)))
                break
            if op == 0x0E and rs == idx and imm == indice:
                achados.append((va, 'xori %s,%s,%d  -> "e igual a %d?"'
                                % (R[rt], R[rs], indice, indice)))
                break
    return sorted(achados)


def main():
    p = argparse.ArgumentParser(
        description='sites que comparam a cidade atual com um indice')
    p.add_argument('--elf', default=ELF_PADRAO)
    p.add_argument('--index', type=int, default=3,
                   help='3 = Tokyo, a unica com acesso proprio no menu')
    a = p.parse_args()

    achados = procura(a.elf, a.index)
    print('%d CANDIDATOS a comparacao com a cidade %d - abra e leia cada um'
          % (len(achados), a.index))
    if a.index == 0:
        print('   (indice 0 nao casa o padrao: `addiu rX,zero,0` nao existe)')
    for va, txt in achados:
        print('   %08X  %s' % (va, txt))


if __name__ == '__main__':
    main()
