# Folder convention

```
<title>/<platform>/<type>/<tool>/
```

## title

| folder | game |
|---|---|
| `midnight_club_2` | Midnight Club II (PS2 and PC files, the Xbox build's city data) |
| `midnight_club_3` | Midnight Club 3: DUB Edition Remix (PS2 release; Alpha 3.2 Remix; Xbox recompilation) |
| `midnight_club_la` | Midnight Club: L.A. (PSP, PS3) |
| `shared` | tools that work with more than one title, or with none (archives, the hub, the fork log) |

A title folder is added when a second game needs the same tool. Do not copy a
tool into a second title to avoid a dependency: move it to `shared` instead.

## platform

| folder | what runs on it |
|---|---|
| `ps2` | PS2 files: `.pck`, `.bnd`, `.ppf`, the ELF, savestates |
| `psp` | PSP files: `.psppck`, the PSP ELF |
| `xbox` | original Xbox files: `.xbck`, `default.xbe`, `assets_x.dat` |
| `recomp` | the native recompilations (XboxXBERecomp and the other forks): hooks, runtime patches, `.mod` shims |
| `any` | not tied to a platform (used with `shared`) |

## type

| folder | what goes in it |
|---|---|
| `audio` | `.bnk`, `.rstm`, `.xsb`/`.xwb`, music and engine sound |
| `cities` | city structure: hoods, `.lvl`, roads, props, city build and install, the city slot |
| `collision` | `_bnd` and type 10/9 collision, `.occlude`, ground planes |
| `emulator` | PCSX2 and PINE helpers, savestates, freecam, screenshots, drive scripts |
| `geometry` | meshes, containers (`.pck`, `.ppf`), VIF/VU, ISO archives, `dave.py`-style packing |
| `menu` | Flash menus (`.pck`/`.swf`), HUD, frontend strings, menu state |
| `modloader` | the modloader: ELF patching, `.pnach`, module injection, the output and self-test scripts |
| `mods` | modloader modules written in C++ (one folder each, with their source) |
| `races` | race files, race order, obstacles, modes |
| `reverse` | disassembly, decompiler exports, symbol names, vtables, field and pointer analysis |
| `shaders` | shader programs and their transplants |
| `textures` | `.tex`, palettes, GS dumps |
| `traffic` | traffic, pedestrians, AI routes, graphs |
| `vehicles` | car performance, vehicle RAM and textures |
| `docs` | format notes, inventories, ImHex patterns, conventions |
| `research` | one-off analysis scripts kept as a record of how a result was found |
| `general` | the rest. Look here last: a tool in `general` should move when its type is known |

## Choosing a folder

1. Pick the title the tool was written for. If it runs on two titles, put it in `shared`.
2. Pick the platform the input files come from. A tool that writes a `.pck` for
   PS2 is `ps2`, even if it runs on Windows.
3. Pick the type by what the tool changes, not by the name of the file it opens.
4. If two types fit, choose the one a contributor would search first, and say
   what else it touches in `summary`.

## The manifest: tool.json

```json
{
  "name": "mc3_perf",
  "kind": "tool",
  "title": "midnight_club_3",
  "platform": "ps2",
  "type": "vehicles",
  "entry": "mc3_perf.py",
  "summary": "one line a search can match: what it does and on what",
  "requires": ["python>=3.10"],
  "origin": "where it came from, with a commit if known",
  "license": "GPL-3.0-or-later",
  "status": "unverified",
  "maintainers": ["znxee"],
  "last_verified": null
}
```

- `kind`: `tool` (has an `entry` that runs), `library` (imported by others),
  `module` (C++, shader, or code run by another program), `data`, `docs`, `research`.
- `name` is unique across the repository. `check` fails on a duplicate.
- `summary` is what `find` searches. Write it so that someone looking for the
  tool would use the same words.
- `status` changes to `verified` only when `last_verified` holds the date and the
  game build it was tested on, for example `2026-10-22, SLUS-21355 v1.04`.

## Paths and secrets

- No absolute paths. Read game and tool locations from environment variables and
  document them in the tool's header.
- No game data. No secrets, tokens or keys. `check` does not scan for them yet:
  look before you commit.
