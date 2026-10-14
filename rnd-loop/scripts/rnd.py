#!/usr/bin/env python3
"""rnd-loop: one R&D process for every task, per-task details in a charter.

Stdlib only (Python >= 3.11 for tomllib) so Gemini and Claude run it the same way.

Layout inside a project (all git-tracked):

    rnd/<task>/charter.toml     what is being improved, how it is measured, the gate
    rnd/<task>/registry.jsonl   one JSON record per run (baseline / experiment / promote)
    rnd/<task>/notebook.md      lab notebook: dated notes, decisions, lessons
    rnd/<task>/reports/         reports written from templates
    rnd/dashboard.html          generated view over every task

Commands:

    rnd.py init <task>                          create charter + notebook from templates
    rnd.py run <task> -H "hypothesis" [--kind baseline|experiment] [--change "..."] [--no-exec]
    rnd.py promote <task> <run-id>              make an experiment the new baseline (after merge)
    rnd.py note <task> "text" [--tag lesson]    append a dated note to the notebook
    rnd.py status [<task>]                      baseline, last runs, open hypotheses
    rnd.py dashboard                            write rnd/dashboard.html
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_DIR / "templates"
SCHEMA = "rnd.record/1"


# ----------------------------------------------------------------------------- paths & io
def project_root(start: Path | None = None) -> Path:
    """Nearest ancestor holding rnd/ or .git (the project the work belongs to)."""
    p = (start or Path.cwd()).resolve()
    for cand in (p, *p.parents):
        if (cand / "rnd").is_dir() or (cand / ".git").exists():
            return cand
    return p


def task_dir(root: Path, task: str) -> Path:
    return root / "rnd" / task


def load_charter(root: Path, task: str) -> dict:
    path = task_dir(root, task) / "charter.toml"
    if not path.is_file():
        sys.exit(f"no charter at {path}; run: rnd.py init {task}")
    return tomllib.loads(path.read_text(encoding="utf-8"))


def read_registry(root: Path, task: str) -> list[dict]:
    path = task_dir(root, task) / "registry.jsonl"
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def append_registry(root: Path, task: str, rec: dict) -> None:
    path = task_dir(root, task) / "registry.jsonl"
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def now() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def git_state(root: Path) -> dict:
    def g(*args: str) -> str:
        try:
            return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=30).stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            return ""
    return {"sha": g("rev-parse", "--short", "HEAD"), "branch": g("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": bool(g("status", "--porcelain", "--untracked-files=no"))}


def current_baseline(records: list[dict]) -> dict | None:
    """The latest baseline, or the run a later promote points to."""
    base = None
    by_id = {r["id"]: r for r in records}
    for r in records:
        if r["kind"] == "baseline":
            base = r
        elif r["kind"] == "promote":
            base = by_id.get(r["promotes"], base)
    return base


def next_id(records: list[dict], task: str) -> str:
    n = sum(1 for r in records if r["kind"] in ("baseline", "experiment")) + 1
    return f"{task}-{n:03d}"


# ----------------------------------------------------------------------------- metrics & gate
def load_metrics(path: Path) -> dict:
    """Evaluator output: {"cases": {name: {metric: value}}, "aggregate": {metric: value}}."""
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("cases", {})
    data.setdefault("aggregate", {})
    return data


def _values(metrics: dict, name: str, scope: str) -> dict[str, float]:
    if scope == "aggregate":
        v = metrics["aggregate"].get(name)
        return {"*": v} if isinstance(v, (int, float)) else {}
    return {c: m[name] for c, m in metrics["cases"].items() if isinstance(m.get(name), (int, float))}


def _check(op: str, value, target) -> bool:
    return {"<=": lambda: value <= target, ">=": lambda: value >= target, "<": lambda: value < target,
            ">": lambda: value > target, "==": lambda: value == target, "!=": lambda: value != target,
            "abs<=": lambda: abs(value - target[0]) <= target[1]}[op]()


def gate(charter: dict, cand: dict, base: dict | None) -> dict:
    """Return {verdict, failures[], improvements[], regressions[]}.

    verdict: accepted (constraints hold, no regression, >=1 improvement), neutral (holds, nothing better),
             rejected (a constraint or a regression failed). A baseline run only checks constraints.
    """
    improvements, regressions = [], []
    now_fail = constraint_failures(charter, cand)
    was_fail = constraint_failures(charter, base["metrics"]) if base is not None else {}
    # Only NEW violations block; ones the baseline already had are "known" (the reason R&D exists),
    # and fixing one counts as an improvement.
    failures = [msg for key, msg in now_fail.items() if key not in was_fail]
    known = [msg for key, msg in now_fail.items() if key in was_fail]
    improvements += [f"fixed: {msg}" for key, msg in was_fail.items() if key not in now_fail]
    if base is not None:
        bm = base["metrics"]
        for m in charter.get("metrics", []):
            goal, tol, scope = m["goal"], float(m.get("tolerance", 0.0)), m.get("scope", "per_case")
            new, old = _values(cand, m["name"], scope), _values(bm, m["name"], scope)
            for case in sorted(set(new) & set(old)):
                delta = new[case] - old[case]
                better = delta > tol if goal == "max" else delta < -tol
                worse = delta < -tol if goal == "max" else delta > tol
                label = f"{case}: {m['name']} {old[case]} -> {new[case]}"
                if better:
                    improvements.append(label)
                elif worse:
                    regressions.append(label)
            for case in sorted(set(old) - set(new)):
                regressions.append(f"{case}: {m['name']} disappeared")
    if failures or regressions:
        verdict = "rejected"
    elif base is None or improvements:
        verdict = "accepted"
    else:
        verdict = "neutral"
    return {"verdict": verdict, "failures": failures, "known_failures": known,
            "improvements": improvements, "regressions": regressions}


def constraint_failures(charter: dict, metrics: dict) -> dict[tuple[str, int], str]:
    """{(case, constraint_index): message} for every violated constraint."""
    out: dict[tuple[str, int], str] = {}
    for i, c in enumerate(charter.get("constraints", [])):
        cases = c.get("cases", ["*"])
        scope_cases = metrics["cases"] if cases == ["*"] else {k: metrics["cases"].get(k, {}) for k in cases}
        for case, m in scope_cases.items():
            v = m.get(c["metric"])
            if v is None:
                out[(case, i)] = f"{case}: {c['metric']} missing ({c.get('why', '')})"
            elif not _check(c["op"], v, c["value"]):
                out[(case, i)] = f"{case}: {c['metric']}={v} fails {c['op']} {c['value']} ({c.get('why', '')})"
    return out


# ----------------------------------------------------------------------------- commands
def cmd_init(args) -> None:
    root = project_root()
    d = task_dir(root, args.task)
    d.mkdir(parents=True, exist_ok=True)
    (d / "reports").mkdir(exist_ok=True)
    for name, dest in (("charter.toml", "charter.toml"), ("notebook.md", "notebook.md")):
        out = d / dest
        if out.exists():
            print(f"keep  {out}")
            continue
        text = (TEMPLATES / name).read_text(encoding="utf-8")
        out.write_text(text.replace("{{task}}", args.task).replace("{{date}}", now()[:10]), encoding="utf-8")
        print(f"wrote {out}")
    print("next: fill charter.toml (question, run.command, metrics, constraints), then: rnd.py run "
          f"{args.task} --kind baseline -H 'current state'")


def cmd_run(args) -> None:
    root = project_root()
    charter = load_charter(root, args.task)
    run = charter["run"]
    metrics_path = (root / run["metrics_file"]).resolve()
    records = read_registry(root, args.task)
    rid = next_id(records, args.task)
    t0 = dt.datetime.now()
    exit_code = None
    if not args.no_exec:
        if metrics_path.exists():
            metrics_path.unlink()  # never grade a stale file
        print(f"[rnd] {rid}: {run['command']}", flush=True)
        proc = subprocess.run(run["command"], cwd=root, shell=True, timeout=run.get("timeout_s", 7200))
        exit_code = proc.returncode
    if not metrics_path.is_file():
        sys.exit(f"[rnd] evaluator produced no metrics file at {metrics_path} (exit {exit_code}); nothing recorded")
    metrics = load_metrics(metrics_path)
    base = None if args.kind == "baseline" else current_baseline(records)
    if args.kind == "experiment" and base is None:
        sys.exit("[rnd] no baseline yet: run with --kind baseline first")
    g = gate(charter, metrics, base)
    rec = {
        "schema": SCHEMA, "id": rid, "task": args.task, "kind": args.kind, "ts": now(),
        "hypothesis": args.hypothesis, "change": args.change or "", "baseline_id": base["id"] if base else None,
        "git": git_state(root), "command_exit": exit_code,
        "duration_s": round((dt.datetime.now() - t0).total_seconds(), 1),
        "metrics": metrics, "gate": g, "verdict": g["verdict"] if args.kind == "experiment" else "baseline",
    }
    if g["failures"] and args.kind == "baseline":
        rec["verdict"] = "baseline_with_failures"
    snap = task_dir(root, args.task) / "runs"
    snap.mkdir(exist_ok=True)
    shutil.copyfile(metrics_path, snap / f"{rid}.json")
    append_registry(root, args.task, rec)
    print(json.dumps({"id": rid, "verdict": rec["verdict"], **{k: g[k] for k in ("failures", "known_failures", "regressions", "improvements")}},
                     indent=2, ensure_ascii=False))


def cmd_promote(args) -> None:
    root = project_root()
    records = read_registry(root, args.task)
    target = next((r for r in records if r["id"] == args.run_id), None)
    if target is None or target["kind"] != "experiment":
        sys.exit(f"{args.run_id} is not an experiment of {args.task}")
    if target["verdict"] != "accepted" and not args.force:
        sys.exit(f"{args.run_id} verdict is {target['verdict']}; pass --force with a reason to promote anyway")
    append_registry(root, args.task, {"schema": SCHEMA, "id": f"{args.run_id}-promote", "task": args.task, "kind": "promote",
                                      "ts": now(), "promotes": args.run_id, "reason": args.reason or "", "git": git_state(root)})
    print(f"baseline of {args.task} is now {args.run_id}")


def cmd_note(args) -> None:
    root = project_root()
    nb = task_dir(root, args.task) / "notebook.md"
    if not nb.is_file():
        sys.exit(f"no notebook at {nb}; run: rnd.py init {args.task}")
    tag = f" `#{args.tag}`" if args.tag else ""
    with nb.open("a", encoding="utf-8", newline="\n") as f:
        f.write(f"\n- **{now()[:16].replace('T', ' ')}**{tag} — {args.text}\n")
    print(f"noted in {nb}")


def _tasks(root: Path) -> list[str]:
    base = root / "rnd"
    return sorted(p.name for p in base.iterdir() if (p / "charter.toml").is_file()) if base.is_dir() else []


def cmd_status(args) -> None:
    root = project_root()
    for task in [args.task] if args.task else _tasks(root):
        charter, records = load_charter(root, task), read_registry(root, task)
        base = current_baseline(records)
        runs = [r for r in records if r["kind"] in ("baseline", "experiment")]
        print(f"\n## {task} — {charter['task'].get('title', '')}")
        print(f"baseline: {base['id'] if base else 'none'}   runs: {len(runs)}   "
              f"accepted: {sum(r['verdict'] == 'accepted' for r in runs)}   "
              f"rejected: {sum(r['verdict'] == 'rejected' for r in runs)}")
        for r in runs[-5:]:
            print(f"  {r['id']}  {r['verdict']:<22} {r['hypothesis'][:70]}")
        for h in charter.get("hypotheses", []):
            if h.get("status", "open") == "open":
                print(f"  open hypothesis: {h['id']} {h['text']}")


def cmd_dashboard(args) -> None:
    root = project_root()
    data = []
    for task in _tasks(root):
        charter = load_charter(root, task)
        nb = task_dir(root, task) / "notebook.md"
        data.append({"task": task, "charter": charter, "records": read_registry(root, task),
                     "notebook": nb.read_text(encoding="utf-8") if nb.is_file() else ""})
    page = (TEMPLATES / "dashboard.html").read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    out = root / "rnd" / "dashboard.html"
    out.write_text(page.replace("/*__DATA__*/[]", payload).replace("{{project}}", html.escape(root.name)), encoding="utf-8")
    print(f"wrote {out}")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="rnd.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init"); p.add_argument("task"); p.set_defaults(fn=cmd_init)
    p = sub.add_parser("run"); p.add_argument("task"); p.add_argument("-H", "--hypothesis", required=True)
    p.add_argument("--kind", choices=("baseline", "experiment"), default="experiment")
    p.add_argument("--change", help="what was changed (commit, flag, policy field)")
    p.add_argument("--no-exec", action="store_true", help="grade the existing metrics file without running the command")
    p.set_defaults(fn=cmd_run)
    p = sub.add_parser("promote"); p.add_argument("task"); p.add_argument("run_id")
    p.add_argument("--force", action="store_true"); p.add_argument("--reason"); p.set_defaults(fn=cmd_promote)
    p = sub.add_parser("note"); p.add_argument("task"); p.add_argument("text"); p.add_argument("--tag")
    p.set_defaults(fn=cmd_note)
    p = sub.add_parser("status"); p.add_argument("task", nargs="?"); p.set_defaults(fn=cmd_status)
    p = sub.add_parser("dashboard"); p.set_defaults(fn=cmd_dashboard)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):  # Windows consoles default to cp1252/cp932
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    args.fn(args)


if __name__ == "__main__":
    main()
