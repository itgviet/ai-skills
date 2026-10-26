#!/usr/bin/env python3
"""Validate skills against the Agent Skills spec (https://agentskills.io/specification).

Usage:
  python _tools/validate_skills.py [PATH ...] [--json] [--strict] [--include-vendored]

  PATH            A skill directory, or a directory of skills (default: the skills repo root).
  --json          Print results as JSON to stdout (diagnostics go to stderr).
  --strict        Treat warnings as failures (exit 1).
  --include-vendored
                  Also check vendored skills (AWS skills with .aws-skill-metadata, and the
                  names in VENDORED). They are skipped by default because upstream owns them.

Errors (spec violations): missing/invalid frontmatter, name rules, name != directory,
description empty or > 1024 chars, compatibility > 500 chars, unknown top-level keys,
non-string metadata values, referenced relative files that do not exist.
Warnings (best practices): description < 150 chars or without a "when to use" cue,
body > 500 lines or > ~5000 tokens, absolute Windows paths, no evals/ directory.

Exit codes: 0 ok, 1 errors (or warnings with --strict), 2 bad arguments.
Stdlib only, Python 3.9+.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
VENDORED = {"archify", "find-skills", "playwright-cli"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
WHEN_RE = re.compile(r"\b(use|when|dùng|khi)\b", re.I)
REF_RE = re.compile(r"(?<![\w/$.-])((?:references|scripts|assets|evals|templates|resources|agents)/[\w./-]*[\w/])")
WINPATH_RE = re.compile(r"(?<![\w/])[A-Za-z]:\\[^\s`'\")|]+")


def parse_frontmatter(text: str):
    m = re.match(r"^﻿?---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.S)
    if not m:
        return None, text
    raw, body = m.group(1), m.group(2)
    fm: dict = {}
    key = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        top = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if top and not line.startswith((" ", "\t")):
            key, val = top.group(1), top.group(2).strip()
            fm[key] = {} if (key == "metadata" and not val) else _scalar(val)
        elif key == "metadata" and isinstance(fm.get("metadata"), dict):
            sub = re.match(r"^\s+([A-Za-z0-9_.-]+):\s*(.*)$", line)
            if sub:
                fm["metadata"][sub.group(1)] = sub.group(2).strip()
        elif key and isinstance(fm.get(key), str):
            fm[key] = (fm[key] + " " + line.strip()).strip()  # folded continuation
    return fm, body


def _scalar(val: str):
    if val[:1] in "\"'":
        try:
            return json.loads(val) if val[0] == '"' else val[1:-1].replace("''", "'")
        except json.JSONDecodeError:
            return val.strip("\"'")
    return re.sub(r"^[>|][-+]?\s*", "", val)


def is_vendored(d: Path) -> bool:
    return (d / ".aws-skill-metadata").exists() or d.name in VENDORED


def check(d: Path) -> dict:
    errors, warnings = [], []
    p = d / "SKILL.md"
    text = p.read_text(encoding="utf-8", errors="replace")
    fm, body = parse_frontmatter(text)
    if fm is None:
        return {"skill": d.name, "errors": ["no YAML frontmatter"], "warnings": []}

    name = fm.get("name")
    if not name:
        errors.append("missing name")
    else:
        if len(name) > 64 or not NAME_RE.match(name):
            errors.append(f"invalid name '{name}' (a-z, 0-9, single hyphens, <= 64 chars)")
        if name != d.name:
            errors.append(f"name '{name}' != directory '{d.name}'")

    desc = fm.get("description") or ""
    if not isinstance(desc, str) or not desc.strip():
        errors.append("missing description")
    else:
        if len(desc) > 1024:
            errors.append(f"description {len(desc)} chars > 1024")
        if len(desc) < 150:
            warnings.append(f"description only {len(desc)} chars; say when to use it")
        if not WHEN_RE.search(desc):
            warnings.append("description has no 'Use when / Dùng khi' cue")

    comp = fm.get("compatibility")
    if comp is not None and not (1 <= len(str(comp)) <= 500):
        errors.append("compatibility must be 1-500 chars")
    extra = sorted(set(fm) - SPEC_KEYS)
    if extra:
        errors.append("non-spec top-level keys (move under metadata): " + ", ".join(extra))
    meta = fm.get("metadata")
    if meta is not None and not isinstance(meta, dict):
        errors.append("metadata must be a mapping")

    lines = body.count("\n")
    tokens = len(text) // 4
    if lines > 500:
        warnings.append(f"body {lines} lines > 500; move detail to references/")
    if tokens > 5000:
        warnings.append(f"~{tokens} tokens > 5000; move detail to references/")

    missing = sorted({r for r in REF_RE.findall(body) if not (d / r).exists()})
    if missing:
        errors.append("referenced files missing: " + ", ".join(missing[:8]))
    win = sorted(set(WINPATH_RE.findall(body)))
    if win:
        warnings.append("absolute Windows paths (prefer skill-relative or $ITGVIET_HOME): " + ", ".join(win[:3]))
    if not (d / "evals").is_dir():
        warnings.append("no evals/ (see agentskills.io/skill-creation/evaluating-skills)")
    return {"skill": d.name, "errors": errors, "warnings": warnings}


def collect(paths, include_vendored):
    out = []
    for raw in paths:
        p = Path(raw).resolve()
        if not p.is_dir():
            print(f"error: not a directory: {raw}", file=sys.stderr)
            sys.exit(2)
        dirs = [p] if (p / "SKILL.md").is_file() else sorted(x for x in p.iterdir() if (x / "SKILL.md").is_file())
        out += [x for x in dirs if include_vendored or not is_vendored(x) or x == p]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("paths", nargs="*", default=[str(REPO)])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--include-vendored", action="store_true")
    a = ap.parse_args()

    results = [check(d) for d in collect(a.paths, a.include_vendored)]
    n_err = sum(bool(r["errors"]) for r in results)
    n_warn = sum(bool(r["warnings"]) for r in results)
    if a.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            status = "FAIL" if r["errors"] else ("WARN" if r["warnings"] else "ok")
            print(f"{status:4} {r['skill']}")
            for e in r["errors"]:
                print(f"     error: {e}")
            for w in r["warnings"]:
                print(f"     warn:  {w}")
    print(f"{len(results)} skills: {n_err} with errors, {n_warn} with warnings", file=sys.stderr)
    return 1 if n_err or (a.strict and n_warn) else 0


if __name__ == "__main__":
    sys.exit(main())
