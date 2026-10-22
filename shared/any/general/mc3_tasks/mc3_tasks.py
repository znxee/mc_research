"""TASKS.md - canonical work queue shared by the MC3 forks.

FORKS.md records changes that already happened. TASKS.md records work that is
still open, claimed, blocked, fixed awaiting verification, verified, or known
to have regressed. Stable IDs and append-only history keep two forks from
silently doing the same work.

Typical use:

    python mc3_tasks.py read
    python mc3_tasks.py find "flash branco"
    python mc3_tasks.py add --title "..." --priority P1 --scope "RECOMP,FLASH" \
        --fork "Fork Recomp" --summary "..." --acceptance "..."
    python mc3_tasks.py claim MC3-0001 --fork "Fork Recomp"
    python mc3_tasks.py resolve MC3-0001 --fork "Fork Recomp" \
        --fix "..." --evidence "teste/captura/hash"
    python mc3_tasks.py verify MC3-0001 --fork "Fork QA" --evidence "..."
    python mc3_tasks.py regress MC3-0001 --fork "Fork Recomp" \
        --cause "..." --introduced-by "commit/build/mod" --evidence "..."
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import os
import re
import sys
import tempfile
import time
import unicodedata

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "TASKS.md")
LOCK = LOG + ".lock"
MARKER = "<!-- MC3_TASKS_BEGIN -->"

STATES = {
    "ABERTO", "EM_ANDAMENTO", "BLOQUEADO", "CORRIGIDO", "VERIFICADO",
    "REGRESSAO", "CANCELADO", "DUPLICADO",
}
PRIORITIES = {"P0", "P1", "P2", "P3", "P4"}

HEAD = f"""# Lista compartilhada de tarefas e bugs

Este e o registro canonico do trabalho pendente entre as forks do MC3. Use
`FORKS.md` para mudancas ja realizadas e este arquivo para bugs, investigacoes,
mods, portes e validacoes ainda em andamento.

## Regras curtas

1. Procure uma entrada existente antes de criar outra: `python mc3_tasks.py find "termos"`.
2. Assuma a entrada com `claim` antes de editar codigo. O responsavel identifica a fork, nao uma pessoa.
3. Nunca reutilize nem renumere IDs. Nunca apague o historico de uma entrada.
4. `CORRIGIDO` significa que ha uma correcao concreta; `VERIFICADO` exige um teste reproduzivel.
5. Se algo voltar a falhar, use `regress`: ele preserva quando foi corrigido e exige registrar causa/evidencia.
6. Ao abandonar uma linha duplicada, marque `DUPLICADO` e aponte o ID canonico.
7. Toda entrada precisa de criterio de aceite. Descoberta sem proximo passo pertence a notas de pesquisa, nao aqui.

## Prioridade

| Nivel | Uso |
| --- | --- |
| `P0` | Bloqueia boot/build, corrompe dados ou impede todas as forks. |
| `P1` | Quebra um caminho principal, regressao grave ou bloqueio de outra tarefa. |
| `P2` | Bug/tarefa normal com impacto claro. |
| `P3` | Instrumentacao, melhoria, documentacao ou conveniencia. |
| `P4` | Ideia e backlog sem urgencia. |

## Estados

| Estado | Significado |
| --- | --- |
| `ABERTO` | Ninguem assumiu ou o trabalho ainda nao comecou. |
| `EM_ANDAMENTO` | Uma fork assumiu e esta trabalhando. |
| `BLOQUEADO` | Falta dependencia, dado, decisao ou ferramenta explicitada no historico. |
| `CORRIGIDO` | Correcao pronta, aguardando verificacao reproduzivel. |
| `VERIFICADO` | Criterio de aceite passou e a evidencia foi registrada. |
| `REGRESSAO` | Algo antes corrigido/verificado voltou a falhar; causa e introducao ficam no historico. |
| `DUPLICADO` | Outra entrada e a fonte canonica. |
| `CANCELADO` | Escopo removido, com justificativa preservada. |

## Comandos

```text
python mc3_tasks.py read [-n 10] [--all] [--state ESTADO] [--priority P1] [--scope MC2]
python mc3_tasks.py find "texto"
python mc3_tasks.py add --title "..." --priority P2 --scope "RECOMP,MC2" --fork "Fork ..." --summary "..." --acceptance "..."
python mc3_tasks.py claim MC3-0001 --fork "Fork ..." [--note "..."]
python mc3_tasks.py block MC3-0001 --fork "Fork ..." --reason "..." --needs "..."
python mc3_tasks.py resolve MC3-0001 --fork "Fork ..." --fix "..." --evidence "..."
python mc3_tasks.py verify MC3-0001 --fork "Fork ..." --evidence "..."
python mc3_tasks.py regress MC3-0001 --fork "Fork ..." --cause "..." --introduced-by "..." --evidence "..."
python mc3_tasks.py reopen MC3-0001 --fork "Fork ..." --reason "..."
python mc3_tasks.py duplicate MC3-0002 --of MC3-0001 --fork "Fork ..." --note "..."
python mc3_tasks.py cancel MC3-0001 --fork "Fork ..." --reason "..."
```

Escopos sugeridos: `ALPHA`, `PS2`, `XBOX`, `RECOMP`, `MOD`, `MC2`, `MC2_TO_MC3`,
`FLASH`, `RENDER`, `AUDIO`, `CITY`, `TRAFFIC`, `PHYSICS`, `TOOLS`, `DOCS`, `TEST`.

{MARKER}
"""

ENTRY_RE = re.compile(r"^## (MC3-\d{4}) — (.+)$", re.M)
FIELD_RE = re.compile(r"^\*\*([^*]+):\*\*\s*(.*)$", re.M)


def today() -> str:
    return dt.date.today().isoformat()


def clean(value: str | None, default: str = "—") -> str:
    if value is None:
        return default
    value = " ".join(str(value).replace("\r", " ").replace("\n", " ").split())
    return value or default


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


class FileLock:
    def __enter__(self):
        deadline = time.monotonic() + 10.0
        while True:
            try:
                fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, f"pid={os.getpid()} time={time.time()}\n".encode())
                os.close(fd)
                return self
            except FileExistsError:
                try:
                    if time.time() - os.path.getmtime(LOCK) > 300:
                        os.unlink(LOCK)
                        continue
                except FileNotFoundError:
                    continue
                if time.monotonic() >= deadline:
                    raise RuntimeError(f"registro ocupado por {LOCK}; tente novamente")
                time.sleep(0.1)

    def __exit__(self, exc_type, exc, tb):
        try:
            os.unlink(LOCK)
        except FileNotFoundError:
            pass


def parse_entry(block: str) -> dict:
    match = ENTRY_RE.search(block)
    if not match:
        raise ValueError("entrada sem cabecalho valido")
    fields = {k: v.strip() for k, v in FIELD_RE.findall(block)}
    history_at = block.find("\n### Historico\n")
    history = []
    if history_at >= 0:
        history = [line[2:] for line in block[history_at:].splitlines() if line.startswith("- ")]
    return {
        "id": match.group(1),
        "title": match.group(2).strip(),
        "state": fields.get("Estado", "ABERTO"),
        "priority": fields.get("Prioridade", "P2"),
        "scope": fields.get("Escopo", "—"),
        "owner": fields.get("Responsavel", "—"),
        "created": fields.get("Criado", today()),
        "updated": fields.get("Atualizado", today()),
        "depends": fields.get("Dependencias", "—"),
        "duplicate": fields.get("Duplicado de", "—"),
        "summary": fields.get("Problema/objetivo", "—"),
        "acceptance": fields.get("Criterio de aceite", "—"),
        "evidence": fields.get("Evidencia atual", "—"),
        "files": fields.get("Arquivos/areas", "—"),
        "history": history,
    }


def render_entry(task: dict) -> str:
    lines = [
        f"## {task['id']} — {task['title']}", "",
        f"**Estado:** {task['state']}",
        f"**Prioridade:** {task['priority']}",
        f"**Escopo:** {task['scope']}",
        f"**Responsavel:** {task['owner']}",
        f"**Criado:** {task['created']}",
        f"**Atualizado:** {task['updated']}",
        f"**Dependencias:** {task['depends']}",
        f"**Duplicado de:** {task['duplicate']}", "",
        f"**Problema/objetivo:** {task['summary']}", "",
        f"**Criterio de aceite:** {task['acceptance']}", "",
        f"**Evidencia atual:** {task['evidence']}", "",
        f"**Arquivos/areas:** {task['files']}", "", "### Historico", "",
    ]
    lines.extend(f"- {event}" for event in task["history"])
    return "\n".join(lines).rstrip()


def load() -> list[dict]:
    if not os.path.isfile(LOG):
        return []
    text = io.open(LOG, encoding="utf-8").read()
    start = text.find(MARKER)
    if start < 0:
        raise RuntimeError(f"{LOG} nao contem o marcador canonico")
    body = text[start + len(MARKER):].strip()
    if not body:
        return []
    blocks = re.split(r"\n(?=## MC3-\d{4} — )", body)
    return [parse_entry(block.strip()) for block in blocks if block.strip()]


def save(tasks: list[dict]) -> None:
    body = "\n\n".join(render_entry(task) for task in tasks)
    content = HEAD.rstrip() + ("\n\n" + body if body else "") + "\n"
    fd, temp = tempfile.mkstemp(prefix="TASKS.", suffix=".tmp", dir=HERE)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(temp, LOG)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def task_by_id(tasks: list[dict], task_id: str) -> tuple[int, dict]:
    task_id = task_id.upper()
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            return index, task
    raise ValueError(f"ID inexistente: {task_id}")


def event(kind: str, fork: str, note: str) -> str:
    return f"{today()} — {kind} — {clean(fork)} — {clean(note)}"


def move_to_top(tasks: list[dict], index: int, task: dict) -> None:
    task["updated"] = today()
    tasks.pop(index)
    tasks.insert(0, task)


def mutate(task_id: str, callback) -> dict:
    with FileLock():
        tasks = load()
        index, task = task_by_id(tasks, task_id)
        callback(task, tasks)
        move_to_top(tasks, index, task)
        save(tasks)
        return task


def add_task(ns) -> dict:
    with FileLock():
        tasks = load()
        key = normalized(ns.title)
        duplicates = [t for t in tasks if normalized(t["title"]) == key and t["state"] not in {"CANCELADO", "DUPLICADO"}]
        if duplicates:
            raise ValueError(f"titulo ja existe em {duplicates[0]['id']}; use find/claim ou marque duplicado")
        highest = max((int(t["id"].split("-")[1]) for t in tasks), default=0)
        task = {
            "id": f"MC3-{highest + 1:04d}", "title": clean(ns.title),
            "state": "ABERTO", "priority": ns.priority,
            "scope": clean(ns.scope), "owner": clean(ns.owner, "—"),
            "created": today(), "updated": today(),
            "depends": clean(ns.depends), "duplicate": "—",
            "summary": clean(ns.summary), "acceptance": clean(ns.acceptance),
            "evidence": clean(ns.evidence, "Ainda sem evidencia reproduzivel."),
            "files": clean(ns.files), "history": [],
        }
        task["history"].append(event("CRIADO", ns.fork, ns.note or ns.summary))
        tasks.insert(0, task)
        save(tasks)
        return task


def show(task: dict) -> None:
    print(render_entry(task))


def last_fixed_date(task: dict) -> str | None:
    for item in reversed(task["history"]):
        if " — CORRIGIDO — " in item or " — VERIFICADO — " in item:
            return item.split(" — ", 1)[0]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command")

    read = sub.add_parser("read", help="show recent/current tasks")
    read.add_argument("-n", type=int, default=10)
    read.add_argument("--all", action="store_true")
    read.add_argument("--state", choices=sorted(STATES))
    read.add_argument("--priority", choices=sorted(PRIORITIES))
    read.add_argument("--scope")
    read.add_argument("--fork")

    find = sub.add_parser("find", help="search all fields and history")
    find.add_argument("query")

    add = sub.add_parser("add", help="create a task after searching for duplicates")
    add.add_argument("--title", required=True)
    add.add_argument("--priority", choices=sorted(PRIORITIES), required=True)
    add.add_argument("--scope", required=True)
    add.add_argument("--fork", required=True)
    add.add_argument("--summary", required=True)
    add.add_argument("--acceptance", required=True)
    add.add_argument("--evidence")
    add.add_argument("--files")
    add.add_argument("--depends")
    add.add_argument("--owner")
    add.add_argument("--note")

    claim = sub.add_parser("claim", help="assign a task and mark it in progress")
    claim.add_argument("id")
    claim.add_argument("--fork", required=True)
    claim.add_argument("--note", default="Trabalho assumido; conferir dependencias e evidencia antes de editar.")

    block = sub.add_parser("block", help="record an explicit blocker")
    block.add_argument("id")
    block.add_argument("--fork", required=True)
    block.add_argument("--reason", required=True)
    block.add_argument("--needs", required=True)

    resolve = sub.add_parser("resolve", help="mark fixed, awaiting verification")
    resolve.add_argument("id")
    resolve.add_argument("--fork", required=True)
    resolve.add_argument("--fix", required=True)
    resolve.add_argument("--evidence", required=True)

    verify = sub.add_parser("verify", help="mark acceptance criteria verified")
    verify.add_argument("id")
    verify.add_argument("--fork", required=True)
    verify.add_argument("--evidence", required=True)

    regress = sub.add_parser("regress", help="record recurrence of a previously fixed problem")
    regress.add_argument("id")
    regress.add_argument("--fork", required=True)
    regress.add_argument("--cause", required=True)
    regress.add_argument("--introduced-by", required=True)
    regress.add_argument("--evidence", required=True)
    regress.add_argument("--fixed-on")

    reopen = sub.add_parser("reopen", help="reopen without claiming a regression")
    reopen.add_argument("id")
    reopen.add_argument("--fork", required=True)
    reopen.add_argument("--reason", required=True)

    duplicate = sub.add_parser("duplicate", help="close an entry in favor of a canonical ID")
    duplicate.add_argument("id")
    duplicate.add_argument("--of", required=True)
    duplicate.add_argument("--fork", required=True)
    duplicate.add_argument("--note", required=True)

    cancel = sub.add_parser("cancel", help="remove a task from scope while preserving history")
    cancel.add_argument("id")
    cancel.add_argument("--fork", required=True)
    cancel.add_argument("--reason", required=True)

    update = sub.add_parser("update", help="update metadata and append a history note")
    update.add_argument("id")
    update.add_argument("--fork", required=True)
    update.add_argument("--note", required=True)
    update.add_argument("--priority", choices=sorted(PRIORITIES))
    update.add_argument("--scope")
    update.add_argument("--owner")
    update.add_argument("--depends")
    update.add_argument("--evidence")
    update.add_argument("--files")

    ns = parser.parse_args()
    try:
        if ns.command == "add":
            task = add_task(ns)
            print(f"created {task['id']}")
            show(task)
            return 0

        if ns.command in {None, "read", "find"}:
            tasks = load()
            if ns.command == "find":
                query = normalized(ns.query)
                tasks = [t for t in tasks if query in normalized(" ".join(str(v) for v in t.values()))]
            elif ns.command == "read":
                if ns.state:
                    tasks = [t for t in tasks if t["state"] == ns.state]
                if ns.priority:
                    tasks = [t for t in tasks if t["priority"] == ns.priority]
                if ns.scope:
                    tasks = [t for t in tasks if normalized(ns.scope) in normalized(t["scope"])]
                if ns.fork:
                    tasks = [t for t in tasks if normalized(ns.fork) in normalized(t["owner"])]
                if not ns.all:
                    tasks = tasks[:ns.n]
            else:
                tasks = tasks[:10]
            if not tasks:
                print("TASKS.md: no matching entries")
                return 1
            for task in tasks:
                print(f"{task['id']}  {task['priority']}  {task['state']:<13}  {task['owner']}  {task['title']}")
            return 0

        if ns.command == "claim":
            def change(task, _tasks):
                if task["state"] in {"CORRIGIDO", "VERIFICADO", "CANCELADO", "DUPLICADO"}:
                    raise ValueError(f"{task['id']} esta {task['state']}; use reopen se for realmente necessario")
                if task["state"] == "EM_ANDAMENTO" and task["owner"] not in {"—", ns.fork}:
                    raise ValueError(f"{task['id']} ja foi assumida por {task['owner']}")
                task["state"], task["owner"] = "EM_ANDAMENTO", clean(ns.fork)
                task["history"].append(event("ASSUMIDO", ns.fork, ns.note))
            task = mutate(ns.id, change)
        elif ns.command == "block":
            def change(task, _tasks):
                task["state"], task["owner"] = "BLOQUEADO", clean(ns.fork)
                task["history"].append(event("BLOQUEADO", ns.fork, f"Motivo: {clean(ns.reason)} | Precisa de: {clean(ns.needs)}"))
            task = mutate(ns.id, change)
        elif ns.command == "resolve":
            def change(task, _tasks):
                if task["state"] in {"VERIFICADO", "CANCELADO", "DUPLICADO"}:
                    raise ValueError(f"{task['id']} esta {task['state']}; use reopen antes de uma nova correcao")
                task["state"], task["owner"], task["evidence"] = "CORRIGIDO", clean(ns.fork), clean(ns.evidence)
                task["history"].append(event("CORRIGIDO", ns.fork, f"Correcao: {clean(ns.fix)} | Evidencia: {clean(ns.evidence)}"))
            task = mutate(ns.id, change)
        elif ns.command == "verify":
            def change(task, _tasks):
                if task["state"] != "CORRIGIDO":
                    raise ValueError(f"{task['id']} esta {task['state']}; verify exige CORRIGIDO")
                task["state"], task["evidence"] = "VERIFICADO", clean(ns.evidence)
                task["history"].append(event("VERIFICADO", ns.fork, f"Criterio de aceite passou. Evidencia: {clean(ns.evidence)}"))
            task = mutate(ns.id, change)
        elif ns.command == "regress":
            def change(task, _tasks):
                if task["state"] not in {"CORRIGIDO", "VERIFICADO"}:
                    raise ValueError(f"{task['id']} esta {task['state']}; regress exige CORRIGIDO ou VERIFICADO")
                fixed = ns.fixed_on or last_fixed_date(task)
                if not fixed:
                    raise ValueError("regress exige --fixed-on porque a entrada nao possui evento CORRIGIDO/VERIFICADO")
                task["state"], task["owner"], task["evidence"] = "REGRESSAO", "—", clean(ns.evidence)
                note = (f"Corrigido antes em: {fixed} | Regressao observada em: {today()} | "
                        f"Causa: {clean(ns.cause)} | Introduzido por: {clean(ns.introduced_by)} | "
                        f"Evidencia: {clean(ns.evidence)}")
                task["history"].append(event("REGRESSAO", ns.fork, note))
            task = mutate(ns.id, change)
        elif ns.command == "reopen":
            def change(task, _tasks):
                task["state"], task["owner"] = "ABERTO", "—"
                task["history"].append(event("REABERTO", ns.fork, ns.reason))
            task = mutate(ns.id, change)
        elif ns.command == "duplicate":
            def change(task, tasks):
                _index, canonical = task_by_id(tasks, ns.of)
                if canonical["id"] == task["id"]:
                    raise ValueError("uma entrada nao pode ser duplicada de si mesma")
                task["state"], task["owner"], task["duplicate"] = "DUPLICADO", "—", canonical["id"]
                task["history"].append(event("DUPLICADO", ns.fork, f"Canonica: {canonical['id']} | {clean(ns.note)}"))
            task = mutate(ns.id, change)
        elif ns.command == "cancel":
            def change(task, _tasks):
                task["state"], task["owner"] = "CANCELADO", "—"
                task["history"].append(event("CANCELADO", ns.fork, ns.reason))
            task = mutate(ns.id, change)
        elif ns.command == "update":
            def change(task, _tasks):
                for source, target in (("priority", "priority"), ("scope", "scope"),
                                       ("owner", "owner"), ("depends", "depends"),
                                       ("evidence", "evidence"), ("files", "files")):
                    value = getattr(ns, source)
                    if value is not None:
                        task[target] = clean(value)
                task["history"].append(event("ATUALIZADO", ns.fork, ns.note))
            task = mutate(ns.id, change)
        else:
            parser.print_help()
            return 2
        print(f"updated {task['id']} -> {task['state']}")
        show(task)
        return 0
    except (ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
