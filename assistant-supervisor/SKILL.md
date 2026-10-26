---
name: assistant-supervisor
description: "Dùng khi một yêu cầu lớn trải nhiều vai trò (code + review + PM + compliance) hoặc chưa rõ nên dùng skill nào: phân loại ý định, kiểm tra rủi ro qua production-safety-guardrail, chọn skill chuyên trách, tra lịch sử giải pháp đã có và tự phản biện (actor-critic) trước khi bàn giao. Dùng khi người dùng giao việc nhiều bước kiểu \"lo hết giúp\", \"làm từ đầu tới cuối\". Không dùng khi việc chỉ có một bước và đã có skill chuyên trách rõ ràng."
compatibility: "Đọc/ghi dữ liệu trong workspace ITGVietAssistant ($ITGVIET_HOME, mặc định D:\\ITGVietAssistant)."
---

# [SKILL-SUP-001] Assistant Supervisor — điều phối nhiều skill

Dùng cho việc lớn nhiều bước: chia việc theo vai trò, gọi đúng skill chuyên trách cho từng phần, chặn rủi ro trước khi làm, tự phản biện trước khi bàn giao. Việc một bước thì gọi thẳng skill chuyên trách, không cần supervisor.

Dữ liệu workspace: `$ITGVIET_HOME` (mặc định `D:\ITGVietAssistant`).

## Gotchas

- Có hai bản memory: `$ITGVIET_HOME/docs/memory/` (master theo CLAUDE.md của workspace) và `$ITGVIET_HOME/memory/` (junction `~/.claude/shared-memory`). `rules/rule-00-supervisor-router.md` còn trỏ `memory/reflexion_log.json`. Đọc/ghi bản `docs/memory/`; nếu thấy hai bản lệch nhau thì báo người dùng thay vì tự gộp.
- `episodic_history.json` và `reflexion_log.json` hiện gần như rỗng (mỗi file 1 mục). Không có kết quả tra cứu thì cứ làm tiếp, đừng coi là lỗi.
- Không ghi trùng với auto-memory của Claude Code (`~/.claude/projects/<dự án>/memory/`). Auto-memory giữ sở thích/feedback theo từng dự án; `episodic_history.json` chỉ giữ **lời giải của bài toán khó dùng lại được cho nhiều dự án**. Một sự việc chỉ ghi một nơi.
- Thao tác terminal trên Windows: kiểm tra cú pháp PowerShell (`Get-ChildItem`, `Select-String`) thay vì alias Unix (nguồn: `reflexion_log.json` REFLECT-2026-001).

## Bảng định tuyến

| Ý định | Skill |
|---|---|
| Thao tác có thể mất dữ liệu / deploy prod / auth / billing / DB schema | `production-safety-guardrail` **trước tiên** |
| Báo lỗi, crash, sửa/refactor nhỏ 1–5 file | `quick-fix` |
| Tính năng mới, đổi kiến trúc, cần spec | `feature-spec` → rồi `dev-executor` |
| Code task đã có spec/yêu cầu rõ | `dev-executor` |
| Review code trước merge/release | `techlead-auditor` (tìm bug nhanh trên diff: `/code-review`) |
| Chuẩn bị release, test plan, Go/No-Go | `release-quality-gate` |
| Chia story/epic thành task, ước lượng | `pm-decomposer` |
| Task/ticket trên OneTech, Feedback Hub | `onetech-workspace-manager` |
| Việc cá nhân không có trên OneTech | `task-lifecycle-manager` |
| Tài liệu kỹ thuật cho codebase | `tech-doc-generator` (một sơ đồ: `archify`) |
| Giao diện, design token, icon SVG | `pro-uiux-design` |
| Ảnh, icon app, asset game, banner store | `visual-artist` |
| Dịch/duyệt chuỗi UI, store listing đa ngôn ngữ | `cultural-localization-strategist` |
| Chính sách Google Play/App Store, quyền, bản quyền asset | `store-policy-compliance` |
| Checklist publish, bàn giao asset, báo cáo cho chủ studio | `project-assistant` |
| R&D, tối ưu thuật toán, "đủ tốt chưa" | `rnd-loop` |
| Log/stack trace rất dài | `context-compressor` |
| File lô lương Vietcombank | `vcb-payroll-exporter` |
| Luyện EN/JA / đánh giá tiến độ học | `it-language-coach` / `language-progress-auditor` |
| Người dùng sửa cách làm, muốn ghi luật lâu dài | `meta-learner` (vượt ngưỡng → `memory-consolidator`) |
| Đóng gói quy trình thành skill | `skill-factory` |

## Quy trình

1. **Triage rủi ro.** Có bước nào thuộc dòng đầu bảng → chạy `production-safety-guardrail` và chờ người dùng xác nhận trước khi làm bước đó.
2. **Tra lời giải cũ** trong `$ITGVIET_HOME/docs/memory/episodic_history.json` và `learned_patterns.json` khi bài toán giống việc đã làm.
3. **Lập kế hoạch**: liệt kê các phần, mỗi phần gắn một skill theo bảng trên; thứ tự theo phụ thuộc.
4. **Thực thi và tự phản biện**: sau mỗi phần chạy build/test/lint thật (RULE-001 trong `learned_patterns.json`: chưa PASS trong terminal thì chưa xong); phần code chạy `techlead-auditor`; tính năng app sắp lên store chạy `store-policy-compliance`. Thất bại → ghi lý do vào `docs/memory/reflexion_log.json`, sửa rồi mới báo.
5. **Ghi lời giải**: chỉ khi bài toán khó và dùng lại được, thêm một mục vào `docs/memory/episodic_history.json` theo đúng cấu trúc mục hiện có (`id`, `timestamp`, `task_type`, `summary`, `resolution`, `outcome`).
