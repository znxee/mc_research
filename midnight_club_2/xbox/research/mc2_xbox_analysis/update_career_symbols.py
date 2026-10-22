import json
from match_mc2_mc3_symbols import XbeImage, index_xbe, build_func_metadata, MC2_XBE_PATH, MC3_XBE_PATH

img2 = XbeImage(MC2_XBE_PATH)
idx2 = index_xbe(img2, "mc2_x86idx.pkl")
meta2 = build_func_metadata(img2, idx2)

img3 = XbeImage(MC3_XBE_PATH)
idx3 = index_xbe(img3, "mc3_x86idx_full.pkl")
meta3 = build_func_metadata(img3, idx3)

with open("mc2_to_mc3_symbols.json", "r", encoding="utf-8") as f:
    syms = json.load(f)

by_mc2 = {int(r["mc2_xbox_va"], 16): r for r in syms}

CAREER_EQUIVALENCES = [
    # 1. mcProgressManager (MC2) <-> mcPgCareer / mcPgFlow (MC3)
    (0x14FA80, 0x28C3E0, 0x4D3FD0, "mcProgressManager__InitUnlockingRules_void", "career_semantic_seed", "loads 'tune/unlockingrules.csv' <-> MC3 'tune/progress/unlockingrules.csv'"),
    (0x14FAF0, 0x278270, 0x4BFBD8, "mcProgressManager__SetupNextCareerRace_void", "career_semantic_seed", "error string 'mcProgressManager::SetupNextCareerRace()' <-> 'mcPgCareer::SetupNextCareerRace()'"),
    (0x14FCC0, 0x277EE0, 0x4BFDB0, "mcProgressManager__ReportRaceResult_int", "career_semantic_seed", "error string 'mcProgressManager::ReportRaceResult' <-> 'mcPgCareer::ReportRaceResult()'"),
    (0x14F770, 0x277CA0, 0x4C0708, "mcProgressManager__MarkRaceAsBeaten_int_int", "career_semantic_seed", "error string 'mcProgressManager::MarkRaceAsBeaten' <-> 'mcPgCareer::WinCurrentCareerRace'"),
    (0x14F300, 0x277530, 0x4C0880, "mcProgressManager__SetupCareerCruise_int", "career_semantic_seed", "sets up career cruise / 'moses_first_follow_ls' <-> 'mcPgCareer::SetupCareerCruise'"),
    (0x14F830, 0x277620, 0x4C0C78, "mcProgressManager__CheckAndRequestPreCityMovie_int", "career_callgraph", "checks -nomovies (0x14F670) and pre_city movie in mcCityData"),
    (0x14F8C0, 0x277760, 0x4C00C8, "mcProgressManager__CheckAndRequestPostRaceMovie_int_int", "career_callgraph", "checks -nomovies (0x14F670) and post_race / alt_post_race movie in mcCityData"),
    (0x14F9F0, 0x2774B0, 0x4C0C78, "mcProgressManager__CheckAndRequestPreRaceMovie_int_int", "career_callgraph", "checks -nomovies (0x14F670) and pre_race movie in mcCityData"),
    (0x14FC50, 0x277E20, 0x4C0400, "mcProgressManager__AdvanceHookmanProgress_void", "career_callgraph", "called by ReportRaceResult when career race/follow won"),
    (0x14EFF0, 0x27D350, 0x4C8990, "mcProgressManager__IsRaceBeaten_int_int_const", "career_callgraph", "queries bitfield/save state if race is beaten (used by CheckRule 'R')"),
    (0x14F140, 0x293EA0, 0x4D7A30, "mcProgressManager__GetHookmanState_int_int_const", "career_callgraph", "queries hookman progress state (used by CheckRule 'H' and 'HTCIO')"),
    (0x14F510, 0x293E40, 0x4C8D98, "mcProgressManager__MarkHookmanBeaten_int_int", "career_callgraph", "marks hookman beaten in current iteration & career"),
    (0x14F560, 0x276FC0, 0x4C0060, "mcProgressManager__SelectHookmanRaceFromFollow_int_int", "career_callgraph", "called by mcRaceHookmen when follow/cruise engages hookman"),
    (0x14F5F0, 0x277350, 0x4C02C0, "mcProgressManager__UpdateHookmanRacesCompleted_int_int", "career_callgraph", "checks if all races of current hookman are completed"),
    (0x14F670, None, None, "mcProgressManager__AreMoviesDisabled_void", "career_callgraph", "checks command-line param '-nomovies'"),
    (0x14F730, None, 0x4BF9E0, "mcProgressManager__ResetCareerIteration_void", "career_callgraph", "resets current career iteration hookman flags"),
    (0x14DD70, None, None, "mcConfig__ParseUnlockCommandLineParams_void", "career_semantic_seed", "parses -unlockall, -unlockraces, -unlockcities, -unlockvehicles, -unlockabilities"),
    (0x14DF10, None, None, "mcConfig__ParseStartupAndRaceCommandLineParams_void", "career_semantic_seed", "parses startup city/race/career flags and calls LoadCityData/LoadRaceInfo"),

    # 2. mcUnlocking (MC2) <-> mcPgUnlockingRulesEval (MC3)
    (0x153A30, 0x28C3E0, 0x4D3FD0, "mcUnlocking__LoadRules_char_const__ptr", "career_semantic_seed", "parses 'tune/unlockingrules.csv' with datCsvParser, calls ConvertRuleIdsToNumerical & BuildCondition"),
    (0x152210, 0x28B510, None, "mcUnlocking__ConvertRuleIdsToNumerical_char_const__ptr__char_const__ptr__int__ref__int__ref", "career_semantic_seed", "error string 'mcUnlocking::ConvertRuleIdsToNumerical: unhandled item type' <-> MC3 0x28B510 (+560B growth)"),
    (0x1520A0, 0x28B850, None, "mcUnlocking__BuildCondition_char_const__ptr__char_const__ptr__uint__ref", "career_semantic_seed", "error string 'mcUnlocking::BuildCondition: unhandled condition type' <-> MC3 0x28B850 (+704B growth)"),
    (0x152320, 0x28AE00, 0x4D50B0, "mcUnlocking__CheckRule_uint_const", "career_semantic_seed", "error string 'mcUnlocking::CheckRule: unhandled condition type' <-> MC3 CheckIfConditionIsMet (+80B growth)"),
    (0x1531B0, 0x28AFA0, None, "mcUnlocking__EvaluateUnlockRule_int_int_const", "career_callgraph", "binary searches RuleOrGroup (0x152B20) and evaluates conditions via CheckRule (0x152320)"),
    (0x153250, 0x28B0A0, None, "mcUnlocking__IsItemUnlocked_int_int_const", "career_callgraph", "wrapper around EvaluateUnlockRule (0x1531B0) for item type + id"),
    (0x153270, 0x28B100, None, "mcUnlocking__PackItemKey_int_int", "career_callgraph", "packs reward/condition type and id into 32-bit key"),
    (0x1532A0, 0x289E10, 0x4D4710, "mcUnlocking__IsNitroUnlockedForPlayer_void_const", "career_callgraph", "checks item type 3 (NITRO) via EvaluateUnlockRule"),
    (0x1532C0, 0x289D80, 0x4D4750, "mcUnlocking__IsSlipstreamTurboUnlocked_bool_const", "career_callgraph", "checks item type 4 (SST) for player/AI"),
    (0x153310, 0x289EF0, 0x4D4790, "mcUnlocking__IsBurnoutUnlocked_bool_const", "career_callgraph", "checks item type 5 (BO) for player/AI"),
    (0x153360, None, 0x4D47D0, "mcUnlocking__IsTwoWheelDrivingUnlocked_bool_const", "career_callgraph", "checks item type 6 (2WD) for player/AI"),
    (0x1533B0, None, 0x4D4810, "mcUnlocking__IsInAirControlUnlocked_bool_const", "career_callgraph", "checks item type 7 (IAC) for player/AI"),
    (0x153400, 0x289CC0, 0x4D42B0, "mcUnlocking__IsCityUnlocked_int_const", "career_callgraph", "checks item type 2 (City) via IsItemUnlocked (0x153250)"),
    (0x153440, None, 0x4D4550, "mcUnlocking__IsVehicleUnlocked_int_const", "career_callgraph", "checks item type 0 (Vehicle) via IsItemUnlocked (0x153250)"),
    (0x153480, None, None, "mcUnlocking__IsHookmanUnlocked_int_int_const", "career_callgraph", "checks item type 1 (Hookman) via IsItemUnlocked (0x153250)"),
    (0x153570, 0x28BC80, None, "mcUnlocking__FinalizeAndSortRuleTables_void", "career_callgraph", "sorts RuleOrGroup tables after parsing unlockingrules.csv"),

    # 3. mcCityData Career/Hookman/Loc Loader (MC2) <-> mc::mcCityData & mc::mcHookmanData (MC3)
    (0x150AA0, 0x26F010, 0x4B7C38, "mc__mcCityData__LoadLocAndLocInfData_datAsciiTokenizer__ref__datAsciiTokenizer__ref", "career_semantic_seed", "parses .loc ('numhookmen', 'hookman', 'numraces', 'arcade', 'battle_modes') and .locinf ('AmbientDensity:', 'ForcedVehicle:'); split in MC3 into LoadRaceData (0x26F010), LoadHookmenData (0x26EB80), LoadRaceDataFromLocInfFile (0x26DA70)"),
    (0x14FF10, 0x26DA10, 0x4B7B20, "mc__mcCityData__LookupHookmanRace_char_const__ptr__int", "career_semantic_seed", "error string \"mcCityData::LookupHookmanRace - failed to find '%s' in hookman %d\""),
    (0x1503B0, None, None, "mc__LookupCar_char_const__ptr", "career_semantic_seed", "error string 'mcConfig::LookupCar() failed - %s'"),
    (0x1504F0, None, 0x4B96F0, "mc__LookupHookman_char_const__ptr__int__ref__int__ref", "career_callgraph", "looks up hookman name across cities (called by mcUnlocking::BuildCondition)"),
    (0x150FA0, None, None, "mc__LookupRaceAcrossCities_char_const__ptr__int__ref__int__ref", "career_callgraph", "looks up race name across cities (called by mcUnlocking::BuildCondition)"),

    # 4. mcRaceHookmen & Cruise/Follow Mode (MC2) <-> mcRaceHookmen (MC3)
    (0x0ADDA0, 0x1D7AB0, 0x3E8248, "mcRaceHookmen__PostLevelLoad_void", "career_callgraph", "initializes hookman cruise/follow icons and subraces"),
    (0x0AE2C0, 0x1D75A0, 0x3E7660, "mcRaceHookmen__DisplayHookmanMessage_int_aiOpponent_const__ptr__int", "career_callgraph", "displays hookman challenge/follow message on HUD"),
    (0x0AE500, 0x1D7780, 0x3E7C58, "mcRaceHookmen__PlayerFinishedFollow_void", "career_semantic_seed", "string 'Follow Completed', reports follow win to mcProgressManager"),
    (0x0AEA80, 0x1D6D70, 0x3E8248, "mcRaceHookmen__LoadAllHookmanSubRaces_void", "career_callgraph", "loads hookman patrol/follow/subraces for current city"),
    (0x0AEEF0, 0x1D7C00, 0x3E7588, "mcRaceHookmen__Update_void", "career_callgraph", "updates roaming hookman engagement, follow distance, and triggers PlayerFinishedFollow / RestartCruise"),
    (0x0AF2F0, 0x1D6D70, 0x3E8710, "mcRaceHookmen__Load_char_const__ptr__char_const__ptr", "career_semantic_seed", "strings 'hud_flash_lights', 'gina_tokyo', 'gina', 'moses', calls LoadAllHookmanSubRaces"),
    (0x0A34F0, 0x1D4F20, 0x3D4A20, "mcRaceBase__LoadHookmanAndRaceHeader_datAsciiTokenizer__ref", "career_semantic_seed", "parses 'racetype', 'RaceStartTime', 'ActualHookman', 'BreakinHookman', 'NumOfLaps', 'RaceDensity' (merged into mcRaceBase::Load in MC3)"),
    (0x09AB90, None, None, "mcHud__ShowFindHookmanPrompt_void", "career_semantic_seed", "string 'HM_FIND_HOOKMAN'"),
    (0x09DAE0, 0x1A1760, 0x3DDA08, "mcRaceOver__CheckAndShowUnlockedCar_void", "career_semantic_seed", "strings 'you_unlock_car', 'SS_%s'"),
    (0x09DC60, 0x1A1760, 0x3DDA08, "mcRaceOver__CheckAndShowUnlockedAbilities_void", "career_semantic_seed", "strings 'Unlock_Slipstream', 'Unlock_Burnout', 'Unlock_InAirControls', 'Unlock_TwoWheelDriving', 'Unlock_Nitro', 'you_unlock_ability'"),
    (0x0983AC, 0x16B51E, 0x34FFD0, "mcMenuRaceOver__HandleCareerAndCruiseSelection_int", "career_semantic_seed", "strings 'ContinueCareerNewCar', 'ContinueCareer', 'RestartCruise', 'NextRace'"),

    # 5. aiBrainHookman (MC2) <-> aiBrainHookman (MC3)
    (0x0C7370, 0x1EB540, 0x3FDE28, "aiBrainHookman__PreUpdate_void", "career_callgraph", "hookman AI pre-update on patrol route"),
    (0x0C73FE, 0x1EBA20, 0x3FDDC8, "aiBrainHookman__Update_void", "career_callgraph", "hookman AI main update: patrol route driving, high-beam flick detection, follow lead"),
    (0x0C77A0, 0x1EC140, 0x3FE580, "aiBrainHookman__RestartCruise_void", "career_semantic_seed", "strings 'c after restart cruise', 'd after restart cruise' <-> aiBrainHookman::RestartCruise"),
    (0x0C7940, 0x1EC250, 0x3FE810, "aiBrainHookman__IsEngagedAndReadyForRace_void_const", "career_callgraph", "called by mcRaceHookmen::Update (0x0AEEF0) to check hookman engagement"),
]

added_or_updated = 0
for mc2_va, mc3_xva, mc3_ps2_va, sym_name, method, ev_note in CAREER_EQUIVALENCES:
    sz2 = meta2["fsize"](mc2_va)
    end2 = meta2["fend"](mc2_va)
    sz3 = meta3["fsize"](mc3_xva) if mc3_xva and mc3_xva in meta3["func_set"] else None
    delta = (sz3 - sz2) if sz3 is not None else None
    entry = {
        "mc2_xbox_va": f"0x{mc2_va:06X}",
        "mc2_xbox_end": f"0x{end2:06X}",
        "mc3_xbox_va": f"0x{mc3_xva:06X}" if mc3_xva else None,
        "mc3_ps2_va": f"0x{mc3_ps2_va:06X}" if mc3_ps2_va else None,
        "symbol": sym_name,
        "symbol_source": f"ps2:0x{mc3_ps2_va:06x}" if mc3_ps2_va else "mc2_career_analysis",
        "match_method": method,
        "score": 15.0,
        "mc2_size": sz2,
        "mc3_size": sz3,
        "size_delta": delta,
        "ret_imm_mc2": meta2["ret"].get(mc2_va),
        "ret_imm_mc3": meta3["ret"].get(mc3_xva) if mc3_xva else None,
        "evidence": [ev_note],
    }
    by_mc2[mc2_va] = entry
    added_or_updated += 1

all_syms = [by_mc2[k] for k in sorted(by_mc2)]
with open("mc2_to_mc3_symbols.json", "w", encoding="utf-8") as f:
    json.dump(all_syms, f, indent=2)

with open("mc2_to_mc3_symbols.tsv", "w", encoding="utf-8") as f:
    f.write("mc2_xbox_va\tmc2_xbox_end\tmc3_xbox_va\tmc3_ps2_va\tsymbol\tmatch_method\tmc2_size\tmc3_size\tsize_delta\tevidence\n")
    for r in all_syms:
        f.write(
            f"{r['mc2_xbox_va']}\t{r['mc2_xbox_end']}\t{r['mc3_xbox_va'] or ''}\t{r['mc3_ps2_va'] or ''}\t"
            f"{r['symbol']}\t{r['match_method']}\t{r['mc2_size']}\t{r['mc3_size'] or ''}\t{r['size_delta'] if r['size_delta'] is not None else ''}\t"
            f"{'; '.join(r.get('evidence', []))}\n"
        )

named = sum(1 for r in all_syms if not r["symbol"].startswith("sub_"))
print(f"Updated mc2_to_mc3_symbols.json: total={len(all_syms)}, named={named} (+{added_or_updated} Career Mode symbols)")
