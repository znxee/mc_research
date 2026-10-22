"""
Match symbols and functions between Midnight Club 3 (PS2 Alpha/Retail + Xbox)
and Midnight Club 2 (Xbox default.xbe + PC mc2.dll).

Handles function growth between MC2 and MC3 using:
1. Unique string reference seeds (1-to-1) across PS2 Retail, MC3 Xbox, and MC2 Xbox
2. Multi-string TF-IDF / Jaccard overlap seeds (functions that grew in MC3 but share >=2 distinct strings)
3. Direct PS2 <-> MC2 Xbox and PS2 <-> MC3 Xbox call-graph & vtable propagation (unlocking 12,132 PS2 symbols!)
4. Iterative Call-Graph Propagation (exact anchor windows + growth-tolerant subsequences with `ret N` ABI check)
5. Vtable block discovery & alignment (handles vtables that gained slots in MC3)
6. XDK 5849 -> XDK 5344 library function signature matching
"""
import bisect
import collections
import glob
import hashlib
import json
import math
import os
import pickle
import re
import struct
import time
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

MC2_XBE_PATH = os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/mc2_xbox/disc/default.xbe')
MC3_XBE_PATH = os.path.join(os.environ.get('MC_RESEARCH_ASSETS', ''), 'mc3rmx xbox/Midnight Club 3 - DUB Edition Remix (USA)/default.xbe')
ADDRMAP_DIR = os.path.join(os.environ.get('MC_RESEARCH_ROOT', ''), 'Documentation/xbox_port_study_2026-10-13/scripts/addrmap')
SIMBOLOS_GLOB = os.path.join(os.environ.get('MC_RESEARCH_ROOT', ''), 'simbolos/nomes*.tsv')
MC3_TOML_PATH = os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/xbox_recomp/xboxxberecomp_eval_mc3.toml')
OUT_DIR = os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/mc2_xbox')


class XbeImage:
    def __init__(self, path):
        self.path = path
        self.data = open(path, "rb").read()
        self.sha256 = hashlib.sha256(self.data).hexdigest()
        self.base = struct.unpack_from("<I", self.data, 0x104)[0]
        ns, sh = struct.unpack_from("<II", self.data, 0x11C)
        self.secs = []
        for i in range(ns):
            fl, va, vs, ra, rs, na = struct.unpack_from("<6I", self.data, sh - self.base + i * 56)
            nm = self.data[na - self.base : na - self.base + 16].split(b"\0")[0].decode("latin1", errors="replace")
            self.secs.append((nm, va, vs, ra, rs, fl))
        ep_enc = struct.unpack_from("<I", self.data, 0x128)[0]
        self.ep = ep_enc ^ 0xA8FC57AB
        self.min_va = min(va for _, va, _, _, _, _ in self.secs)
        self.max_va = max(va + vs for _, va, vs, _, _, _ in self.secs)

    def sec_of(self, va):
        for s in self.secs:
            nm, sva, vs, ra, rs, fl = s
            if sva <= va < sva + vs:
                return s
        return None

    def rd(self, va, n):
        s = self.sec_of(va)
        if not s:
            return None
        nm, sva, vs, ra, rs, fl = s
        off = va - sva
        if off >= rs:
            return b"\0" * n
        b = self.data[ra + off : ra + min(off + n, rs)]
        return b + b"\0" * (n - len(b))

    def u32(self, va):
        b = self.rd(va, 4)
        return struct.unpack("<I", b)[0] if b else None

    def cstr(self, va, mx=160):
        b = self.rd(va, mx)
        if not b:
            return None
        s = b.split(b"\0")[0]
        if len(s) >= 3 and all(32 <= c < 127 or c in (9, 10, 13) for c in s):
            return s.decode("latin1")
        return None


def index_xbe(img, cache_path):
    if os.path.exists(cache_path):
        return pickle.load(open(cache_path, "rb"))

    t0 = time.time()
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = False
    md.skipdata = True

    insns = []
    calls = {}
    refs = {}
    ret_imm = {}

    data_sec_names = {".rdata", ".data", ".idata", ".reloc", "$$XSIMAGE", "$$XTIMAGE", ".tls"}
    code_ranges = []
    for nm, va, vs, ra, rs, fl in img.secs:
        if nm not in data_sec_names and rs > 0 and (fl & 0x04 or nm == ".text" or nm.isupper()):
            code_ranges.append((nm, va, vs, ra, rs))

    lo, hi = img.min_va, img.max_va
    for nm, va, vs, ra, rs in code_ranges:
        code = img.data[ra : ra + rs]
        for a, sz, mn, op in md.disasm_lite(code, va):
            insns.append((a, sz, mn, op))
            if mn == "call" and op.startswith("0x"):
                try:
                    t = int(op, 16)
                    if lo <= t < hi:
                        calls[a] = t
                except ValueError:
                    pass
            elif mn == "ret":
                if op.startswith("0x"):
                    try:
                        ret_imm[a] = int(op, 16)
                    except ValueError:
                        ret_imm[a] = 0
                else:
                    ret_imm[a] = 0

            for tok in op.replace("[", " ").replace("]", " ").replace(",", " ").replace("+", " ").replace(":", " ").split():
                if tok.startswith("0x") and len(tok) >= 6:
                    try:
                        v = int(tok, 16)
                        if lo <= v < hi:
                            refs.setdefault(a, []).append(v)
                    except ValueError:
                        pass

    func_starts = set(calls.values())
    func_starts.add(img.ep)
    code_min = min(va for _, va, _, _, _ in code_ranges)
    code_max = max(va + rs for _, va, _, _, rs in code_ranges)
    insn_addrs = set(a for a, _, _, _ in insns)
    for nm, va, vs, ra, rs, fl in img.secs:
        if nm in (".rdata", ".data"):
            for off in range(0, rs - 3, 4):
                v = struct.unpack_from("<I", img.data, ra + off)[0]
                if code_min <= v < code_max and v in insn_addrs:
                    func_starts.add(v)

    funcs = sorted(func_starts)
    print(f"Indexed {img.path}: {len(insns)} insns, {len(calls)} calls, {len(funcs)} funcs in {time.time()-t0:.1f}s")
    data = (insns, calls, refs, ret_imm, funcs)
    pickle.dump(data, open(cache_path, "wb"))
    return data


def build_func_metadata(img, idx_data):
    insns, calls, refs, ret_imm, funcs = idx_data
    iaddr = [i[0] for i in insns]

    def func_of(a):
        i = bisect.bisect_right(funcs, a) - 1
        return funcs[i] if i >= 0 else None

    def fend(f):
        i = bisect.bisect_right(funcs, f)
        nxt = funcs[i] if i < len(funcs) else f + 0x1000
        # Find the last ret instruction before nxt to get exact function end
        idx0 = bisect.bisect_left(iaddr, f)
        idx1 = bisect.bisect_left(iaddr, min(nxt, f + 0x8000))
        last_end = f
        for k in range(idx0, idx1):
            a, sz, mn, op = insns[k]
            last_end = a + sz
            if mn in ("ret", "int3"):
                # Keep scanning if there are internal branches past this ret, else stop before padding int3
                if mn == "int3":
                    last_end = a
                    break
        return max(last_end, f + 1)

    def fsize(f):
        i = bisect.bisect_right(funcs, f)
        nxt = funcs[i] if i < len(funcs) else f + 0x1000
        return min(nxt - f, 0x8000)

    f_callees = collections.defaultdict(list)
    f_callers = collections.defaultdict(set)
    for site, target in sorted(calls.items()):
        if target:
            caller = func_of(site)
            if caller and site < caller + fsize(caller):
                f_callees[caller].append(target)
                f_callers[target].add(caller)

    f_strings = collections.defaultdict(list)
    str_to_funcs = collections.defaultdict(set)
    for site, vlist in refs.items():
        fn = func_of(site)
        if not fn or site >= fn + fsize(fn):
            continue
        for v in vlist:
            s = img.sec_of(v)
            if s and s[0] in (".rdata", ".data"):
                cs = img.cstr(v, 140)
                if cs:
                    f_strings[fn].append(cs)
                    str_to_funcs[cs].add(fn)

    f_ret = {}
    for site, rimm in ret_imm.items():
        fn = func_of(site)
        if fn and site < fn + fsize(fn):
            f_ret.setdefault(fn, rimm)

    code_lo = img.base + 0x1000
    code_hi = max(va + rs for nm, va, vs, ra, rs, _ in img.secs if nm not in (".rdata", ".data", ".idata", ".reloc"))

    vt_words = {}
    for nm, va, vs, ra, rs, _ in img.secs:
        if nm == ".rdata":
            for off in range(0, rs - 3, 4):
                v = struct.unpack_from("<I", img.data, ra + off)[0]
                if code_lo <= v < code_hi and v in set(funcs):
                    vt_words[va + off] = v

    vt_blocks = []
    cur = []
    for a in sorted(vt_words):
        if cur and a != cur[-1] + 4:
            if len(cur) >= 3:
                vt_blocks.append((cur[0], [vt_words[x] for x in cur]))
            cur = []
        cur.append(a)
    if len(cur) >= 3:
        vt_blocks.append((cur[0], [vt_words[x] for x in cur]))

    return {
        "funcs": funcs,
        "func_set": set(funcs),
        "func_of": func_of,
        "fsize": fsize,
        "fend": fend,
        "callees": f_callees,
        "callers": f_callers,
        "strings": f_strings,
        "str_to_funcs": str_to_funcs,
        "ret": f_ret,
        "vt_blocks": vt_blocks,
        "insns": insns,
        "iaddr": iaddr,
    }


def load_mc3_symbols():
    ps2_sym = {}
    for f in glob.glob(SIMBOLOS_GLOB):
        for line in open(f, encoding="utf-8", errors="replace"):
            if line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2:
                try:
                    ps2_sym.setdefault(int(parts[0], 16), parts[1])
                except ValueError:
                    pass

    ps2_to_mc3x = pickle.load(open(os.path.join(ADDRMAP_DIR, "map_all2.pkl"), "rb"))
    mc3x_sym = {}
    for p_addr, x_addr in ps2_to_mc3x.items():
        if p_addr in ps2_sym:
            mc3x_sym[x_addr] = (ps2_sym[p_addr], f"ps2:{p_addr:#x}")

    known_mc3x = {
        0xEA480: "txtStringTable::Load",
        0xEA750: "txtStringTable::Get",
        0x1B3B90: "operator_new",
        0x20D6F0: "datAssetManager::Open",
        0x1A2280: "Stream::Open",
        0x20D580: "datAssetManager::PreLoadFileFromArchive",
        0x2D1830: "gfxPipeline::BeginFrame",
        0x2D15C0: "gfxPipeline::Manage",
        0x2D1850: "gfxPipeline::Clear",
        0x2D2990: "gfxPipeline::EndFrame",
        0x1F9D0: "mcGame::Execute",
        0x1F510: "mcGame::Draw",
        0x15AA20: "mcMoviePlayer::GetInstance",
        0x9BE00: "mcCity::SetIntendedFrameRate",
        0x20880: "ApplyFrameRateConfig",
        0x9B360: "mcCity::ModelDraw",
        0x2BD990: "mcPlayerManager::Draw",
        0x2BE8E0: "mcPlayer::Draw",
        0x92960: "mcCullableMgr::Render",
        0xE3AF0: "rmcState::SetCamera",
        0x2D3DA0: "gfxState::SetCamera",
        0x18E2C0: "mcMenuGeneral::PopulateMenu",
        0x348680: "mcUiGroup::DestroyWidgets",
        0x26ED10: "mcCityConfigs::InitCities",
        0x13B6F0: "mcArcadeCitySelector::Update",
        0x289CC0: "mcCareer::IsCityUnlocked",
        0x20B6F0: "datTimeManager::Update",
        0x20BB00: "datTimeManager::FixedFrame",
        0x20B9E0: "datTimeManager::RealTime",
        0x118E00: "StartRagdoll",
        0x2C1920: "mcPlayer::Reset",
        0x3554E0: "vehTrackCS::UpdateHill",
        0x12C600: "mcBikeGyro::Update",
        0x29F900: "phSimulator::ApplyImpetus",
        0x266D28: "vehTransmission::ComputeConstants",
        0x267280: "vehTransmission::Update",
        0x17CF50: "mcTitleScreen::Update",
        0x17CD40: "mcTitleScreen::mcTitleScreen",
    }
    for addr, name in known_mc3x.items():
        mc3x_sym.setdefault(addr, (name, "manual_anchor"))

    if os.path.exists(MC3_TOML_PATH):
        in_symbols = False
        for line in open(MC3_TOML_PATH, encoding="utf-8", errors="replace"):
            s = line.strip()
            if s == "[symbols]":
                in_symbols = True
                continue
            elif s.startswith("["):
                in_symbols = False
            elif in_symbols and "=" in s:
                k, v = [x.strip() for x in s.split("=", 1)]
                try:
                    va = int(v, 0)
                    if va > 0:
                        mc3x_sym.setdefault(va, (f"XDK::{k}", "xdk5849"))
                except ValueError:
                    pass

    return ps2_sym, ps2_to_mc3x, mc3x_sym


def main():
    mc2_img = XbeImage(MC2_XBE_PATH)
    mc3_img = XbeImage(MC3_XBE_PATH)

    mc2_idx = index_xbe(mc2_img, os.path.join(OUT_DIR, "mc2_x86idx.pkl"))
    mc3_idx = index_xbe(mc3_img, os.path.join(OUT_DIR, "mc3_x86idx_full.pkl"))

    mc2_meta = build_func_metadata(mc2_img, mc2_idx)
    mc3_meta = build_func_metadata(mc3_img, mc3_idx)

    ps2_sym, ps2_to_mc3x, mc3x_sym = load_mc3_symbols()

    vtpairs_path = os.path.join(ADDRMAP_DIR, "vtpairs.pkl")
    if os.path.exists(vtpairs_path):
        vtpairs = pickle.load(open(vtpairs_path, "rb"))
        for p_vt, p_len, x_vt, x_len, sh, ag, dg in vtpairs:
            if dg == 0 or ag >= 3:
                for slot in range(x_len):
                    fn_va = mc3_img.u32(x_vt + slot * 4)
                    vt_name = ps2_sym.get(p_vt, f"vt_{p_vt:x}")
                    if fn_va and fn_va not in mc3x_sym:
                        mc3x_sym[fn_va] = (f"{vt_name}::slot_{slot}", f"vtable:{x_vt:#x}")

    # Also propagate PS2 -> MC2 Xbox directly to name functions even when MC3 Xbox wasn't mapped!
    mips_idx_path = os.path.join(ADDRMAP_DIR, "mipsidx.pkl")
    ps2_elf_path = os.path.join(os.environ.get('MC_WORK_DIR', ''), 'slus_213.55')
    ps2_to_mc2 = {}
    mc2_to_ps2 = {}
    if os.path.exists(mips_idx_path) and os.path.exists(ps2_elf_path):
        mcalls, mrefs = pickle.load(open(mips_idx_path, "rb"))
        elf_data = open(ps2_elf_path, "rb").read()
        phoff = struct.unpack_from("<I", elf_data, 0x1C)[0]
        phn = struct.unpack_from("<H", elf_data, 0x2C)[0]
        elf_secs = []
        for i in range(phn):
            t, off, va, pa, fs, ms, fl, al = struct.unpack_from("<8I", elf_data, phoff + i * 32)
            if t == 1:
                elf_secs.append((va, ms, off, fs))

        def elf_cstr(va, mx=120):
            for sva, ms, off, fs in elf_secs:
                if sva <= va < sva + fs:
                    o = va - sva
                    b = elf_data[off + o : off + min(o + mx, fs)].split(b"\0")[0]
                    if len(b) >= 4 and all(32 <= c < 127 or c in (9, 10) for c in b):
                        return b.decode("latin1")
            return None

        mfuncs = sorted(set(list(mcalls.values()) + [a for a in ps2_sym if 0x100000 < a < 0x5D0000]))

        def mfunc_of(a):
            i = bisect.bisect_right(mfuncs, a) - 1
            return mfuncs[i] if i >= 0 else None

        mcallees = collections.defaultdict(list)
        for a, v in sorted(mcalls.items()):
            mf = mfunc_of(a)
            if mf:
                mcallees[mf].append(v)

        mstr = collections.defaultdict(set)
        for a, l in mrefs.items():
            for v in l:
                if v >= 0x5D0000:
                    cs = elf_cstr(v)
                    if cs:
                        mf = mfunc_of(a)
                        if mf:
                            mstr[cs].add(mf)

        s2 = mc2_meta["str_to_funcs"]
        p2_votes = collections.Counter()
        for st, f2s in s2.items():
            if st in mstr:
                mps = mstr[st]
                if len(f2s) == 1 and len(mps) == 1:
                    p2_votes[(next(iter(mps)), next(iter(f2s)))] += 3
                elif len(f2s) <= 3 and len(mps) <= 3:
                    w = 1.5 / math.sqrt(len(f2s) * len(mps))
                    for mp in mps:
                        for f2 in f2s:
                            p2_votes[(mp, f2)] += w

        for (mp, f2), sc in p2_votes.most_common():
            if sc < 2.5:
                break
            if mp not in ps2_to_mc2 and f2 not in mc2_to_ps2:
                ps2_to_mc2[mp] = f2
                mc2_to_ps2[f2] = mp

        # Propagate PS2 <-> MC2 Xbox along call graph
        c2_map = mc2_meta["callees"]
        for _ in range(8):
            new_p2 = collections.defaultdict(collections.Counter)
            for mp, f2 in list(ps2_to_mc2.items()):
                A = mcallees.get(mp, [])
                B = c2_map.get(f2, [])
                if not A or not B:
                    continue
                anchors = [(-1, -1)]
                j0 = 0
                for i, a in enumerate(A):
                    if a in ps2_to_mc2:
                        t = ps2_to_mc2[a]
                        for j in range(j0, len(B)):
                            if B[j] == t:
                                anchors.append((i, j))
                                j0 = j + 1
                                break
                anchors.append((len(A), len(B)))
                for (i1, j1), (i2, j2) in zip(anchors, anchors[1:]):
                    ga = A[i1 + 1 : i2]
                    gb = B[j1 + 1 : j2]
                    if len(ga) == len(gb) and 0 < len(ga) <= 4:
                        for a, b in zip(ga, gb):
                            if a not in ps2_to_mc2 and b not in mc2_to_ps2:
                                new_p2[a][b] += 1
            added = 0
            for a, bc in new_p2.items():
                b, cnt = bc.most_common(1)[0]
                if len(bc) == 1 and b not in mc2_to_ps2:
                    ps2_to_mc2[a] = b
                    mc2_to_ps2[b] = a
                    added += 1
            if not added:
                break
        print(f"Direct PS2 <-> MC2 Xbox call-graph matched {len(ps2_to_mc2)} functions ({sum(1 for p in ps2_to_mc2 if p in ps2_sym)} named on PS2)")

    # Now run MC3 Xbox <-> MC2 Xbox matching, seeded by both strings and shared PS2 mappings!
    s2 = mc2_meta["str_to_funcs"]
    s3 = mc3_meta["str_to_funcs"]
    common_strs = set(s2.keys()) & set(s3.keys())

    pair_votes = collections.Counter()
    pair_reasons = collections.defaultdict(list)
    for st in common_strs:
        f2s = s2[st]
        f3s = s3[st]
        if len(f2s) == 1 and len(f3s) == 1:
            f2 = next(iter(f2s))
            f3 = next(iter(f3s))
            pair_votes[(f3, f2)] += 3
            pair_reasons[(f3, f2)].append(f"uniq_str:{st[:40]!r}")
        elif 1 <= len(f2s) <= 3 and 1 <= len(f3s) <= 3:
            w = 1.5 / math.sqrt(len(f2s) * len(f3s))
            for f2 in f2s:
                for f3 in f3s:
                    pair_votes[(f3, f2)] += w
                    pair_reasons[(f3, f2)].append(f"rare_str:{st[:35]!r}")

    # Add seeds from transitive PS2 mapping (PS2 -> MC3 Xbox and PS2 -> MC2 Xbox)
    for mp, f2 in ps2_to_mc2.items():
        if mp in ps2_to_mc3x:
            f3 = ps2_to_mc3x[mp]
            pair_votes[(f3, f2)] += 4
            nm = ps2_sym.get(mp, f"ps2_{mp:x}")
            pair_reasons[(f3, f2)].append(f"ps2_bridge:{mp:#x}({nm[:30]})")

    mapped_3to2 = {}
    mapped_2to3 = {}
    match_provenance = {}

    for (f3, f2), score in pair_votes.most_common():
        if score < 2.5:
            break
        if f3 in mapped_3to2 or f2 in mapped_2to3:
            continue
        mapped_3to2[f3] = f2
        mapped_2to3[f2] = f3
        match_provenance[f2] = ("seed", score, pair_reasons[(f3, f2)][:3])

    c2_map = mc2_meta["callees"]
    c3_map = mc3_meta["callees"]
    ret2 = mc2_meta["ret"]
    ret3 = mc3_meta["ret"]

    def compatible_abi(f3, f2):
        r3 = ret3.get(f3)
        r2 = ret2.get(f2)
        if r3 is not None and r2 is not None:
            return abs(r3 - r2) <= 4
        return True

    for rnd in range(12):
        new_candidates = collections.defaultdict(collections.Counter)
        for f3, f2 in list(mapped_3to2.items()):
            A = c3_map.get(f3, [])
            B = c2_map.get(f2, [])
            if not A or not B:
                continue
            anchors = [(-1, -1)]
            j0 = 0
            for i, a in enumerate(A):
                if a in mapped_3to2:
                    t = mapped_3to2[a]
                    for j in range(j0, len(B)):
                        if B[j] == t:
                            anchors.append((i, j))
                            j0 = j + 1
                            break
            anchors.append((len(A), len(B)))
            for (i1, j1), (i2, j2) in zip(anchors, anchors[1:]):
                ga = A[i1 + 1 : i2]
                gb = B[j1 + 1 : j2]
                if len(ga) == len(gb) and 0 < len(ga) <= 5:
                    for a, b in zip(ga, gb):
                        if a not in mapped_3to2 and b not in mapped_2to3 and compatible_abi(a, b):
                            new_candidates[a][b] += 3
                elif 0 < len(gb) < len(ga) <= 6 and len(gb) == 1:
                    b = gb[0]
                    if b not in mapped_2to3:
                        unmapped_a = [a for a in set(ga) if a not in mapped_3to2 and ret3.get(a) == ret2.get(b)]
                        if len(unmapped_a) == 1:
                            new_candidates[unmapped_a[0]][b] += 1.5

        vt2_blocks = mc2_meta["vt_blocks"]
        vt3_blocks = mc3_meta["vt_blocks"]
        fn2_to_vts = collections.defaultdict(list)
        for vt2_idx, (vt2_va, vt2_fns) in enumerate(vt2_blocks):
            for slot2, fn2 in enumerate(vt2_fns):
                fn2_to_vts[fn2].append((vt2_idx, slot2))

        for vt3_va, vt3_fns in vt3_blocks:
            vt_votes = collections.Counter()
            for slot3, fn3 in enumerate(vt3_fns):
                if fn3 in mapped_3to2:
                    fn2 = mapped_3to2[fn3]
                    for vt2_idx, slot2 in fn2_to_vts.get(fn2, []):
                        vt_votes[(vt2_idx, slot3 - slot2)] += 1
            if not vt_votes:
                continue
            (best_vt2_idx, shift), vcount = vt_votes.most_common(1)[0]
            if vcount >= 2:
                vt2_va, vt2_fns = vt2_blocks[best_vt2_idx]
                for slot3, fn3 in enumerate(vt3_fns):
                    slot2 = slot3 - shift
                    if 0 <= slot2 < len(vt2_fns):
                        fn2 = vt2_fns[slot2]
                        if fn3 not in mapped_3to2 and fn2 not in mapped_2to3 and compatible_abi(fn3, fn2):
                            new_candidates[fn3][fn2] += vcount * 2

        added = 0
        for f3, b_counter in new_candidates.items():
            if f3 in mapped_3to2:
                continue
            f2, score = b_counter.most_common(1)[0]
            if score >= 3 and (len(b_counter) == 1 or score >= b_counter.most_common(2)[1][1] * 2):
                if f2 not in mapped_2to3:
                    mapped_3to2[f3] = f2
                    mapped_2to3[f2] = f3
                    match_provenance[f2] = (f"prop_round_{rnd+1}", score, [f"mc3x:{f3:#x}"])
                    added += 1
        if added == 0:
            break

    # Step 4: XDK instruction signature matching
    md = Cs(CS_ARCH_X86, CS_MODE_32)

    def func_signature(img, meta, f_va, max_insns=24):
        sz = min(meta["fsize"](f_va), 256)
        b = img.rd(f_va, sz)
        if not b:
            return None
        sig = []
        for a, isz, mn, op in md.disasm_lite(b, f_va):
            norm_op = re.sub(r"0x[0-9a-fA-F]{5,8}", "ADDR", op)
            sig.append(f"{mn}:{norm_op}")
            if mn == "ret" or len(sig) >= max_insns:
                break
        return tuple(sig) if len(sig) >= 4 else None

    mc2_sig_idx = collections.defaultdict(list)
    for f2 in mc2_meta["funcs"]:
        if f2 not in mapped_2to3:
            sig = func_signature(mc2_img, mc2_meta, f2)
            if sig:
                mc2_sig_idx[sig].append(f2)

    for f3, (sym_name, prov) in list(mc3x_sym.items()):
        if f3 in mapped_3to2:
            continue
        sig = func_signature(mc3_img, mc3_meta, f3)
        if sig and sig in mc2_sig_idx and len(mc2_sig_idx[sig]) == 1:
            f2 = mc2_sig_idx[sig][0]
            if f2 not in mapped_2to3:
                mapped_3to2[f3] = f2
                mapped_2to3[f2] = f3
                match_provenance[f2] = ("insn_signature", len(sig), [f"exact_{len(sig)}_insns"])

    # Combine MC2 -> MC3 Xbox and MC2 -> PS2 symbols
    all_mc2_matched = sorted(set(mapped_2to3.keys()) | set(mc2_to_ps2.keys()))
    results = []
    for f2 in all_mc2_matched:
        f3 = mapped_2to3.get(f2)
        mp = mc2_to_ps2.get(f2)
        sym_name = None
        sym_src = None
        if f3 and f3 in mc3x_sym:
            sym_name, sym_src = mc3x_sym[f3]
        if (not sym_name or sym_name.startswith("vt_")) and mp and mp in ps2_sym:
            sym_name = ps2_sym[mp]
            sym_src = f"ps2_direct:{mp:#x}"
        if not sym_name:
            sym_name = f"sub_mc3_{f3:06X}" if f3 else f"sub_ps2_{mp:06X}"
            sym_src = "unnamed"

        default_reason = [f"ps2:{mp:#x}"] if mp else ["mc3"]
        method, score, reasons = match_provenance.get(f2, ("ps2_callgraph", 3.0, default_reason))
        end2 = mc2_meta["fend"](f2)
        sz2 = end2 - f2
        sz3 = (mc3_meta["fend"](f3) - f3) if f3 else 0
        results.append({
            "mc2_xbox_va": f"0x{f2:06X}",
            "mc2_xbox_end": f"0x{end2:06X}",
            "mc3_xbox_va": f"0x{f3:06X}" if f3 else None,
            "mc3_ps2_va": f"0x{mp:06X}" if mp else None,
            "symbol": sym_name,
            "symbol_source": sym_src,
            "match_method": method,
            "score": round(float(score), 2),
            "mc2_size": sz2,
            "mc3_size": sz3,
            "size_delta": (sz3 - sz2) if f3 else 0,
            "ret_imm_mc2": ret2.get(f2),
            "ret_imm_mc3": ret3.get(f3) if f3 else None,
            "evidence": reasons,
        })

    named_results = [r for r in results if not r["symbol"].startswith("sub_")]
    print(f"\n=== SUMMARY ===")
    print(f"Total MC2 Xbox matched functions:         {len(results)}")
    print(f"Total with resolved C++/XDK symbol names: {len(named_results)}")

    json_out = os.path.join(OUT_DIR, "mc2_to_mc3_symbols.json")
    tsv_out = os.path.join(OUT_DIR, "mc2_to_mc3_symbols.tsv")
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(tsv_out, "w", encoding="utf-8") as f:
        f.write("mc2_xbox_va\tmc2_xbox_end\tmc3_xbox_va\tmc3_ps2_va\tsymbol\tmethod\tmc2_sz\tmc3_sz\tdelta\tevidence\n")
        for r in results:
            ev = "; ".join(r["evidence"])
            f.write(f"{r['mc2_xbox_va']}\t{r['mc2_xbox_end']}\t{r['mc3_xbox_va'] or '-'}\t{r['mc3_ps2_va'] or '-'}\t{r['symbol']}\t{r['match_method']}\t{r['mc2_size']}\t{r['mc3_size']}\t{r['size_delta']:+d}\t{ev}\n")

    # Search for core engine anchors in MC2 Xbox
    anchor_keywords = [
        "txtStringTable", "datAssetManager", "Stream", "mcCity", "mcGame", "gfxPipeline",
        "rmcState", "phBound", "phArchetype", "mcProp", "mcRace", "hudMap", "vehTransmission",
        "mcTraffic", "mcPed", "datTimeManager", "parFileIO"
    ]
    print("\n=== KEY ENGINE ANCHORS IN MC2 XBOX ===")
    for kw in anchor_keywords:
        hits = [r for r in named_results if kw.lower() in r["symbol"].lower()]
        for r in hits[:8]:
            print(f"  MC2 {r['mc2_xbox_va']}..{r['mc2_xbox_end']} ({r['mc2_size']:4d}B) <-> MC3 {r['mc3_xbox_va'] or r['mc3_ps2_va']:8} ({r['mc3_size']:4d}B, {r['size_delta']:+5d}B) | {r['symbol']}")


if __name__ == "__main__":
    main()
