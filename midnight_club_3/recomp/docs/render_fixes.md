# Render fixes in the Xbox recompilation

Each entry: the symptom, the cause, the fix and how it was checked. Addresses are
on `default.xbe`.

## Pedestrians drawn with a frozen skeleton

- **Symptom:** pedestrians stood still, the whole body rigid.
- **Cause:** the skinning shader multiplies bone indices by constant `c9` (slot 105,
  value 256). The game writes it once at start-up (0x2D6FCA). A state block the
  game saves and restores around a D3DX effect (`CreateStateBlock` 0x4172D2,
  `ApplyStateBlock` 0x416DFF) reads its values from the XDK shadow copy at
  0x421CC0. The recompilation's HLE `SetVertexShaderConstant1/4` did not keep that
  copy, so the restore wrote zeros over `c9`: every vertex used bone 0.
- **Fix:** the HLE functions write the shadow copy. `[data] D3D_VertexShaderConstants
  = 0x421CC0` in `game.toml`.
- **Checked:** pedestrians change pose from frame to frame.

## HUD text and gauges with black backgrounds

- **Symptom:** text, gauges and button prompts drawn with black boxes around them.
- **Cause:** the textures are P8 (palettized). `SetPalette` is not a known export in
  this image, so the palette stayed empty and the textures lost their alpha.
- **Fix:** `SyncDeferred` reads the palettes from the device (`CDevice_Palettes`,
  0xF98) for each stage.
- **Checked:** gauges come out round and yellow; menu prompts are visible.

## Square black minimap background

- **Symptom:** the round minimap had a black square behind it.
- **Cause:** the game clears only the alpha channel (flag 0x80) before drawing its
  round mask there. The recompilation cleared all four channels.
- **Fix:** the Xbox clear flags are per channel: R 0x10, G 0x20, B 0x40, A 0x80. A
  partial clear is drawn with a masked full screen pass (`MaskedClear`), using the
  render target write mask.
- **Checked:** the minimap is round.

## Oval of white light around the car

- **Symptom:** a white oval around the car in some views.
- **Cause:** the headlight volumes are counted in the alpha channel with the NV2A
  signed blend factors `0xF005` and `0xF006`. The source byte is two's complement
  (0xFF is -1/255): each face moves the alpha count by one step. Read as unsigned,
  the count saturates.
- **Fix:** `SignedBlendOp` runs two passes: the non-negative values, then the
  magnitude of the negative ones with the opposite operation. `PixelKey::signed_half`
  keeps the two apart.
- **Checked:** the oval no longer appears in the test captures after the fix.

## Car paint without reflection in every profile

- **Symptom:** car paint was flat, even in `legacy`.
- **Cause:** D3DX effect passes record their states into an XDK state block on first
  use. The end-of-block function reads the pixel shader from `CDevice+0x784`. The
  HLE `SetPixelShader` never stored it there, so every pass replayed pixel shader 0
  and the fixed function defaults.
- **Fix:** the HLE stores the handle at `CDevice+0x784` and keeps XDK shaped pixel
  shader objects, with a reference count at +0 and the default at +0xC, freed on the
  last release.
- **Debugging:** run with `MC3PS_NOTES=1` and F3. The capture's `frame.txt` gets a
  `note SetTexture/SetPixelShader ... from <guest address>` line between the draws.
  Shader sources are in `assets_x.dat`, folder `$/shaderlibx/cars/`.
- **Rule:** when an HLE replaces an XDK setter, it must also keep the guest fields
  that native code reads back: state blocks, `Get*` functions.

## Bink movies running at the frame rate

- Covered in [delta_time.md](delta_time.md), item 4 of "The fix".

## Open

- Street lamp shadows (optional, off by default) are not verified in a full race.
