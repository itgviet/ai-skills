---
name: pm-decomposer
description: "Dùng khi cần chia user story, epic hoặc yêu cầu khách thành các task nhỏ (≤ 4 giờ) có tiêu đề [FE/BE/DB], ước lượng, tiêu chí nghiệm thu dạng checklist và phụ thuộc, để đưa vào sprint hoặc tạo trên OneTech. Dùng khi người dùng nói \"chia task\", \"breakdown\", \"ước lượng giúp\", \"lên sprint\". Đặc tả kỹ thuật đầy đủ → feature-spec."
---

# PM Decomposer: Agile Task Breakdown Engine

Chia user story/epic/yêu cầu khách thành micro-task sẵn sàng đưa vào sprint.

## Gotchas

- **Mỗi task ≤ 4 giờ** và có AC kiểm thử được (RULE-PM-001, learned_patterns RULE-003). Task ước lượng > 4h thì chia tiếp — task lớn là nơi ước lượng sai nhiều nhất.
- **Liệt kê file cần sửa/tạo** cho từng task (RULE-PM-001), dựa trên đọc repo thật, không đoán theo tên module.
- **Ghi phụ thuộc** giữa các task để xếp thứ tự trong sprint.
- **Đưa lên OneTech:** tạo task bằng skill `onetech-workspace-manager` (lệnh `create`); khi tạo hàng loạt trên hệ thống thật, liệt kê danh sách cho người dùng duyệt trước rồi mới tạo.
- Story có đổi schema DB, API breaking hoặc > 5 file → làm spec bằng `feature-spec` trước, rồi lấy `tasks.md` làm đầu vào.

## Quy trình

1. **Phân tích story:** Who (người dùng nào) · What (nhu cầu) · Why (giá trị). Thiếu thông tin quan trọng thì hỏi 1–3 câu trước khi chia.
2. **Phân rã kỹ thuật** theo lớp, chỉ những lớp story thực sự chạm tới: DB schema/migration · API endpoint · UI component & tích hợp · unit/E2E test.
3. **Viết từng task theo mẫu:**

```markdown
### [FE|BE|DB|QA] <Tên task ngắn>
- **Ước lượng:** <giờ, ≤ 4h> (hoặc story point nếu team dùng SP)
- **File:** `path/a.ts` (sửa), `path/b.ts` (tạo)
- **Phụ thuộc:** <task ID | không>
- **AC:**
  - [ ] Given <bối cảnh>, When <hành động>, Then <kết quả>
  - [ ] <tiêu chí kiểm được khác>
```

4. **Tổng kết:** bảng task (ID, tên, giờ, phụ thuộc) + tổng giờ, để người dùng chọn đưa vào sprint nào.
