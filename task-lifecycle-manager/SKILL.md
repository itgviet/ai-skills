---
name: task-lifecycle-manager
description: "Dùng khi người dùng giao, hỏi hoặc báo xong việc cá nhân cần nhớ qua nhiều phiên mà không nằm trên OneTech (\"ghi lại việc này\", \"tôi còn việc gì\", \"việc X xong rồi\"): thêm task, xem bảng việc đang mở, đánh dấu DONE và lưu trữ theo tháng trong workspace ITGVietAssistant. Task có mã OneTech hoặc ticket khách → onetech-workspace-manager."
compatibility: "Đọc/ghi dữ liệu trong workspace ITGVietAssistant ($ITGVIET_HOME, mặc định D:\\ITGVietAssistant)."
---

# [SKILL-PM-003] Task Lifecycle Manager

Ghi nhận, tra cứu và đóng các việc cá nhân người dùng giao cho trợ lý, giữ được qua nhiều phiên làm việc. Lưu trữ theo `RULE-PM-002` (`rules/rule-08-task-tracking-governance.md`): một file active nhỏ đọc hằng ngày, việc đã xong chuyển sang archive theo tháng.

## Nơi lưu (trong `$ITGVIET_HOME`, mặc định `D:\ITGVietAssistant`)

| File | Vai trò |
| :--- | :--- |
| `$ITGVIET_HOME/docs/memory/tasks_active.json` | Mảng `active_tasks`: chỉ việc chưa xong (`TODO`, `IN_PROGRESS`, `BLOCKED`), giữ < 30 việc. Truy vấn hằng ngày chỉ đọc file này. |
| `$ITGVIET_HOME/docs/memory/archive/tasks/tasks_done_YYYY_MM.json` | Mảng `completed_tasks`: việc `DONE` theo tháng hoàn thành. Chỉ đọc khi người dùng hỏi lịch sử. |

## ⚠️ Gotchas

- **`data/tasks_store.json` là cache OneTech** do `onetech-workspace-manager` ghi (≈450 KB). Không đọc để trả lời "tôi còn việc gì", không ghi vào — mỗi lần `cli.py sync` sẽ ghi đè và file quá lớn để nạp vào context. Task có mã OneTech (`task 7972`) hay ticket khách thì chuyển sang `onetech-workspace-manager`.
- **`$ITGVIET_HOME/docs/memory/tasks_store.json` là file cũ (stub rỗng)**, không còn dùng — đừng ghi task mới vào đó.
- **Archive nằm trong thư mục con `archive/tasks/`**, không phải `archive/` trực tiếp như ghi trong RULE-PM-002; file tháng chưa tồn tại thì tạo mới cùng cấu trúc (`version`, `partition: "ARCHIVE_YYYY_MM"`, `description`, `completed_tasks`).
- **Mã `TASK-NNN` không có bộ đếm riêng**: lấy số lớn nhất trong `tasks_active.json` và file archive tháng hiện tại + tháng trước, cộng 1. Không tái sử dụng mã đã có.
- **Ghi file JSON bằng cách đọc → sửa → ghi lại toàn bộ** (UTF-8, giữ nguyên các trường khác như `version`, `description`) và cập nhật `last_updated` theo giờ UTC. Ghi đè bằng nội dung đoán sẽ làm mất việc của người dùng.

## Bản ghi task

```json
{
  "task_id": "TASK-001",
  "title": "Thiết kế API Authentication",
  "project": "ITGVietAssistant",
  "category": "DEV",
  "priority": "P1-HIGH",
  "status": "TODO",
  "created_at": "2026-10-06T08:50:00Z",
  "completed_at": null,
  "acceptance_criteria": ["Hash password bằng bcrypt", "Cấp phát JWT token"],
  "notes": ""
}
```

`priority`: `P0-CRITICAL` | `P1-HIGH` | `P2-MEDIUM` | `P3-LOW`. `category`: `DEV` | `LEAD` | `PM` | `OPS` | `PERSONAL`.

## Thao tác

**Thêm việc** ("ghi lại việc này", "nhắc tôi…"): sinh `task_id`, điền những trường người dùng nói; trường không rõ để mặc định (`P2-MEDIUM`, `TODO`) và nói lại cho người dùng biết đã đặt gì. Nếu active đã ≥ 30 việc, báo người dùng và đề nghị đóng/hủy bớt trước.

**Hỏi việc còn lại** ("tôi còn việc gì"): chỉ đọc `tasks_active.json`, trả bảng sắp theo ưu tiên rồi ngày tạo:

| Mã | Việc | Dự án | Ưu tiên | Trạng thái | Tiêu chí nghiệm thu |
| :---: | :--- | :---: | :---: | :---: | :--- |
| `TASK-001` | Thiết kế API Auth | `ITGVietAssistant` | 🔴 `P1-HIGH` | ⏳ `IN_PROGRESS` | Cấp phát JWT token |

Người dùng hỏi cả việc OneTech: trả bảng việc cá nhân, rồi lấy phần OneTech bằng `onetech-workspace-manager` (`cli.py list --mine --status open`) và trình bày tách riêng.

**Báo xong** ("việc X xong rồi"): tìm theo mã hoặc tiêu đề (nhiều kết quả khớp → hỏi lại), đặt `status: "DONE"`, `completed_at`, xóa khỏi `active_tasks`, thêm vào `completed_tasks` của file archive tháng hiện tại. Xác nhận lại và liệt kê các việc còn lại.

**Đổi trạng thái/ưu tiên/hủy**: sửa tại chỗ trong `tasks_active.json`; việc hủy chuyển vào archive với `status: "CANCELLED"` thay vì xóa, để còn lịch sử.

**Tra lịch sử** ("tháng trước làm gì"): lúc này mới đọc file archive tương ứng.
