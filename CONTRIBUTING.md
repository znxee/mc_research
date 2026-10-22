# Contributing

Anyone can add a tool, and anyone can improve one. The repository is private for
now; ask the maintainer for access. Tools are added the same way whether you write
them by hand or with an AI agent.

## Set up once

```bash
git clone git@github.com:znxee/mc_research.git
cd mc_research
export MC_RESEARCH_AUTHOR="your-github-handle"          # written into your tools and commits
export MC_RESEARCH_AGENT="Claude Code claude-haiku-5-5" # optional: your agent and model
```

Python 3.10 or later is the only requirement. The `gh` command line is optional;
without it, `contribute` pushes a branch and you open the pull request on GitHub.

## Add a new tool

1. **Search first.** A tool may already exist.

   ```bash
   python scripts/mc_research.py find "what you need, in plain words"
   ```

2. **Create the folder and manifest.** The title, platform and type come from
   [CONVENTION.md](CONVENTION.md). The command refuses a name that is taken.

   ```bash
   python scripts/mc_research.py new my_tool \
       --title midnight_club_3 --platform ps2 --type geometry \
       --summary "one line: what it reads, what it writes, what game build"
   ```

   This creates `midnight_club_3/ps2/geometry/my_tool/` with `tool.json` and a starter
   `my_tool.py`. Edit the code and keep the header: it lists the environment
   variables the tool reads.

3. **Read game files through environment variables.** Never write a drive letter or
   a personal path in code; `check` rejects them. If your tool needs a new variable,
   add its meaning to `ENV_MEANING` in `scripts/mc_research.py`, then run `index`.

4. **Check it.**

   ```bash
   python scripts/mc_research.py check
   python scripts/mc_research.py run my_tool --help
   ```

5. **Contribute it.** This branches, commits with your name and agent in the
   message, pushes, and opens a pull request.

   ```bash
   python scripts/mc_research.py contribute my_tool --message "what it does and what game build it was tested on"
   ```

## Improve a tool that exists

Change the tool in its own folder. Do not copy it somewhere else. Keep the old
behaviour working for other users: add an option rather than change a default.
Update `summary`, `requires` and `status` in `tool.json` when you change what it
does. Then `check` and `contribute` as above.

## Mark a tool verified

A tool is `unverified` until someone runs it on a copy of the game they own.
When you have run it, set `status` to `verified` and `last_verified` to the date
and the game build, for example `2026-10-22, SLUS-21355 v1.04`, and say in the
pull request what you ran.

## What is accepted

- Tools that read a copy of a game you own. The repository never ships game files.
- Format notes and inventories in `docs/`, with the build they were made from.
- Fixes with a short test: the input, the command, and the expected output.

## What is not accepted

- Game data, ISO, ELF, assets, savestates, or any file you do not have the right to share.
- Secrets, tokens, drive letters, personal paths and e-mail addresses.
- A copy of a tool that already exists elsewhere in the repository.
- Unfinished work from a private fork, presented as a finished tool. Mark it
  `experimental` in `status` if you must publish it.

## Licence

Your contribution is released under GPL-3.0-or-later, the licence of this
repository. Keep the credits of anyone whose work you build on, in the tool's
header and in `CREDITS.md`.
