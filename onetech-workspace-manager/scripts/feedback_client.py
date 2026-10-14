import sys
import json
import time
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Optional

CONFIG_STORE_PATH = Path.home() / ".config" / "configstore" / "firebase-tools.json"
FIREBASE_PROJECT = "itgviet-plan"
FIRESTORE_BASE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT}/databases/(default)/documents"

class FeedbackHubClient:
    """Client tương tác với ITG Customer Feedback Hub (https://plan.itgviet.com) qua Firestore REST API."""

    def __init__(self, config_path: Path = CONFIG_STORE_PATH):
        self.config_path = config_path

    def _ensure_fresh_token(self) -> str:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file cấu hình Firebase CLI tại: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        tokens = data.get("tokens", {})
        access_token = tokens.get("access_token")
        expires_at = tokens.get("expires_at", 0)

        # Check if token is expired or expires within 60 seconds
        if not access_token or (time.time() * 1000) >= (expires_at - 60000):
            self._refresh_via_cli()
            with open(self.config_path, "r", encoding="utf-8") as f2:
                data2 = json.load(f2)
            access_token = data2.get("tokens", {}).get("access_token")

        return access_token

    def _refresh_via_cli(self) -> None:
        """Kích hoạt Firebase CLI tự động làm mới access token."""
        try:
            subprocess.run(["firebase", "projects:list"], capture_output=True, text=True, check=True, shell=True, encoding="utf-8")
        except Exception as e:
            print(f"[WARN] Không thể làm mới token qua Firebase CLI: {e}", file=sys.stderr)

    def _request(self, path: str, method: str = "GET", payload: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, str]] = None) -> Any:
        token = self._ensure_fresh_token()
        url = f"{FIRESTORE_BASE_URL}/{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        data_bytes = json.dumps(payload).encode("utf-8") if payload else None
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            # If 401 Unauthorized, refresh token and retry once
            if e.code == 401:
                self._refresh_via_cli()
                new_token = self._ensure_fresh_token()
                headers["Authorization"] = f"Bearer {new_token}"
                req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
                with urllib.request.urlopen(req) as resp2:
                    raw = resp2.read().decode("utf-8")
                    return json.loads(raw) if raw else {}
            raise RuntimeError(f"Firestore API Error ({e.code}): {err_body}")

    def _parse_firestore_fields(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for k, v in fields.items():
            if "stringValue" in v:
                result[k] = v["stringValue"]
            elif "integerValue" in v:
                result[k] = int(v["integerValue"])
            elif "booleanValue" in v:
                result[k] = v["booleanValue"]
            elif "doubleValue" in v:
                result[k] = float(v["doubleValue"])
            elif "arrayValue" in v:
                vals = v["arrayValue"].get("values", [])
                result[k] = [list(item.values())[0] if isinstance(item, dict) else item for item in vals]
            elif "mapValue" in v:
                result[k] = self._parse_firestore_fields(v["mapValue"].get("fields", {}))
            elif "nullValue" in v:
                result[k] = None
            else:
                result[k] = list(v.values())[0] if v else None
        return result

    def get_projects(self) -> List[Dict[str, Any]]:
        """Lấy danh sách các dự án đang quản lý trên Feedback Hub."""
        resp = self._request("projects")
        docs = resp.get("documents", [])
        projects = []
        for d in docs:
            fields = self._parse_firestore_fields(d.get("fields", {}))
            key = d.get("name", "").split("/")[-1]
            fields["key"] = fields.get("key", key)
            projects.append(fields)
        return projects

    def get_tickets(self, project_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lấy danh sách tickets, có thể lọc theo project_key (ví dụ: cafenhatsinh, issx, dtg)."""
        resp = self._request("tickets")
        docs = resp.get("documents", [])
        tickets = []
        target = project_key.lower().strip() if project_key else None
        for d in docs:
            fields = self._parse_firestore_fields(d.get("fields", {}))
            doc_id = d.get("name", "").split("/")[-1]
            fields["id"] = fields.get("id", doc_id)
            p_key = (fields.get("projectKey") or "").lower()
            if target and p_key != target:
                continue
            tickets.append(fields)
        # Sắp xếp vé mới nhất lên đầu
        tickets.sort(key=lambda t: t.get("createdAt") or 0, reverse=True)
        return tickets

    def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """Lấy thông tin chi tiết một ticket cùng các trao đổi (comments)."""
        d = self._request(f"tickets/{ticket_id}")
        ticket = self._parse_firestore_fields(d.get("fields", {}))
        ticket["id"] = d.get("name", "").split("/")[-1]

        # Fetch comments
        try:
            c_resp = self._request(f"tickets/{ticket_id}/comments")
            c_docs = c_resp.get("documents", [])
            comments = []
            for cd in c_docs:
                cf = self._parse_firestore_fields(cd.get("fields", {}))
                cf["id"] = cd.get("name", "").split("/")[-1]
                comments.append(cf)
            comments.sort(key=lambda c: c.get("createdAt") or 0)
            ticket["comments"] = comments
        except Exception:
            ticket["comments"] = []

        return ticket

    def upload_image(self, file_path: str, project_key: str = "cafenhatsinh") -> str:
        """Tải ảnh evidence lên Firebase Storage (itgviet-plan.firebasestorage.app) và trả về URL xem trực tiếp."""
        from pathlib import Path
        import mimetypes
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"Không tìm thấy file ảnh: {file_path}")

        token = self._ensure_fresh_token()
        now_ms = int(time.time() * 1000)
        file_name = f"evidence_{now_ms}_{p.name}"
        storage_path = f"feedbacks/{project_key}/{file_name}"
        encoded_storage_path = urllib.parse.quote(storage_path, safe="")

        mime_type = mimetypes.guess_type(str(p))[0] or "image/png"
        with open(p, "rb") as f:
            image_bytes = f.read()

        upload_url = f"https://firebasestorage.googleapis.com/v0/b/itgviet-plan.firebasestorage.app/o?name={encoded_storage_path}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": mime_type
        }
        req = urllib.request.Request(upload_url, data=image_bytes, headers=headers, method="POST")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            download_token = data.get("downloadTokens")

        public_url = f"https://firebasestorage.googleapis.com/v0/b/itgviet-plan.firebasestorage.app/o/{encoded_storage_path}?alt=media&token={download_token}"
        return public_url

    def update_status(self, ticket_id: str, status: str, comment: Optional[str] = None, image_urls: Optional[List[str]] = None, author_name: str = "Việt Nguyễn Tùng (Kỹ sư ITG)") -> Dict[str, Any]:
        """Cập nhật trạng thái ticket (received | in_progress | pending_deploy | ready_for_uat | resolved | rejected)."""
        now_ms = int(time.time() * 1000)
        payload = {
            "fields": {
                "status": {"stringValue": status},
                "updatedAt": {"integerValue": str(now_ms)}
            }
        }
        url_path = f"tickets/{ticket_id}?updateMask.fieldPaths=status&updateMask.fieldPaths=updatedAt"
        res = self._request(url_path, method="PATCH", payload=payload)

        if comment or image_urls:
            self.add_comment(ticket_id, comment or f"Cập nhật trạng thái sang {status}", author_name=author_name, image_urls=image_urls)

        return res

    def link_onetech_task(self, ticket_id: str, onetech_task_id: int, project_id: int = 82) -> Dict[str, Any]:
        """Liên kết ticket với OneTech Workspace Task ID."""
        now_ms = int(time.time() * 1000)
        task_url = f"https://workspace.onetech.vn/projects/{project_id}/tasks/{onetech_task_id}"
        payload = {
            "fields": {
                "oneTechTaskId": {"integerValue": str(onetech_task_id)},
                "oneTechTaskUrl": {"stringValue": task_url},
                "updatedAt": {"integerValue": str(now_ms)}
            }
        }
        url_path = f"tickets/{ticket_id}?updateMask.fieldPaths=oneTechTaskId&updateMask.fieldPaths=oneTechTaskUrl&updateMask.fieldPaths=updatedAt"
        return self._request(url_path, method="PATCH", payload=payload)

    def add_comment(self, ticket_id: str, content: str, author_name: str = "Việt Nguyễn Tùng (Kỹ sư ITG)", author_email: str = "vietnt@itg.vn", author_role: str = "engineer", image_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """Gửi comment phản hồi tới Khách hàng trên Ticket thread."""
        now_ms = int(time.time() * 1000)
        comment_id = f"cmt_{now_ms}"
        img_values = []
        if image_urls:
            img_values = [{"stringValue": url} for url in image_urls]

        payload = {
            "fields": {
                "id": {"stringValue": comment_id},
                "ticketId": {"stringValue": ticket_id},
                "authorName": {"stringValue": author_name},
                "authorEmail": {"stringValue": author_email},
                "authorRole": {"stringValue": author_role},
                "senderName": {"stringValue": author_name},
                "senderRole": {"stringValue": author_role},
                "content": {"stringValue": content},
                "createdAt": {"integerValue": str(now_ms)},
                "imageUrls": {"arrayValue": {"values": img_values}}
            }
        }
        url_path = f"tickets/{ticket_id}/comments?documentId={comment_id}"
        return self._request(url_path, method="POST", payload=payload)
