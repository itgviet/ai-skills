import sys
import argparse
import json
from pathlib import Path

# Add script dir to sys.path
sys.path.insert(0, str(Path(__file__).parent))
from onetech_client import OneTechClient, DEFAULT_USER_ID

def main():
    parser = argparse.ArgumentParser(description="OneTech Workspace CLI Automation Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. Projects
    projects_p = subparsers.add_parser("projects", help="Liệt kê danh sách dự án của bạn")

    # 2. Sync
    sync_p = subparsers.add_parser("sync", help="Đồng bộ tasks về tasks_store.json")
    sync_p.add_argument("--project", type=int, default=82, help="Project ID (Mặc định: 82)")

    # 3. List
    list_p = subparsers.add_parser("list", help="Liệt kê tasks")
    list_p.add_argument("--project", type=int, default=82, help="Project ID")
    list_p.add_argument("--sprint", type=int, default=None, help="Sprint ID")
    list_p.add_argument("--mine", action="store_true", help="Chỉ lấy task gán cho tôi")

    # 4. Update
    update_p = subparsers.add_parser("update", help="Cập nhật task")
    update_p.add_argument("task_id", type=int, help="Task ID (ví dụ: 7305, 8273, 8086)")
    update_p.add_argument("--title", type=str, help="Tiêu đề mới")
    update_p.add_argument("--status", type=str, choices=["todo", "in_progress", "review", "done", "cancel"], help="Trạng thái mới")
    update_p.add_argument("--sprint", type=int, help="Sprint ID mới")
    update_p.add_argument("--priority", type=str, choices=["low", "medium", "high", "critical"], help="Mức ưu tiên mới")

    # 5. Create
    create_p = subparsers.add_parser("create", help="Tạo task mới / bug mới")
    create_p.add_argument("--project", type=int, default=82, help="Project ID")
    create_p.add_argument("--title", type=str, required=True, help="Tiêu đề task")
    create_p.add_argument("--sprint", type=int, default=79, help="Sprint ID (Mặc định: 79)")
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
    comment_p = subparsers.add_parser("comment", help="Đăng bình luận vào task")
    comment_p.add_argument("task_id", type=int, help="Task ID")
    comment_p.add_argument("--message", type=str, required=True, help="Nội dung bình luận")
    comment_p.add_argument("--image", type=str, default=None, help="Đường dẫn file ảnh đính kèm")

    args = parser.parse_args()
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
        assignee = DEFAULT_USER_ID if args.mine else None
        tasks = client.get_tasks(project_id=args.project, sprint_id=args.sprint, assignee_id=assignee)
        print(f"Tìm thấy {len(tasks)} tasks:")
        for t in tasks:
            print(f"- [#{t.get('id')}] [{str(t.get('status')).upper()}] ({str(t.get('priority')).upper()}) | {t.get('title')}")

    elif args.command == "update":
        payload = {}
        if args.title: payload["title"] = args.title
        if args.status: payload["status"] = args.status
        if args.sprint is not None: payload["sprintId"] = args.sprint
        if args.priority: payload["priority"] = args.priority

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

        payload = {
            "title": args.title,
            "description": args.description,
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
        msg = args.message
        if args.image:
            print(f"Đang upload ảnh đính kèm: {args.image}...")
            img_url = client.upload_image(args.image)
            full_url = f"https://workspace.onetech.vn{img_url}" if img_url.startswith("/") else img_url
            msg += f"\n\n![attachment]({full_url})"

        res = client.add_comment(args.task_id, msg)
        print(f"[THÀNH CÔNG] Đã đăng comment vào Task #{args.task_id} (Comment ID #{res.get('id')})")

if __name__ == "__main__":
    main()
