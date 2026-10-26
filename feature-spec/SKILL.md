---
name: feature-spec
description: "Dùng khi bắt đầu một tính năng mới, thay đổi kiến trúc hoặc mở rộng scope cần đặc tả: viết/cập nhật requirements.md, design.md, tasks.md trong docs/specs/<app_id>/, chờ người dùng duyệt, thực thi theo từng task có cổng kiểm thử và đồng bộ ngược spec khi code thay đổi. Dùng cả khi người dùng chỉ nói \"làm tính năng X\", \"lên kế hoạch cho...\" mà phạm vi vượt vài file. Sửa bug hoặc chỉnh nhỏ → quick-fix."
metadata:
  version: "2.0.0"
  author: "itgviet"
  last_updated: "2026-09-23"
---

# SKILL: Universal Feature & Architecture Specification & Execution Protocol (`feature-spec`)

Quy trình cho thay đổi lớn: tính năng/màn hình/module mới, thay đổi kiến trúc, DB migration, refactor phức tạp hoặc tác động > 5 file. Gồm hai phần: **tạo đặc tả** (requirements → design → tasks) và **thực thi đặc tả** (chạy task → cổng kiểm thử → tự audit → bàn giao).

## Gotchas

- **Vị trí spec:** `docs/specs/<app_id>/requirements.md`, `design.md`, `tasks.md` trong repo dự án (RULE-SDD-001). Không dùng `.kiro/specs/` hay `spec/` như bản cũ của skill này. Nếu CLAUDE.md/AGENTS.md của dự án quy định chỗ khác thì theo dự án.
- **Spec là tài liệu sống:** mỗi khi code thay đổi so với spec (mở rộng scope, đổi schema, thêm API), cập nhật ngược `requirements.md` → `design.md` → `tasks.md`. Bàn giao mà spec chưa khớp code bị tính FAIL quality gate (RULE-SDD-001). Thay đổi cấu trúc lớn thì cập nhật cả `SYSTEM_ARCHITECTURE_AND_USER_GUIDE.md`/`README.md` của dự án.
- **Task ≤ 4 giờ**, mỗi task có AC kiểm thử được, liệt kê file cần sửa và phụ thuộc (RULE-PM-001, learned_patterns RULE-003).
- **UI ID:** mọi màn hình, nút, input chính có `id`/`data-testid` theo tiền tố `screen-*`, `tab-*`, `modal-*`, `sheet-*`, `btn-*`, `input-*`... (RULE-UI-002). Dự án nhiều màn hình duy trì `docs/specs/<module>/ui_screen_registry.md`.
- **ADR:** thay đổi tech stack, schema hoặc thư viện lõi thì ghi ADR (RULE-ENG-001).
- **Không thêm dependency mới** khi người dùng chưa đồng ý; ưu tiên thư viện đã có trong `package.json`/`pyproject.toml`/`build.gradle`..., vì mỗi dependency mới là chi phí bảo trì và rủi ro bảo mật lâu dài.
- **Branch:** mỗi tính năng một nhánh `feat/<ticket-id>-<topic>` tách từ base mới nhất (RULE-GIT-001).

## Chọn quy trình

| Tiêu chí | `quick-fix` | `feature-spec` |
| :--- | :--- | :--- |
| Phạm vi | 1–5 file | > 5 file / nhiều module |
| Bản chất | Fix bug, UI nhỏ, refactor đơn lẻ | Tính năng, màn hình, module mới; refactor lớn |
| DB & schema | Không đổi | Có migration |
| API | Giữ nguyên | API mới hoặc breaking |

Thao tác chạm dữ liệu thật, deploy production, auth hoặc thanh toán → chạy `production-safety-guardrail` trước.

## Phần A — Tạo đặc tả

### Giai đoạn 1: Requirements
Yêu cầu mập mờ hoặc có nhiều hướng: dừng và hỏi người dùng 1–3 câu trắc nghiệm, mỗi câu có phương án `(Recommended)`, vì spec viết trên giả định sai sẽ kéo sai cả design và tasks.
Tạo `docs/specs/<app_id>/requirements.md` theo mẫu `assets/requirements.md` (đọc mẫu khi bắt đầu giai đoạn này). Phải có: in/out of scope, FR/NFR, trạng thái UI, AC dạng Given-When-Then.

### Giai đoạn 2: Technical Design
Đọc code hiện có trước khi thiết kế và ghi các file đã đọc vào mục Codebase Audit — thiết kế không dựa trên code thật thường đụng pattern sẵn có. Kiểm tra dependency manifest để tái sử dụng.
Tạo `design.md` theo mẫu `assets/design.md`: kiến trúc & data flow, schema + migration/rollback, state machine, API contract (khớp interface client sau khi API client tự transform), localization key, error/edge case.

### Giai đoạn 3: Execution Task Plan
Tạo `tasks.md` theo mẫu `assets/tasks.md`: bảng task có checkpoint và scope lock theo file, ma trận truy vết AC → task → test.

### 🛑 Gate 1: Người dùng duyệt
Trình bày tóm tắt ba file và chờ người dùng duyệt rồi mới sang Phần B, vì đây là điểm rẻ nhất để đổi hướng.

## Phần B — Thực thi đặc tả

### Giai đoạn 4: Chạy từng task
Vòng lặp: chọn task → đánh dấu `in_progress` → sửa code trong scope lock → chạy cổng kiểm thử → fail thì sửa và chạy lại → pass thì đánh dấu `completed` và commit → tới checkpoint thì dừng báo cáo.

Cổng kiểm thử sau mỗi task: build/type-check, lint, unit/regression test của stack. Ưu tiên script có sẵn trong dự án (`package.json`, `Makefile`, CI); bảng lệnh theo stack nằm ở skill `quick-fix` (Phase 5). Không đánh dấu xong khi chưa chạy (learned_patterns RULE-001).

### Giai đoạn 5: Tự audit trước khi báo cáo
- [ ] Đáp ứng đủ FR, NFR, AC trong `requirements.md`.
- [ ] Mọi text hiển thị qua localization key; đủ trạng thái Loading/Empty/Error.
- [ ] Không phá API cũ, dữ liệu DB hiện có hay module khác.
- [ ] Không còn file debug, secret hardcode; code khớp `design.md`.
- [ ] Spec đã đồng bộ ngược với code (xem Gotchas).

### Giai đoạn 6: Bàn giao
Báo cáo theo mẫu `assets/delivery.md` (5 góc nhìn + hướng dẫn kiểm thử thủ công) và chờ người dùng xác nhận.
