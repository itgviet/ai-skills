---
name: meta-learner
description: "Dùng khi người dùng sửa cách làm của trợ lý hoặc nêu một sở thích cần áp dụng lâu dài (\"lần sau đừng...\", \"từ giờ luôn...\", \"nhớ là...\") và muốn ghi thành luật trong workspace ITGVietAssistant: tìm luật tương tự trong unit_registry.json và learned_patterns.json, ưu tiên sửa luật cũ thay vì tạo mới, báo lại Unit ID đã cập nhật. Không dùng cho ghi chú chỉ liên quan cuộc hội thoại hiện tại."
compatibility: "Đọc/ghi dữ liệu trong workspace ITGVietAssistant ($ITGVIET_HOME, mặc định D:\\ITGVietAssistant)."
---

# [SKILL-META-001] Meta-Learner — ghi luật mới, gộp trước khi thêm

Biến một lần người dùng sửa cách làm thành luật lâu dài trong workspace ITGVietAssistant (`$ITGVIET_HOME`, mặc định `D:\ITGVietAssistant`), sao cho không sinh luật trùng.

## Ghi vào đâu

| Loại tri thức | Nơi ghi |
|---|---|
| Luật làm việc dùng cho mọi dự án (dev, review, PM, bảo mật) | `$ITGVIET_HOME/docs/memory/learned_patterns.json`, hoặc file luật tương ứng trong `$ITGVIET_HOME/rules/` |
| Sở thích cá nhân của người dùng (giao tiếp, định dạng task OneTech…) | `$ITGVIET_HOME/docs/memory/user_preferences.md` |
| Feedback/sự thật chỉ đúng cho **một dự án** | auto-memory của agent cho dự án đó (Claude Code: `~/.claude/projects/<dự án>/memory/`), **không** ghi vào workspace |
| Bài học R&D | `rnd_playbook.md` qua skill `rnd-loop` |

Một sự việc chỉ ghi một nơi. Trước khi ghi vào workspace, kiểm tra auto-memory của agent đã có chưa; nếu đã có thì chỉ chuyển lên workspace khi nó đúng cho nhiều dự án.

## Gotchas

- Có hai bản: `docs/memory/` (master) và `memory/` (junction `~/.claude/shared-memory`). `docs/memory/user_preferences.md` **cũ hơn** `memory/user_preferences.md` (bản `memory/` có thêm quy ước task OneTech: tiêu đề tiếng Anh `[Module] ...`, nội dung tiếng Việt 3 phần). Khi sửa preferences, so hai bản trước; nếu lệch thì báo người dùng chọn bản chuẩn thay vì ghi đè.
- `learned_patterns.json` có cấu trúc `learned_rules[]` với `id` dạng `RULE-00N`, `category` (`DEVELOPER`/`TECHLEAD`/`PM`…), `pattern`, `rule`, `source`. ID này khác không gian tên với Unit ID trong `rules/` (`RULE-DEV-001`…), đừng lẫn.
- Ngưỡng 30 mục lấy từ `anti_entropy_policy.max_active_patterns` trong `docs/memory/unit_registry.json`; đọc giá trị ở đó thay vì nhớ số.

## Quy trình

1. **Trích luật**: một câu hành động được ("Không báo hoàn thành khi chưa chạy test PASS trong terminal"), kèm lý do người dùng đưa ra và nguồn (ngày, việc gì). Không ghi lời khen chung chung hay việc chỉ liên quan cuộc hội thoại hiện tại.
2. **Tìm trùng** trong `learned_patterns.json`, các file `rules/*.md` và `unit_registry.json` (cùng bản chất dù khác chữ, ví dụ "dùng camelCase" và "tên biến phải là camelCase").
3. **Gộp hơn tạo mới**: có luật gần giống → sửa câu chữ luật đó. Luật mới trái luật cũ → cập nhật luật cũ, ghi lý do đổi.
4. **Kiểm ngưỡng**: số mục `learned_rules` chạm ngưỡng → chạy `memory-consolidator` trước khi thêm.
5. **Báo lại** cho người dùng: luật đã ghi/sửa, file, ID.
