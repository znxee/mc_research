# MC3-0015: independent Cruise pool - next implementation boundary

This is research for the next stage. As requested on 2026-10-22, MC3-0015 is
paused and the shipped executable uses the original ambient traffic in every
render profile by default. The race-template bridge and the independent Cruise
pilot remain in source for later work, gated by explicit opt-in flags.

## Paused checkpoint (2026-10-22)

The final investigation isolated two separate native boundaries:

* Ordinary Cruise can Open both Jetta and Scion `_o` files through 0x20D6F0,
  and typed load 0x2105F0 returns a valid Scion resource. The isolated probe
  returned to gameplay (`202103`, `202418`); missing Dave archive content is
  not the explanation.
* An independent zero-count owner pool (six 0x43c slots, native 0x108 config,
  0x88 Start, explicit manager+8 lifetime) reached `aiOpponent::Init`. Direct
  G500, Jetta and Scion `_o` loads then reached shader PageIn and asserted in
  0xDFB40: first shader word `0x000000AA`, masked type 42 where the retail
  factory accepts 0..3. G500 run `20261021-205656` and instrumented run
  `20261021-210050` preserve this failure. The relocation was mathematically
  consistent: G500 entry 0x828EE0C0 + delta 0x00D43300 = 0x836313C0. The
  read-only Dave probe `inspect_xbck.py` confirmed `0xAA` in the source XBCK
  (Jetta `_o` at file offset +0x5CE4). Do not replace type 42 blindly.
* Native asynchronous preloader 0x105CA0 has 15 free cache slots and resolves
  `vp_jetta_03` to registry index 1, but its registration via 0x210620/
  0x20DC00 fails with `-1` for
  `resources\\vehicle\\vp_jetta_03\\vp_jetta_03_o.xbck` (run `205255`).
  The earlier `204941` trial accidentally selected the `_g` suffix because
  the garage's fifth argument was copied; argument six selects `_o`.
* Enhanced Arcade Race remains functional with the existing opponent-template
  bridge: `203914` and `205935` both built six full vehicles. Its `_o` loads
  occur during city setup, whereas the synthetic Cruise pilot attempted its
  new load after gameplay reached state 2. This timing difference is a lead,
  not yet a proven root cause.

Resume by comparing 0x105A74 PageIn inputs and the 0x20DC00/0x1A2000 file
index route during city setup versus state 2; test early resource preparation
at 0x1E4561 before changing shader parsing. The opt-in runner is
`probe_arcade_traffic.py --arcade-mode cruise --cruise-pilot --resource-probe`;
expect an assertion until the resource path is fixed. `--traffic-vp-bridge`
explicitly enables the existing race/Career bridge, while ordinary launches
keep native traffic. The source and failed run logs are retained for review.

The paused build was verified after the default switch: enhanced Arcade
Cruise `runs/20261022-042224/result.json` and Arcade Race
`runs/20261022-042416/result.json` both PASS, built zero extra owners and
returned to frontend state 7. An explicit bridge run
`runs/20261022-042604/result.json` PASS built six complete vehicles, made six
native removals and returned to frontend. The shipped EXE SHA-256 is
`5976F833EFA518892D97AC09850BE174F1D1AAAC55B38021A50FD892DBC60AC7`.

## Correction: Cruise can open and load an arbitrary `_o` resource

The earlier inference that Cruise lacks `_o` resource registration was wrong.
At 0x2126E8 the *same* static asset manager, vtable `0x46D768`, Open target
`0x20D6F0` and extension context `0x453F68` appear in Arcade Race and Cruise.
In ordinary Cruise, the one-shot opt-in probe `runs/20261021-202103` opened
both `vp_jetta_03_o` and `vp_d_scion_tc_05_o` through that native Open method;
both returned stream `0x4BF500`. The stronger `runs/20261021-202418` also
called native typed load 0x2105F0 for Scion `_o` *without an opponent* and got
resource `0x832B0400`. At 0x21270C its header was read successfully (0x80
bytes, version word 1, type 0x38D030, body length 0x5F770). The probe freed
the returned typed buffer and restored the player's original path; Cruise
continued into gameplay and `result.json` reports PASS.

Thus the synthetic aiOpponent Init assertion in runs `144332`/`144514` is
**context-specific to that pilot's construction/invocation**, not proof of a
missing archive entry, mount, resource registration, or `_o` preload. The next
experiment must compare the old pilot's call stack, Start/config fields,
manager and loader return/header at 0x2126C0 while `g_constructing=1`.

## Career free roam: native hookmen are a working template source

The user's Career screenshot showed enhanced traffic repeating the hookman cars,
while Arcade Race repeated its opponents. The dedicated Career run
`runs/20261021-155408/result.json` confirms the underlying initialization:
Continue Career entered San Diego free roam, native `aiOpponentManager::Init`
reported `race_count=3`, and `aiOpponent::Init` requested the `_o` resources for
`vp_montecarlo_78`, `vp_gs430_04`, and `vp_eclipse_04`. The bridge captured
those three live configs/starts and built six complete physical traffic cars
from them. All six followed the ambient route oracle during the 12-second run;
the result recorded six owners, 8 route samples each, and at most 18.47 m
tracking error. The player requested the unsuffixed `vp_jetta_03` resource.
The stricter `runs/20261021-155808/result.json` passed with the resource
probe, bridge and route requirements enabled: 15 seconds of gameplay, six
complete owners, six native physical removals, and a clean return to frontend
state 7. The Career pause menu has five rows, so the runner now selects its
actual `Go to Menus` row instead of the Arcade row.

This establishes a **template/ownership dependency**, not an inherent need
for race AI to drive the traffic cars. The enhanced cars use their own native
vehicle/physics objects and the ambient lane oracle; the existing opponents
currently provide valid configs/starts and owner storage. Career
hookmen happen to provide that context, so the visible selection follows the
hookman pool. Arcade Cruise has no opponent manager/init at all; its earlier
synthetic Init still returned null at 0x2105F0, although the isolated typed
load now succeeds. To select arbitrary `vp_*` models, create an independently
owned, lifecycle-safe config/start pool and isolate why the old nested Init
changed the resource load outcome. Adding a dummy race AI
would be a diagnostic shortcut, not the desired final design.

## Cruise probe and failed synthetic pool

`runs/20261021-142538/result.json`: the new `--arcade-mode cruise` harness
entered actual Cruise, simulated 12 seconds and returned through its native
pause/Go to Menus path with 8 seconds of settled frontend observation. There
were zero opponent init captures, zero complete traffic actors, and no
`aiOpponentManager::Init` reserve/ready hook. Cruise pause has Go to Menus at
visible row 5; race has it at row 6. The harness now handles both.

`runs/20261021-142744/result.json` is a deliberately preserved FAIL from a
temporary independent pool. It allocated six owner slots separately,
constructed three 0x108-byte mcCarConfig values with native constructor
0x271D20 and native type/profile setters 0x270AC0/0x270A90, and initialized
0x88-byte aiOpponentStart values with native Clear 0x1CA210. The pool became
ready and began the first native aiOpponent::Init. At 0x105B69 the game's own
resource load asserted because 0x2105F0 returned null; the call was reached
from 0x105B80/0x105AA0 after the car-name lookup 0x26A6A0. No full vehicle
was built. The assertion text at Xbox VA 0x455230 says that retail cannot
make a car resource dynamically; the attempted path format at 0x4552A0 is
`$/resources/vehicle/%s/%s`. Dave archive `assets_x.dat_2` **does** contain
`resources/vehicle/vp_d_scion_tc_05/vp_d_scion_tc_05.xbck`, so file absence
is not established. The actual formatted path and requested resource type
still need capture at 0x105B36/0x2126E5. The pool source and crashing EXE
were removed; the race-validated behavior was rebuilt and regression-tested
in `runs/20261021-143117/result.json`. Merely constructing config and Start
objects does **not** prepare the same car-resource context as Arcade race.

A read-only, opt-in hook at native 0x105B36 (`--resource-probe` in the Arcade
runner) now records the exact path immediately before 0x2105F0. In the race
run `143744`, native opponents requested `_o` variants; the player requested
the unsuffixed Jetta. Normal Cruise run `144145` requested only the unsuffixed
Jetta and returned to the frontend. Two later *opt-in* synthetic Cruise probes
then established the exact missing operation:

* `144332` attempted a Jetta opponent. Native Init requested
  `$/resources/vehicle/vp_jetta_03/vp_jetta_03_o`; 0x2105F0 returned null and
  the retail build asserted at 0x105B69. The player's unsuffixed Jetta had
  loaded successfully one second earlier.
* `144514` attempted a Scion opponent. It requested
  `$/resources/vehicle/vp_d_scion_tc_05/vp_d_scion_tc_05_o` and hit the same
  assertion.

Both `_o.xbck` files are present in `assets_x.dat_2`, and their header type is
0x38D030, the exact type passed to 0x2105F0 in the failing call. Thus the
problem is not explained by a missing archive entry, bad file header, or
using the player's unsuffixed resource path. The later isolated native typed
load proves Cruise can read Scion `_o` outside that failed Init. The pilot code was again
removed after these captures; only the read-only path probe remains installed.
The final executable passed enhanced race with six complete owners and menu
return in `runs/20261021-144659/result.json`, then ordinary Cruise and menu
return in `runs/20261021-144842/result.json`. Its SHA-256 is
`ECFD1C747EEF3F2F245B935D06D4F69D13D05E22419B7D5255D5980129D0BFCE`.

## Native routines found during the long soak

| Xbox VA | Identified behavior | Evidence |
|---|---|---|
| 0x271D20 | mcCarConfig constructor, vtable 0x4483DC | matches alpha constructor structure; defaults at +E3/+F9 |
| 0x26FE80 | mcCarConfig default/clear portion | writes blank strings, appearance/performance defaults |
| 0x270AC0 | vehicle type name setter | bounded 0x16-byte format to config+E3 |
| 0x270A90 | vehicle profile name setter | bounded 0x0D-byte copy to config+F9 |
| 0x270AE0 | vehicle type lookup from name | passes config+E3 to 0x26A6A0 |
| 0x1CA210 | aiOpponentStart::Clear | matches alpha default bytes, pose +38, config +64, ends +84 |

The config allocation size is exactly 0x108: native `sub_00150F3D` pushes
0x108 into `operator new` at 0x1B3B90 and immediately calls the constructor
at 0x271D20; it does this twice. `sub_00148CF0` also reserves a 0x108-byte
stack config. The profile setter terminates at +105. Do NOT infer the size
from the 0x450 spacing between config pointers in a race load: adjacent heap
allocations explain that spacing, not object size.

`runs/20261021-051524/checkpoint_templates/` contains five native starts
(0x88 each) and configs (0x108 each), plus their live pointers/model names.
These dumps are evidence to compare default fields, not pointer-bearing
blobs to deserialize into a different process.

## Remaining implementation

1. Verify default Start ownership and the manager's zero-count allocation path.
2. Compare the failed nested synthetic aiOpponent::Init with the successful
   isolated Cruise 0x2105F0 call: the 0x2126E8 Open result, 0x21270C header,
   type/output pointers, Start/config fields and live manager. Identify the
   *actual* difference before changing the loader. Then build a whitelist
   using native config construction/name/profile setters with explicit
   lifetime through city teardown.
3. Inspect aiOpponent::Init argument 3 and its Cruise brain branches against
   native race data before choosing synthetic defaults. Do not transplant
   process pointers or assume all racing defaults are valid in Cruise.
4. When normal opponent count is zero, reserve collision-resolvable owner
   storage at manager+8 without adding race standings. The ordinary manager
   global destructor skips that array when its count is zero, so explicit
   release/clearing is needed for any independently allocated backing storage.
5. Keep native vehAutoMgr capacity hook (128 in enhanced), unique IDs,
   pause gate and complete native destruction. Repeating only the old factory
   constructor experiment loses reset/activation and is not full physics.
6. Add a visible Arcade/Cruise probe. Require actual native initialization,
   motion, lane tracking, respawn/reuse, cleanup and no heap corruption.

Also still pending: replace address-based model hashing with a verified
logical ambient-slot identity plus explicit seed, nearest-traffic pool reuse,
impact/turn quality checks across more models, and repeated city loads.
