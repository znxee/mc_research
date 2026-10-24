# Traffic limits of the `vp_` vehicle bridge on the Xbox recompilation

The `vp_` bridge replaces San Diego's cruise traffic with full vehicles (the
`vp_` models), instead of the original traffic. It works at the default profile
and opts in with the flags below. Tested on the San Diego cruise.

## Result

On 24 Oct 2026, 100 cars with 30 models ran at 128 MB guest memory at about 25
frames per second, with the flags below.

## Fixed limits and their flags

| Limit | Default | Flag | Note |
|---|---|---|---|
| Car resource cache [0x50A08C] | 16 | `--mc3-car-cache=64` | The player's acquire nests the cruise build, so the code retries. The same flag lifts the per-car lists: [0x53890C] (188, overflowed at the 48th car), [0x536704] (100), and [0x4D6308] (256 built-in slots, overflowed at the 60th; they become windows), and the contact guard outside the physics level. |
| Live lanes | the pool from the city list | `--mc3-traffic-ambient-scale` | Restores the ambient pool from the resource (48) instead of the city list. It rebuilds the pool before any car is active. 30 live lanes were used for the test. |
| Models beyond 18 spawns | 18 | `--mc3-traffic-cruise-late-models` | The acquire at state 2 ran outside the Begin and End of the car handler (0x109ED0 and 0x109F40), which switch the shader factory. Without it: `Invalid type ... ResourcePageIn`. With the flag, the acquire runs between them. |
| Physics objects | 96 | `--mc3-car-cache` | From car 92 on, the physics level stopped including new cars (they sat at 0,0,0) and broke the cleanup at Go to Menus (0xED8A0). The flag grows the table in Init (0x2AC730). |

## Camera and late models

- `--mc3-traffic-follow` points the player's cameras (+0x6C) at pool cars and turns off
  the camera collision (+0x15C), which pulled the camera into the car it followed.
  Changing only the D3D view is not enough: the city draws from another camera.
- A late model appeared without bumpers and wheels. The model loader for a car is
  `[0x507668]` during a race, not the parts loader `[0x5319E4]`. `car_late_load`
  swaps the loader during 0x109D40.
- 0x109ED0 and 0x109F40 bracket the drawing of a frame. They are not the loading
  bracket.

## Debugging

- `--mc3-write-watch` sets DR0 on a location and logs the writer and the guest stack.
- A minidump with dbghelp gives the host instruction pointer of a crash.
- **Look for fixed lists before blaming memory.** Each limit above first looked like
  running out of memory. The heap at 128 MB still had about 44 MB free. The pattern
  to search is `{ptr, cap u16, count u16}` appended without a bound check.

See also [runtime_and_memory.md](runtime_and_memory.md).
