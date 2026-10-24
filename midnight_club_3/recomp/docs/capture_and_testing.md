# Captures, input and tests on the Xbox recompilation

## Captures

- Run with the environment variable `XBE_CAPTURE_DIR` set to a folder, and press F3.
  The next frame is saved: every draw in `frame.txt`, each render target as a 32 bit
  BMP, and the textures the frame read.
- In `frame.txt`, each draw line gives the render target, the vertex and pixel
  shader handles, the blend and the stages. Each `clear` line is numbered among the
  draws, so a clear can be found between two draws.
- **Read alpha from the BMP directly.** Image libraries such as PIL may drop the
  alpha channel of a 32 bit BMP. Read the four bytes per pixel yourself.
- Targets are saved after the draws that matter when a draw with a given write
  mask is seen (for example `alphamask_post`). Add a probe like that to find the draw
  that changes a channel.

## Input and the test route

- The keyboard is driven with `keybd_event`. Enter is A, Space is Start, arrows move,
  RShift accelerates, F3 captures, F6 teleports (when the module is on).
- Menu route to a San Diego cruise, with the profile already made:
  1. wait about 30 s for the title screen, press Enter, Enter, Enter;
  2. press Space, wait 8 s;
  3. Down, Down (to Arcade), Enter;
  4. Space, Enter, Enter;
  5. wait about 45 s for the race to load.
- Profile creation makes a new `Player N` if the cursor starts on a blank entry.
  Check the screen after each step; a mis-press can enter Career instead.

## Settings

- The recompilation reads `settings.toml` at start. A test that changes it must back
  up the file and restore it afterwards. `recomp_harness scenario` does this.
- Earlier test scripts restored a stale copy of the file. Compare the file with its
  backup before and after a run.

## Scripted scenario

`recomp_harness` (in `midnight_club_3/recomp/emulator/recomp_harness`) runs the route
above with `scenario arcade-race <name>`. Set `MC3_RECOMP_DIR` to the folder holding
`MC3RemixXBE.exe` first. It writes screenshots and a copy of `mc3_xbe.log` to
`MC_OUTPUT_DIR`. The sampled speed of the race is in the log as `MC3 dt:` lines.

## Logs

- Release builds write only `LOGR` and `LOGE` lines. `LOGI` is filtered out.
- The race speed is logged every 5 s as `MC3 dt: <fps>, game <s per real s>`.
- The MC2 city logs `MC2 LA:` lines (see [mc2_la_slot.md](mc2_la_slot.md)).
