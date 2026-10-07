---
name: assistant-supervisor
description: >-
  Supervisor Routing & Orchestration Skill: Tự động phân tích ý định (Intent Classification), điều phối các subagents chuyên trách, kích hoạt kiểm thử Actor-Critic và bảo vệ hệ thống bằng HITL Guardrails.
---

# Assistant Supervisor: SOTA Agent Orchestrator

Skill này đóng vai trò Trực ban Điều hành (Central Orchestrator) của Antigravity.

## 🎯 4 Nhiệm Vụ Tự Động Hóa Của Supervisor

### 1. Intent Recognition (Nhận Diện Ý Định Tự Động)
- Phân tích câu lệnh của User và tự quyết định kích hoạt luồng tương ứng (`dev-executor`, `techlead-auditor`, `pm-decomposer`, hoặc `meta-learner`).

### 2. Episodic Memory Retrieval (Tra Cứu Lịch Sử Giải Pháp)
- Tra cứu `docs/memory/episodic_history.json` và `docs/memory/learned_patterns.json` để kiểm tra xem lỗi hoặc bài toán này đã từng được giải quyết thành công trước đây hay chưa.

### 3. Actor-Critic Verification Loop (Vòng Lặp Phê Bình 2 Tầng)
- Chạy thử nghiệm code hoặc thiết kế.
- Tự động gọi `techlead-auditor` để thẩm định kết quả trước khi đưa cho User.

### 4. Episodic Logging (Ghi Nhận Giải Pháp Vào Episodic Memory)
- Sau khi hoàn thành xuất sắc một tác vụ phức tạp hoặc sửa một bug khó, tự động lưu lại "Execution Trace" vào `docs/memory/episodic_history.json`.
