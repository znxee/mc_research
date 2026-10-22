# -*- coding: utf-8 -*-
"""Le de volta o modelo convertido e compara com a fonte MC2, lado a lado."""
import io
import math
import os
import struct
from PIL import Image, ImageDraw

SC = os.path.join(os.environ.get('MC_SCRATCH_DIR', ''), 'city')
MOD = os.path.join(SC, 'atlanta_mc2test.pck')
MC2 = os.path.join(os.environ.get('MC2_PC_RESEARCH', ''), 'assets_p/city/losangeles/models/l_downtown_blk_04_x#geom_0_main.xmod')


def read_xmod(path):
    txt = io.open(path, encoding='latin1').read().splitlines()
    v, t1, adj, strips = [], [], [], []
    for line in txt:
        f = line.strip().split()
        if not f:
            continue
        if f[0] == 'v' and len(f) >= 4:
            v.append((float(f[1]), float(f[2]), float(f[3])))
        elif f[0] == 't1' and len(f) >= 3:
            t1.append((float(f[1]), float(f[2])))
        elif f[0] == 'adj' and len(f) >= 5:
            adj.append((int(f[1]), int(f[4])))
        elif f[0] in ('stp', 'str') and len(f) >= 3:
            strips.append((f[0] == 'str', [int(x) for x in f[2:2 + int(f[1])]]))
    return v, t1, adj, strips


def tris_from_strip(pts, odd):
    out = []
    for i in range(2, len(pts)):
        a, b, c = (i - 2, i - 1, i) if (i % 2 == 0) != odd else (i - 1, i - 2, i)
        out.append((pts[a], pts[b], pts[c]))
    return out


def render(tris, path, size=430, title=''):
    if not tris:
        return False
    pts = [p for t in tris for p in t]
    cx = (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2
    cy = (min(p[1] for p in pts) + max(p[1] for p in pts)) / 2
    cz = (min(p[2] for p in pts) + max(p[2] for p in pts)) / 2
    span = max(max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)) or 1
    a, b = math.radians(28), math.radians(-38)
    ca, sa, cb, sb = math.cos(a), math.sin(a), math.cos(b), math.sin(b)

    def proj(p):
        x, y, z = p[0] - cx, p[1] - cy, p[2] - cz
        x, z = x * cb - z * sb, x * sb + z * cb
        y, z = y * ca - z * sa, y * sa + z * ca
        s = size * 0.40 / span
        return (size / 2 + x * s, size / 2 - y * s, z)

    img = Image.new('RGB', (size, size), (26, 26, 30))
    dr = ImageDraw.Draw(img)
    faces = []
    for t in tris:
        q = [proj(p) for p in t]
        ax, ay = q[1][0] - q[0][0], q[1][1] - q[0][1]
        bx, by = q[2][0] - q[0][0], q[2][1] - q[0][1]
        if abs(ax * by - ay * bx) < 0.3:
            continue
        faces.append((sum(p[2] for p in q) / 3, q))
    faces.sort(key=lambda f: f[0])
    n = len(faces) or 1
    for i, (_z, q) in enumerate(faces):
        c = int(70 + 145 * i / n)
        dr.polygon([(p[0], p[1]) for p in q], fill=(c, c, min(255, c + 22)),
                   outline=(22, 22, 26))
    dr.text((8, 8), title, fill=(235, 235, 235))
    img.save(path)
    return True


# fonte MC2
v, t1, adj, strips = read_xmod(MC2)
cx = sum(p[0] for p in v) / len(v)
cy = sum(p[1] for p in v) / len(v)
cz = sum(p[2] for p in v) / len(v)
src_t = []
for odd, idxs in strips:
    pts = [tuple(a - b for a, b in zip(v[adj[i][0]], (cx, cy, cz))) for i in idxs]
    src_t += tris_from_strip(pts, odd)
print('fonte MC2: %d triangulos em %d tiras' % (len(src_t), len(strips)))

# so as 9 primeiras tiras (as que couberam)
src9 = []
for odd, idxs in strips[:9]:
    pts = [tuple(a - b for a, b in zip(v[adj[i][0]], (cx, cy, cz))) for i in idxs]
    src9 += tris_from_strip(pts, odd)
print('primeiras 9 tiras: %d triangulos' % len(src9))

# le de volta do .pck convertido
d = open(MOD, 'rb').read()
va = struct.unpack_from('<I', d, 0)[0]
BASE = va - 0x80
F = lambda x: x - BASE
U = lambda o: struct.unpack_from('<I', d, o)[0]

mo = None
for o in range(0x80, len(d) - 0x50, 4):
    if U(o) == 0x7A0090:
        raw = bytes(d[o + 0x48:o + 0x70]).split(b'\0')[0]
        if raw == b'a_inst_low_60s_03x':
            mo = o
            break
mesh = F(U(mo + 0x14))
main = F(U(mesh + 0x10))
out_t = []
nblocks = 0
for gi in range(24):
    gp = U(main + 8 * gi)
    gc = struct.unpack_from('<H', d, main + 8 * gi + 4)[0]
    if not (0x80 <= F(gp) < len(d)) or not (1 <= gc <= 512):
        break
    t = F(gp)
    for k in range(gc):
        bp = F(U(t + 8 * k))
        if not (0x80 <= bp < len(d) - 0x10):
            continue
        sc_ = struct.unpack_from('<f', d, bp + 4)[0]
        cnt = struct.unpack_from('<I', d, bp + 8)[0]
        if not (1 <= cnt <= 4096):
            continue
        pos = [tuple(c * sc_ for c in struct.unpack_from('<hhh', d, bp + 0x10 + 6 * i))
               for i in range(cnt)]
        odd = d[bp + 0x0C:bp + 0x0E] == b'\x27\x02'
        out_t += tris_from_strip(pos, odd)
        nblocks += 1
print('lido de volta do .pck: %d blocos, %d triangulos' % (nblocks, len(out_t)))

# erro maximo entre fonte e resultado
if len(src9) == len(out_t):
    err = max(max(abs(a - b) for pa, pb in zip(ta, tb) for a, b in zip(pa, pb))
              for ta, tb in zip(src9, out_t))
    print('ERRO MAXIMO de posicao (quantizacao s16, escala 1/256): %.4f unidades' % err)
else:
    print('contagem difere: fonte9=%d lido=%d' % (len(src9), len(out_t)))

render(src_t, os.path.join(SC, 'v_mc2_full.png'), title='MC2 completo (%d tris)' % len(src_t))
render(src9, os.path.join(SC, 'v_mc2_9.png'), title='MC2, 9 primeiras tiras (%d tris)' % len(src9))
render(out_t, os.path.join(SC, 'v_mc3_out.png'), title='lido do .pck MC3 (%d tris)' % len(out_t))

ims = [Image.open(os.path.join(SC, n)) for n in ('v_mc2_full.png', 'v_mc2_9.png', 'v_mc3_out.png')]
sh = Image.new('RGB', (430 * 3, 430), (18, 18, 20))
for i, im in enumerate(ims):
    sh.paste(im, (430 * i, 0))
sh.save(os.path.join(SC, 'verify.png'))
print('-> verify.png')
