"""mc2_xbox_pillar_feet: pillar feet MC2 left without a dummybound (hoods, models and props of the Xbox/PC assets_p) -> <city>_pillars.txt for the recomp host

    python mc2_xbox_pillar_feet.py --city losangeles --out hdd/Z/mc2/city/losangeles/losangeles_pillars.txt
    python mc2_xbox_pillar_feet.py --city tokyo      --out hdd/Z/mc2/city/tokyo_mc2/tokyo_pillars.txt

MC2 gives a standing pillar its collision through an invisible prop, `*_prop_dummybound_*` (FixedObject), placed by
hand and not under every pillar. For every hood instance whose type name holds pylon / pillar / column / colmn /
support (not `supportbase`: those are 0.4 m kerbs between the freeway pillars) this takes the feet of its LOD 0 model
(vertices below 1 m in model space, grouped within 2.5 m), puts them in the world and keeps those with no dummybound
within --near metres. The recomp host (mc2_props.cpp) places a dummybound at each line of the file. Same rule and same
counts as the PS2 tool mc2_pillar_legs: Los Angeles 80, Tokyo 412, Paris none.

All of MC2's city files read here are text: city/<city>/*.hood (instance_component: type + 4 rows of the matrix),
city/<city>/models/<type>_0_<part>.xmod ("v x y z" lines) and city/<city>/<city>.prop (prop with prop_template).

Environment variables this tool reads (set them, do not edit the code):
    MC2_PC_RESEARCH   the Midnight Club II (PC) research folder, with its assets_p/ (or pass --assets)

Origin: the PS2 tool mc2_pillar_legs (rule and NOT_PILLAR), written for mc_research by znxee.
"""
import argparse
import glob
import math
import os
import re
import sys

KEYS = re.compile(r"pylon|pillar|column|colmn|support", re.I)
NOT_PILLAR = re.compile(r"supportbase", re.I)
NUM = r"-?[\d.]+(?:e[-+]?\d+)?"


def hood_instances(root, folder):
    """[(type, 12 floats: rows x, y, z, translation)] of every hood of the city."""
    out = []
    for f in sorted(glob.glob(os.path.join(root, "city", folder, "*.hood"))):
        text = open(f, errors="ignore").read()
        for m in re.finditer(r"instance_component\s+\d+\s*\{(.*?)\n\}", text, re.S):
            body = m.group(1)
            ty = re.search(r"type:\s*(\S+)", body)
            rows = re.findall(r"^\s*(%s)\s+(%s)\s+(%s)\s*$" % (NUM, NUM, NUM), body, re.M)
            if ty and len(rows) >= 4:
                out.append((ty.group(1).lower(), [float(v) for row in rows[:4] for v in row]))
    return out


def model_feet(root, folder, ty, cache):
    """(x, z) of each foot of the type's LOD 0 model, in model space."""
    if ty in cache:
        return cache[ty]
    low = []
    for f in glob.glob(os.path.join(root, "city", folder, "models", ty + "_0_*.xmod")):
        for m in re.finditer(r"^v\s+(\S+)\s+(\S+)\s+(\S+)", open(f, errors="ignore").read(), re.M):
            p = (float(m.group(1)), float(m.group(2)), float(m.group(3)))
            if p[1] < 1.0:
                low.append(p)
    groups = []
    for p in low:
        for g in groups:
            if abs(g[0] - p[0]) < 2.5 and abs(g[1] - p[2]) < 2.5:
                g[2].append(p)
                break
        else:
            groups.append([p[0], p[2], [p]])
    cache[ty] = [(sum(q[0] for q in g[2]) / len(g[2]), sum(q[2] for q in g[2]) / len(g[2])) for g in groups]
    return cache[ty]


def dummybounds(root, folder):
    """(x, z) of every dummybound prop the city's .prop places."""
    stem = "tokyo" if folder.startswith("tokyo") else folder
    text = open(os.path.join(root, "city", folder, stem + ".prop"), errors="ignore").read()
    out = []
    for m in re.finditer(r"prop\s+\d+\s*\{(.*?)\n\}", text, re.S):
        tm = re.search(r"prop_template:\s*(\S+)", m.group(1))
        if tm and "dummybound" in tm.group(1).lower():
            mt = re.search(r"matrix\s*\{(.*?)\}", m.group(1), re.S)
            n = [float(x) for x in re.findall(NUM, mt.group(1))]
            out.append((n[9], n[11]))
    return out


def to_world(m, p):
    return tuple(p[0] * m[c] + p[1] * m[3 + c] + p[2] * m[6 + c] + m[9 + c] for c in range(3))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--city", required=True, help="the folder under assets_p/city: losangeles, paris or tokyo")
    ap.add_argument("--assets", default=os.path.join(os.environ.get("MC2_PC_RESEARCH", ""), "assets_p"),
                    help="MC2's assets_p folder (default: $MC2_PC_RESEARCH/assets_p)")
    ap.add_argument("--out", help="write the feet here, one 'x y z' line each")
    ap.add_argument("--near", type=float, default=3.0, help="a dummybound this close covers a foot")
    a = ap.parse_args()
    if not os.path.isdir(os.path.join(a.assets, "city", a.city)):
        sys.exit("no %s/city/%s: set MC2_PC_RESEARCH or pass --assets" % (a.assets, a.city))
    inst = hood_instances(a.assets, a.city)
    covered = dummybounds(a.assets, a.city)
    cache, feet, per_type = {}, [], {}
    for ty, m in inst:
        if not KEYS.search(ty) or NOT_PILLAR.search(ty):
            continue
        for fx, fz in model_feet(a.assets, a.city, ty, cache):
            w = to_world(m, (fx, 0.0, fz))
            if any(math.hypot(w[0] - x, w[2] - z) < a.near for x, z in covered):
                continue
            feet.append(w)
            per_type[ty] = per_type.get(ty, 0) + 1
    for ty, n in sorted(per_type.items()):
        print("%-40s %4d feet" % (ty, n))
    print("%d feet without a dummybound (%d dummybounds, %d instances in the city)" % (len(feet), len(covered), len(inst)))
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w", newline="\n") as f:
            f.write("# mc2_xbox_pillar_feet.py --city %s: x y z of pillar feet MC2 left without a dummybound\n" % a.city)
            for w in feet:
                f.write("%.2f %.2f %.2f\n" % w)


if __name__ == "__main__":
    main()
