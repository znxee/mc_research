# MC3-0015 - complete `vp_*` traffic bridge

Work in progress, owned by Fork Recomp. This is a bounded runtime prototype,
not acceptance of the whole traffic replacement. The installed executable is
`../xboxxberecomp_eval/templates/game/MC3RemixXBE.exe`.

## Architecture

Only the enhanced profile enables the bridge. The original ambient object
supplies lane planning and traffic rules. A separate `aiOpponent::Init` creates
the full `mcCar` stack (input, sim, collider, damage, audio and render instance).
There is no per-frame copying or scanning/writing of physical car matrices.
Legacy and hybrid return immediately from the construction hooks.

The opponent manager backing allocation has six extra 0x43C-byte slots, while
its original opponent count and vector destructor header stay unchanged.
These extra owners have unique native collision IDs but do not enter race
standings. Construction is bounded to **six** simultaneous actors. Native ambient
deactivation retires the physical actor through aiOpponent destruction; the
next construction finds an actually free owner slot (not active-count indexing).
Respawn stress and repeated city teardown still need acceptance checks.

## Confirmed Xbox boundaries and offsets

| Xbox VA | Function / hook |
|---:|---|
| `0x0006D7D0` | `aiAmbientVehicleInstances::AddAmbientVehicle` |
| `0x00071AC0` | shared `aiAmbientVehicle::Init` entry |
| `0x0006C936`, `0x0006D843` | Init call sites: initial population / respawn |
| `0x00073FF0` | ambient Render; ECX is ambient+0x10 |
| `0x00078940` | ambient Update(float); lane oracle update |
| `0x00079AB0` | ambient Deactivate; release full actor before lane disposal |
| `0x0001D9B0` | native ShouldRunPauseUpdateLoopOnly gate |
| `0x0035D200`, `0x0035D500` | vehAutoMgr capacity constructor / unchecked AddEntry |
| `0x001E43C0`, `0x001E4413` | opponent manager Init / backing allocation |
| `0x001E4561` | opponent manager settled, ready for extra construction |
| `0x001EC2D0`, `0x001ED2F0` | opponent constructor / full Init |
| `0x001ED328` | factory result capture inside opponent Init |
| `0x001FA970`, `0x001FB040` | opponent factory constructor / Construct |
| `0x002C8690` | racer Reset, entity Reset and physics activation |
| `0x001F1710`, `0x001ED9C0` | target Reset / opponent UpdateInput |
| `0x001E45F0`, `0x001E471C` | release extra owners before manager cleanup |
| `0x001EC430` | opponent destructor, without freeing placement storage |

* Ambient size: 0x21C. phInst is at +0x24; Matrix34 at +0x34;
  world translation at +0x58. **+0x24 is not the matrix.**
* Ambient state +0xC4: 1 is collider state, unsuitable as a live lane oracle.
  Current lane +0xFC; requested rail speed +0xE0.
* Complete mcCar size 0x3138; runtime vtable observed 0x454F40.
  Input +4, sim +8, physical/render instance +0x1C, collider +0x44.
* Render/physics instance vtable 0x46C750; Matrix34 +0x10, position +0x34.
* Opponent size 0x43C; entity at +0x20, target storage at +0x7C.
* Opponent Init receives `(slot, start, arg2, arg3)`; start size 0x88,
  position/yaw at +0x38, config pointer +0x64, vehicle name config+0xE3.
* `phLevel` singleton 0x5580F0. Its vtable+0x18 removes a phInst, as used
  by original ambient Deactivate at 0x79AB0. Detaching only the collider
  preserves the lane object; its lane update must then run independently of
  physics culling, once per simulation tick.
* The target's +0x0C vector is used as a spline tangent by aiInput. Supply a
  unit direction; speed is the separate float argument to UpdateInput.

The reference clock slows when the physical car falls behind after impact;
this keeps the native route within reach without teleporting the physical car.
State 2 alone is not a simulation gate: it remains set in Pause. The bridge
uses native ShouldRunPauseUpdateLoopOnly, which checks gGameState+9 at 0x557ED0.
Do not infer pause from the raw/scaled dt alone.

Guest stack memory is in 0xD0000000..0xE0000000. A memory reader limited to
physical RAM silently reads zero for Init stack arguments and causes a null
start/config crash. The bridge reader includes committed stack/system pages.
Read known image globals/vtables separately; they are outside physical RAM.

## Runtime checks

Run from this directory:

```powershell
python probe_arcade_traffic.py --soak-seconds 65 --require-bridge --require-route --exit-to-menu
python probe_arcade_traffic.py --arcade-mode cruise --soak-seconds 5 --exit-to-menu --resource-probe
python probe_arcade_traffic.py --render-profile legacy --soak-seconds 20
```

Each run gets its own timestamped directory. The runner navigates the visible
native UI to Arcade / Ordered Race or Cruise; the visible main menu and shared cursor
are not interchangeable. It removes MC3_MC2_DIR from the child environment.
Screens, game.log, actual guest object/component dumps and result.json are
retained. An exception, process exit or stalled frame counter fails the run.
`--require-route` also rejects a frozen oracle, a vehicle that never moves,
or tracking error over 100 m. `--exit-to-menu` uses the native Pause menu,
Go to Menus, and Yes confirmation; it requires frontend state 7 and an owner
release marker. Do not substitute process termination for this lifecycle check. A basic PASS without this option proves boot/
simulation only, not lane tracking. These are coarse smoke thresholds,
not final traffic quality criteria.

Evidence before lane fixes:

* `runs/20261021-041935`: 35 s, full physical actor/components, no guest
  exception; failed behavior: original ghost collider changed the oracle to
  collider state and requested speed zero. Basic runner PASS was insufficient.
* `runs/20261021-042644`: duplicate collider successfully removed; 40 s without
  guest exception, but distant/frozen lane reference produced runaway driving.
  Do not treat this run as successful route tracking.

## Still required before closing MC3-0015

1. Verify native lane updates, turns, intersections and braking against actual
   physical poses; do not accept only a model or a successful constructor.
2. Stress the six-actor pool during movement, ambient respawns and slot reuse.
3. Supply validated independent vp configs in Cruise, where no race opponent
   template is available. Current prototype captures loaded race opponents.
4. Exercise pause, restart, leaving the city and repeated loads; confirm owner,
   sim, collider, render and audio cleanup, including partial Init failure.
5. Keep the 10-minute stationary soak as a baseline; add player movement and
   repeated city loads before marking the complete traffic task corrected.

## Follow-up runtime evidence

* `runs/20261021-043249`: one full actor, 45 s, actor displacement 321.41 m,
  oracle 316.17 m, max tracking error 19.57 m. Native lane choices, turn,
  stopping and restarting observed in telemetry.
* `runs/20261021-043546`: correctly FAIL: a 32-entry observation cache filled
  with parked scenery and built no full actor. Replaced by a 512-entry cache
  and admission filtering for lane-controlled traffic.
* `runs/20261021-044027`: six full actors, 65 s, all moved; max error 27.09 m.
  Pool included H2, Hummer and Yukon. Its extra inspection did NOT actually
  pause (old boot pad overwrite), so it does not prove pause or cleanup.
* `runs/20261021-044442`: legacy boot/gameplay smoke, 15 s, zero bridge logs
  and zero full actor constructions.
* `runs/20261021-044722`: native pause now opens after limiting the boot pad
  injection in hooks.cpp to pre-game states. Captured Go to Menus and its
  confirmation. The inspection timer expired before accepting Yes, so this
  is NOT evidence of destruction/return to frontend. Also revealed that the
  old bridge advanced its oracle during pause; fixed with native 0x1D9B0 gate.

The raw pad injection in Mc3MainLoopPadProbe must skip state 2 as well as
state 5. Rewriting current/previous raw pad buffers in gameplay swallowed
Start transitions. Keep the native pad poll authoritative during the race.

## Capacity overflow found by lifecycle testing

The old six-actor smoke PASS is NOT a clean-heap acceptance result.
`runs/20261021-045216` reached Pause / Go to Menus / Yes, released all six
owners, then crashed in native heap validation. The identical legacy flow
`runs/20261021-045625` returned to frontend successfully with zero bridge actors.

`runs/20261021-045919` walked the native heap after every construction. The
first four extra actors preserved block boundaries; construction number five
overwrote a heap header with component pointers. The corruption precedes
destruction; skipping the heap check or repairing backlinks is wrong.

A temporary write watch in `runs/20261021-050710` captured writes at guest
0x80F694E0/4 by host RVAs EC7B81/EC7BD7. The matching PDB resolved both to
`__imp__sub_0035D500`, generated x86_recomp.101.cpp line 21058. The temporary
page-protection/VEH code has been removed. These physical watched addresses
are evidence for that run, not production offsets or an API.

Confirmed boundary: vehAutoMgr constructor 0x35D200 receives capacity 10 in
this game (measured in run 051245). That argument allocates every entity/
component pointer table and initializes +0x7C. Enhanced now uses 128, at the
native allocator/lifetime boundary. Native AddEntry/DelEntry/update/destruction
remain responsible for the components. Before constructing traffic, the bridge
verifies the live manager capacity. If enhanced was selected only after legacy
initialized the manager, construction is disabled until an enhanced restart.

The runner rejects `MC3TRAFFIC heap BAD` as well as guest exceptions. A test
that terminates the process cannot substitute for native city teardown.

## Current race validation

`runs/20261021-104046/result.json` passed 600 s in enhanced Arcade race with
six complete `vp_*` vehicles, 366 route samples per car, six native physical
removals, one already-detached ambient cleanup, and 23 s of settled frontend
observation. The maximum sampled lane gap was 28.11 m. The separate
`runs/20261021-103926/result.json` exercised the four-entry native setup
bound under a Scion template and kept heap/backlinks valid. After a failed
Cruise-only pilot was removed, `runs/20261021-143117/result.json` passed a
fresh race regression on the restored executable. The final read-only
resource-probe build passed `runs/20261021-144659/result.json` with six actors
and `runs/20261021-144842/result.json` in ordinary Cruise, both through native
Go to Menus and settled frontend observation. `CRUISE_NEXT.md` documents
the independent Cruise resource blocker; moving-player retirement/reuse and
repeated city loads remain open.

## Historical 600 s gameplay binary (not current lifecycle validation)

SHA256: D9ECA183C9FFCCED05811A577794D5780F9DA5E4CFF4EB0DF13AC9BA1392F9A3.

* `runs/20261021-051245`: six full actors, 20 s, valid heap after all six
  constructions and all six destructions, native return to frontend PASS.
* `runs/20261021-051524/verified_result.json`: six full actors, 600 s soak,
  598.647 s of actor telemetry, no exception or bad heap, all six destructed,
  frontend state 7 restored. Max tracking error 27.07 m. Models: Golf R32 and
  SRT-4 (the native source pool also contained Scion tC). Native race standings
  remained six contestants despite the six extra traffic owners.
* The soak's original `result.json` is intentionally preserved as FAIL: its
  old movement oracle used net displacement. One car traveled 1760.83 m but
  finished only 9.69 m from its first sample. Movement validation now measures
  cumulative horizontal path, filtering sub-10 cm resting jitter. A closed
  40 m loop and a stationary 0 m actor were separately replayed to check this
  correction. Revalidate the immutable evidence with:

```powershell
python verify_recorded_run.py runs/20261021-051524
```

The separate verified result is PASS; the raw run result and original metrics
are not rewritten. No ambient retirements happened in this stationary soak.
This does not prove moving-player respawn behavior or an independent Cruise
pool. See `CRUISE_NEXT.md` for those implementation boundaries.

Start enhanced at process launch (`--mc3-render-profile=enhanced`), then use
Arcade / Ordered Race to exercise the current opponent-backed prototype.
Switching only the renderer after boot does not retroactively reserve the
vehicle manager's component capacity. Legacy and hybrid keep stock traffic.

## Extended frontend settling uncovered a later failure

The 600 s gameplay/heap result is valid only for its recorded observation
window. `runs/20261021-052931` kept the returned frontend alive for eight
seconds and found C0000005 at 76.975 s, through physics calls 0x2AB86A /
0x1951D4 after six clean native destructions. Its original result.json was
a false PASS because the old runner did not rescan the log after the final
frontend wait; this has been corrected. Do not describe the entire menu
return lifecycle as stable based on 051245 or 051524 alone.

Final-binary legacy comparison `runs/20261021-053524` passed the same native
menu route and extended frontend wait, with no bridge constructions. The
post-return physics problem therefore needs bridge-specific investigation.
The task remains EM_ANDAMENTO. Current research logs shared-type reference
counts before/after construction and destruction; no speculative reference
count edits or suppression of the physics fault are installed.

## Follow-up lifecycle work

See `LIFECYCLE_INVESTIGATION.md` for exact native removal evidence, immutable
failed runs and current investigation. Read the latest entry before treating
a menu-return PASS from a shorter observation window as stability evidence.
The runner now rejects read-only `MC3TRAFFIC physics BAD` diagnostics and
visually confirms the Go to Menus row (the native blur darkens gold below
the profile-screen highlight detector threshold).
