"""Build optional *_traffic_vpo.pck packs from real opponent *_o.pck donors.

Original traffic packs, tuning, density, trains and player packages are never
overwritten. Enable the separate traffic_opponents.mod with = shim in [mods];
disable with = 0 and cold boot. This is an ambient-geometry replacement, not
opponent AI. Colors are semantic Civic-atlas swatches, not detailed VP skins.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile

import mc3_traffic_mlod as mlod
import mc3_traffic_wheels as wheels

DONORS = {
    "va_civic_sh": "vp_350z_04",
    "va_odessey_sh": "vp_escalade_03",
    "va_tacoma_sh": "vp_ram_04",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(source, vehicles, output, stock_wheels=True):
    source, vehicles, output = map(Path, (source, vehicles, output))
    if source.resolve() == output.resolve():
        raise ValueError("output must not overwrite the original pack")
    before = sha(source)
    tp = mlod.traffic.TrafficPck(str(source))
    roots = dict(tp.roots())
    applicable = {k: v for k, v in DONORS.items() if k in roots}
    if not applicable or "va_civic_sh" not in roots:
        raise ValueError("no supported common cars/Civic atlas in %s" % source)
    # Resolve every dependency before doing work; no half-built active pack.
    donors = {}
    for slot, name in applicable.items():
        donor = vehicles / name / (name + "_o.pck")
        if not donor.is_file():
            raise FileNotFoundError(donor)
        donors[slot] = donor
    output.parent.mkdir(parents=True, exist_ok=True)
    result = dict(source=str(source), source_sha256=before, output=str(output),
                  replacements=[], unchanged_vehicles=sorted(set(roots)-set(applicable)),
                  imported_player_shaders=0, lod="MLOD", stock=True,
                  physics="original ambient bounds/tuning",
                  wheels="VP stock MLOD + mounting caches" if stock_wheels else "original ambient")
    with tempfile.TemporaryDirectory(prefix="mc3_vpo_") as scratch:
        current = source
        for step, (slot, donor) in enumerate(donors.items()):
            target = Path(scratch) / (str(step) + ".pck")
            r = mlod.insert(str(current), str(donor), slot, str(target),
                            lod="MLOD", stock=True, shader_profile="traffic-stock",
                            uv_profile="civic-share", body_atlas="va_civic_sh",
                            body_atlas_source=str(source))
            wheel_report = None
            if stock_wheels:
                setup = wheels.stock_setup(donor,vehicles,vehicles.parent.parent/'tune/vehicle')
                wheel_tp = mlod.traffic.TrafficPck(str(target))
                wheel_report = wheels.insert(wheel_tp,slot,setup)
                wheel_tp.save(str(target))
            result["replacements"].append(dict(
                vehicle=slot, donor=str(donor), donor_sha256=sha(donor),
                stats=r["merged_stats"], appended_bytes=r["appended_bytes"],
                parts=[p["name"] for p in r["donor"]],
                atlas_bindings=r["atlas_bindings"], material_map=r["material_map"],
                stock_wheels=wheel_report))
            current = target
        final = mlod.traffic.TrafficPck(str(current))
        if final.roots() != tp.roots():
            raise ValueError("vehicle directory unexpectedly changed")
        wheel_slots = {w['slot'] for r in result['replacements'] if r['stock_wheels']
                       for w in r['stock_wheels']['wheels']}
        for piece in tp.pieces():
            if ((piece["vehicle"] not in applicable or piece["piece_id"] != 0)
                    and piece.get('slot') not in wheel_slots):
                # Buses, trains, shadows and every non-selected piece stay VA.
                slot = piece.get("slot")
                if slot is not None and final.pck.U(slot) != tp.pck.U(slot):
                    raise ValueError("unselected slot changed")
        allowed=set(range(12,16))
        for piece in tp.pieces():
            if piece['vehicle'] in applicable and piece['piece_id']==0:
                allowed.update(range(piece['slot'],piece['slot']+4))
        for name,root in tp.roots():
            if name in applicable:allowed.update(range(root+8,root+12))
        for r in result['replacements']:
            if r['stock_wheels']:allowed.update(r['stock_wheels']['changed_prefix_offsets'])
        bad=[i for i,(a,b) in enumerate(zip(tp.data,final.data)) if a!=b and i not in allowed]
        if bad:raise ValueError("untyped prefix changes: %r"%bad[:12])
        if sha(source) != before:
            raise ValueError("source changed during build; not publishing output")
        # Generated artifact, not an edit to source. Publish only after checks.
        output.write_bytes(Path(current).read_bytes())
    result.update(bytes=output.stat().st_size, original_bytes=source.stat().st_size,
                  sha256=sha(output), original_unchanged=sha(source)==before)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hostfs", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True,
                    help="staging directory; never changes mc3boot.ini")
    ap.add_argument("--city", action="append",
                    help="repeat to limit cities; default all *_traffic.pck")
    ap.add_argument("--ambient-wheels", action="store_true",
                    help="compatibility: retain original VA wheels/mounting points")
    ns = ap.parse_args()
    city_dir = ns.hostfs / "ASSETS/resources/city"
    sources = ([city_dir / (city + "_traffic.pck") for city in ns.city]
               if ns.city else sorted(city_dir.glob("*_traffic.pck")))
    if not sources:
        raise SystemExit("no city traffic packs found")
    reports = []
    for source in sources:
        if source.stem.endswith("_vpo"):
            continue
        out = ns.out / "ASSETS/resources/city" / (source.stem + "_vpo.pck")
        r = build(source, ns.hostfs / "ASSETS/resources/vehicle", out,
                  stock_wheels=not ns.ambient_wheels)
        reports.append(r)
        print("%s: %d replacements, %+d bytes; original unchanged" %
              (source.name, len(r["replacements"]), r["bytes"]-r["original_bytes"]),
              flush=True)
    (ns.out / "manifest.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
