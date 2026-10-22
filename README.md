# mc_research

Shared tools for reverse engineering and modding the **Midnight Club** games
(Midnight Club II, Midnight Club 3: DUB Edition Remix, Midnight Club: L.A.), on
PS2, PSP, Xbox and the native recompilations.

The goal is one place where people and AI agents find a tool before they write
one, improve the tool that exists instead of forking it, and commit what they
build so the next person can use it.

> This repository holds **tools only**. No game data, ISO, ELF or asset is
> included, and none may be committed. Every tool reads files from your own copy
> of the game.

## Start here

```bash
python scripts/mc_research.py find <words>       # look for a tool first
python scripts/mc_research.py run <tool> [args]  # run it (all tool folders are on PYTHONPATH)
python scripts/mc_research.py check              # validate manifests and syntax
python scripts/mc_research.py index              # rebuild INDEX.md and catalog.json
```

`INDEX.md` lists every tool. `catalog.json` is the same data for machines.

## Layout

```
<title>/<platform>/<type>/<tool>/
    tool.json        the manifest: what it is, where it runs, its status
    <tool>.py        the code
```

- **title**: `midnight_club_2`, `midnight_club_3`, `midnight_club_la`, or `shared`
  for tools that work across titles.
- **platform**: `ps2`, `psp`, `xbox`, `recomp`, or `any`.
- **type**: `audio`, `cities`, `collision`, `emulator`, `geometry`, `menu`,
  `modloader`, `mods`, `races`, `reverse`, `shaders`, `textures`, `traffic`,
  `vehicles`, `docs`, `research`, `general`. The full rules are in
  [CONVENTION.md](CONVENTION.md).

Each tool lives in its own folder, so imports between tools keep working (the
runner puts every folder on `PYTHONPATH`).

## Status

Every manifest carries a `status`:

- `unverified`: moved here from the original kit, not yet run in this layout;
- `verified`: someone ran it on a copy of the game and wrote the result in `last_verified`;
- `experimental`: works for its author, expect rough edges.

## Credits and license

GPL-3.0-or-later, see [LICENSE](LICENSE). The people whose work the tools build on
are listed in [CREDITS.md](CREDITS.md). Keep those credits when you change a tool.

## Contributing

Read [AGENTS.md](AGENTS.md) (the rules followed by AI agents) and
[CONTRIBUTING.md](CONTRIBUTING.md) (the rules for everyone).
