---
name: memory-consolidator
description: "Dùng khi bộ nhớ/luật của workspace ITGVietAssistant phình to hoặc mâu thuẫn: learned_patterns.json vượt 30 mục, một file trong rules/ vượt 150 dòng, có luật trùng hoặc trái nhau, log cũ hơn 60 ngày. Gộp trùng, đánh DEPRECATED luật cũ, chuyển log vào archive và đồng bộ unit_registry.json. Dùng khi người dùng nói \"dọn memory\", \"gộp rule\", hoặc khi meta-learner báo vượt ngưỡng. Auto-memory của Claude Code → consolidate-memory."
compatibility: "Đọc/ghi dữ liệu trong workspace ITGVietAssistant ($ITGVIET_HOME, mặc định D:\\ITGVietAssistant)."
---

# [SKILL-PRUNE-001] Memory Consolidator — dọn và gộp tri thức workspace

Giữ luật và memory của workspace ITGVietAssistant (`$ITGVIET_HOME`, mặc định `D:\ITGVietAssistant`) gọn và không mâu thuẫn. Phạm vi chỉ gồm dữ liệu workspace; auto-memory theo dự án của Claude Code (`~/.claude/projects/<dự án>/memory/`) do `consolidate-memory` lo, không đụng tới ở đây.

## Ngưỡng

Đọc từ `anti_entropy_policy` trong `$ITGVIET_HOME/docs/memory/unit_registry.json` (hiện tại):

| Thành phần | Ngưỡng | Khi vượt |
|---|---|---|
| `docs/memory/learned_patterns.json` → `learned_rules` | `max_active_patterns` = 30 | gom nhóm, gộp mục cùng bản chất |
| Mỗi file `rules/*.md` | `max_lines_per_rule_file` = 150 dòng | tách phần chi tiết sang file tham chiếu hoặc gộp các luật nhỏ |
| Log/lịch sử (`episodic_history.json`, `reflexion_log.json`, archive task) | cũ hơn 60 ngày, không còn dùng | chuyển vào `docs/memory/archive/` |

## Gotchas

- Hai bản memory song song: `docs/memory/` (master) và `memory/` (junction `~/.claude/shared-memory`). Hiện đã lệch: `unit_registry.json` và `user_preferences.md` khác nhau giữa hai bản; `memory/tasks_store.json` ~450 KB trong khi `docs/memory/tasks_store.json` rỗng. Không tự gộp hai bản; liệt kê khác biệt và để người dùng chọn bản chuẩn.
- `unit_registry.json` thiếu nhiều skill đang dùng (onetech-workspace-manager, production-safety-guardrail, rnd-loop, skill ngôn ngữ/đồ họa/compliance). Khi đồng bộ registry, đối chiếu với `$ITGVIET_HOME/skills/*/SKILL.md` và báo danh sách thiếu.
- `memory/rnd_playbook.md` do `rnd-loop` quản lý (giới hạn 40 mục riêng), không gộp vào `learned_patterns.json`.

## Quy trình

1. **Quét**: đếm mục/dòng theo bảng ngưỡng; liệt kê Unit ID trong `unit_registry.json`.
2. **Gộp trùng**: hai luật cùng bản chất → giữ một luật tổng quát, mục kia đổi `status` thành `CONSOLIDATED` (các trạng thái hợp lệ nằm trong `lifecycle_states` của registry).
3. **Xử lý mâu thuẫn**: chỉ dẫn mới trái chỉ dẫn cũ → luật cũ thành `DEPRECATED`, ghi lý do.
4. **Lưu trữ**: chuyển log cũ vào `docs/memory/archive/`, unit liên quan thành `ARCHIVED`.
5. **Đồng bộ registry** và báo cáo: đã gộp gì, deprecate gì, chuyển gì, còn gì vượt ngưỡng.

Bước 2–4 sửa dữ liệu luật của người dùng: trình bày danh sách thay đổi dự kiến trước, làm sau khi người dùng đồng ý.
