import sys
import argparse
import json
from pathlib import Path

# Add script dir to sys.path
sys.path.insert(0, str(Path(__file__).parent))
from onetech_client import OneTechClient, DEFAULT_USER_ID
from feedback_client import FeedbackHubClient

def main():
    parser = argparse.ArgumentParser(description="OneTech Workspace & ITG Feedback Hub CLI Automation Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. Projects
    projects_p = subparsers.add_parser("projects", help="Liệt kê danh sách dự án của bạn trên OneTech")

    # 2. Sync
    sync_p = subparsers.add_parser("sync", help="Đồng bộ tasks về tasks_store.json")
    sync_p.add_argument("--project", type=int, default=82, help="Project ID (Mặc định: 82)")

    # 3. List
    list_p = subparsers.add_parser("list", help="Liệt kê tasks OneTech (Siêu tốc từ cache, dùng --live để lấy trực tiếp)")
    list_p.add_argument("--project", type=int, default=None, help="Project ID (ví dụ: 82, 76)")
    list_p.add_argument("--sprint", type=int, default=None, help="Sprint ID")
    list_p.add_argument("--status", type=str, default=None, choices=["todo", "in_progress", "review", "done", "open"], help="Lọc trạng thái: todo | in_progress | review | done | open (chưa hoàn thành)")
    list_p.add_argument("--search", type=str, default=None, help="Tìm kiếm từ khóa trong tiêu đề hoặc nội dung")
    list_p.add_argument("--mine", action="store_true", help="Chỉ lấy task gán cho tôi")
    list_p.add_argument("--live", action="store_true", help="Bỏ qua cache, gọi trực tiếp qua browser")
    list_p.add_argument("--limit", type=int, default=50, help="Số task tối đa hiển thị (Mặc định: 50)")

    # 3b. Task Detail
    task_p = subparsers.add_parser("task", help="Xem chi tiết một task (Siêu tốc từ cache)")
    task_p.add_argument("task_id", type=int, help="Task ID (ví dụ: 7972, 8370)")
    task_p.add_argument("--live", action="store_true", help="Bỏ qua cache, lấy dữ liệu trực tiếp từ OneTech")
    task_p.add_argument("--comments", action="store_true", help="Lấy kèm danh sách bình luận")

    # 3c. Comments
    comments_p = subparsers.add_parser("comments", help="Xem, thêm hoặc xóa bình luận của task")
    comments_p.add_argument("task_id", type=int, help="Task ID")
    comments_p.add_argument("--add", type=str, default=None, help="Thêm bình luận mới (Tự động chuẩn hóa Markdown)")
    comments_p.add_argument("--image", type=str, default=None, help="Đính kèm ảnh khi thêm bình luận")
    comments_p.add_argument("--delete", type=int, default=None, help="Xóa bình luận theo Comment ID")

    # 4. Update
    update_p = subparsers.add_parser("update", help="Cập nhật task OneTech")
    update_p.add_argument("task_id", type=int, help="Task ID (ví dụ: 7305, 8273, 8086)")
    update_p.add_argument("--title", type=str, help="Tiêu đề mới")
    update_p.add_argument("--status", type=str, choices=["todo", "in_progress", "review", "done", "cancel"], help="Trạng thái mới")
    update_p.add_argument("--sprint", type=int, help="Sprint ID mới")
    update_p.add_argument("--priority", type=str, choices=["low", "medium", "high", "critical"], help="Mức ưu tiên mới")

    # 5. Create
    create_p = subparsers.add_parser("create", help="Tạo task mới / bug mới trên OneTech")
    create_p.add_argument("--project", type=int, default=82, help="Project ID")
    create_p.add_argument("--title", type=str, required=True, help="Tiêu đề task")
    create_p.add_argument("--sprint", type=int, default=None, help="Sprint ID")
    create_p.add_argument("--parent", type=int, default=None, help="Parent Task / Epic ID (ví dụ: 8273)")
    create_p.add_argument("--type", type=str, default="task", choices=["task", "epic", "story", "bug", "subtask"], help="Loại task")
    create_p.add_argument("--priority", type=str, default="medium", choices=["low", "medium", "high", "critical"], help="Ưu tiên")
    create_p.add_argument("--severity", type=str, default=None, choices=["minor", "major", "critical"], help="Mức độ nghiêm trọng của bug")
    create_p.add_argument("--status", type=str, default="todo", choices=["todo", "in_progress", "review", "done"], help="Trạng thái")
    create_p.add_argument("--assignee", type=str, default=DEFAULT_USER_ID, help="User ID người được giao")
    create_p.add_argument("--description", type=str, default="", help="Mô tả")
    create_p.add_argument("--image", type=str, default=None, help="Đường dẫn file ảnh đính kèm (sẽ tự động upload và nhúng vào comment)")

    # 6. Upload
    upload_p = subparsers.add_parser("upload", help="Upload ảnh lên OneTech CDN")
    upload_p.add_argument("image_path", type=str, help="Đường dẫn file ảnh trên máy")

    # 7. Comment
    comment_p = subparsers.add_parser("comment", help="Đăng bình luận vào task OneTech")
    comment_p.add_argument("task_id", type=int, help="Task ID")
    comment_p.add_argument("--message", type=str, required=True, help="Nội dung bình luận")
    comment_p.add_argument("--image", type=str, default=None, help="Đường dẫn file ảnh đính kèm")

    # 8. Feedback Hub
    fb_p = subparsers.add_parser("feedback", help="Quản lý & truy cứu ITG Customer Feedback Hub (plan.itgviet.com)")
    fb_p.add_argument("action", choices=["projects", "list", "get", "status", "comment", "link"], help="Hành động: projects | list | get | status | comment | link")
    fb_p.add_argument("--project", type=str, default=None, help="Mã dự án Feedback Hub (ví dụ: cafenhatsinh, issx, dtg)")
    fb_p.add_argument("--ticket", type=str, default=None, help="Mã ticket (ví dụ: CAFENHATSINH-818, CAFENHATSINH-584)")
    fb_p.add_argument("--status", type=str, choices=["received", "in_progress", "pending_deploy", "ready_for_uat", "resolved", "rejected"], help="Trạng thái mới của ticket")
    fb_p.add_argument("--message", type=str, default=None, help="Nội dung bình luận gửi tới khách hàng")
    fb_p.add_argument("--author", type=str, default="Việt Nguyễn Tùng (Kỹ sư ITG)", help="Tên người bình luận (mặc định: Việt Nguyễn Tùng (Kỹ sư ITG))")
    fb_p.add_argument("--image", type=str, default=None, help="Đường dẫn file ảnh bằng chứng (evidence) đính kèm")
    fb_p.add_argument("--task", type=int, default=None, help="OneTech Task ID để liên kết")
    fb_p.add_argument("--onetech-project", type=int, default=82, help="OneTech Project ID (mặc định: 82)")

    # 9. Timesheet
    ts_p = subparsers.add_parser("timesheet", help="Quản lý & tự động log timesheet OneTech Workspace")
    ts_p.add_argument("action", choices=["log", "list", "today", "week", "delete"], help="Hành động: log | list | today | week | delete")
    ts_p.add_argument("--task", type=int, default=None, help="OneTech Task ID")
    ts_p.add_argument("--hours", type=float, default=None, help="Số giờ làm việc (ví dụ: 2.5, 4.0, 8.0)")
    ts_p.add_argument("--desc", type=str, default="", help="Mô tả công việc (What did you work on?)")
    ts_p.add_argument("--type", type=str, default="development", choices=[
        "development", "testing", "bugfix", "code_review", "meeting",
        "documentation", "deployment", "research", "support", "design", "planning", "other"
    ], help="Loại hoạt động (Mặc định: development)")
    ts_p.add_argument("--date", type=str, default=None, help="Ngày ghi nhận (định dạng YYYY-MM-DD, mặc định: hôm nay)")
    ts_p.add_argument("--entry-id", type=int, default=None, help="ID của bản ghi timesheet khi cần xóa")

    args = parser.parse_args()

    if args.command == "feedback":
        fb_client = FeedbackHubClient()

        if args.action == "projects":
            prjs = fb_client.get_projects()
            print(f"Danh sách {len(prjs)} dự án trên Feedback Hub (plan.itgviet.com):")
            for p in prjs:
                print(f"- [{p.get('key')}] {p.get('name')} | OneTech ID: #{p.get('oneTechProjectId', 'N/A')}")

        elif args.action == "list":
            tickets = fb_client.get_tickets(project_key=args.project)
            p_desc = f"dự án '{args.project}'" if args.project else "tất cả dự án"
            print(f"Tìm thấy {len(tickets)} tickets trên Feedback Hub ({p_desc}):")
            for t in tickets:
                ot_str = f" [OneTech: #{t.get('oneTechTaskId')}]" if t.get('oneTechTaskId') else ""
                print(f"- [{t.get('id')}] ({t.get('projectKey')}) [{str(t.get('status')).upper()}] [{str(t.get('severity')).upper()}] {t.get('title')}{ot_str}")

        elif args.action == "get":
            if not args.ticket:
                print("[LỖI] Cần truyền --ticket <TICKET_ID> để xem chi tiết.")
                return
            t = fb_client.get_ticket(args.ticket)
            print(f"=== CHI TIẾT TICKET {t.get('id')} ===")
            print(f"Dự án: {t.get('projectKey')}")
            print(f"Tiêu đề: {t.get('title')}")
            print(f"Loại: {t.get('type')} | Mức độ: {t.get('severity')} | Trạng thái: {t.get('status')}")
            print(f"Khách hàng: {t.get('clientName')} ({t.get('clientEmail')})")
            if t.get('description'):
                print(f"Mô tả: {t.get('description')}")
            if t.get('clientEnvironment'):
                env = t['clientEnvironment']
                print(f"Môi trường: {env.get('os')} | {env.get('browser')} | {env.get('deviceType')} ({env.get('screenResolution')})")
            if t.get('imageUrls'):
                print(f"Ảnh đính kèm ({len(t['imageUrls'])}):")
                for img in t['imageUrls']:
                    print(f"  - {img}")
            if t.get('oneTechTaskId'):
                print(f"OneTech Task: #{t.get('oneTechTaskId')} ({t.get('oneTechTaskUrl')})")
            comments = t.get('comments', [])
            print(f"\nTrao đổi ({len(comments)} comments):")
            for c in comments:
                print(f"- [{c.get('authorName')} ({c.get('authorRole')})]: {c.get('content')}")

        elif args.action == "status":
            if not args.ticket or not args.status:
                print("[LỖI] Cần truyền --ticket <TICKET_ID> và --status <STATUS>.")
                return
            img_urls = []
            if args.image:
                print(f"[ĐANG TẢI] Đang upload ảnh evidence: {args.image}...")
                img_url = fb_client.upload_image(args.image, project_key=args.project or "cafenhatsinh")
                img_urls.append(img_url)
                print(f"[THÀNH CÔNG] Đã upload ảnh: {img_url}")
            fb_client.update_status(args.ticket, args.status, comment=args.message, image_urls=img_urls if img_urls else None, author_name=args.author)
            print(f"[THÀNH CÔNG] Đã cập nhật ticket {args.ticket} sang trạng thái: {args.status}")

        elif args.action == "comment":
            if not args.ticket or not args.message:
                print("[LỖI] Cần truyền --ticket <TICKET_ID> và --message <NỘI DUNG>.")
                return
            img_urls = []
            if args.image:
                print(f"[ĐANG TẢI] Đang upload ảnh evidence: {args.image}...")
                img_url = fb_client.upload_image(args.image, project_key=args.project or "cafenhatsinh")
                img_urls.append(img_url)
                print(f"[THÀNH CÔNG] Đã upload ảnh: {img_url}")
            fb_client.add_comment(args.ticket, args.message, author_name=args.author, image_urls=img_urls if img_urls else None)
            print(f"[THÀNH CÔNG] Đã gửi bình luận tới khách hàng trên ticket {args.ticket}!")

        elif args.action == "link":
            if not args.ticket or not args.task:
                print("[LỖI] Cần truyền --ticket <TICKET_ID> và --task <ONETECH_TASK_ID>.")
                return
            fb_client.link_onetech_task(args.ticket, args.task, project_id=args.onetech_project)
            print(f"[THÀNH CÔNG] Đã liên kết ticket {args.ticket} với OneTech Task #{args.task}!")

        return

    # Standard OneTech Commands
    client = OneTechClient()

    if args.command == "projects":
        prjs = client.get_projects()
        print(f"Danh sách {len(prjs)} dự án của bạn:")
        for p in prjs:
            print(f"- [#{p.get('id')}] {p.get('name')}")

    elif args.command == "sync":
        count = client.sync_to_local_store(project_id=args.project)
        print(f"[THÀNH CÔNG] Đã đồng bộ {count} tasks vào tasks_store.json!")

    elif args.command == "list":
        # Ưu tiên đọc siêu tốc từ cache (tasks_store.json) nếu không yêu cầu --live
        store_path = Path(r"d:\ITGVietAssistant\data\tasks_store.json")
        tasks = []
        from_cache = False

        if not args.live and store_path.exists():
            try:
                with open(store_path, "r", encoding="utf-8") as f:
                    store_data = json.load(f)
                tasks = store_data.get("tasks", [])
                from_cache = True
            except Exception:
                pass

        if from_cache and tasks:
            # Lọc theo dự án
            if args.project:
                tasks = [t for t in tasks if t.get("project_id") == args.project]
            # Lọc theo sprint
            if args.sprint is not None:
                tasks = [t for t in tasks if t.get("sprint_id") == args.sprint]
            # Lọc theo người phụ trách
            if args.mine:
                tasks = [t for t in tasks if t.get("is_mine") or t.get("assignee_id") == DEFAULT_USER_ID]
            # Lọc theo trạng thái
            if args.status:
                st = args.status.lower()
                if st == "open":
                    tasks = [t for t in tasks if str(t.get("status", "")).upper() != "DONE"]
                else:
                    tasks = [t for t in tasks if str(t.get("status", "")).lower() == st]
            # Tìm kiếm từ khóa
            if args.search:
                q = args.search.lower()
                tasks = [t for t in tasks if q in str(t.get("title", "")).lower() or q in str(t.get("notes", "")).lower()]

            total_found = len(tasks)
            display_tasks = tasks[:args.limit]
            print(f"Tìm thấy {total_found} tasks (Cache: {store_path.name}{f', hiển thị {len(display_tasks)}' if total_found > args.limit else ''}):")
            for t in display_tasks:
                tid = t.get("onetech_task_id") or t.get("id") or t.get("task_id")
                st = str(t.get("status", "TODO")).upper()
                pri = str(t.get("priority", "MEDIUM")).upper().replace("P0-", "").replace("P1-", "").replace("P2-", "")
                p_name = f" [{t.get('project')}]" if not args.project and t.get("project") else ""
                print(f"- [#{tid}] [{st}] ({pri}){p_name} | {t.get('title')}")
        else:
            # Live fetch qua browser
            assignee = DEFAULT_USER_ID if args.mine else None
            pid = args.project or 82
            tasks = client.get_tasks(project_id=pid, sprint_id=args.sprint, assignee_id=assignee)
            if args.status:
                st = args.status.lower()
                if st == "open":
                    tasks = [t for t in tasks if str(t.get("status", "")).lower() != "done"]
                else:
                    tasks = [t for t in tasks if str(t.get("status", "")).lower() == st]
            if args.search:
                q = args.search.lower()
                tasks = [t for t in tasks if q in str(t.get("title", "")).lower()]

            print(f"Tìm thấy {len(tasks)} tasks (Live OneTech Project #{pid}):")
            for t in tasks[:args.limit]:
                print(f"- [#{t.get('id')}] [{str(t.get('status')).upper()}] ({str(t.get('priority')).upper()}) | {t.get('title')}")

    elif args.command == "task":
        task = client.get_task(args.task_id, live=args.live)
        if not task:
            print(f"Không tìm thấy Task #{args.task_id}!")
            return

        tid = task.get("onetech_task_id") or task.get("id") or args.task_id
        code = task.get("task_id", f"TASK-{tid}")
        print(f"\n{'='*60}")
        print(f"📌 CHI TIẾT TASK: #{tid} ({code})")
        print(f"{'='*60}")
        print(f"Tiêu đề       : {task.get('title')}")
        print(f"Dự án         : {task.get('project', 'N/A')} (Project ID #{task.get('project_id', 'N/A')})")
        print(f"Trạng thái    : {str(task.get('status', 'N/A')).upper()}")
        print(f"Độ ưu tiên    : {task.get('priority', 'N/A')}")
        print(f"Sprint        : {task.get('sprint', 'Sprint None')}")
        print(f"Người phụ trách: {task.get('assignee_name', task.get('assignee', {}).get('name', 'N/A'))}")
        if task.get("due_date"):
            print(f"Hạn hoàn thành: {task.get('due_date')}")

        desc = task.get("description") or task.get("notes") or ""
        if desc:
            import re
            clean_desc = re.sub(r'<[^>]+>', ' ', desc).strip()
            clean_desc = re.sub(r'\s+', ' ', clean_desc)
            print(f"\nMô tả tóm tắt :\n{clean_desc[:400]}{'...' if len(clean_desc) > 400 else ''}")

        ac = task.get("acceptance_criteria") or []
        if ac:
            print(f"\nTiêu chuẩn nghiệm thu (Acceptance Criteria):")
            for idx, a in enumerate(ac, 1):
                print(f"  {idx}. {a}")

        if args.comments:
            comments = client.get_comments(tid)
            print(f"\nBình luận ({len(comments)}):")
            for c in comments:
                author = c.get("author", {}).get("firstName", "") + " " + c.get("author", {}).get("lastName", "")
                created = (c.get("createdAt") or "").split("T")[0]
                body = (c.get("content") or "").strip()
                print(f"- [{created}] {author.strip() or 'User'}:\n  {body}\n")
        print(f"{'='*60}\n")

    elif args.command == "comments":
        if args.add:
            msg = args.add.replace("\\n", "\n")
            if args.image:
                print(f"Đang upload ảnh đính kèm: {args.image}...")
                img_url = client.upload_image(args.image)
                full_url = f"https://workspace.onetech.vn{img_url}" if img_url.startswith("/") else img_url
                msg += f"\n\n![attachment]({full_url})"

            res = client.add_comment(args.task_id, msg)
            print(f"[THÀNH CÔNG] Đã đăng bình luận vào Task #{args.task_id} (ID #{res.get('id')})")
        elif args.delete:
            res = client.delete_comment(args.task_id, args.delete)
            print(f"[THÀNH CÔNG] Đã xóa bình luận #{args.delete} của Task #{args.task_id}")
        else:
            comments = client.get_comments(args.task_id)
            print(f"Danh sách {len(comments)} bình luận của Task #{args.task_id}:")
            for c in comments:
                author = c.get("author", {}).get("firstName", "") + " " + c.get("author", {}).get("lastName", "")
                created = c.get("createdAt") or ""
                cid = c.get("id")
                body = (c.get("content") or "").strip()
                print(f"\n[#{cid}] {created} | {author.strip() or 'User'}:")
                print(f"{body}")

    elif args.command == "update":
        payload = {}
        if args.title: payload["title"] = args.title
        if args.status: payload["status"] = args.status
        if args.sprint is not None: payload["sprintId"] = args.sprint
        if args.priority: payload["priority"] = args.priority
        if hasattr(args, "description") and args.description:
            payload["description"] = args.description.replace("\\n", "\n")

        if not payload:
            print("Không có thông tin nào để cập nhật.")
            return

        res = client.update_task(args.task_id, payload)
        print(f"[THÀNH CÔNG] Đã cập nhật Task #{args.task_id}: {res.get('title')}")

    elif args.command == "create":
        # Resolve assignee if passed as alias
        assignee_id = args.assignee
        if assignee_id.lower() in ["dinhpl", "dinh"]:
            assignee_id = "8a8ba39d-f341-4202-ba1d-b530f94f0168"
        elif assignee_id.lower() in ["vietnt", "viet", "me"]:
            assignee_id = DEFAULT_USER_ID

        clean_desc = args.description.replace("\\n", "\n") if args.description else ""
        payload = {
            "title": args.title,
            "description": clean_desc,
            "type": args.type,
            "priority": args.priority,
            "status": args.status,
            "sprintId": args.sprint,
            "assigneeId": assignee_id
        }
        if args.severity:
            payload["severity"] = args.severity
        if args.parent:
            payload["parentId"] = args.parent

        res = client.create_task(args.project, payload)
        new_id = res.get("id")
        print(f"[THÀNH CÔNG] Đã tạo Task mới #{new_id}: {res.get('title')}")

        if args.image and new_id:
            print(f"Đang upload ảnh đính kèm: {args.image}...")
            img_url = client.upload_image(args.image)
            full_url = f"https://workspace.onetech.vn{img_url}" if img_url.startswith("/") else img_url
            comment_content = f"Ảnh đính kèm:\n\n![attachment]({full_url})"
            client.add_comment(new_id, comment_content)
            print(f"[THÀNH CÔNG] Đã đính kèm ảnh vào comment của Task #{new_id}!")

    elif args.command == "upload":
        url = client.upload_image(args.image_path)
        print(f"[THÀNH CÔNG] Ảnh đã được upload: https://workspace.onetech.vn{url}")

    elif args.command == "comment":
        msg = args.message.replace("\\n", "\n") if args.message else ""
        if args.image:
            print(f"Đang upload ảnh đính kèm: {args.image}...")
            img_url = client.upload_image(args.image)
            full_url = f"https://workspace.onetech.vn{img_url}" if img_url.startswith("/") else img_url
            msg += f"\n\n![attachment]({full_url})"

        res = client.add_comment(args.task_id, msg)
        print(f"[THÀNH CÔNG] Đã đăng comment vào Task #{args.task_id} (Comment ID #{res.get('id')})")

    elif args.command == "timesheet":
        if args.action == "today":
            res = client.get_daily_time(date_str=args.date)
            date_val = res.get("date", "Hôm nay")
            total = res.get("totalHours", 0)
            target = 8.0
            pct = min(100, int((total / target) * 100)) if target > 0 else 0
            print(f"📊 Timesheet ngày {date_val}: {total}h / {target}h ({pct}%)")

        elif args.action == "week":
            from datetime import datetime, timedelta
            now = datetime.now()
            start_of_week = now - timedelta(days=now.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            s_date = args.date or start_of_week.strftime("%Y-%m-%d")
            e_date = end_of_week.strftime("%Y-%m-%d")

            days_data = client.get_user_timesheet(s_date, e_date)
            total_week_hours = sum(float(d.get("totalHours", 0)) for d in days_data)
            pct_week = min(100, int(total_week_hours / 40.0 * 100))

            print(f"📊 BẢNG THỐNG KÊ TIMESHEET TUẦN ({s_date} -> {e_date}):")
            print(f"Tổng số giờ đã ghi nhận: {total_week_hours:.1f}h / 40.0h ({pct_week}%)")
            print("-" * 65)

            days_map = {d.get("date"): d for d in days_data}
            curr = start_of_week
            while curr <= end_of_week:
                d_str = curr.strftime("%Y-%m-%d")
                weekday_name = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"][curr.weekday()]
                day_info = days_map.get(d_str)
                h = float(day_info.get("totalHours", 0)) if day_info else 0.0
                status_icon = "✅" if h >= 8.0 else ("⚠️" if h > 0 else "⚪")
                print(f"{status_icon} {weekday_name} ({d_str}): {h:.1f}h / 8.0h")
                if day_info and day_info.get("entries"):
                    for e in day_info["entries"]:
                        print(f"    • [#{e.get('taskId')}] {e.get('hours')}h ({e.get('activityType')}): {e.get('taskTitle')}")
                curr += timedelta(days=1)

        elif args.action == "list":
            if not args.task:
                print("[LỖI] Cần truyền --task <TASK_ID> để xem timesheet của task.")
                return
            entries = client.get_time_entries(args.task)
            print(f"Danh sách {len(entries)} bản ghi timesheet của Task #{args.task}:")
            for e in entries:
                u = e.get("user") or {}
                u_name = f"{u.get('firstName', '')} {u.get('lastName', '')}".strip() or "Me"
                log_d = (e.get("loggedDate") or "")[:10]
                print(f"- [#{e.get('id')}] {e.get('hours')}h ({e.get('activityType')}) bởi {u_name} ngày {log_d}: {e.get('description') or 'Không có ghi chú'}")

        elif args.action == "log":
            if not args.task or not args.hours:
                print("[LỖI] Cần truyền --task <TASK_ID> và --hours <SỐ_GIỜ> (ví dụ: --task 8274 --hours 2.5)")
                return
            desc = args.desc.replace("\\n", "\n") if args.desc else ""
            res = client.log_time(
                task_id=args.task,
                hours=args.hours,
                description=desc,
                activity_type=args.type,
                logged_date=args.date
            )
            print(f"[THÀNH CÔNG] Đã log {args.hours}h ({args.type}) vào Task #{args.task} ngày {args.date or 'hôm nay'}!")
            if desc:
                print(f"Ghi chú: {desc}")

        elif args.action == "delete":
            if not args.entry_id:
                print("[LỖI] Cần truyền --entry-id <ID> để xóa.")
                return
            ok = client.delete_time_entry(args.entry_id)
            if ok:
                print(f"[THÀNH CÔNG] Đã xóa bản ghi timesheet #{args.entry_id}!")
            else:
                print(f"[LỖI] Không thể xóa bản ghi timesheet #{args.entry_id}.")

if __name__ == "__main__":
    main()
