# MC2 career xboxrecomp oracle

This directory is an independent CPU-side oracle for the MC2 career port. It
uses the original Xbox `default.xbe` and the title-agnostic disassembler from
`sp00nznet/xboxrecomp`; it does not substitute MC3 assets or execute MC2 code in
the MC3 process.

The full `.text` scan found 15,683 functions and 915,096 instructions. Run
`extract_selected.py` after regenerating `disasm/` to produce the small,
reviewable `selected_career_functions.asm` and its provenance manifest.

The selected set covers the state transition authority and the natural
Hookman path:

- `0x0C73FE` — `aiBrainHookman::Update`
- `0x14F300` — `mcProgressManager::SetupCareerCruise`
- `0x14F560` — `mcProgressManager::SelectHookmanRaceFromFollow`
- `0x14F8C0` — `mcProgressManager::CheckAndRequestPostRaceMovie`
- `0x14FAF0` — `mcProgressManager::SetupNextCareerRace`
- `0x14FC50` — `mcProgressManager::AdvanceHookmanProgress`
- `0x14FCC0` — `mcProgressManager::ReportRaceResult`

xboxrecomp currently owns `0x0C73FE` under the larger detected range beginning
at `0x0C7370`; IDA separates `PreUpdate` and `Update` at `0x0C73FE`. Keep the
IDA boundary for semantic hooks and use the xboxrecomp range to audit the full
fall-through/control-flow owner. The other six selected starts were detected
exactly by both tools.

Use the extracted instructions to settle control-flow, field-offset, and
result-code disagreements. Use the existing IDA/REA dossier for semantic names
and readable pseudocode. A full MC2 executable is unnecessary for those
questions and would add unrelated D3D/audio/kernel bring-up work.

## Confirmed natural Hookman gate

`aiBrainHookman::Update` compares the horizontal distance against the float at
XBE VA `0x34E28C` (`50.0f`) and the absolute height difference against the
float at `0x34E290` (`5.0f`). The Xbox action is the left-thumb click; the MC3
runtime also maps keyboard `F` to that pad bit for debugging.

In the current MC3 recomp, the wrapper at `0x001EBA20` is not dispatched often
enough during career cruise to own the observer tick. The host view callback is
the validated per-frame source; the bridge still gates itself to MC2 Career and
throttles duplicate views. Do not restore a timer based only on calls to
`0x001EBA20` without first proving it runs in cruise.

The follow-loss values come from the MC2 constructor at `0x0C7284`:
`aiBrainHookman + 0x3F4 = 40000.0f` (the squared 200-unit distance) and
`+0x3F8 = 5.0f` (the grace timer). `Update` resets the timer while the player
is within 200 units and decrements it continuously outside that radius. The
MC3 bridge reproduces this reset/countdown behavior before calling
`OnFollowLost("out_of_range")`.

`mcRaceHookmen::Update` supplies the success condition. It first requires the
Hookman brain's completion-status virtual method, then compares the horizontal
player/Hookman separation with `784.0f`; `PlayerFinishedFollow` runs only below
that squared distance, giving a strict 28-unit radius. The MC3 bridge now keeps
route completion and proximity as separate inputs and applies that same limit.

The current MC2 Career cruise does not instantiate the retail MC3
`aiBrainHookman`: a one-shot heap scan after eight live car matrices found zero
objects with vtable `0x46BDF8`. `--mc3-mc2-test-route-complete` is therefore a
headless-test oracle for the completion bit only. It must be replaced by the
ported route/brain status before the encounter is considered fully natural.
