---
name: skill-factory
description: >-
  Skill tự động đóng gói các quy trình làm việc lặp lại (SOP) thành một Custom Skill độc lập hoàn chỉnh (.gemini/skills/<skill-name>/SKILL.md).
---

# Skill Factory: Automated Skill Generator

Sử dụng skill này khi cần biến một quy trình làm việc thủ công (Code review checklist đặc thù, Sprint report theo mẫu JIRA của công ty, Auto-deployment script...) thành một Skill tái sử dụng.

## 📋 Hướng Dẫn Thực Thi

1. **Xác định thông tin Skill**:
   - `name`: Tên viết bằng kebab-case (ví dụ: `jira-sprint-report`, `docker-security-audit`).
   - `description`: Mô tả ngắn gọn 1-2 câu về mục tiêu và khi nào cần kích hoạt.
   - `workflow`: Các bước thực thi chi tiết từ 1 đến N.

2. **Khởi tạo File cấu trúc**:
   Tạo file mới tại `.gemini/skills/<skill-name>/SKILL.md` với cấu trúc YAML frontmatter chuẩn:

```markdown
---
name: <skill-name>
description: <Mô tả mục tiêu của skill>
---

# <Tên Skill Hướng Dẫn>

## 📌 Điều Kiện Kích Hoạt
Kích hoạt skill này khi...

## 🔄 Các Bước Thực Thi
1. Bước 1: ...
2. Bước 2: ...

## 🎯 Tiêu Chí Hoàn Thành (Acceptance Criteria)
- [ ] Checklist 1
- [ ] Checklist 2
```

3. **Đăng ký Skill với Trợ Lý**:
   Ghi nhận skill vừa tạo vào danh mục skill local để tự động khuyên dùng cho các task sau.
