> Upstream project: https://github.com/mzzvxm/LARecomp (no licence published). Its code is not in this
> repository; this note only records how we built and used it for analysis.

# LARecomp built on this machine (20/10/2026, MC3-0008 / MC3-0012 reference)

LARecomp (Midnight Club: Los Angeles Complete Edition, Xbox 360, static recompilation) runs here as a visual
reference for the MC3 renderer work. Study only: no LARecomp code or shader goes into MC3, no MCLA data leaves this
machine.

## What is where (all under `X:\mc3-alpha-decomp\research\render_mcla\`)

| Path | What |
| --- | --- |
| `mcla_iso\` | the disc image, extracted from `X:\Midnight Club - Los Angeles - Complete Edition (USA, Europe).7z` |
| `MCLA_Game_Files\` | `default.xex`, the four `xarchive_*.rpf`, the `.bik` videos, taken out of the image with `xiso_extract.py` |
| `xiso_extract.py` | a small XDVDFS reader (partition at 0, 0x2080000, 0xFD90000 or 0x18300000); `--list`, `--only REGEX` |
| `rexglue-sdk-0.10.0\win-amd64\` | ReXGlue SDK 0.10.0 (GitHub rexglue/rexglue-sdk, SHA-256 ad4485da...0c11b; Windows Defender flagged the zip as `Trojan:Win32/Suschil!rfn` on 19/10, the user released it, the hash matches the published one) |
| `directx-headers-download\DirectX-Headers-1.619.5\` | Microsoft's D3D12 headers (GitHub microsoft/DirectX-Headers v1.619.5): the installed Windows SDK 10.0.22621 lacks Shader Model 6.8 and the enhanced barriers |
| `LARecomp\out\build\win-amd64-relwithdebinfo\larecomp.exe` | the build |

## How it was built

```bat
cd LARecomp
copy ..\MCLA_Game_Files\default.xex out\build\win-amd64-release\assets\default.xex
..\rexglue-sdk-0.10.0\win-amd64\bin\rexglue.exe codegen larecomp_manifest.toml
rem with VsDevCmd (VS 2022) and the LLVM 23 of xbox_recomp\toolchain:
cmake --preset win-amd64-relwithdebinfo -DCMAKE_PREFIX_PATH=<sdk>\win-amd64 -DCMAKE_CXX_COMPILER=<llvm>\clang++.exe ^
      -DCMAKE_RC_COMPILER=<llvm>\llvm-rc.exe "-DCMAKE_CXX_FLAGS=-I<DirectX-Headers>\include\directx" .
cmake --build out/build/win-amd64-relwithdebinfo
```

Two local changes to the LARecomp copy, both build fixes:

- `src/compat/msvc_stl_compat.cpp` (added to `CMakeLists.txt` at the end): the prebuilt SDK libraries call two
  vectorized STL helpers (`__std_find_first_of_trivial_pos_1`, `__std_find_last_of_trivial_pos_1`) that MSVC 14.39's
  library lacks; the file gives them with the same contract.
- the DirectX-Headers include path, on the command line only.

## Running it

```bat
set REX_LOG_LEVEL=warn
set MCLA_GAME_DATA=X:\mc3-alpha-decomp\research\render_mcla\MCLA_Game_Files
LARecomp\out\build\win-amd64-relwithdebinfo\larecomp.exe --clock_no_scaling=true
```

The window is titled `LARecomp (60 FPS Enhanced)`; `render_ab`'s `capture_window` (PrintWindow) captures it. The pause
menu has Time of Day (hold time, set the hour), Debug Camera (freecam) and the shadow switches.

## What it showed (20/10)

At night: every car's headlights throw a warm pool on the road ahead and light the cars in front; a car standing in a
beam shades it (dynamic). Street lamps light nothing dynamically and cast no shadow. Reference frames:
`larecomp_night_01.png` here (photo mode, the player's car in front of traffic).
