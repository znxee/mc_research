"""Transplante conservador de VIF v7/forge para o PCK moderno.

Seleciona o destino a partir do centro mundial e da forma exata dos pacotes.
Quando dois componentes ocupam o mesmo centro, o payload da referencia v7
serve apenas como desempate. Malhas modernas com outra divisao sao preservadas.
"""

import argparse
import hashlib
import importlib.util
import json
import os
import struct
import sys

import mc3_v7_to_current as common


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def digest_city(pck, mesh):
    h = hashlib.sha256()
    for group in common.packet_entries_city(pck, mesh):
        for offset, qw, nv in group:
            h.update(struct.pack("<HH", qw, nv))
            h.update(pck.data[offset:offset + 16 * qw])
    return h.hexdigest()


def digest_mesh(path):
    h = hashlib.sha256()
    for group in common.packet_entries_mesh(path):
        for payload, qw, nv in group:
            h.update(struct.pack("<HH", qw, nv))
            h.update(payload)
    return h.hexdigest()


def distance(a, b):
    return sum((float(a[i]) - float(b[i])) ** 2 for i in range(3)) ** 0.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--forged", required=True)
    ap.add_argument("--reference", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--tools", default=os.environ.get('MC_RESEARCH_ROOT', ''))
    ap.add_argument("--output")
    ap.add_argument("--json")
    ap.add_argument("--tolerance", type=float, default=.002)
    args = ap.parse_args()

    mc2 = load("mc2_to_mc3", os.path.join(args.tools, "experimental", "mc2_to_mc3.py"))
    hf = load("mc3_hood_fill", os.path.join(args.tools, "mc3_hood_fill.py"))
    pck = mc2.Pck(args.base)
    original = bytes(pck.data)

    active = []
    for hood_index, hood in enumerate(hf.hoods(pck)):
        for unique_index, (_label, meshes, _component, cd) in enumerate(
                hf.uniques_do_hood(pck, hood_index)):
            centre = struct.unpack_from("<3f", pck.data, cd + 0x2C)
            for mesh in meshes:
                groups = common.packet_entries_city(pck, mesh)
                active.append({
                    "hood": hood[0], "unique": unique_index, "mesh": mesh,
                    "centre": centre, "groups": groups,
                    "shape": common.shape_city(groups),
                })

    items = json.load(open(args.report, encoding="utf-8"))["component_results"]
    chosen = []
    skipped = []
    occupied = set()
    forged_names = {name.lower(): name for name in os.listdir(args.forged)
                    if name.lower().endswith(".pck")}

    for item in items:
        filename = item["name"].lower() + ".mesh.pck"
        real_name = forged_names.get(filename)
        if not real_name:
            skipped.append({"name": filename, "reason": "no_forged_file"})
            continue
        forged_path = os.path.join(args.forged, real_name)
        replacement = common.packet_entries_mesh(forged_path)
        shape = common.shape_mesh(replacement)
        candidates = [obj for obj in active
                      if obj["shape"] == shape
                      and distance(obj["centre"], item["centre"]) < args.tolerance]
        reason = None
        if len(candidates) > 1:
            reference_path = os.path.join(args.reference, filename)
            if os.path.isfile(reference_path):
                old_digest = digest_mesh(reference_path)
                exact_old = [obj for obj in candidates
                             if digest_city(pck, obj["mesh"]) == old_digest]
                if len(exact_old) == 1:
                    candidates = exact_old
                else:
                    reason = "ambiguous_same_centre_shape"
            else:
                reason = "ambiguous_without_reference"
        elif not candidates:
            reason = "modern_shape_differs"
        if len(candidates) != 1:
            skipped.append({
                "name": filename, "reason": reason or "ambiguous",
                "candidate_count": len(candidates), "centre": item["centre"],
            })
            continue
        target = candidates[0]
        if target["mesh"] in occupied:
            skipped.append({"name": filename, "reason": "target_already_used",
                            "mesh": target["mesh"]})
            continue
        occupied.add(target["mesh"])
        chosen.append((filename, target, replacement))

    changed_ranges = []
    changed_bytes = 0
    unchanged_components = 0
    for filename, target, replacement in chosen:
        component_changed = False
        for current_group, replacement_group in zip(target["groups"], replacement):
            for (offset, qw, nv), (payload, rq, rn) in zip(
                    current_group, replacement_group):
                if (qw, nv) != (rq, rn):
                    raise AssertionError("shape inconsistente em " + filename)
                old = bytes(pck.data[offset:offset + 16 * qw])
                if old != payload:
                    component_changed = True
                    changed_bytes += sum(a != b for a, b in zip(old, payload))
                    changed_ranges.append((offset, offset + 16 * qw, filename))
                    pck.data[offset:offset + 16 * qw] = payload
        if not component_changed:
            unchanged_components += 1

    if len(pck.data) != len(original):
        raise AssertionError("tamanho do PCK mudou")
    allowed = bytearray(len(original))
    for start, end, _name in changed_ranges:
        allowed[start:end] = b"\x01" * (end - start)
    for offset, (before, after) in enumerate(zip(original, pck.data)):
        if before != after and not allowed[offset]:
            raise AssertionError("byte estrutural alterado em 0x%X" % offset)

    reasons = {}
    for item in skipped:
        reasons[item["reason"]] = reasons.get(item["reason"], 0) + 1
    result = {
        "base": os.path.abspath(args.base),
        "output": os.path.abspath(args.output) if args.output else None,
        "selected_components": len(chosen),
        "selected_but_identical": unchanged_components,
        "changed_packet_ranges": len(changed_ranges),
        "changed_bytes": changed_bytes,
        "skipped": skipped,
        "skip_reasons": reasons,
        "structural_bytes_changed": 0,
        "size_before": len(original),
        "size_after": len(pck.data),
    }
    print("selecionados:", len(chosen), "de", len(items))
    print("ja identicos:", unchanged_components)
    print("pacotes alterados:", len(changed_ranges), "bytes diferentes:", changed_bytes)
    print("preservados:", len(skipped), reasons)
    print("tamanho:", len(original), "->", len(pck.data), "; bytes estruturais alterados: 0")
    if args.output:
        with open(args.output, "wb") as stream:
            stream.write(pck.data)
        print("gravado:", os.path.abspath(args.output))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
