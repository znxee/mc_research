"""
mc2_pvs.py - the potentially-visible set of a Midnight Club 2 city

MC2 does not draw everything within a radius. Every 40-unit cell of the city
grid carries a list of the components and instances that can be seen from it,
precomputed; the renderer only tests those. MC3 has no reader for this at all
(`.pvc` and `nopvs` survive in its ELF as strings without code), and the port's
renderer culls by radius + frustum + screen size, so this list is an
optimisation the port does not have yet.

    python mc2_pvs.py check  [CIDADE ...]        # the structural self-tests
    python mc2_pvs.py stats  [CIDADE ...]        # what it would cut, per city
    python mc2_pvs.py cell   CIDADE X Z          # the visible set at world X,Z

WHERE IT LIVES
    PS2: block `PVS0` of `resource/<c>/<c>.rsc` (name = the city). The loose
    `city/<c>/<c>.pvc` is the SAME data - not per-vertex colours, which is what
    the old inventory said. Loader: MC2 PS2 sub_26A6B8 (`city/%s`, extension
    `pvc` when not running from the resource).

FORMAT (MC2 PS2 slus_202.09: sub_26A6B8 load, sub_26A858 query, sub_26BD10
record lookup, sub_26B930 cell index - read from the code, then checked)
    +0  u8  0x39      version; the game tests `== 0x39` (sets a1+6)
    +1  u8  W         grid width   (LA 90, Paris 85, Tokyo 89)
    +2  u16 0
    +4  u32 H         grid height  (LA 81, Paris 75, Tokyo 68)
    +8  u32 offset[W*H], cell = z*W + x, relative to +8; 0 = no record
    record:
        f32 height    the list is only used while the camera is below
                      height + a margin (a1+12); above it the game falls back
                      to the distance path
        u16 n1        bit 15 = DELTA: XOR the LEFT cell's raw ranges in
        u16 n2
        n1 x u16      ranges into the COMPONENT list (`unique_component`s)
        n2 x u16      ranges into the INSTANCE list (`instance_component`s)
        range = start & 0x3FFF, length = (value >> 14) + 1 (1..4 indices)
    Index order is the game's (sub_26B208): hoods in `.lvl` order, then each
    hood's records in file order.

    The delta is ONE level: the game reads the left neighbour's RAW ranges with
    sub_26BD10, never its resolved list, and no delta cell points at another
    (checked). XOR means an index present in both lists is removed.

    A record with n1 = n2 = 0 does NOT mean "nothing visible": sub_26A858 takes
    that branch to LABEL_92 and uses the distance path for that cell, which also
    adapts the draw distance to the frame time (a1+28/32/52/56).
"""

import argparse
import math
import os
import re
import statistics
import struct
import sys

import mc2_rsc as M

ROOT = os.path.join(os.environ.get('MC2_PS2_RESEARCH', ''), 'assets')
CITIES = ('losangeles', 'paris', 'tokyo')
CELL = 40.0


class Pvs(object):
    """One city's PVS plus the component/instance order it indexes."""

    def __init__(self, city, root=ROOT):
        self.city = city
        lvl = open(os.path.join(root, 'city', city, city + '.lvl')).read()
        num = r'(-?[\d.]+)'
        self.emin = [float(v) for v in
                     re.search(r'extents_min \{\s*' + r'\s+'.join([num] * 3), lvl).groups()]
        self.hoods = re.findall(r'hood \d+ \{\s*name:\s*(\S+)', lvl)
        r = M.Rsc(os.path.join(root, 'resource', city, city + '.rsc'))
        off, fcc, size = r.entries[r.indices('PVS0')[0]]
        self.data = r.data[off:off + size]
        self.version = self.data[0]
        self.W = self.data[1]
        self.H = struct.unpack_from('<I', self.data, 4)[0]
        self.ox = math.floor(self.emin[0] / CELL)
        self.oz = math.floor(self.emin[2] / CELL)
        self.comps, self.insts = [], []
        for h in self.hoods:
            text = open(os.path.join(root, 'city', city, h + '.hood')).read()
            for kind, out in (('unique_component', self.comps),
                              ('instance_component', self.insts)):
                for blk in re.finditer(kind + r' \d+ \{(.*?)\n\}', text, re.S):
                    b = blk.group(1)
                    nm = re.search(r'(?:name|type):\s*(\S+)', b).group(1)
                    out.append((h, nm, [float(v) for v in M._EMIN.search(b).groups()],
                                [float(v) for v in M._EMAX.search(b).groups()]))

    # -- raw access ---------------------------------------------------------
    def offset(self, cell):
        return struct.unpack_from('<I', self.data, 8 + 4 * cell)[0]

    def raw(self, cell):
        """(height, components, instances, delta) as stored, or None."""
        if not (0 <= cell < self.W * self.H):
            return None
        off = self.offset(cell)
        if not off:
            return None
        p = 8 + off
        h, = struct.unpack_from('<f', self.data, p)
        n1, n2 = struct.unpack_from('<HH', self.data, p + 4)
        p += 8
        delta = bool(n1 & 0x8000)
        n1 &= 0x7FFF
        lists = []
        for n in (n1, n2):
            out = []
            for _ in range(n):
                w, = struct.unpack_from('<H', self.data, p)
                p += 2
                out.extend(range(w & 0x3FFF, (w & 0x3FFF) + (w >> 14) + 1))
            lists.append(out)
        return h, lists[0], lists[1], delta

    def visible(self, cell):
        """(height, component set, instance set) as the game resolves it;
        None for no record, and the sets are both empty for 'use distance'."""
        rec = self.raw(cell)
        if rec is None:
            return None
        h, l1, l2, delta = rec
        if not delta:
            return h, set(l1), set(l2)
        left = self.raw(cell - 1) if cell % self.W else None
        out = []
        for own, base in ((l1, left[1] if left else []), (l2, left[2] if left else [])):
            s = set(base)
            for v in own:
                s.symmetric_difference_update((v,))
            out.append(s)
        return h, out[0], out[1]

    def cell_of(self, x, z):
        cx = math.floor(x / CELL) - self.ox
        cz = math.floor(z / CELL) - self.oz
        return cz * self.W + cx if 0 <= cx < self.W and 0 <= cz < self.H else None


def cmd_check(args):
    fails = 0
    for city in args.cidades or CITIES:
        p = Pvs(city)
        print('=== %s: grade %dx%d, %d componentes, %d instancias' %
              (city, p.W, p.H, len(p.comps), len(p.insts)))
        cells = range(p.W * p.H)

        def test(label, ok, detail):
            nonlocal fails
            print('  %-58s %s   %s' % (label, 'PASSA' if ok else 'FALHA', detail))
            fails += not ok

        test('versao 0x39, largura == W do .lvl', p.version == 0x39,
             'byte0 %#x, W %d, H %d' % (p.version, p.W, p.H))
        hi1 = hi2 = -1
        nested = deltas = 0
        for c in cells:
            r = p.raw(c)
            if not r:
                continue
            hi1 = max([hi1] + r[1])
            hi2 = max([hi2] + r[2])
            if r[3]:
                deltas += 1
                left = p.raw(c - 1) if c % p.W else None
                nested += bool(left and left[3])
        test('maior indice da lista 1 == componentes - 1', hi1 == len(p.comps) - 1,
             '%d de %d' % (hi1, len(p.comps)))
        test('maior indice da lista 2 == instancias - 1', hi2 == len(p.insts) - 1,
             '%d de %d' % (hi2, len(p.insts)))
        test('delta de um nivel so (vizinha nunca e delta)', nested == 0,
             '%d celulas delta, %d aninhadas' % (deltas, nested))
        ok = tot = 0
        for k, lst in ((1, p.comps), (2, p.insts)):
            for i, (h, nm, a, b) in enumerate(lst):
                v = p.visible(p.cell_of((a[0] + b[0]) / 2, (a[2] + b[2]) / 2) or -1)
                if v and (v[1] or v[2]):
                    tot += 1
                    ok += i in v[k]
        test('todo objeto e visivel da propria celula (celulas com lista)', ok == tot,
             '%d de %d' % (ok, tot))
    print('\n%d testes falharam' % fails)
    return 1 if fails else 0


def cmd_stats(args):
    for city in args.cidades or CITIES:
        p = Pvs(city)
        n = p.W * p.H
        with_list = empty = none = 0
        sizes = []
        offs = sorted(o for o in (p.offset(c) for c in range(n)) if o)
        ends = offs[1:] + [len(p.data) - 8]
        sizes = [e - o for o, e in zip(offs, ends)]
        objs = [((a[0] + b[0]) / 2, (a[2] + b[2]) / 2, math.dist(a, b) / 2)
                for _, _, a, b in p.comps + p.insts]
        ratio = []
        for c in range(n):
            v = p.visible(c)
            if v is None:
                none += 1
                continue
            if not (v[1] or v[2]):
                empty += 1
                continue
            with_list += 1
            if c % 5:
                continue
            x = ((c % p.W) + p.ox + 0.5) * CELL
            z = ((c // p.W) + p.oz + 0.5) * CELL
            inr = sum(1 for (ox, oz, r) in objs if (ox - x) ** 2 + (oz - z) ** 2 < (600 + r) ** 2)
            ratio.append((len(v[1]) + len(v[2])) / max(1, inr))
        print('%-10s celulas %d: com lista %d, vazias (=distancia) %d, sem registro %d | '
              'bloco %d B, registro mediano %d B, maior %d B | lista/raio600 mediana %.2f'
              % (city, n, with_list, empty, none, len(p.data), statistics.median(sizes),
                 max(sizes), statistics.median(ratio)))
    return 0


def cmd_cell(args):
    p = Pvs(args.cidade)
    c = p.cell_of(args.x, args.z)
    v = p.visible(c) if c is not None else None
    if v is None:
        print('celula %s: sem registro' % c)
        return 0
    if not (v[1] or v[2]):
        print('celula %d: registro vazio -> o MC2 usa o caminho por distancia aqui' % c)
        return 0
    print('celula %d (altura %.1f): %d componentes, %d instancias visiveis' %
          (c, v[0], len(v[1]), len(v[2])))
    for i in sorted(v[1])[:40]:
        print('   comp %4d  %s / %s' % (i, p.comps[i][0], p.comps[i][1]))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    sub = ap.add_subparsers(dest='cmd')
    for n in ('check', 'stats'):
        s = sub.add_parser(n)
        s.add_argument('cidades', nargs='*')
    s = sub.add_parser('cell')
    s.add_argument('cidade')
    s.add_argument('x', type=float)
    s.add_argument('z', type=float)
    a = ap.parse_args(argv)
    if not a.cmd:
        ap.print_help()
        return 2
    return {'check': cmd_check, 'stats': cmd_stats, 'cell': cmd_cell}[a.cmd](a)


if __name__ == '__main__':
    sys.exit(main())
