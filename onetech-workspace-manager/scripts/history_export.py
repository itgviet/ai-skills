"""Xuất lịch sử công việc (chỉ đọc) ra data/work_history để dựng dashboard sau này.

Nguồn: OneTech (tasks, timesheet), Feedback Hub (tickets), git commits, và snapshot trạng thái task.
Không gọi PUT/POST/DELETE; không ghi token/cookie ra file.
"""
import csv
import json
import os
import re
import subprocess
from datetime import datetime, date, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from onetech_client import OneTechClient, DEFAULT_USER_ID, PROJECT_ROOT
from feedback_client import FeedbackHubClient

DEFAULT_OUT_DIR = PROJECT_ROOT / "data" / "work_history"
TIMESHEET_START = "2026-02-01"
GIT_ROOTS = [Path(r"D:\Projects"), Path(r"D:\itgviet"), Path(r"D:\Research"), PROJECT_ROOT / "skills"]
GIT_SKIP_DIRS = {"node_modules", ".venv", "venv", "build", "dist", ".gradle", "Pods", "__pycache__", ".dart_tool"}
GIT_MAX_DEPTH = 4
MY_EMAILS = {"vietnt@nexconstruct.asia", "vietnt@onetech.vn", "vietnt@itg.vn"}
MY_NAME_RE = re.compile(r"\bvietnt\b|\bvi[eệ]t\b", re.IGNORECASE)  # "Viet" chỉ khi là một từ riêng (loại TranVietDuc, itgviet)

# Các trường được so sánh để quyết định ghi snapshot mới
SNAPSHOT_FIELDS = ["status", "workflow_status_id", "workflow_status_name", "assignee_id", "sprint_id", "progress", "completed_date"]

_SECRET_KEY_RE = re.compile(r"password|token|cookie|secret|apikey|api_key|authorization", re.IGNORECASE)
_SECRET_VAL_RES = [
    (re.compile(r"([?&](?:token|access_token|key|sig|signature)=)[^&\s\"')]+", re.IGNORECASE), r"\1REDACTED"),
    (re.compile(r"Bearer\s+[A-Za-z0-9._\-]+"), "Bearer REDACTED"),
]


def _scrub(obj: Any) -> Any:
    """Loại bỏ khóa nhạy cảm và che token trong URL trước khi ghi ra đĩa."""
    if isinstance(obj, dict):
        return {k: _scrub(v) for k, v in obj.items() if not _SECRET_KEY_RE.search(str(k))}
    if isinstance(obj, list):
        return [_scrub(v) for v in obj]
    if isinstance(obj, str):
        for rx, rep in _SECRET_VAL_RES:
            obj = rx.sub(rep, obj)
        return obj
    return obj


def _iso(v: Any) -> Optional[str]:
    """Chuẩn hóa thời gian (ISO string / epoch ms / Firestore timestamp) về ISO 8601."""
    if v in (None, ""):
        return None
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v / 1000 if v > 1e11 else v, tz=timezone.utc).isoformat()
    if isinstance(v, dict) and "seconds" in v:
        return datetime.fromtimestamp(int(v["seconds"]), tz=timezone.utc).isoformat()
    return str(v)


def _num(v: Any) -> Optional[float]:
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _write_json(path: Path, data: Any):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_scrub(data), f, ensure_ascii=False, indent=2)


def _write_csv(path: Path, rows: List[Dict[str, Any]], fields: List[str]):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in _scrub(rows):
            w.writerow({k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v) for k, v in r.items()})


# ---------------------------------------------------------------- OneTech

def _user_name(u: Dict[str, Any]) -> str:
    full = f"{(u.get('firstName') or '').strip()} {(u.get('lastName') or '').strip()}".strip()
    return full or (u.get("email") or "").split("@")[0]


def normalize_onetech(raw: Dict[str, Any], user_id: str):
    """Trả về (projects, tasks). Giữ dự án user là thành viên, cộng các task có dính tới user ở dự án khác."""
    users: Dict[str, Dict[str, Any]] = {}
    for pdata in raw["perProject"].values():
        for m in pdata.get("members") or []:
            u = m.get("user") or {}
            if m.get("userId"):
                users[m["userId"]] = {"name": _user_name(u), "email": u.get("email")}

    projects, tasks = [], []
    for p in raw["projects"]:
        pdata = raw["perProject"].get(str(p["id"])) or raw["perProject"].get(p["id"]) or {}
        members = pdata.get("members") or []
        my_member = next((m for m in members if m.get("userId") == user_id), None)
        sprints = {s["id"]: s for s in pdata.get("sprints") or []}
        wf = {w["id"]: w for w in pdata.get("workflowStatuses") or []}
        ptasks = pdata.get("tasks") or []
        titles = {t["id"]: t.get("title") for t in ptasks}

        kept = 0
        for t in ptasks:
            followers = [f.get("userId") or f.get("id") if isinstance(f, dict) else f for f in (t.get("followers") or [])]
            involves_me = user_id in (t.get("assigneeId"), t.get("reporterId")) or user_id in followers
            if not my_member and not involves_me:
                continue
            kept += 1
            sp = sprints.get(t.get("sprintId")) or {}
            w = wf.get(t.get("workflowStatusId")) or {}
            tasks.append({
                "task_id": t["id"],
                "project_id": p["id"],
                "project_key": p.get("key"),
                "project_name": p.get("name"),
                "title": t.get("title"),
                "type": t.get("type"),
                "status": t.get("status"),
                "workflow_status_id": t.get("workflowStatusId"),
                "workflow_status_name": w.get("name"),
                "workflow_status_is_final": w.get("isFinal"),
                "priority": t.get("priority"),
                "severity": t.get("severity"),
                "bug_status": t.get("bugStatus"),
                "points": t.get("points"),
                "estimated_hours": _num(t.get("estimatedHours")),
                "actual_hours": _num(t.get("actualHours")),
                "progress": t.get("progress"),
                "parent_id": t.get("parentId"),
                "parent_title": titles.get(t.get("parentId")),
                "sprint_id": t.get("sprintId"),
                "sprint_name": sp.get("name"),
                "sprint_start": sp.get("startDate"),
                "sprint_end": sp.get("endDate"),
                "assignee_id": t.get("assigneeId"),
                "assignee_name": (users.get(t.get("assigneeId")) or {}).get("name"),
                "reporter_id": t.get("reporterId"),
                "reporter_name": (users.get(t.get("reporterId")) or {}).get("name"),
                "followers": followers,
                "is_mine": t.get("assigneeId") == user_id,
                "involves_me": involves_me,
                "created_at": t.get("createdAt"),
                "updated_at": t.get("updatedAt"),
                "start_date": t.get("startDate"),
                "due_date": t.get("dueDate"),
                "actual_start_date": t.get("actualStartDate"),
                "actual_end_date": t.get("actualEndDate"),
                "completed_date": t.get("completedDate"),
                "description": t.get("description"),
            })
        if my_member or kept:
            projects.append({
                "project_id": p["id"], "key": p.get("key"), "name": p.get("name"), "type": p.get("type"),
                "status": p.get("status"), "department": p.get("department"),
                "start_date": p.get("startDate"), "end_date": p.get("endDate"), "created_at": p.get("createdAt"),
                "is_member": bool(my_member), "my_role": (my_member or {}).get("role"),
                "my_joined_at": (my_member or {}).get("joinedAt"),
                "task_count": kept,
                "sprints": [{"id": s["id"], "name": s.get("name"), "status": s.get("status"),
                             "start_date": s.get("startDate"), "end_date": s.get("endDate")} for s in sprints.values()],
                "workflow_statuses": [{"id": w["id"], "name": w.get("name"), "order": w.get("order"),
                                       "is_final": w.get("isFinal")} for w in wf.values()],
            })
    return projects, tasks, users


def normalize_timesheet(days: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen, rows = set(), []
    for d in days:
        for e in d.get("entries") or []:
            if e.get("id") in seen:
                continue
            seen.add(e.get("id"))
            rows.append({
                "entry_id": e.get("id"),
                "date": (e.get("loggedDate") or d.get("date") or "")[:10],
                "hours": _num(e.get("hours")),
                "activity_type": e.get("activityType"),
                "description": e.get("description"),
                "task_id": e.get("taskId"),
                "task_title": e.get("taskTitle"),
                "task_type": e.get("taskType"),
                "task_status": e.get("taskStatus"),
                "project_id": e.get("projectId"),
                "project_key": e.get("projectKey"),
                "project_name": e.get("projectName"),
                "created_at": e.get("createdAt"),
            })
    rows.sort(key=lambda r: (r["date"], r["entry_id"] or 0))
    return rows


def append_snapshots(path: Path, tasks: List[Dict[str, Any]], now: str) -> int:
    """Ghi snapshot dạng event-sourced: chỉ thêm dòng khi task mới xuất hiện hoặc trường theo dõi thay đổi."""
    last: Dict[int, Dict[str, Any]] = {}
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    last[r["task_id"]] = r
                except Exception:
                    continue
    written = 0
    with open(path, "a", encoding="utf-8") as f:
        for t in tasks:
            cur = {k: t.get(k) for k in SNAPSHOT_FIELDS}
            prev = last.get(t["task_id"])
            if prev and all(prev.get(k) == cur[k] for k in SNAPSHOT_FIELDS):
                continue
            rec = {"snapshot_at": now, "task_id": t["task_id"], "project_id": t["project_id"], **cur,
                   "updated_at": t.get("updated_at"),
                   "change": "baseline" if not prev else ",".join(k for k in SNAPSHOT_FIELDS if prev.get(k) != cur[k])}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            written += 1
    return written


# ---------------------------------------------------------------- Feedback Hub

def normalize_tickets(tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for t in tickets:
        comments = t.get("comments") if isinstance(t.get("comments"), list) else None
        rows.append({
            "ticket_id": t.get("id"),
            "project_key": t.get("projectKey"),
            "title": t.get("title"),
            "type": t.get("type"),
            "severity": t.get("severity"),
            "status": t.get("status"),
            "created_at": _iso(t.get("createdAt")),
            "updated_at": _iso(t.get("updatedAt")),
            "resolved_at": _iso(t.get("resolvedAt") or t.get("closedAt")),
            "client_name": t.get("clientName"),
            "onetech_task_id": t.get("oneTechTaskId"),
            "onetech_project_id": t.get("oneTechProjectId"),
            "image_count": len(t.get("imageUrls") or []),
            "comment_count": len(comments) if comments is not None else t.get("commentCount"),
            "raw": {k: v for k, v in t.items() if k not in ("comments",)},
        })
    rows.sort(key=lambda r: r["created_at"] or "")
    return rows


# ---------------------------------------------------------------- Git

def find_repos(roots: List[Path]) -> List[Path]:
    repos = []

    def walk(d: Path, depth: int):
        try:
            if (d / ".git").exists():
                repos.append(d)
                return
            if depth >= GIT_MAX_DEPTH:
                return
            for c in d.iterdir():
                if c.is_dir() and not c.name.startswith(".") and c.name not in GIT_SKIP_DIRS:
                    walk(c, depth + 1)
        except (PermissionError, OSError):
            pass

    for r in roots:
        if r.exists():
            walk(r, 0)
    return repos


def _is_me(name: str, email: str) -> bool:
    return (email or "").lower() in MY_EMAILS or (email or "").lower().startswith("vietnt@") or bool(MY_NAME_RE.search(name or ""))


def collect_commits(repos: List[Path]):
    """Trả về (commits, failed_repos)."""
    commits, failed = [], []
    for repo in repos:
        try:
            proc = subprocess.run(
                ["git", "-C", str(repo), "log", "--all", "--no-merges", "--numstat",
                 "--format=%x1e%H%x1f%an%x1f%ae%x1f%aI%x1f%s"],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180,
            )
            if proc.returncode != 0:
                raise RuntimeError(f"exit {proc.returncode}: {proc.stderr.strip()[:200]}")
            out = proc.stdout
            remote = subprocess.run(["git", "-C", str(repo), "remote", "get-url", "origin"],
                                    capture_output=True, text=True, timeout=30).stdout.strip()
        except Exception as e:
            print(f"[WARN] git log thất bại ở {repo}: {e}")
            failed.append({"repo": str(repo), "error": str(e)})
            continue
        remote = re.sub(r"//[^/@]+@", "//", remote)  # bỏ credential nhúng trong URL
        for block in out.split("\x1e"):
            if not block.strip():
                continue
            head, _, stat = block.partition("\n")
            parts = head.split("\x1f")
            if len(parts) < 5:
                continue
            h, an, ae, ad, subj = parts[:5]
            if not _is_me(an, ae):
                continue
            files = ins = dels = 0
            for line in stat.strip().splitlines():
                cols = line.split("\t")
                if len(cols) >= 3:
                    files += 1
                    ins += int(cols[0]) if cols[0].isdigit() else 0
                    dels += int(cols[1]) if cols[1].isdigit() else 0
            commits.append({
                "date": ad, "repo": repo.name, "repo_path": str(repo), "remote": remote,
                "hash": h, "author_name": an, "author_email": ae, "subject": subj,
                "files_changed": files, "insertions": ins, "deletions": dels,
            })
    # Cùng một commit có thể nằm ở nhiều bản clone/fork: đánh dấu bản lặp để dashboard lọc
    seen = set()
    for c in commits:
        c["is_duplicate"] = c["hash"] in seen
        seen.add(c["hash"])
    commits.sort(key=lambda c: c["date"])
    return commits, failed


# ---------------------------------------------------------------- Run

README = """# work_history

Read-only export of the user's work history, regenerated by
`python skills/onetech-workspace-manager/scripts/cli.py history`.
All files except `status_snapshots.jsonl` are overwritten on each run. Timestamps are ISO 8601 (UTC unless an offset is given).
Tokens, cookies, passwords and signed-URL tokens are stripped before writing.

| File | Source | Content |
|---|---|---|
| `manifest.json` | all | Run time, user id, counts per source, list of git repos scanned, errors per source. |
| `projects.json` | OneTech `/api/projects` + `/members` `/sprints` `/workflow-statuses` | Projects the user is a member of (or has tasks in): `project_id, key, name, type, status, department, start_date, end_date, created_at, is_member, my_role, my_joined_at, task_count, sprints[{id,name,status,start_date,end_date}], workflow_statuses[{id,name,order,is_final}]`. |
| `users.json` | OneTech `/members` | `{userId: {name, email}}` for every member seen in any project. |
| `tasks.json` / `tasks.csv` | OneTech `/api/projects/{id}/tasks` | One row per task: `task_id, project_id, project_key, project_name, title, type, status, workflow_status_id, workflow_status_name, workflow_status_is_final, priority, severity, bug_status, points, estimated_hours, actual_hours, progress, parent_id, parent_title, sprint_id, sprint_name, sprint_start, sprint_end, assignee_id, assignee_name, reporter_id, reporter_name, followers, is_mine (assignee is me), involves_me (assignee/reporter/follower), created_at, updated_at, start_date, due_date, actual_start_date, actual_end_date, completed_date`. `description` is only in the JSON. Includes all tasks of member projects plus tasks involving the user elsewhere. |
| `timesheet.json` / `timesheet.csv` | OneTech `/api/users/me/timesheet?start&end` (monthly) | One row per time entry: `entry_id, date (YYYY-MM-DD), hours, activity_type, description, task_id, task_title, task_type, task_status, project_id, project_key, project_name, created_at`. Data starts 2026-02-09. |
| `tickets.json` / `tickets.csv` | Feedback Hub (Firestore `tickets`) | `ticket_id, project_key, title, type, severity, status, created_at, updated_at, resolved_at, client_name, onetech_task_id, onetech_project_id, image_count, comment_count`; JSON also has `raw` (all ticket fields, scrubbed). |
| `commits.json` / `commits.csv` | `git log --all --no-merges --numstat` in repos under D:\\Projects, D:\\itgviet, D:\\Research, D:\\ITGVietAssistant\\skills | Commits authored by the user (email vietnt@nexconstruct.asia / vietnt@onetech.vn / vietnt@itg.vn / any `vietnt@`, or name with the word "vietnt"/"Viet"/"Việt"): `date, repo, repo_path, remote, hash, author_name, author_email, subject, files_changed, insertions, deletions, is_duplicate`. The same commit can live in several clones/forks: one row per (repo, hash); `is_duplicate` is true on every copy after the first, so filter it out to count unique commits. |
| `status_snapshots.jsonl` | derived from tasks | **Append-only, never overwritten.** OneTech has no task-history API, so each run appends a line for every task that is new (`change: "baseline"`) or whose `status, workflow_status_id, workflow_status_name, assignee_id, sprint_id, progress, completed_date` changed since its last line (`change` lists the changed fields). Fields: `snapshot_at, task_id, project_id, <tracked fields>, updated_at, change`. Replaying lines per task in order gives its state over time; a task is unchanged between two lines. `snapshot_runs.jsonl` records every run time, so "no line" means "unchanged as of that run". Run daily for useful granularity. |
| `snapshot_runs.jsonl` | derived | Append-only: `{run_at, tasks_seen, lines_written}` per run. |
"""


def run(out_dir: Path, sources: set, ts_start: str, user_id: str = DEFAULT_USER_ID):
    out_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    counts: Dict[str, Any] = {}
    errors: Dict[str, str] = {}
    manifest: Dict[str, Any] = {"generated_at": now, "user_id": user_id, "sources": sorted(sources)}

    if "onetech" in sources:
        print("[1/3] OneTech: projects, tasks, sprints, members, workflow statuses, timesheet...")
        try:
            raw = OneTechClient().fetch_history_raw(ts_start, date.today().isoformat(), user_id)
            projects, tasks, users = normalize_onetech(raw, user_id)
            failed = raw.get("failed") or []
            # Dự án lấy tasks/members thất bại: giữ lại dữ liệu lần chạy trước thay vì làm mất
            failed_pids = {int(m.group(1)) for f in failed
                           for m in [re.match(r"/api/projects/(\d+)/(?:tasks|members)$", f["url"])] if m}
            prev_tasks_path = out_dir / "tasks.json"
            if failed_pids and prev_tasks_path.exists():
                kept_pids = {p["project_id"] for p in projects}
                prev = json.loads(prev_tasks_path.read_text(encoding="utf-8"))
                carried = [t for t in prev if t["project_id"] in failed_pids - kept_pids]
                tasks.extend(carried)
                counts["tasks_carried_over"] = len(carried)
            if failed:
                errors["onetech_fetch"] = f"{len(failed)} request(s) failed after retries: " + ", ".join(f"{f['url']} ({f['error']})" for f in failed)
                print(f"[WARN] {errors['onetech_fetch']}")
            timesheet = normalize_timesheet(raw["timesheet"])
            _write_json(out_dir / "projects.json", projects)
            _write_json(out_dir / "users.json", users)
            _write_json(out_dir / "tasks.json", tasks)
            _write_csv(out_dir / "tasks.csv", tasks, [k for k in tasks[0].keys() if k != "description"] if tasks else ["task_id"])
            _write_json(out_dir / "timesheet.json", timesheet)
            _write_csv(out_dir / "timesheet.csv", timesheet, list(timesheet[0].keys()) if timesheet else ["entry_id"])
            fresh = [t for t in tasks if t["project_id"] not in failed_pids]
            snap_lines = append_snapshots(out_dir / "status_snapshots.jsonl", fresh, now)
            with open(out_dir / "snapshot_runs.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps({"run_at": now, "tasks_seen": len(tasks), "lines_written": snap_lines}) + "\n")
            counts.update({
                "projects_total": len(raw["projects"]), "projects_exported": len(projects),
                "tasks": len(tasks), "tasks_mine": sum(1 for t in tasks if t["is_mine"]),
                "timesheet_entries": len(timesheet), "timesheet_days": len({r["date"] for r in timesheet}),
                "timesheet_hours": round(sum(r["hours"] or 0 for r in timesheet), 2),
                "snapshot_lines_written": snap_lines,
            })
        except Exception as e:
            errors["onetech"] = str(e)
            print(f"[LỖI] OneTech: {e}")

    if "tickets" in sources:
        print("[2/3] Feedback Hub tickets...")
        try:
            tickets = normalize_tickets(FeedbackHubClient().get_tickets())
            _write_json(out_dir / "tickets.json", tickets)
            _write_csv(out_dir / "tickets.csv", tickets, [k for k in tickets[0].keys() if k != "raw"] if tickets else ["ticket_id"])
            counts["tickets"] = len(tickets)
        except Exception as e:
            errors["tickets"] = str(e)
            print(f"[LỖI] Feedback Hub: {e}")

    if "git" in sources:
        print("[3/3] Git commits...")
        try:
            repos = find_repos(GIT_ROOTS)
            commits, failed_repos = collect_commits(repos)
            if failed_repos:
                errors["git_repos_failed"] = "; ".join(f"{f['repo']} ({f['error']})" for f in failed_repos)
            _write_json(out_dir / "commits.json", commits)
            _write_csv(out_dir / "commits.csv", commits, list(commits[0].keys()) if commits else ["hash"])
            manifest["git_repos"] = [str(r) for r in repos]
            counts.update({"git_repos": len(repos), "git_repos_with_my_commits": len({c["repo_path"] for c in commits}),
                           "commits": len(commits), "commits_unique": sum(1 for c in commits if not c["is_duplicate"])})
        except Exception as e:
            errors["git"] = str(e)
            print(f"[LỖI] Git: {e}")

    # Chạy một phần (--sources) thì giữ lại counts của các nguồn khác từ lần chạy trước
    manifest_path = out_dir / "manifest.json"
    if manifest_path.exists() and sources != {"onetech", "tickets", "git"}:
        try:
            prev = json.loads(manifest_path.read_text(encoding="utf-8"))
            counts = {**prev.get("counts", {}), **counts}
            manifest = {**prev, **manifest}
        except Exception:
            pass
    manifest.update({"counts": counts, "errors": errors})
    _write_json(out_dir / "manifest.json", manifest)
    (out_dir / "README.md").write_text(README, encoding="utf-8")

    print(f"\n=== Work history đã xuất ra {out_dir} ===")
    for k, v in counts.items():
        print(f"- {k}: {v}")
    for k, v in errors.items():
        print(f"- [LỖI] {k}: {v}")
