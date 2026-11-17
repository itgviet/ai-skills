import sys
import os
import json
import re
import time
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Optional



class LoginExpired(PermissionError):
    """The Feedback Hub login (Firebase CLI) has expired: only `firebase login --reauth` by the user fixes it."""


CLI_TIMEOUT = 40    # seconds for a firebase / gcloud token refresh
HTTP_TIMEOUT = 30   # seconds for one Feedback Hub request
_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
CONFIG_STORE_PATH = Path.home() / ".config" / "configstore" / "firebase-tools.json"
GCLOUD_BACKOFF = 1800   # after gcloud fails (expired login), skip it this long instead of trying on every poll
_gcloud_dead_until = 0.0


def _cli_env() -> dict:
    """gcloud must never prompt: with an expired login it asked "re-authenticate?" on a console nobody sees and waited
    for ever; with prompts disabled it fails at once."""
    env = dict(os.environ)
    env["CLOUDSDK_CORE_DISABLE_PROMPTS"] = "1"
    return env


def _kill_tree(proc) -> None:
    """A timeout used to kill only cmd.exe: gcloud / firebase underneath kept running and kept the pipe open
    (13 hung `gcloud auth print-access-token` processes piled up in one day, one per Feedback Hub poll)."""
    try:
        if sys.platform.startswith("win"):
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True, creationflags=_NO_WINDOW, timeout=15)
        else:
            proc.kill()
    except Exception:
        pass


def _run_cli(args, timeout: int = None, shell: bool = False) -> tuple:
    """Run a token CLI quietly: no console, no stdin, no prompts; on timeout the whole process tree goes.
    Returns (returncode, stdout, stderr); raises subprocess.TimeoutExpired."""
    proc = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            encoding="utf-8", errors="ignore", shell=shell, env=_cli_env(), creationflags=_NO_WINDOW)
    try:
        out, err = proc.communicate(timeout=timeout or CLI_TIMEOUT)
        return proc.returncode, out or "", err or ""
    except subprocess.TimeoutExpired:
        _kill_tree(proc)
        try:
            proc.communicate(timeout=5)
        except Exception:
            pass
        raise


def _gcloud_token() -> str | None:
    """An access token from gcloud, or None (failed / timed out: then skipped for GCLOUD_BACKOFF)."""
    global _gcloud_dead_until
    if time.time() < _gcloud_dead_until:
        return None
    cmd = ["cmd.exe", "/c", "gcloud", "auth", "print-access-token"] if sys.platform.startswith("win") else ["gcloud", "auth", "print-access-token"]
    try:
        code, out, _err = _run_cli(cmd, timeout=25)
        token = out.strip() if code == 0 else ""
    except Exception:
        token = ""
    if not token or " " in token:
        _gcloud_dead_until = time.time() + GCLOUD_BACKOFF
        return None
    return token
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

    _refreshed_at = 0.0

    def _refresh_via_cli(self) -> None:
        """Kích hoạt làm mới access token qua ADC hoặc Firebase CLI."""
        self._refreshed_at = time.time()
        # Ưu tiên làm mới qua ADC (Application Default Credentials)
        adc_path = Path(os.environ.get("APPDATA", "")) / "gcloud" / "application_default_credentials.json"
        if not adc_path.exists():
            adc_path = Path.home() / ".config" / "gcloud" / "application_default_credentials.json"
        if adc_path.exists():
            try:
                with open(adc_path, "r", encoding="utf-8") as f:
                    adc = json.load(f)
                if adc.get("refresh_token") and adc.get("client_id") and adc.get("client_secret"):
                    req_data = urllib.parse.urlencode({
                        "refresh_token": adc["refresh_token"],
                        "client_id": adc["client_id"],
                        "client_secret": adc["client_secret"],
                        "grant_type": "refresh_token"
                    }).encode("utf-8")
                    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=req_data, method="POST")
                    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
                        res = json.loads(resp.read().decode("utf-8"))
                        token = res.get("access_token")
                        if token and self.config_path.exists():
                            with open(self.config_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                            data.setdefault("tokens", {})["access_token"] = token
                            data["tokens"]["expires_at"] = int((time.time() + 3500) * 1000)
                            with open(self.config_path, "w", encoding="utf-8") as f:
                                json.dump(data, f, indent=2)
                            return
            except Exception:
                pass

        # Tiếp theo thử gcloud auth print-access-token (không hỏi, không treo; hỏng thì nghỉ 30 phút)
        try:
            token = _gcloud_token()
            if token and self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data.setdefault("tokens", {})["access_token"] = token
                data["tokens"]["expires_at"] = int((time.time() + 3500) * 1000)
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                return
        except Exception:
            pass

        try:
            cmd = "firebase.cmd" if sys.platform.startswith("win") else "firebase"
            # no stdin and a time limit: with an expired login the CLIs ask to sign in again and, without a console
            # (the dashboard engine), waited for an answer forever
            code, out, err = _run_cli([cmd, "projects:list"], shell=True)
            if code != 0:
                raise subprocess.CalledProcessError(code, cmd, out, err)
        except subprocess.TimeoutExpired as e:
            raise LoginExpired("Feedback Hub: Firebase CLI chờ đăng nhập lại, chạy `firebase login --reauth`") from e
        except subprocess.CalledProcessError as e:
            if re.search(r"no longer valid|--reauth", f"{e.stdout or ''} {e.stderr or ''}", re.I):
                # the refresh token itself expired: gcloud would only wait for a sign-in too
                raise LoginExpired("Feedback Hub: phiên Firebase đã hết hạn (401), chạy `firebase login --reauth`") from e
            self._refresh_gcloud(e)
        except Exception as e:
            self._refresh_gcloud(e)

    def _refresh_gcloud(self, e) -> None:
            try:
                token = _gcloud_token()
                if token and self.config_path.exists():
                    with open(self.config_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    data.setdefault("tokens", {})["access_token"] = token
                    data["tokens"]["expires_at"] = int((time.time() + 3500) * 1000)
                    with open(self.config_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                    return
            except Exception:
                pass
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
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            # If 401 Unauthorized, refresh token and retry once
            if e.code == 401:
                if self._refreshed_at and time.time() - self._refreshed_at < 120:
                    # just refreshed and still refused: the login itself is the problem, a 2nd refresh only costs time
                    raise LoginExpired("Feedback Hub từ chối token mới (401): chạy `firebase login --reauth`") from e
                self._refresh_via_cli()
                new_token = self._ensure_fresh_token()
                headers["Authorization"] = f"Bearer {new_token}"
                req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
                with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp2:
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
        params = {"pageSize": "300"}
        resp = self._request("tickets", params=params)
        docs = resp.get("documents", [])
        # Firestore phân trang: đọc tiếp nextPageToken để không mất tickets cũ
        while resp.get("nextPageToken"):
            params["pageToken"] = resp["nextPageToken"]
            resp = self._request("tickets", params=params)
            docs.extend(resp.get("documents", []))
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
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT * 4) as resp:
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
