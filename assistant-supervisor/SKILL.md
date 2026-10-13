---
name: assistant-supervisor
description: "Autonomous Supervisor Router: intent classification, agent orchestration, actor-critic verification, and HITL guardrails."
---

# Assistant Supervisor: SOTA Agent Orchestrator

Skill này đóng vai trò Trực ban Điều hành (Central Orchestrator) của Antigravity.

## 🎯 4 Nhiệm Vụ Tự Động Hóa Của Supervisor

### 1. Intent Recognition & Safety Triage (Nhận Diện Ý Định & Thẩm Định An Toàn)
- Tự động quét và phân loại rủi ro thông qua `production-safety-guardrail`:
  * Nếu phát hiện yêu cầu rủi ro cao (xóa dữ liệu, sửa DB schema, can thiệp auth/thanh toán) -> Kích hoạt **HARD STOP**, lập Báo cáo Đánh giá Tác động và xin User phê duyệt trực tiếp.
  * Với các yêu cầu thông thường: Phân tích câu lệnh và kích hoạt luồng tương ứng (`project-assistant`, `dev-executor`, `techlead-auditor`, `pm-decomposer`, `pro-uiux-design`, `visual-artist`, `store-policy-compliance`, hoặc `meta-learner`).

### 2. Episodic Memory Retrieval (Tra Cứu Lịch Sử Giải Pháp)
- Tra cứu `docs/memory/episodic_history.json` và `docs/memory/learned_patterns.json` để kiểm tra xem lỗi hoặc bài toán này đã từng được giải quyết thành công trước đây hay chưa.

### 3. Actor-Critic Verification Loop (Vòng Lặp Phê Bình Đa Tầng)
- Chạy thử nghiệm code hoặc thiết kế trên môi trường giả lập an toàn (Local Emulator), tuân thủ nguyên tắc Zero-Destructive của `production-safety-guardrail`.
- Kỹ thuật: Tự động gọi `techlead-auditor` để thẩm định chất lượng mã nguồn & bảo mật.
- Pháp chế & Chính sách Store: Tự động gọi `store-policy-compliance` để rà soát bản quyền tài nguyên (Asset/Font/Audio), quyền riêng tư người dùng (GDPR/COPPA/Data Safety), và các điều khoản bắt buộc của Google Play / App Store trước khi release hoặc chốt tính năng.

### 4. Episodic Logging (Ghi Nhận Giải Pháp Vào Episodic Memory)
- Sau khi hoàn thành xuất sắc một tác vụ phức tạp hoặc sửa một bug khó, tự động lưu lại "Execution Trace" vào `docs/memory/episodic_history.json`.

