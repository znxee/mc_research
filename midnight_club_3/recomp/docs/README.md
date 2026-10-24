# Midnight Club 3 Xbox recompilation: findings

Notes from the XboxXBERecomp work on MC3 Remix (Xbox, XDK 5849). Each file holds
one area: what was found, the addresses and flags to use, how it was verified,
and what is still open. Addresses are virtual addresses of `default.xbe`.

| Document | Area |
|---|---|
| [delta_time.md](delta_time.md) | why the game ran at half speed, and how unlocked frame rates keep its speed |
| [render_profiles.md](render_profiles.md) | `legacy`, `enhanced` and `hybrid` render profiles and their features |
| [render_fixes.md](render_fixes.md) | pedestrians, HUD palettes, channel clears, the signed blend oval, pixel shader state blocks |
| [runtime_and_memory.md](runtime_and_memory.md) | guest threads, the 128 MB mode, heap and debugging tips |
| [mc2_la_slot.md](mc2_la_slot.md) | Midnight Club II's Los Angeles on the Xbox recompilation: city slot, races, colliding and lit |
| [traffic_limits.md](traffic_limits.md) | the fixed limits of `vp_` traffic and the flags that raise them |
| [capture_and_testing.md](capture_and_testing.md) | frame captures, input driving, settings handling and the test route |

## Status meanings

- **verified**: reproduced in a game run, with the evidence named in the document.
- **open**: known, not solved. Each document lists its open items.

## Tools that go with these notes

- `recomp_harness`: starts the recompilation, presses keys, takes screenshots, runs the arcade race scenario.
- `render_ab`: A/B runners for render profiles (FMV, title and menu captures per profile; in-game race captures with the HUD).
- `traffic_vehicle_bridge`: investigation tools for the `vp_` traffic bridge.
