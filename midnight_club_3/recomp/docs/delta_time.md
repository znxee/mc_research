# Delta time and unlocked frame rates

## The finding

The Xbox build runs a **fixed step**. Every timing preset is mode 0 with rate 60
and one sample, so `mcGame::ApplyFrameRateConfig` (0x20880) calls
`datTimeManager::FixedFrame(60, 1)` (0x20BB00, its only caller is 0x208CB). Each
update advances exactly 1/60 s, whatever real time it took.

The game was tuned for 60 updates a second, menus included. The recompilation's
default `fps_cap = 30` therefore ran the game at **half speed** (measured:
`30.0 fps, game 0.500 s per real s`). Removing the frame limit made it run
faster. This half-speed behaviour already existed before the delta time work.

## The fix

1. **Variable step.** The hook at 0x208D0 runs right after `FixedFrame` and clears
   the fixed-mode flag `0x534770` and the fixed step `0x4B2D58`, as `RealTime(0)`
   (0x20BAB0) does. The timer then measures real time.
2. **No rounding.** The hook at 0x20893 skips `mov byte [0x534776], bl`, which
   rounds the measured dt up to 1/60, 1/30, 0.05 or 1/15.
3. **Per-update constants.** Each constant the game advanced by once per update is
   scaled to the real time of that update against the 60 Hz tick it was tuned for:
   `c -> c * dt * 60`. The scaled dt is the game's (0x4B2D48), the raw measured dt
   (0x4B2D70), or, for the loading thread, the time since the same call site last ran.
   Eighteen sites are covered: loading screen flashes, sky, replay camera, camera
   update (0x2C2686), car gyroscope (0x125CB0, 0x125EBF), impulse (0x29FBA6), fades,
   music (0x1D21F), front end camera (0x15A799), pedestrian animation (0x22B18D),
   and the movie subtitles.
4. **Video.** The fork's `BinkWait` (0x3ACDF0) had been replaced by "never wait", so
   movies ran as fast as frames were shown. It now waits on real time, using the
   frame rate in `BINK +0x14 / +0x18` and the current frame in `+0x0C`.

## Measurements

| `fps_cap` | frames per second | game seconds per real second |
|---|---|---|
| 30 (vsync) | 30.0 | 1.000 (was 0.500) |
| 60 (vsync) | 60.0 | 1.000 |
| 0 (no vsync) | 116 to 227 | 0.998 to 0.999 |

A throttle test (1.5 s of accelerator from the arcade start) gave the same
speedometer reading at 30, 60 and about 150 fps. Intro movies with the frame limit
off ran at 29.95 to 30.15 frames per second, against 29.97 in the file.

## Left alone, and why

- **Frame lock** (0x4B4E8C) is kept native. The game writes 2 during races, the
  same value as on the console, so its six readers behave as they do there.
- **Vibration** (0x361C01 steps by 1/30 per update). Its consumer was not found,
  so it is not scaled.
- **Loading screen** time reads near zero for a few frames, and the sky does not
  run there. Expected.

## Open

- The roughly 5% extra acceleration seen on the PS2 at 60 fps was not measured on the
  Xbox build. The speedometer is too coarse to show it.
- Vibration needs a consumer to scale.
