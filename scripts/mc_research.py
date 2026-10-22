"""mc_research: find, run and index the tools in this repository.

    python scripts/mc_research.py find <words>        search name, summary, title, platform, type
    python scripts/mc_research.py run <tool> [args]   run a tool, with every tool folder on PYTHONPATH
    python scripts/mc_research.py check               validate every tool.json and compile every .py
    python scripts/mc_research.py index               rewrite INDEX.md and catalog.json from the manifests
    python scripts/mc_research.py new <name> ...      create a tool folder with its manifest and a starter file
    python scripts/mc_research.py contribute <name>   check, branch, commit and open a pull request

Only the standard library is used. A tool is any folder that holds a tool.json.
Set MC_RESEARCH_AUTHOR (your name or handle) and MC_RESEARCH_AGENT (the agent
and model you run with, e.g. "Claude Code claude-haiku-5-5") before contributing.
"""
import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ("name", "kind", "title", "platform", "type", "entry", "summary", "license", "status")
KINDS = {"tool", "library", "module", "data", "docs", "research"}
OSES = {"any", "windows", "linux", "macos"}
# the convention's vocabulary (CONVENTION.md is the reference; keep the two in step)
TITLES = {"midnight_club_2", "midnight_club_3", "midnight_club_la", "shared"}
PLATFORMS = {"ps2", "psp", "xbox", "xbox360", "pc", "recomp", "shared", "any"}
TYPES = {"audio", "cities", "collision", "docs", "emulator", "general", "geometry", "menu", "modloader",
         "mods", "races", "research", "reverse", "shaders", "textures", "traffic", "vehicles"}


def manifests():
    for path in sorted(ROOT.rglob("tool.json")):
        if ".git" in path.parts:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        data["path"] = path.parent.relative_to(ROOT).as_posix()
        yield data


def find(words):
    words = [w.lower() for w in words]
    hits = []
    for m in manifests():
        hay = " ".join(str(m.get(k, "")) for k in ("name", "summary", "title", "platform", "type", "path")).lower()
        score = sum(1 for w in words if w in hay)
        if score:
            hits.append((-score, m["path"], m))
    for _, _, m in sorted(hits, key=lambda h: (h[0], h[1])):
        print(f"{m['path']}\n    {m['summary']}  [{m['status']}]")
    if not hits:
        print("no tool matches; search again with other words before creating one")
    return 0 if hits else 1


def run(name, args):
    target = None
    for m in manifests():
        if m["name"] == name or m["path"] == name:
            target = m
            break
    if target is None:
        print(f"no tool named {name!r}; try: find {name}", file=sys.stderr)
        return 2
    if not target["entry"]:
        print(f"{name} has no entry point; read {target['path']}/tool.json", file=sys.stderr)
        return 2
    folder = ROOT / target["path"]
    # every tool folder goes on the path: tools import each other (mc2_rsc, mc3_bound, bnk_tool...)
    folders = {str((ROOT / m["path"]).resolve()) for m in manifests()}
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(sorted(folders) + [env.get("PYTHONPATH", "")])
    env.setdefault("MC_RESEARCH_ROOT", str(ROOT))
    cmd = [sys.executable, str(folder / target["entry"]), *args]
    return subprocess.call(cmd, cwd=os.getcwd(), env=env)


DRIVE_PATH = re.compile(r"^[A-Za-z]:[\\/]")


def drive_literals(path):
    """(line, value) of every string literal in the file that starts with a drive letter."""
    import io
    import tokenize
    found = []
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(path.read_text(encoding="utf-8", errors="replace")).readline))
    except (tokenize.TokenError, SyntaxError):
        return found
    for tok in tokens:
        if tok.type == tokenize.STRING:
            try:
                value = ast.literal_eval(tok.string)
            except (ValueError, SyntaxError):
                continue
            if isinstance(value, str) and DRIVE_PATH.match(value) and len(value) < 260 and ";" not in value:
                found.append((tok.start[0], value))
    return found


def check():
    bad = 0
    names = {}
    for m in manifests():
        needed = REQUIRED if m.get("kind") == "tool" else tuple(k for k in REQUIRED if k != "entry")
        missing = [k for k in needed if k not in m or m[k] in ("", None)]
        if missing:
            print(f"{m['path']}: missing {', '.join(missing)}")
            bad += 1
        if any(o not in OSES for o in m.get("os", ["any"])):
            print(f"{m['path']}: unknown os {m.get('os')!r}")
            bad += 1
        if m.get("kind") not in KINDS:
            print(f"{m['path']}: unknown kind {m.get('kind')!r}")
            bad += 1
        for field, allowed in (("title", TITLES), ("platform", PLATFORMS), ("type", TYPES)):
            if m.get(field) and m[field] not in allowed:
                print(f"{m['path']}: {field} {m[field]!r} is not in the convention")
                bad += 1
        if m["name"] in names:
            print(f"{m['path']}: name {m['name']!r} also at {names[m['name']]}")
            bad += 1
        names[m["name"]] = m["path"]
        folder = ROOT / m["path"]
        if m["entry"].endswith(".py") and not (folder / m["entry"]).exists():
            print(f"{m['path']}: entry {m['entry']} not found")
            bad += 1
        for py in folder.rglob("*.py"):
            try:
                ast.parse(py.read_bytes(), filename=str(py))
            except SyntaxError as e:
                print(f"{py.relative_to(ROOT)}:{e.lineno}: {e.msg}")
                bad += 1
                continue
            for line, value in drive_literals(py):
                print(f"{py.relative_to(ROOT)}:{line}: absolute drive path {value[:60]!r}; use an environment variable")
                bad += 1
    print("ok" if not bad else f"{bad} problem(s)")
    return 1 if bad else 0


def index():
    rows = list(manifests())
    catalog = [{k: m.get(k) for k in ("name", "kind", "title", "platform", "type", "entry", "summary",
                                      "status", "path", "maintainers", "last_verified")} for m in rows]
    (ROOT / "catalog.json").write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Tool index", "", "Generated by `scripts/mc_research.py index`. Do not edit by hand.", "",
             "| tool | title | platform | type | kind | status | summary |",
             "|---|---|---|---|---|---|---|"]
    for m in rows:
        lines.append(f"| [{m['name']}]({m['path']}/) | {m['title']} | {m['platform']} | {m['type']} | "
                     f"{m['kind']} | {m['status']} | {m['summary'].replace('|', '/')} |")
    (ROOT / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    environment()
    print(f"{len(rows)} tools indexed")
    return 0


ENV_READ = re.compile(r"os\.environ\.get\(\s*['\"]([A-Z][A-Z0-9_]+)['\"]")


def environment():
    """ENVIRONMENT.md: every variable a tool reads, and the tools that read it."""
    users = {}
    for py in sorted(ROOT.rglob("*.py")):
        if ".git" in py.parts:
            continue
        for var in ENV_READ.findall(py.read_text(encoding="utf-8", errors="replace")):
            users.setdefault(var, set()).add(py.parent.relative_to(ROOT).as_posix())
    lines = ["# Environment variables", "",
             "Generated by `scripts/mc_research.py index`. Do not edit by hand. Set a variable to the",
             "folder or file it names. Empty means the tool looks in the current folder, so set it.", "",
             "| variable | meaning | used by |", "|---|---|---|"]
    for var in sorted(users):
        meaning = ENV_MEANING.get(var, "see the tools below")
        tools = ", ".join(f"`{t}`" for t in sorted(users[var])[:4])
        more = f" and {len(users[var]) - 4} more" if len(users[var]) > 4 else ""
        lines.append(f"| `{var}` | {meaning} | {tools}{more} |")
    (ROOT / "ENVIRONMENT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


ENV_MEANING = {
    "MC_RESEARCH_ROOT": "this repository's root (set by `run`; the tools folder when used by hand)",
    "MC_RESEARCH_AUTHOR": "your name or handle, written into new tools and commits",
    "MC_RESEARCH_AGENT": "the agent and model you run with, written as the AI-Assisted-By trailer",
    "MC3_HOSTFS": "the HostFS folder of the PS2 game (the files the emulator loads as host0:)",
    "MC3_HOSTFS_ALT": "a second HostFS folder some tools also look at",
    "MC3_ALPHA_HOSTFS": "the HostFS folder of the Alpha 3.2 Remix build",
    "MC3_ELF_DIR": "the folder holding the retail ELF (SLUS_213.55) and its edits",
    "MC3_CLEAN_ASSETS": "an unmodified copy of the game's ASSETS folder, used as a reference",
    "MC3_ISO_SOURCE": "the source folder for building a modded ISO",
    "MC3_PCSX2_DIR": "the folder with pcsx2-qt.exe",
    "MC3_PCSX2_DATA": "PCSX2's own data folder (the one with inis/, logs/ and sstates/)",
    "MC2_PC_RESEARCH": "the Midnight Club II (PC) research folder, with its assets_p/ and video/",
    "MC2_PS2_RESEARCH": "the Midnight Club II (PS2) research folder, with its assets/",
    "MC_RESEARCH_ASSETS": "the research folder that holds the game builds and dumps",
    "MC_WORK_DIR": "the working folder for extracted files and scratch analysis",
    "MC_OUTPUT_DIR": "where tools write their results",
    "MC_SCRATCH_DIR": "a scratch folder for test runs",
    "RECOMP_DIR": "the root of the XboxXBERecomp checkout (the native Xbox recompilation)",
    "IDA_DIR": "the IDA Pro install folder",
    "FFDEC_DIR": "the folder with ffdec-cli.exe (JPEXS Free Flash Decompiler)",
    "MSYS_DIR": "the MSYS2 install folder (bash)",
    "SYSTEM_FONTS_DIR": "the system fonts folder",
    "RIM_IMPORTER_DIR": "the folder of the external Rim Importer tool",
}


STARTER = '''"""{name}: {summary}

Environment variables this tool reads (set them, do not edit the code):
    none yet

Origin: written for mc_research by {author}.
"""
import argparse


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    args = ap.parse_args()
    print("{name}: not implemented yet")


if __name__ == "__main__":
    main()
'''


def new(argv):
    import argparse
    ap = argparse.ArgumentParser(prog="new", description="create a tool folder from the convention")
    ap.add_argument("name", help="tool name: lowercase letters, digits and underscores")
    ap.add_argument("--title", required=True, choices=sorted(TITLES))
    ap.add_argument("--platform", required=True, choices=sorted(PLATFORMS))
    ap.add_argument("--type", required=True, choices=sorted(TYPES))
    ap.add_argument("--summary", required=True, help="one line a search can match")
    ap.add_argument("--author", default=os.environ.get("MC_RESEARCH_AUTHOR", "unknown"))
    ap.add_argument("--kind", default="tool", choices=sorted(KINDS))
    ap.add_argument("--os", default="any", choices=sorted(OSES))
    a = ap.parse_args(argv)
    if not re.fullmatch(r"[a-z][a-z0-9_]*", a.name):
        print("name must be lowercase letters, digits and underscores, starting with a letter", file=sys.stderr)
        return 2
    if any(m["name"] == a.name for m in manifests()):
        print(f"a tool named {a.name!r} already exists; find it with: find {a.name}", file=sys.stderr)
        return 1
    folder = ROOT / a.title / a.platform / a.type / a.name
    folder.mkdir(parents=True)
    entry = f"{a.name}.py" if a.kind == "tool" else ""
    if entry:
        (folder / entry).write_text(STARTER.format(name=a.name, summary=a.summary, author=a.author), encoding="utf-8")
    manifest = {
        "name": a.name, "kind": a.kind, "title": a.title, "platform": a.platform, "type": a.type,
        "entry": entry, "summary": a.summary, "os": [a.os],
        "requires": ["python>=3.10"] if entry else [],
        "origin": f"contributed by {a.author}", "license": "GPL-3.0-or-later", "status": "unverified",
        "maintainers": [a.author], "last_verified": None,
    }
    (folder / "tool.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"created {folder.relative_to(ROOT).as_posix()}")
    print("next: edit the code, then run: python scripts/mc_research.py check")
    return 0


def contribute(argv):
    """Validate one tool folder, put it on a branch, commit it and open a pull request."""
    import argparse
    ap = argparse.ArgumentParser(prog="contribute", description="send one tool folder as a pull request")
    ap.add_argument("name", help="tool name, as in tool.json")
    ap.add_argument("--message", default="", help="what the tool does and why it is new or changed")
    a = ap.parse_args(argv)
    target = next((m for m in manifests() if m["name"] == a.name), None)
    if target is None:
        print(f"no tool named {a.name!r}", file=sys.stderr)
        return 2
    if check() != 0:
        print("fix the problems above, then contribute again", file=sys.stderr)
        return 1
    branch = f"contrib/{a.name}"

    def git(*cmd, check_ok=True):
        r = subprocess.run(["git", *cmd], cwd=ROOT, capture_output=True, text=True)
        if check_ok and r.returncode:
            print(f"git {' '.join(cmd)} failed:\n{r.stderr}", file=sys.stderr)
            sys.exit(1)
        return r.stdout.strip()

    if git("status", "--porcelain", "--", target["path"]) == "" and git("log", "-1", "--format=%H", "--", target["path"]):
        print("nothing changed in this tool since the last commit", file=sys.stderr)
        return 1
    index()
    git("checkout", "-B", branch)
    git("add", "--", target["path"], "INDEX.md", "catalog.json")
    agent = os.environ.get("MC_RESEARCH_AGENT", "")
    trailer = f"\n\nAI-Assisted-By: {agent}" if agent else ""
    message = (a.message or f"Add or update {a.name}") + trailer
    git("commit", "-m", message)
    git("push", "-u", "origin", branch)
    gh = subprocess.run(["gh", "pr", "create", "--fill", "--head", branch], cwd=ROOT, capture_output=True, text=True)
    if gh.returncode == 0:
        print(gh.stdout.strip())
    else:
        print(f"pushed {branch}. Open a pull request on GitHub from it (gh not available or failed: {gh.stderr.strip()})")
    return 0


def main(argv):
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "find":
        return find(rest)
    if cmd == "run" and rest:
        return run(rest[0], rest[1:])
    if cmd == "check":
        return check()
    if cmd == "index":
        return index()
    if cmd == "new":
        return new(rest)
    if cmd == "contribute":
        return contribute(rest)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
