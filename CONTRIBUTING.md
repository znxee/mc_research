# Contributing

Thank you for helping. The repository is private for now; contributors are
added by the maintainer.

## Before you start

1. Read [README.md](README.md) and [CONVENTION.md](CONVENTION.md).
2. Search: `python scripts/mc_research.py find <words>`. Improving an existing
   tool is almost always better than adding a second one.

## Making a change

- Work on a branch, not on `main`.
- One tool or one fix per commit. Say in the message what changed and on which
  game build you tested it.
- Run `python scripts/mc_research.py check` before you push. If you added or
  renamed a tool, run `index` too and commit `INDEX.md` and `catalog.json`.
- Update `tool.json` when the behaviour, requirements or status changes.

## What is accepted

- Tools that work on a copy of a game you own. The tool does not ship the game.
- Format notes and inventories in `docs/` with the build they were made from.
- Fixes with a short test: the input, the command, and the expected output.

## What is not accepted

- Game data, ISO, ELF, assets, savestates, or any file you do not have the right to share.
- Secrets, tokens, absolute paths and personal information.
- A copy of a tool that already exists in another folder.

## Licence

By contributing you agree that your work is released under GPL-3.0-or-later,
the licence of this repository. Keep the credits of anyone whose work you build on.
