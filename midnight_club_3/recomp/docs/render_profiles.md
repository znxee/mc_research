# Render profiles of the Xbox recompilation

The D3D12 backend has one code path. A **profile** is a policy over that path, fixed
at boot. D3D8/NV2A translation, Bink, Flash, targets and present are shared, so a
compatibility fix reaches every profile.

| Profile | What it draws |
|---|---|
| `legacy` | The console path, the regression reference, with the approved `motion-blur` baseline. |
| `enhanced` | The approved package, including the `motion-blur` baseline. |
| `hybrid` | The console path plus features named one by one. `light-shadow` and `motion-blur` are its defaults. |

A profile change needs a restart; the boot log says so.

## Selecting

The command line wins over `settings.toml`, which wins over `legacy`.

```text
--mc3-render-profile=legacy|enhanced|hybrid
--mc3-render-feature=post,materials,contact-shadow,vehicle-shadow,sun-shadow   (repeatable)
--mc3-render-disable=<feature list>        wins over everything
--mc3-render-capture-ab=<tag>              F3 captures go to gpu_captures/<time>_<tag>_<profile>
--mc3-render-timing                        CPU and GPU frame time every 600 presents
--mc3-gpu-index=<n>                        adapter, in high-performance order
```

`settings.toml` keys: `render_profile`, `render_features`, `gpu_index` (-1 is the
first high-performance adapter). Feature names accept underscores too.

A feature requested before its code exists is logged as `pending` and stays off.
`legacy` ignores additions outside its baseline; `enhanced` ignores features outside
its package. To test one feature alone, use `hybrid`.

## Features

| Feature | State | Notes |
|---|---|---|
| `post` | `enhanced`; `hybrid` on request | One full screen pass over the 3D scene, once per frame, before the overlay. HUD, minimap, gauges, Flash, text and video are never filtered. |
| `contact-shadow` | `enhanced`; `hybrid` on request | The car's contact shadow. The origin is the Matrix34 from vtable 0x46C750; the car looks along -z. |
| `vehicle-shadow` | `enhanced`; `hybrid` on request | Casters come from the stream output of the vertex shader's clip positions. |
| `sun-shadow` | `hybrid` only, under test | Two cascades side by side in one map, sharing the same stream output buffers. |
| `reflections` | `enhanced`; `hybrid` on request | Car paint, glass and wet road reflections, sharper and shaped by a combiner stage. |
| `light-shadow` | `enhanced`; on by default in `hybrid` | MCLA style headlight beams with shadows for nearby cars. Street lamp shadows are optional and off. |
| `motion-blur` | default in all profiles | A calibrated depth and reprojection streak pass. It suppresses the original 480p radial blur. `--mc3-render-disable=motion-blur` restores the old effect. |
| `materials` | pending | Parsed, logged as pending, no effect. |

## Lessons that apply to every profile

- Windows `near` and `far` are macros: never use them as field names.
- Scene and overlay split: XYZRHW draws never decide where the 3D scene ends. Bink and
  the game's glow and blur are XYZRHW. The first non-XYZRHW draw with no depth test
  after the 3D draws is the start of the HUD.
- The game's sun and moon light is `SetLight` slot 2. Slot 0 is the default white light
  at 45 degrees; slot 1 is per object (street lamps). The night city light is black,
  so the last value set in a race is kept.
- Alpha test is on almost everywhere (ALWAYS or GEQUAL 0). "Has alpha test" only counts
  if the pass can discard something; what the game clipped from the camera casts no shadow.
- Frame time on the GPU varies 0.3 to 0.8 ms between identical races. Compare the
  stamps of the same pass, not whole frames.

## How to test

Use `render_ab` (in `midnight_club_3/recomp/emulator/render_ab`). It has runners for
FMV, title and menu captures per profile, and for in-game race captures with the HUD.
Compare inside one F3 capture (the `post_pre` and `post` targets of the same frame),
or against a legacy run of the same boot. Boot scenes are not pixel stable between
processes, even the legal and FMV screens.
