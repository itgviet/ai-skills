import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

USER_DATA_DIR = Path(r"C:\Users\vietn\.gemini\config\playwright_profile")
STORE_FILE = Path(r"d:\ITGVietAssistant\data\tasks_store.json")
DEFAULT_USER_ID = "19bcfc0a-1108-40bd-810a-abbe7af46fc5"


class OneTechClient:
    def __init__(self, user_data_dir: Path = USER_DATA_DIR):
        self.user_data_dir = user_data_dir

    def _execute_browser(self, callback):
        """Khởi chạy Chromium headless với persistent profile để gọi API/DOM an toàn."""
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(self.user_data_dir),
                headless=True
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://workspace.onetech.vn/projects/82/sprints", wait_until="networkidle", timeout=25000)
            result = callback(page)
            context.close()
            return result

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
            if sprint_id is not None:
                tasks = [t for t in tasks if t.get("sprintId") == sprint_id]
            if assignee_id is not None:
                tasks = [t for t in tasks if t.get("assigneeId") == assignee_id]
            return tasks
        return self._execute_browser(action)

    def update_task(self, task_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Cập nhật thuộc tính của task (tự động map workflowStatusId khi đổi status)."""
        # Auto-map workflowStatusId and bugStatus if status is provided
        if "status" in payload and "workflowStatusId" not in payload:
            wf_map = {
                "todo": (405, "new"),
                "in_progress": (406, "assigned"),
                "review": (408, "fixed"),
                "done": (409, "closed"),
                "cancel": (405, "closed")
            }
            raw_st = payload["status"].lower()
            if raw_st in wf_map:
                payload["workflowStatusId"] = wf_map[raw_st][0]
                if "bugStatus" not in payload:
                    payload["bugStatus"] = wf_map[raw_st][1]

        def action(page):
            js_code = f"""() => fetch('/api/tasks/{task_id}', {{
                method: 'PUT',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({json.dumps(payload)})
            }}).then(r => r.json())"""
            return page.evaluate(js_code)
        return self._execute_browser(action)

    def create_task(self, project_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo task mới hoặc epic mới trên dự án."""
        def action(page):
            js_code = f"""() => fetch('/api/projects/{project_id}/tasks', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({json.dumps(payload)})
            }}).then(r => r.json())"""
            return page.evaluate(js_code)
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

    def add_comment(self, task_id: int, content: str, author_id: str = None) -> Dict[str, Any]:
        """Đăng bình luận vào Task (Hỗ trợ Markdown và ảnh đính kèm)."""
        uid = author_id or DEFAULT_USER_ID
        def action(page):
            js_code = f"""() => fetch('/api/tasks/{task_id}/comments', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({json.dumps({'content': content, 'authorId': uid})})
            }}).then(r => r.json())"""
            return page.evaluate(js_code)
        return self._execute_browser(action)

    def sync_to_local_store(self, project_id: int = 82, user_id: str = DEFAULT_USER_ID, project_name: str = "") -> int:
        """Đồng bộ task của dự án vào tasks_store.json (Hỗ trợ đa dự án & bảo toàn ghi chú/chat)."""
        def action(page):
            tasks = page.evaluate(f"() => fetch('/api/projects/{project_id}/tasks').then(r => r.json())")
            sprints_raw = page.evaluate(f"() => fetch('/api/projects/{project_id}/sprints').then(r => r.json())")
            sprints = {s["id"]: s["name"] for s in sprints_raw}

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
            status_map = {"todo": "TODO", "in_progress": "IN_PROGRESS", "review": "REVIEW", "done": "DONE", "cancel": "CANCELLED"}

            # Load existing store
            existing_data = {}
            existing_tasks_map = {}
            if STORE_FILE.exists():
                try:
                    with open(STORE_FILE, "r", encoding="utf-8") as f:
                        existing_data = json.load(f)
                    for t in existing_data.get("tasks", []):
                        if t.get("onetech_task_id"):
                            existing_tasks_map[t["onetech_task_id"]] = t
                except Exception:
                    pass

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

                task_obj = {
                    "task_id": prev.get("task_id", f"TASK-{idx:03d}"),
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
                    "status": status_map.get(raw_status, "TODO"),
                    "type": t.get("type", "task"),
                    "bugStatus": t.get("bugStatus") or ("new" if t.get("type") == "bug" else None),
                    "workflowStatusId": t.get("workflowStatusId") or 405,
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
            with open(STORE_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "version": "2.0",
                    "system": "Antigravity Multi-Project Task Store",
                    "last_updated": datetime.now().isoformat(),
                    "next_task_index": len(all_tasks) + 1,
                    "user": {"name": "Viet Nguyen Tung", "email": "vietnt@onetech.vn", "role": "Team Lead / Developer"},
                    "current_project_id": project_id,
                    "tasks": all_tasks
                }, f, ensure_ascii=False, indent=2)

            return len(formatted)

        return self._execute_browser(action)
