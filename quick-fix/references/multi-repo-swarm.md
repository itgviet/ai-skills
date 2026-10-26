# Multi-Repo Swarm Mode & 5 góc nhìn vai trò

Đọc file này khi bug chạm từ 2 repo/workspace trở lên (Mobile + Backend, Web + API...) hoặc là lỗi phân tán Client–Server: lệch API contract, race condition, concurrency, lifecycle bị ngắt quãng.

## Khi nào chọn Swarm thay vì Solo

| Tiêu chí | Solo Fast Mode | Multi-Agent Swarm Mode |
| :--- | :--- | :--- |
| Phạm vi repo | 1 repo | ≥ 2 repo (cross-repo) |
| Độ phức tạp | Micro bug, lint, UI tweak, 1–3 file | Lệch contract API, race condition, lifecycle |
| Cách chạy | 1 agent tự đóng nhiều vai | Supervisor + worker theo domain + critic độc lập |
| Lý do | Nhanh, ít token | Critic độc lập tránh thiên kiến xác nhận; mỗi worker giữ context gọn |

Công cụ giao việc cho subagent: Claude Code: `Agent` (subagent/fork) · Antigravity: `invoke_subagent` / `manage_subagents` / `send_message`.

## Vai trò trong Swarm

```
Supervisor (khóa scope, chốt API contract, chia việc)
   ├─ Worker Backend  (API, ORM, job queue; chạy pytest / go test / mvn test)
   └─ Worker Client   (Mobile/Web: state, event; chạy tsc, UI test)
          ↓ bàn giao git diff của cả hai bên
Critic (chỉ review, không viết code) → PASS → Delivery report
```

1. **Supervisor (agent cha):** nhận bug, phân tích root cause liên hệ thống, chốt contract (schema request/response) trước khi giao việc, để hai worker sửa theo cùng một hợp đồng. Không đọc log trung gian của worker để giữ context gọn.
2. **Worker theo domain:** mỗi worker làm trong repo của mình, sửa theo Minimal Diff, tự chạy test của stack đó.
3. **Critic:** không viết code, vì người viết code dễ bỏ qua lỗi của chính mình. Chỉ tìm: lệch contract giữa hai bên, race condition, mất dữ liệu, "vá triệu chứng". Supervisor chỉ cho commit khi Critic PASS.

## 5 góc nhìn mọi thay đổi phải thỏa (Solo cũng áp dụng)

1. **Quản lý:** khóa scope, không "tiện tay" sửa lan sang phần khác.
2. **Lập trình viên:** sửa nguyên nhân gốc, giữ kiến trúc và style hiện có.
3. **Tester/QC:** không tái phát lỗi cũ, có bằng chứng chạy thật, thử trường hợp biên.
4. **Designer/UX:** không vỡ layout responsive, màu, spacing của design system.
5. **Khách hàng:** có tóm tắt 1–2 câu dễ hiểu về lợi ích của thay đổi.

Báo cáo bàn giao theo 5 góc nhìn này: dùng mẫu `assets/report-template.md`.
