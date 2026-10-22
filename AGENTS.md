# Instructions for AI agents

This repository is the shared toolbox for Midnight Club research. Follow this
order every time you need to do something to the game files, and do not skip
steps 1 and 2.

## 1. Look for an existing tool first

```bash
python scripts/mc_research.py find <what you need, in plain words>
```

Search with several words: the name of the file format, the platform, the
action (`convert`, `dump`, `patch`, `inventory`). Try synonyms before deciding
there is nothing. Read `INDEX.md` for the full list when the search is empty.

If a tool matches, read its folder: `tool.json` and the header of the code.

## 2. Use it before you change it

Run the tool as it is, on the input it was written for, and check the output.
Only then decide whether it is good enough.

```bash
python scripts/mc_research.py run <tool> --help
```

## 3. Update the tool that exists

If the tool is close but misses something you need:

- change the tool in its own folder, do not copy it into another one;
- keep the behaviour it already has for other users. Add an option rather than
  change a default, and say so in the commit message;
- update `tool.json` (`summary`, `requires`, `status`) to match what changed;
- run `check` before you commit.

Commit the update when the user asked you to share it. A change that only
serves your local job stays local.

## 4. Create a tool only when none exists

Create it only after step 1 found nothing that does the job, even partly.

- Put it in the folder the convention names (`CONVENTION.md`). Pick the title,
  platform and type; use `shared` if it crosses titles.
- Write a `tool.json` with `status: "unverified"`. Write the header of the code:
  what it reads, what it writes, which environment variables it needs.
- Run `check`, then `index`, then commit both the tool and the regenerated
  `INDEX.md` and `catalog.json`.

## Rules that do not bend

- Never commit game data, ISO files, ELF files, assets, savestates or
  anything that belongs to someone else's copy of a game.
- Never commit secrets, tokens, personal paths or the user's e-mail.
- Never hard-code a drive or folder. Use an environment variable, with a
  documented name. `MC_RESEARCH_ROOT` is set for you by `run`.
- Keep the licence and credits. A tool ported from someone else's work names
  them in its header and in `CREDITS.md`.
- Do not edit `INDEX.md` or `catalog.json` by hand. Run `index`.
- Do not publish unfinished work from a fork as if it were a finished tool.
  Mark it `experimental`.

## Commit messages

Describe what the tool does and what changed, in English. End the message with
the trailer the user's agent is configured to add, for example:

```
Co-Authored-By: Claude Haiku 5.5 <noreply@anthropic.com>
```

## When you are not sure

Say so in your reply and leave the tool unchanged. Ask the user before you
publish a tool that other people will depend on.
