"""
Build flat XBE image for MC2 Xbox (`default.xbe`), run IDA Pro 9.0 headless (32-bit metapc + Hex-Rays x86)
to decompile key functions across all porting subsystems, and export `ida_flat/capture.json` + `ida_flat/sections.json`
for REA 6.4.0 organization.
"""
import hashlib
import json
import os
import struct
import subprocess
from pathlib import Path
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

MC2_XBE = Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/mc2_xbox/disc/default.xbe'))
SYMBOLS_JSON = Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/mc2_xbox/mc2_to_mc3_symbols.json'))
IDA_DIR = Path(os.environ.get('IDA_DIR', ''))
WORK_DIR = Path(os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/mc2_xbox/ida_flat'))


def build_flat_image():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    data = MC2_XBE.read_bytes()
    xbe_sha256 = hashlib.sha256(data).hexdigest()

    base = struct.unpack_from("<I", data, 0x104)[0]
    hdr_sz = struct.unpack_from("<I", data, 0x108)[0]
    img_sz = struct.unpack_from("<I", data, 0x10C)[0]
    ns, sh = struct.unpack_from("<II", data, 0x11C)
    ep_enc = struct.unpack_from("<I", data, 0x128)[0]
    ep = ep_enc ^ 0xA8FC57AB

    flat = bytearray(img_sz)

    sections = []
    for i in range(ns):
        fl, va, vs, ra, rs, na = struct.unpack_from("<6I", data, sh - base + i * 56)
        nm = data[na - base : na - base + 16].split(b"\0")[0].decode("latin1", errors="replace")
        img_off = va - base
        copy_len = min(rs, vs, max(0, img_sz - img_off))
        if copy_len > 0 and ra + copy_len <= len(data):
            flat[img_off : img_off + copy_len] = data[ra : ra + copy_len]
        sections.append({
            "name": nm,
            "virtual_addr": f"0x{va:08X}",
            "virtual_size": vs,
            "raw_addr": f"0x{ra:08X}",
            "raw_size": rs,
            "flags": fl,
            "executable": bool(fl & 0x04),
            "writable": bool(fl & 0x01),
            "image_offset": f"0x{img_off:08X}",
        })

    flat_path = WORK_DIR / "mc2_xbe_flat.bin"
    for old_db in WORK_DIR.glob("mc2_xbe_flat*"):
        if old_db != flat_path:
            old_db.unlink()
    flat_path.write_bytes(flat)

    sec_meta = {
        "xbe_path": str(MC2_XBE),
        "xbe_sha256": xbe_sha256,
        "base_address": f"0x{base:08X}",
        "entry_point": f"0x{ep:08X}",
        "image_size": img_sz,
        "image_size_hex": f"0x{img_sz:08X}",
        "flat_image": str(flat_path),
        "language_id": "x86:LE:32:default",
        "compiler_spec": "windows",
        "sections": sections,
    }
    (WORK_DIR / "sections.json").write_text(json.dumps(sec_meta, indent=2), encoding="utf-8")
    return data, base, sections


def find_clean_func_end(code_bytes, start_va, max_len=4096, xbe_bytes=None, sections=None):
    """Find exact instruction-aligned end of an MSVC x86 function, resolving switch jump tables in .rdata."""
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    last_end = start_va
    max_branch = start_va

    def rd_u32(va):
        if not xbe_bytes or not sections:
            return None
        for s in sections:
            sva = int(s["virtual_addr"], 16)
            rs = s["raw_size"]
            if sva <= va <= sva + rs - 4:
                ra = int(s["raw_addr"], 16)
                off = ra + (va - sva)
                return struct.unpack_from("<I", xbe_bytes, off)[0]
        return None

    for a, sz, mn, op in md.disasm_lite(code_bytes[:max_len], start_va):
        if mn == "int3":
            if a >= max_branch:
                return a if a > start_va else last_end
            continue
        last_end = a + sz
        if mn.startswith("j") and mn != "jmp" and op.startswith("0x"):
            try:
                t = int(op, 16)
                if start_va < t < start_va + max_len:
                    max_branch = max(max_branch, t)
            except ValueError:
                pass
        elif mn == "jmp":
            if op.startswith("0x"):
                try:
                    t = int(op, 16)
                    if start_va <= t < start_va + max_len:
                        max_branch = max(max_branch, t)
                    elif a >= max_branch:
                        return last_end
                except ValueError:
                    if a >= max_branch:
                        return last_end
            else:
                # Indirect jump through switch table: extract table address 0xXXXXXX
                for tok in op.replace("[", " ").replace("]", " ").replace("+", " ").replace("*", " ").split():
                    if tok.startswith("0x") and len(tok) >= 7:
                        try:
                            tbl_va = int(tok, 16)
                            for k in range(64):
                                target_va = rd_u32(tbl_va + k * 4)
                                if target_va and start_va < target_va < start_va + max_len:
                                    max_branch = max(max_branch, target_va)
                                else:
                                    break
                        except ValueError:
                            pass
        elif mn == "ret":
            if a >= max_branch:
                return last_end
    return last_end


def select_target_functions(xbe_bytes, base, sections):
    syms = json.loads(SYMBOLS_JSON.read_text(encoding="utf-8"))
    # Select representative functions across key subsystems for porting MC2 -> MC3
    priority_Substrings = [
        "Main_void",
        "mc__mcCityData__mcCityData",
        "mcCity__InitGlobalLighting",
        "mcCityModelInfo__Load",
        "mcCityEnvMap__LoadCondition",
        "mcPropType__LoadTuneData",
        "mcPropType__LoadTypeData",
        "phArchetype__LoadData",
        "phArchetypePhys__LoadData",
        "mcArchetypeBreak__LoadData",
        "mcTrainManager__LoadCityTrains",
        "mcRaceConfig__SetCity",
        "mcLayerRace__Load",
        "mcRaceBase__LoadResetPosition",
        "mcRaceBase__LoadWeather",
        "mcRaceBase__LoadHelicopters",
        "mcRaceBase__LoadOpponentCarAiInfo",
        "mcRaceAmbient__LoadProperties",
        "mcHeliRace__LoadProperties",
        "hudMapLocal__SharedDataLocalMap__TextureData__FileIO",
        "mcPlayerCamera__InitCameras",
        "mcReplayCamera__Init",
        "mcCarParticlesManager__mcCarParticlesManager",
        "mcCarModEngine__FileIO",
        "mcCarDamageTune__GetTypeName",
        "mcCarModelTune__GetTypeName",
        "mcMoviePlayer__Play",
        "mcMenuGeneral__PopulateMenu",
        "mcMenuHud__PopulateMenu",
        "mcMenuShell__ChangeState",
        "parFileIO__FileIO",
        "txtFontTex__SetBilinear",
        "mcLightning__initStaticData",
        "mcSpotlightTuneParams__FileIO",
        "lightGlowCondition__FileIO",
        "mcAudioCityWalla",
        "txtStringTable__Load",
        "txtStringTable__Get",
        "datAssetManager__SetPath",
        "datAssetManager__Open",
        "sndBank__AddStream",
        "crSkeletonData__Load",
        "gfxPipeline__BeginFrame",
        "gfxPipeline__Clear",
        "gfxPipeline__EndFrame",
        "gfxPipeline__SetViewport",
        "phBound__Load",
        "phArchetypeMgr__RegisterArchetype",
        "phArchetypeMgr__PostLoadCompute",
        "hudMap__Init",
        "hudMapLocal__Init",
        "hudMapGlobal__SharedDataGlobalMap__FileIO",
        "mcRaceBase__LoadOpponentPersonality",
        "mcRaceBase__LoadAmbientRoadOverride",
        "mcRaceBase__LoadClosedRoads",
        # Career Mode, ProgressManager, Unlocking, Hookmen & Roaming AI
        "mcProgressManager__InitUnlockingRules",
        "mcProgressManager__SetupNextCareerRace",
        "mcProgressManager__ReportRaceResult",
        "mcProgressManager__MarkRaceAsBeaten",
        "mcProgressManager__SetupCareerCruise",
        "mcProgressManager__CheckAndRequestPreCityMovie",
        "mcProgressManager__CheckAndRequestPostRaceMovie",
        "mcProgressManager__CheckAndRequestPreRaceMovie",
        "mcProgressManager__AdvanceHookmanProgress",
        "mcProgressManager__IsRaceBeaten",
        "mcProgressManager__GetHookmanState",
        "mcProgressManager__MarkHookmanBeaten",
        "mcProgressManager__SelectHookmanRaceFromFollow",
        "mcProgressManager__UpdateHookmanRacesCompleted",
        "mcConfig__ParseUnlockCommandLineParams",
        "mcUnlocking__LoadRules",
        "mcUnlocking__ConvertRuleIdsToNumerical",
        "mcUnlocking__BuildCondition",
        "mcUnlocking__CheckRule",
        "mcUnlocking__EvaluateUnlockRule",
        "mcUnlocking__IsItemUnlocked",
        "mcUnlocking__IsNitroUnlockedForPlayer",
        "mcUnlocking__IsSlipstreamTurboUnlocked",
        "mcUnlocking__IsBurnoutUnlocked",
        "mcUnlocking__IsTwoWheelDrivingUnlocked",
        "mcUnlocking__IsInAirControlUnlocked",
        "mcUnlocking__IsCityUnlocked",
        "mcUnlocking__IsVehicleUnlocked",
        "mcUnlocking__IsHookmanUnlocked",
        "mc__mcCityData__LoadLocAndLocInfData",
        "mc__mcCityData__LoadMovieData",
        "mc__mcCityData__LookupHookmanRace",
        "mc__LoadCityData_char_const",
        "mc__LoadCityData_datAsciiTokenizer",
        "mc__LookupHookman",
        "mcRaceConfig__LoadInfo",
        "mcRaceConfig__LoadRaceInfo",
        "mcRaceHookmen__PostLevelLoad",
        "mcRaceHookmen__DisplayHookmanMessage",
        "mcRaceHookmen__PlayerFinishedFollow",
        "mcRaceHookmen__LoadAllHookmanSubRaces",
        "mcRaceHookmen__Update",
        "mcRaceHookmen__Load_char_const",
        "mcRaceBase__LoadHookmanAndRaceHeader",
        "mcRaceBase__LoadOpponents",
        "mcRaceBase__Load_datAsciiTokenizer",
        "mcRaceCheckpoint__PlayerFinished",
        "mcHud__ShowFindHookmanPrompt",
        "mcRaceOver__CheckAndShowUnlockedCar",
        "mcRaceOver__CheckAndShowUnlockedAbilities",
        "mcMenuRaceOver__PopulateMenu",
        "mcMenuRaceOver__HandleCareerAndCruiseSelection",
        "aiBrainHookman__PreUpdate",
        "aiBrainHookman__Update_void",
        "aiBrainHookman__RestartCruise",
        "aiBrainHookman__IsEngagedAndReadyForRace",
    ]

    selected = []
    seen_va = set()

    def sec_for_va(va):
        for s in sections:
            sva = int(s["virtual_addr"], 16)
            rs = s["raw_size"]
            if sva <= va < sva + rs:
                return s
        return None

    for r in syms:
        sym = r["symbol"]
        if any(p.lower() in sym.lower() for p in priority_Substrings):
            va = int(r["mc2_xbox_va"], 16)
            if va in seen_va:
                continue
            s = sec_for_va(va)
            if not s:
                continue
            ra = int(s["raw_addr"], 16)
            sva = int(s["virtual_addr"], 16)
            off = ra + (va - sva)
            end_va = find_clean_func_end(xbe_bytes[off : off + 4096], va, max_len=4096, xbe_bytes=xbe_bytes, sections=sections)
            if end_va > va + 4:
                seen_va.add(va)
                r_copy = dict(r)
                r_copy["mc2_xbox_va_int"] = va
                r_copy["mc2_xbox_end_int"] = end_va
                r_copy["mc2_xbox_end"] = f"0x{end_va:06X}"
                selected.append(r_copy)

    selected.sort(key=lambda x: x["mc2_xbox_va_int"])
    # Ensure no two selected ranges overlap and trim trailing 0xCC (int3) padding
    for i in range(len(selected) - 1):
        if selected[i]["mc2_xbox_end_int"] > selected[i + 1]["mc2_xbox_va_int"]:
            va = selected[i]["mc2_xbox_va_int"]
            s = sec_for_va(va)
            ra = int(s["raw_addr"], 16)
            sva = int(s["virtual_addr"], 16)
            limit_va = selected[i + 1]["mc2_xbox_va_int"]
            while limit_va > va + 4 and xbe_bytes[ra + (limit_va - 1 - sva)] == 0xCC:
                limit_va -= 1
            selected[i]["mc2_xbox_end_int"] = limit_va
            selected[i]["mc2_xbox_end"] = f"0x{limit_va:06X}"
    return selected


IDA_SCRIPT_TEMPLATE = r'''
import ida_auto, ida_bytes, ida_funcs, ida_ida, ida_hexrays, ida_name, ida_segment, ida_ua, idc, json, hashlib, traceback

ida_auto.enable_auto(True)

out = {"processor": ida_ida.inf_get_procname(), "functions": []}
try:
    s = ida_segment.get_first_seg()
    out["initial_base"] = 0x10000
    out["bitness"] = ida_ida.inf_get_app_bitness()
    out["base"] = 0x10000
    out["hexrays"] = bool(ida_hexrays.init_hexrays_plugin())

    # Apply symbol names to all matched functions first so Hex-Rays pseudocode uses real C++ names!
    for va, sym_name in @ALL_NAMES@:
        clean_name = "".join(c if c.isalnum() or c == "_" else "_" for c in sym_name)
        ida_name.set_name(va, clean_name, ida_name.SN_NOWARN | ida_name.SN_NOCHECK)

    for a, b, sym_name in @RANGES@:
        ida_auto.plan_range(a, b)
        ida_auto.auto_make_proc(a)
    ida_auto.auto_wait()

    for a, b, sym_name in @RANGES@:
        f_obj = ida_funcs.get_func(a)
        if not f_obj or f_obj.start_ea != a:
            if f_obj:
                ida_funcs.del_func(f_obj.start_ea)
            ida_ua.create_insn(a)
            ida_funcs.add_func(a, b)
            ida_auto.auto_wait()
            f_obj = ida_funcs.get_func(a)
            if not f_obj:
                ida_funcs.add_func(a)
                ida_auto.auto_wait()
                f_obj = ida_funcs.get_func(a)
        b_actual = f_obj.end_ea if (f_obj and f_obj.start_ea == a and f_obj.end_ea > a) else b
        if b_actual <= a:
            b_actual = b
        clean_name = "".join(c if c.isalnum() or c == "_" else "_" for c in sym_name)
        ida_name.set_name(a, clean_name, ida_name.SN_NOWARN | ida_name.SN_NOCHECK)
        if out["hexrays"]:
            ida_hexrays.mark_cfunc_dirty(a, False)
        ins = []
        ea = a
        while ea < b_actual:
            ins.append({"address": hex(ea), "text": idc.generate_disasm_line(ea, 0)})
            step = ida_bytes.get_item_size(ea)
            ea += step if step > 0 else 1
        raw_bytes = ida_bytes.get_bytes(a, b_actual - a)
        f = {
            "address": hex(a),
            "end": hex(b_actual),
            "symbol": sym_name,
            "instructions": ins,
            "bytes_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        }
        try:
            cfunc = ida_hexrays.decompile(a) if out["hexrays"] else None
            f["pseudocode"] = str(cfunc) if cfunc is not None else None
        except Exception as e:
            f["pseudocode"] = None
            f["decompile_error"] = str(e)
        out["functions"].append(f)
except Exception:
    out["error"] = traceback.format_exc()

with open(@OUTPUT@, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)
idc.qexit(0)
'''


def main():
    print("Building flat XBE image for IDA...")
    xbe_bytes, base, sections = build_flat_image()
    selected = select_target_functions(xbe_bytes, base, sections)
    print(f"Selected {len(selected)} key porting functions for IDA Hex-Rays decompilation")

    all_syms = json.loads(SYMBOLS_JSON.read_text(encoding="utf-8"))
    all_names = [
        (int(r["mc2_xbox_va"], 16), r["symbol"])
        for r in all_syms
        if not r["symbol"].startswith("sub_")
    ]
    ranges = [(r["mc2_xbox_va_int"], r["mc2_xbox_end_int"], r["symbol"]) for r in selected]

    script_path = WORK_DIR / "capture_mc2.py"
    output_path = WORK_DIR / "capture.json"
    log_path = WORK_DIR / "capture.log"
    xbe_copy = WORK_DIR / "mc2_default.xbe"
    for old_db in WORK_DIR.glob("mc2_default*"):
        old_db.unlink()
    xbe_copy.write_bytes(xbe_bytes)
    if log_path.exists():
        log_path.unlink()

    script_code = (
        IDA_SCRIPT_TEMPLATE
        .replace("@ALL_NAMES@", repr(all_names))
        .replace("@RANGES@", repr(ranges))
        .replace("@OUTPUT@", repr(str(output_path)))
    )
    script_path.write_text(script_code, encoding="utf-8")

    idat_exe = IDA_DIR / "idat.exe"
    if not idat_exe.exists():
        idat_exe = IDA_DIR / "idat64.exe"

    print(f"Running IDA headless ({idat_exe.name}) with Hex-Rays x86...")
    cmd = [
        str(idat_exe),
        "-A",
        "-a",
        f"-L{log_path}",
        f"-S{script_path}",
        str(xbe_copy),
    ]
    res = subprocess.run(cmd, timeout=240, capture_output=True)
    if res.returncode != 0:
        print(f"IDA exited with code {res.returncode}")
    if not output_path.exists():
        raise RuntimeError(f"capture.json was not created. Check {log_path}")

    cap = json.loads(output_path.read_text(encoding="utf-8"))
    if cap.get("error"):
        print("IDA script error:", cap["error"])
    funcs = cap.get("functions", [])
    decompiled_cnt = sum(1 for fn in funcs if fn.get("pseudocode"))
    print(f"IDA capture complete: {len(funcs)} functions captured, {decompiled_cnt} with Hex-Rays C++ pseudocode!")


if __name__ == "__main__":
    main()
