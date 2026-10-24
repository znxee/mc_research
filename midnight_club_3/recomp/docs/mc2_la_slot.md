# Midnight Club II's Los Angeles on the Xbox recompilation

The recompilation draws Midnight Club II's Los Angeles where MC3 draws its own
city, using the original PC files of the MC2 game. Nothing of MC2 is distributed:
the user points `MC3_MC2_DIR` at their own copy of MC2's `assets_p`.

## Status

| Part | State |
|---|---|
| Baked city blocks (`#geom_0_*`, world space), textures | in game |
| Per-vertex lighting from `.xbcpv` ("CPV1" format) | in game |
| Lit windows (second texture coordinates) | in game |
| 8511 instances from the `.hood` files, baked into world space | in game; 884 have only `_1_main`, drawn always |
| Collision: the city's `OTGRID` or `QUADTREE` read by the game's own `LoadAscii` (0x234DF0) from the `.bnd` copied to the cache partition | in game (hook 0x2A3C6 replaces the archetype `+0xC` offsets) |
| City slot (record 13), name, races from `assets_x.dat_6` | in game |
| Arcade city list shows "Los Angeles" and it starts a race | in game |
| Minimap for Los Angeles | open: the game's `hud_map_losangeles` texture is missing, so the minimap is black |
| Career and other menus | open |
| AI routes (`.aib`) | open: uses the San Diego shell |
| Props, traffic and pedestrian data | open: still San Diego's |
| Spawn point | open: the start position is still the San Diego cruise's; `MC3_MC2_TELEPORT` moves the car by hand |
| Level grid | open: the grid is San Diego's; the west and south edges (x < -1250, z < -1250) may have no collision |
| Unloading the city with the swapped bound | not tested |

## Where things are

- **Registry.** The Xbox registry (0x26ED10) makes 14 city records of 0x50 bytes at
  `[0x557EE4]`: sd, atlanta, detroit, tokyo, dlc1 to dlc8, nocity, and record 13,
  left as `not_initialized`. `Mc2LaRegister` (hook 0x26F001) writes `losangeles`
  there, with San Diego's code and hood list.
- **Races.** `assets_x.dat_6` (a Dave archive built with `dave.py -cf -cn -d`) holds
  `tune/race/losangeles.loc`, `.locinf`, `.override` and 501 race files taken from the
  PS2 port. The game mounts `assets_x.dat_1` to `_8` on its own, and a `_6` overrides
  the stock archives.
- **File redirect.** `Stream::Open` (0x1A2280, hook `Mc2LaPaths`) maps `losangeles` to
  `sd` for city files, but not for `tune/race`. Paths use backslashes in the game:
  compare with both separators.
- **Arcade selector.** The real city step is the modulo at 0x13B6F0 (`% 12`). It is
  widened to `% 14` so it reaches record 13 (hooks 0x13B723 and 0x13B72E). The
  unlock test `IsCityUnlocked` (0x289CC0) answers "unlocked" for record 13.
  Two other functions look similar and are not the selector: 0x17D600 and 0x1886E0.
- **Per-city audio table.** `0x4AFBC8` has 12 entries of 20 bytes, one per city 0 to
  11. Record 13 read past it and crashed the race load. Hooks `0x61E00` and `0x61DAC`
  give Los Angeles San Diego's entry.
- **Display name.** The string lookup (0xEA750) returns `!!CM_losangeles!!` when a key
  is missing. Hook `0xEA790` returns a prepared "Los Angeles" entry for that key.
- **Drawing.** `mcCity::ModelDraw` (0x9B3C5, hook `Mc2CityDraw`) calls the recompilation's
  host draw instead of `0x97A30`. The cullable lists 2 and 3 of `mcCullableMgr::Render`
  (0x92A48) hold MC3's city models, so they are skipped while MC2's city is drawn. The
  camera is the game's view and projection from `SetTransform`.

## Debugging notes

- The race log shows `MC2 LA: on` when Los Angeles is the city being played, and each
  redirected file as `MC2 LA: <from> -> <to>`.
- `MC3_MC2_ALWAYS=1` puts Los Angeles in place of any city, for testing without the menus.
- `MC3_MC2_TELEPORT=x,y,z` moves the car; F6 in game does the same from the current
  camera (see the module's header).
- A crash in the audio thread at a race start was the process-block bug in
  [runtime_and_memory.md](runtime_and_memory.md), not the city.
