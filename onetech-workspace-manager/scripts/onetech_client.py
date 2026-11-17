import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from playwright.sync_api import sync_playwright
import tempfile
import time as _time


def _store_write(data: dict) -> None:
    """Write tasks_store.json in one step (temp file + replace): a plain open("w") truncates first, and a reader in that
    window (the sync below, the dashboard) saw an empty file. Retries while another process holds the file (Windows)."""
    STORE_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=STORE_FILE.name + ".", suffix=".tmp", dir=str(STORE_FILE.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        for i in range(60):
            try:
                os.replace(tmp, STORE_FILE)
                return
            except PermissionError:
                if i == 59:
                    raise
                _time.sleep(0.05)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def _store_read() -> dict:
    """Read tasks_store.json, retrying while a writer is replacing it. Raises when it stays unreadable: treating it as
    empty made the sync write back only the synced project and drop every other one."""
    err = None
    for _ in range(6):
        try:
            with open(STORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, PermissionError, UnicodeDecodeError) as e:
            err = e
            _time.sleep(0.1)
    raise RuntimeError(f"tasks_store.json unreadable, sync aborted so nothing is lost: {err}")

sys.stdout.reconfigure(encoding='utf-8')

# Dynamic resolution: scripts -> skill -> skills -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]

def _resolve_user_data_dir() -> Path:
    env_profile = os.environ.get("PLAYWRIGHT_PROFILE_DIR")
    if env_profile and Path(env_profile).exists():
        return Path(env_profile)
    proj_profile = PROJECT_ROOT / "data" / "playwright_profile"
    if proj_profile.exists():
        return proj_profile
    home = Path.home()
    for candidate in [
        home / ".gemini" / "config" / "playwright_profile",
        home / ".kiro" / "playwright_profile",
        home / ".config" / "itgviet" / "playwright_profile"
    ]:
        if candidate.exists():
            return candidate
    return proj_profile

USER_DATA_DIR = _resolve_user_data_dir()
STORE_FILE = PROJECT_ROOT / "data" / "tasks_store.json"
EVENTS_FILE = PROJECT_ROOT / "data" / "dashboard_events.jsonl"


def event_origin() -> Dict[str, str]:
    """Who is acting through this CLI, for the dashboard's change log: a Claude Code session (its id is in the
    environment) or the user at a terminal."""
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID")
    return {"via": "cli", "actor": f"claude:{sid}" if sid else "me"}


def log_dashboard_event(event_type: str, message: str, meta: Optional[Dict[str, Any]] = None) -> None:
    """Append one line to data/dashboard_events.jsonl; the dashboard reads it within seconds into its change log."""
    record = {"timestamp": datetime.now().isoformat(), "type": event_type, "message": message, "meta": {**(meta or {}), **event_origin()}}
    try:
        EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(EVENTS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as err:
        print("[Warning] Could not write dashboard event:", err)
DEFAULT_USER_ID = "19bcfc0a-1108-40bd-810a-abbe7af46fc5"

# CLI status -> (workflow status name on the project's board, bugStatus).
# The workflow status ID is resolved per project by name: every project has its own IDs.
STATUS_WORKFLOW = {
    "todo": ("To Do", "new"),
    "in_progress": ("In Progress", "assigned"),
    "implementing": ("Implementing", "assigned"),
    "review": ("Review", "fixed"),
    "done": ("Done", "closed"),
    "cancel": ("To Do", "closed"),  # OneTech native cancel: status=cancel on the To Do column
}


class OneTechClient:
    def __init__(self, user_data_dir: Path = USER_DATA_DIR):
        self.user_data_dir = user_data_dir

    def _sync_task_to_local_store(self, task_id: int, payload: Dict[str, Any], res: Dict[str, Any] = None):
        """Tự động đồng bộ trạng thái task vào tasks_store.json và dashboard_events.jsonl."""
        try:
            if not STORE_FILE.exists():
                return
            data = _store_read()

            tasks = data.get("tasks", [])
            target = None
            for t in tasks:
                if t.get("onetech_task_id") == task_id or str(t.get("task_id")) == str(task_id):
                    target = t
                    break

            status_map = {
                "todo": "TODO",
                "in_progress": "IN_PROGRESS",
                "implementing": "IN_PROGRESS",
                "review": "REVIEW",
                "done": "DONE",
                "cancel": "CANCELLED"
            }

            updated = False
            new_st_upper = None
            if "status" in payload:
                st = str(payload["status"]).lower()
                new_st_upper = status_map.get(st, st.upper())
                if target:
                    target["status"] = new_st_upper
                    if new_st_upper == "DONE":
                        target["completed_at"] = datetime.now().isoformat()
                    updated = True

            if target:
                if "title" in payload:
                    target["title"] = payload["title"]
                    updated = True
                if "workflowStatusId" in payload:
                    target["workflowStatusId"] = payload["workflowStatusId"]
                    updated = True
                if "bugStatus" in payload:
                    target["bugStatus"] = payload["bugStatus"]
                    updated = True
                if "priority" in payload:
                    p_map = {"critical": "P0-CRITICAL", "high": "P1-HIGH", "medium": "P2-MEDIUM", "low": "P3-LOW"}
                    target["priority"] = p_map.get(str(payload["priority"]).lower(), str(payload["priority"]).upper())
                    updated = True

            if updated:
                data["last_updated"] = datetime.now().isoformat()
                _store_write(data)

            # Log real-time event so Dashboard UI picks it up immediately
            msg = f"Task #{task_id} updated" + (f" -> {new_st_upper}" if new_st_upper else "")
            record = {
                "timestamp": datetime.now().isoformat(),
                "type": "TASK_UPDATED",
                "message": msg,
                "meta": {"task_id": task_id, "payload": payload, **event_origin()}
            }
            EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(EVENTS_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            print("[Warning] Could not sync task update to local store:", e)

    # ---- one browser profile, several processes ----
    # The dashboard engine (localhost:8988) keeps this profile open in a long-lived headless browser. Chrome locks the
    # cookie store of a profile in use, so a second browser on it reads no login and OneTech answers 401 "Unauthorized":
    # that is NOT an expired session. Before opening the profile, ask the engine to lend it (it closes its browser and
    # stays off until we release it or the lease runs out). No engine running = nothing to ask.
    ENGINE_URL = os.environ.get("ONETECH_ENGINE_URL", "http://127.0.0.1:8988")

    def _engine_post(self, path: str, body: dict, timeout: float):
        import urllib.request
        req = urllib.request.Request(self.ENGINE_URL + path, data=json.dumps(body).encode("utf-8"),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8") or "{}")

    def profile_lease(self, seconds: int = 180):
        """Context manager: hold the browser profile for this process. Use it around any code that opens
        self.user_data_dir itself (e.g. a visible login window): `with client.profile_lease(900): ...`."""
        from contextlib import contextmanager

        @contextmanager
        def _lease():
            leased = False
            if not getattr(self, "_in_engine", False):
                try:
                    leased = bool(self._engine_post("/api/onetech/gateway/lease", {"seconds": seconds, "holder": f"pid {os.getpid()}"}, 3.0).get("success"))
                except Exception:
                    leased = False          # engine not running (or old engine): nothing to coordinate with
            try:
                yield leased
            finally:
                if leased:
                    try:
                        self._engine_post("/api/onetech/gateway/release", {"holder": f"pid {os.getpid()}"}, 5)
                    except Exception:
                        pass
        return _lease()

    def _execute_browser(self, callback):
        with self.profile_lease():
            return self._execute_browser_unleased(callback)

    def _execute_browser_unleased(self, callback):
        """Khởi chạy Chromium headless với persistent profile để gọi API/DOM an toàn (tối ưu băng thông)."""
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(self.user_data_dir),
                headless=True
            )
            page = context.pages[0] if context.pages else context.new_page()
            # Tối ưu băng thông: chặn các tài nguyên nặng (ảnh, font, video, css) không cần cho API fetch
            try:
                def _filter_route(route):
                    if route.request.resource_type in ["image", "media", "font", "stylesheet"]:
                        route.abort()
                    else:
                        route.continue_()
                page.route("**/*", _filter_route)
            except Exception:
                pass
            page.goto("https://workspace.onetech.vn", wait_until="commit", timeout=35000)
            page.wait_for_timeout(1000)
            result = callback(page)
            context.close()
            return result

    @staticmethod
    def _workflow_status_id(page, project_id: int, status: str) -> int:
        """Look up the workflowStatusId of a CLI status in this project's own workflow."""
        name = STATUS_WORKFLOW[status][0]
        statuses = page.evaluate(f"() => fetch('/api/projects/{int(project_id)}/workflow-statuses').then(r => r.json())")
        for s in statuses:
            if str(s.get("name", "")).strip().lower() == name.lower():
                return s["id"]
        raise ValueError(f"Project #{project_id} has no workflow status named '{name}'")

    def get_current_user(self) -> Dict[str, Any]:
        """Lấy thông tin tài khoản đang đăng nhập."""
        return self._execute_browser(
            lambda page: page.evaluate("() => fetch('/api/auth/user').then(r => r.json())")
        )

    def get_projects(self) -> List[Dict[str, Any]]:
        """Lấy danh sách dự án của user."""
        return self._execute_browser(
            lambda page: page.evaluate("() => fetch('/api/my-projects').then(r => r.json())")
        )

    def get_sprints(self, project_id: int = 82) -> List[Dict[str, Any]]:
        """Lấy danh sách Sprints trong dự án."""
        return self._execute_browser(
            lambda page: page.evaluate(f"() => fetch('/api/projects/{project_id}/sprints').then(r => r.json())")
        )

    def get_members(self, project_id: int = 82) -> List[Dict[str, Any]]:
        """Lấy danh sách thành viên dự án."""
        return self._execute_browser(
            lambda page: page.evaluate(f"() => fetch('/api/projects/{project_id}/members').then(r => r.json())")
        )

    def get_tasks(self, project_id: int = 82, sprint_id: Optional[int] = None, assignee_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lấy danh sách tasks, có thể lọc theo sprint hoặc người phụ trách."""
        def action(page):
            tasks = page.evaluate(f"() => fetch('/api/projects/{project_id}/tasks').then(r => r.json())")
            if not isinstance(tasks, list):
                # e.g. {"message": "Unauthorized"} when the OneTech login in the browser profile expired.
                msg = tasks.get("message") if isinstance(tasks, dict) else tasks
                raise RuntimeError(f"OneTech không trả danh sách task ({msg}). Đăng nhập lại OneTech rồi chạy lại.")
            if sprint_id is not None:
                tasks = [t for t in tasks if t.get("sprintId") == sprint_id]
            if assignee_id is not None:
                tasks = [t for t in tasks if t.get("assigneeId") == assignee_id]
            return tasks
        return self._execute_browser(action)

    def update_task(self, task_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Cập nhật thuộc tính của task (tự động map workflowStatusId khi đổi status)."""
        if payload.get("description"):
            payload["description"] = self._markdown_to_html(payload["description"])
        raw_st = str(payload.get("status", "")).lower()
        if raw_st in STATUS_WORKFLOW and "bugStatus" not in payload:
            payload["bugStatus"] = STATUS_WORKFLOW[raw_st][1]

        def action(page):
            # workflowStatusId differs per project (DTGenius #76: 333-338, insightScanX #82: 405-410),
            # so it is looked up from the task's own project instead of a hardcoded table.
            # Cancel is OneTech's own status on the To Do column: sending a workflowStatusId with it
            # makes the server reset status to "todo", so cancel only sends status + bugStatus.
            if raw_st in STATUS_WORKFLOW and raw_st != "cancel" and "workflowStatusId" not in payload:
                project_id = page.evaluate(f"() => fetch('/api/tasks/{task_id}').then(r => r.json()).then(t => t.projectId)")
                payload["workflowStatusId"] = self._workflow_status_id(page, project_id, raw_st)
            js_code = f"""() => fetch('/api/tasks/{task_id}', {{
                method: 'PUT',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({json.dumps(payload)})
            }}).then(r => r.json())"""
            return page.evaluate(js_code)
        res = self._execute_browser(action)
        self._sync_task_to_local_store(task_id, payload, res)
        return res

    def create_task(self, project_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo task mới hoặc epic mới trên dự án."""
        if payload.get("description"):
            payload["description"] = self._markdown_to_html(payload["description"])
        raw_st = str(payload.get("status") or "todo").lower()
        payload["status"] = raw_st
        if raw_st in STATUS_WORKFLOW and "bugStatus" not in payload:
            payload["bugStatus"] = STATUS_WORKFLOW[raw_st][1]
        def action(page):
            if raw_st in STATUS_WORKFLOW and raw_st != "cancel" and "workflowStatusId" not in payload:
                payload["workflowStatusId"] = self._workflow_status_id(page, project_id, raw_st)
            return page.evaluate("""async ([pid, data]) => {
                const res = await fetch(`/api/projects/${pid}/tasks`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                return await res.json();
            }""", [project_id, payload])
        return self._execute_browser(action)

    def upload_image(self, image_path: str) -> str:
        """Tải ảnh lên OneTech CDN (/api/upload-image) và trả về URL ảnh dạng /uploads/..."""
        import base64
        from pathlib import Path
        img_p = Path(image_path)
        if not img_p.exists():
            raise FileNotFoundError(f"Không tìm thấy file ảnh: {image_path}")

        with open(img_p, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("utf-8")

        file_name = img_p.name
        def action(page):
            js_code = f"""async () => {{
                const b64 = "{b64_data}";
                const byteCharacters = atob(b64);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {{
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }}
                const byteArray = new Uint8Array(byteNumbers);
                const blob = new Blob([byteArray], {{ type: 'image/png' }});
                const file = new File([blob], '{file_name}', {{ type: 'image/png' }});

                const formData = new FormData();
                formData.append('image', file);

                const res = await fetch('/api/upload-image', {{
                    method: 'POST',
                    body: formData
                }});
                if (!res.ok) throw new Error('Upload image failed with status: ' + res.status);
                const data = await res.json();
                return data.url;
            }}"""
            return page.evaluate(js_code)
        return self._execute_browser(action)

    @staticmethod
    def _markdown_to_html(text: str) -> str:
        """Chuyển Markdown đơn giản sang HTML cho field description.

        OneTech render description bằng innerHTML (khối prose), KHÔNG parse markdown,
        nên ### / - / ** gửi thẳng sẽ hiện nguyên văn và dấu < > bị nuốt như thẻ HTML.
        Nếu text đã là HTML (bắt đầu bằng thẻ khối) thì giữ nguyên.
        """
        if not text:
            return ""
        import html as _html
        t = text.replace("\r\n", "\n").strip()
        if re.match(r"^\s*<(!--|h[1-6]|p|ul|ol|div|table|blockquote)\b", t, flags=re.I):
            return t

        def inline(s: str) -> str:
            s = _html.escape(s, quote=False)
            s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
            s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
            s = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"<em>\1</em>", s)
            s = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", r'<img src="\2" alt="\1">', s)
            s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
            return s

        out, para, list_tag = [], [], None

        def flush_para():
            if para:
                out.append("<p>" + "<br>".join(para) + "</p>")
                para.clear()

        def close_list():
            nonlocal list_tag
            if list_tag:
                out.append(f"</{list_tag}>")
                list_tag = None

        for raw in t.split("\n"):
            line = raw.rstrip()
            if not line.strip():
                flush_para(); close_list(); continue
            m = re.match(r"^(#{1,6})\s+(.*)$", line)
            if m:
                flush_para(); close_list()
                lvl = min(len(m.group(1)) + 1, 6)  # ### -> h4 cho vừa cỡ chữ của prose-sm
                out.append(f"<h{lvl}>{inline(m.group(2).strip())}</h{lvl}>")
                continue
            m = re.match(r"^\s*[-*•]\s+(.*)$", line)
            if m:
                flush_para()
                if list_tag != "ul":
                    close_list(); out.append("<ul>"); list_tag = "ul"
                out.append(f"<li>{inline(m.group(1).strip())}</li>")
                continue
            m = re.match(r"^\s*\d+[.)]\s+(.*)$", line)
            if m:
                flush_para()
                if list_tag != "ol":
                    close_list(); out.append("<ol>"); list_tag = "ol"
                out.append(f"<li>{inline(m.group(1).strip())}</li>")
                continue
            close_list()
            para.append(inline(line.strip()))
        flush_para(); close_list()
        return "\n".join(out)

    @staticmethod
    def _sanitize_markdown(text: str) -> str:
        """Chuyển đổi các thẻ HTML sang Markdown/Plain text để tránh lỗi hiển thị trên OneTech."""
        if not text:
            return ""
        import re
        t = text
        t = re.sub(r'<strong>(.*?)</strong>', r'**\1**', t, flags=re.DOTALL)
        t = re.sub(r'<b>(.*?)</b>', r'**\1**', t, flags=re.DOTALL)
        t = re.sub(r'<code>(.*?)</code>', r"'\1'", t, flags=re.DOTALL)
        t = re.sub(r'<li>(.*?)</li>', r'• \1\n', t, flags=re.DOTALL)
        t = re.sub(r'<p>(.*?)</p>', r'\1\n', t, flags=re.DOTALL)
        t = re.sub(r'<br\s*/?>', '\n', t)
        t = re.sub(r'<[^>]+>', '', t)  # Xóa các thẻ HTML còn sót
        t = re.sub(r'\n{3,}', '\n\n', t)
        return t.strip()

    def get_task(self, task_id: int, live: bool = False) -> Optional[Dict[str, Any]]:
        """Lấy thông tin chi tiết một task (ưu tiên đọc siêu tốc từ tasks_store.json, dùng live=True để gọi API)."""
        if not live and STORE_FILE.exists():
            try:
                with open(STORE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for t in data.get("tasks", []):
                    if t.get("onetech_task_id") == task_id or t.get("id") == task_id or t.get("task_id") == f"TASK-{task_id}":
                        return t
            except Exception:
                pass

        def action(page):
            return page.evaluate(f"() => fetch('/api/tasks/{task_id}').then(r => r.json())")
        return self._execute_browser(action)

    def get_comments(self, task_id: int) -> List[Dict[str, Any]]:
        """Lấy danh sách bình luận của task từ OneTech Workspace."""
        def action(page):
            return page.evaluate(f"() => fetch('/api/tasks/{task_id}/comments').then(r => r.json())")
        res = self._execute_browser(action)
        return res if isinstance(res, list) else []

    def delete_comment(self, task_id: int, comment_id: int) -> Dict[str, Any]:
        """Xóa bình luận khỏi task trên OneTech Workspace."""
        def action(page):
            js_code = f"""() => fetch('/api/tasks/{task_id}/comments/{comment_id}', {{
                method: 'DELETE'
            }}).then(r => ({{ status: r.status, ok: r.ok }}))"""
            return page.evaluate(js_code)
        return self._execute_browser(action)

    def add_comment(self, task_id: int, content: str, author_id: str = None) -> Dict[str, Any]:
        """Đăng bình luận vào Task (Tự động chuẩn hóa Markdown/Text thuần, chống lỗi lộ thẻ HTML)."""
        uid = author_id or DEFAULT_USER_ID
        clean_content = self._sanitize_markdown(content)
        def action(page):
            js_code = f"""() => fetch('/api/tasks/{task_id}/comments', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({json.dumps({'content': clean_content, 'authorId': uid})})
            }}).then(r => r.json())"""
            return page.evaluate(js_code)
        return self._execute_browser(action)

    def sync_to_local_store(self, project_id: int = 82, user_id: str = DEFAULT_USER_ID, project_name: str = "") -> int:
        """Đồng bộ task của dự án vào tasks_store.json (Hỗ trợ đa dự án & bảo toàn ghi chú/chat)."""
        def action(page):
            tasks = page.evaluate(f"() => fetch('/api/projects/{project_id}/tasks').then(r => r.json())")
            sprints_raw = page.evaluate(f"() => fetch('/api/projects/{project_id}/sprints').then(r => r.json())")
            if isinstance(tasks, dict) and (tasks.get("message") == "Unauthorized" or tasks.get("statusCode") == 401):
                raise RuntimeError("Phiên đăng nhập OneTech đã hết hạn (Unauthorized), vui lòng bấm Đăng nhập lại.")
            if isinstance(sprints_raw, dict) and (sprints_raw.get("message") == "Unauthorized" or sprints_raw.get("statusCode") == 401):
                raise RuntimeError("Phiên đăng nhập OneTech đã hết hạn (Unauthorized), vui lòng bấm Đăng nhập lại.")
            if not isinstance(tasks, list):
                tasks = []
            if not isinstance(sprints_raw, list):
                sprints_raw = []
            sprints = {s["id"]: s["name"] for s in sprints_raw if isinstance(s, dict) and "id" in s}

            members_raw = page.evaluate(f"() => fetch('/api/projects/{project_id}/members').then(r => r.json()).catch(() => [])")
            members_map = {}
            for m in (members_raw or []):
                u = m.get("user") or {}
                fn = (u.get("firstName") or "").strip()
                ln = (u.get("lastName") or "").strip()
                full = f"{fn} {ln}".strip()
                email = ((u.get("email") or "").split("@")[0]).strip()
                alias = email or full or "user"
                disp = f"{full} ({alias})" if full and alias and full != alias else (full or alias)
                members_map[m.get("userId")] = {
                    "id": m.get("userId"),
                    "name": disp,
                    "alias": alias,
                    "email": u.get("email")
                }

            priority_map = {"critical": "P0-CRITICAL", "high": "P1-HIGH", "medium": "P2-MEDIUM", "low": "P3-LOW"}
            status_map = {"todo": "TODO", "in_progress": "IN_PROGRESS", "review": "REVIEW", "done": "DONE", "cancel": "CANCELLED", "pending": "PENDING"}

            # Load existing store
            existing_data = {}
            existing_tasks_map = {}
            if STORE_FILE.exists():
                existing_data = _store_read()   # raises rather than wiping the other projects
                for t in existing_data.get("tasks", []):
                    if t.get("onetech_task_id"):
                        existing_tasks_map[t["onetech_task_id"]] = t

            # Filter out current project tasks from existing list to replace with fresh sync
            other_project_tasks = [t for t in existing_data.get("tasks", []) if t.get("project_id", 82) != project_id]

            p_name = project_name
            if not p_name:
                p_name = f"Project #{project_id}"
                # Try finding from projects cache
                prjs_file = STORE_FILE.parent / "projects.json"
                if prjs_file.exists():
                    try:
                        with open(prjs_file, "r", encoding="utf-8") as pf:
                            for p in json.load(pf):
                                if p.get("id") == project_id:
                                    p_name = p.get("name", p_name)
                                    break
                    except Exception:
                        pass

            formatted = []
            idx = len(other_project_tasks) + 1
            # Local ids must stay unique across the whole store: keep a task's previous id only if nobody else uses it,
            # otherwise (and for new tasks) take the next number above every id already in use.
            def _id_num(v):
                try:
                    return int(str(v).replace("TASK-", ""))
                except Exception:
                    return 0
            other_ids = {str(x.get("task_id")) for x in other_project_tasks if x.get("task_id")}
            all_known = other_ids | {str(p.get("task_id")) for p in existing_tasks_map.values() if p.get("task_id")}
            next_num = max([_id_num(v) for v in all_known] + [len(other_project_tasks) + len(tasks)]) + 1
            assigned_ids = set()
            for t in tasks:
                aid = t.get("assigneeId")
                assignees = t.get("assignees") or []
                is_mine = (aid == user_id) or any((a.get("id") == user_id if isinstance(a, dict) else a == user_id) for a in assignees)

                m_info = members_map.get(aid, {})
                assignee_name = m_info.get("name") if aid else "Unassigned"
                assignee_alias = m_info.get("alias") if aid else "unassigned"

                raw_status = (t.get("status") or "todo").lower()
                raw_priority = (t.get("priority") or "medium").lower()
                sp_name = sprints.get(t.get("sprintId"), f"Sprint {t.get('sprintId')}")
                t_id = t.get("id")
                prev = existing_tasks_map.get(t_id, {})
                parent_id = t.get("parentId")
                tasks_lookup = {item["id"]: (item.get("title") or item.get("name")) for item in tasks}
                parent_title = tasks_lookup.get(parent_id) if parent_id else None

                local_id = prev.get("task_id")
                if not local_id or local_id in assigned_ids or local_id in other_ids:
                    local_id = f"TASK-{next_num:03d}"
                    next_num += 1
                assigned_ids.add(local_id)

                task_obj = {
                    "task_id": local_id,
                    "onetech_task_id": t_id,
                    "project_id": project_id,
                    "project": p_name,
                    "title": t.get("title") or t.get("name"),
                    "parent_id": parent_id,
                    "parent_title": parent_title,
                    "sprint": sp_name,
                    "sprint_id": t.get("sprintId"),
                    "category": "APP" if "[APP" in (t.get("title") or "") else ("CMS" if "[CMS" in (t.get("title") or "") else "DEV"),
                    "priority": priority_map.get(raw_priority, "P2-MEDIUM"),
                    "status": status_map.get(raw_status, raw_status.upper() or "TODO"),  # unknown statuses kept, never silently TODO
                    "type": t.get("type", "task"),
                    "bugStatus": t.get("bugStatus") or ("new" if t.get("type") == "bug" else None),
                    "workflowStatusId": t.get("workflowStatusId"),
                    "assignee_id": aid,
                    "assignee_name": assignee_name,
                    "assignee_alias": assignee_alias,
                    "is_mine": is_mine,
                    "created_at": t.get("createdAt") or datetime.now().isoformat(),
                    "completed_at": t.get("completedAt") if raw_status == "done" else None,
                    "due_date": t.get("dueDate"),
                    "estimate_hours": t.get("estimate"),
                    "acceptance_criteria": [f"Nghiệm thu OneTech Task #{t_id}", f"Sprint: {sp_name}"],
                    "notes": t.get("description") or f"Đồng bộ từ OneTech Workspace Task #{t_id}",
                    "discussions": prev.get("discussions", []),
                    "custom_requirements": prev.get("custom_requirements", []),
                    "dev_solution": prev.get("dev_solution", "")
                }
                formatted.append(task_obj)
                idx += 1

            all_tasks = other_project_tasks + formatted
            STORE_FILE.parent.mkdir(parents=True, exist_ok=True)
            _store_write({
                "version": "2.0",
                "system": "Antigravity Multi-Project Task Store",
                "last_updated": datetime.now().isoformat(),
                "next_task_index": len(all_tasks) + 1,
                "user": {"name": "Viet Nguyen Tung", "email": "vietnt@onetech.vn", "role": "Team Lead / Developer"},
                # syncing another project in the background must not switch the project you work in
                "current_project_id": existing_data.get("current_project_id") or project_id,
                "tasks": all_tasks
            })

            return len(formatted)

        return self._execute_browser(action)

    def get_time_entries(self, task_id: int) -> List[Dict[str, Any]]:
        """Lấy danh sách các bản ghi timesheet của task."""
        return self._execute_browser(
            lambda page: page.evaluate(f"() => fetch('/api/tasks/{task_id}/time-entries', {{ credentials: 'include' }}).then(r => r.json())")
        )

    def get_daily_time(self, date_str: Optional[str] = None) -> Dict[str, Any]:
        """Lấy tổng số giờ đã log trong ngày (so với mục tiêu 8.0h)."""
        d = date_str or datetime.now().strftime("%Y-%m-%d")
        return self._execute_browser(
            lambda page: page.evaluate(f"() => fetch('/api/users/me/daily-time?date={d}', {{ credentials: 'include' }}).then(r => r.json())")
        )

    def get_user_timesheet(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Lấy bảng thống kê timesheet của user theo khoảng thời gian."""
        res = self._execute_browser(
            lambda page: page.evaluate(f"() => fetch('/api/users/me/timesheet?start={start_date}&end={end_date}', {{ credentials: 'include' }}).then(r => r.json())")
        )
        if isinstance(res, dict) and (res.get("message") == "Unauthorized" or res.get("statusCode") == 401):
            raise RuntimeError("Phiên đăng nhập OneTech đã hết hạn (Unauthorized), vui lòng bấm Đăng nhập lại.")
        if not isinstance(res, list):
            return []
        return res

    def fetch_history_raw(self, ts_start: str, ts_end: str, user_id: str = DEFAULT_USER_ID) -> Dict[str, Any]:
        """Đọc (chỉ GET) toàn bộ dữ liệu thô cho lịch sử công việc trong một phiên trình duyệt:
        projects + tasks/sprints/members/workflow-statuses của từng dự án + timesheet."""
        def action(page):
            return page.evaluate("""async ([tsStart, tsEnd, me]) => {
                // OneTech giới hạn tần suất (HTTP 429): gọi tuần tự, chờ theo Retry-After rồi thử lại
                const failed = [];
                const sleep = ms => new Promise(res => setTimeout(res, ms));
                const get = async (u) => {
                    let last = '';
                    for (let attempt = 0; attempt < 8; attempt++) {
                        try {
                            const r = await fetch(u, { credentials: 'include' });
                            if (r.ok && (r.headers.get('content-type') || '').includes('json')) return await r.json();
                            last = 'HTTP ' + r.status;
                            if (r.status === 429) {
                                const ra = parseFloat(r.headers.get('retry-after') || r.headers.get('ratelimit-reset') || '');
                                await sleep((isFinite(ra) && ra > 0 ? ra : Math.min(60, 5 * 2 ** attempt)) * 1000 + 500);
                                continue;
                            }
                        } catch (e) { last = String(e); }
                        await sleep(1000 * (attempt + 1));
                    }
                    failed.push({ url: u, error: last });
                    return null;
                };
                const projects = (await get('/api/projects')) || [];
                const perProject = {};
                for (const p of projects) {
                    const members = await get(`/api/projects/${p.id}/members`);
                    const tasks = await get(`/api/projects/${p.id}/tasks`);
                    const isMember = (members || []).some(m => m.userId === me);
                    const involved = (tasks || []).some(t => t.assigneeId === me || t.reporterId === me);
                    // sprints/workflow chỉ cần cho dự án sẽ được xuất
                    const relevant = isMember || involved || members === null || tasks === null;
                    perProject[p.id] = {
                        tasks: tasks || [], members: members || [],
                        sprints: relevant ? (await get(`/api/projects/${p.id}/sprints`)) || [] : [],
                        workflowStatuses: relevant ? (await get(`/api/projects/${p.id}/workflow-statuses`)) || [] : [],
                    };
                }
                // Timesheet: một lần gọi cho cả khoảng (API dùng start/end)
                const timesheet = (await get(`/api/users/me/timesheet?start=${tsStart}&end=${tsEnd}`)) || [];
                return { projects, perProject, timesheet, failed };
            }""", [ts_start, ts_end, user_id])
        return self._execute_browser(action)

    def log_time(
        self,
        task_id: int,
        hours: float,
        description: Optional[str] = None,
        activity_type: str = "development",
        logged_date: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Tự động ghi nhận (log) timesheet cho task trên OneTech Workspace."""
        d = logged_date or datetime.now().strftime("%Y-%m-%d")
        uid = user_id or DEFAULT_USER_ID

        def action(page):
            payload = {
                "userId": uid,
                "hours": str(hours),
                "description": description or None,
                "activityType": activity_type,
                "loggedDate": f"{d}T00:00:00.000Z"
            }
            js_code = f"""() => fetch('/api/tasks/{task_id}/time-entries', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({json.dumps(payload)}),
                credentials: 'include'
            }}).then(async r => {{
                if (!r.ok) {{
                    const err = await r.text();
                    throw new Error(`HTTP ${{r.status}}: ${{err}}`);
                }}
                return r.json();
            }})"""
            return page.evaluate(js_code)

        return self._execute_browser(action)

    def delete_time_entry(self, entry_id: int) -> bool:
        """Xóa một bản ghi timesheet."""
        def action(page):
            js_code = f"""() => fetch('/api/time-entries/{entry_id}', {{
                method: 'DELETE',
                credentials: 'include'
            }}).then(r => r.ok)"""
            return page.evaluate(js_code)
        return self._execute_browser(action)

