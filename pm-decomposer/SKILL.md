---
name: pm-decomposer
description: >-
  Skill dành cho Project Manager Agent: Tự động phân rã User Story/BRD thành các Micro-tasks kỹ thuật chi tiết kèm tiêu chuẩn nghiệm thu (Acceptance Criteria) và estimate.
---

# PM Decomposer: Agile Task Breakdown Engine

Skill này tự động hóa công việc quản lý backlog, lập kế hoạch Sprint và phân rã công việc cho team.

## ⚙️ Quy Trình Phân Rã 3 Bước

### Bước 1: Analysis (Phân Tích User Story)
Trích xuất:
- **Who**: Đối tượng người dùng.
- **What**: Tính năng/Yêu cầu kinh doanh.
- **Why**: Giá trị mang lại.

### Bước 2: Decomposition (Phân Rã Kỹ Thuật)
Tách thành các Micro-tasks kỹ thuật <= 4h:
- DB Schema Migration / Data Model
- API Endpoint Implementation
- UI Component & Integration
- Unit / E2E Testing Task

### Bước 3: Acceptance Criteria & Markdown Export
Với mỗi task, tự động sinh:
- **Title**: `[FE/BE/DB] Tên task ngắn gọn`
- **Estimate**: Story points hoặc Giờ làm việc.
- **Acceptance Criteria**: Danh sách checklist dạng `- [ ]` cụ thể.
- **Dependencies**: Task nào cần hoàn thành trước.
