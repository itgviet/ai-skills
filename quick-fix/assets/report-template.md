### 📋 BÁO CÁO HOÀN THÀNH (QUICK FIX REPORT)

#### 👔 1. Quản lý (Scope & DoD)
- **Tech Stack:** [Node.js / Python / Java / Go / C# / ...]
- **Chế độ thực thi:** [Solo Fast Mode / Multi-Agent Swarm Mode]
- **Git Branch:** `[branch_name]` (theo RULE-GIT-001)
- **Commit Message:** `[type(scope): subject]` (Conventional Commits)
- **File đã sửa:** `[file_path_1]`, `[file_path_2]`
- **Trạng thái:** ✅ Đúng scope, không đụng module ngoài.

#### 💻 2. Lập trình viên (Technical Summary & Self-Audit)
- **Root Cause:** [nguyên nhân gốc, kèm file:dòng]
- **Giải pháp:** [đã sửa gì và vì sao sửa ở đó]
- **Tự review / Critic review:** [kết quả soát git diff: log thừa, null-safety, idempotency, side-effect]

#### 🧪 3. Tester / QC (Verification Evidence & Traceability)
- **Đối chiếu yêu cầu:** [từng yêu cầu → đã đáp ứng ở đâu]
- **Kiểm thử tự động (lệnh thật đã chạy + kết quả):**
  - Build/Type-check: `[lệnh]` → [Pass/Fail]
  - Lint: `[lệnh]` → [Pass/Fail]
  - Unit/Regression: `[lệnh]` → [x passed, y failed]
- **Edge cases đã thử:** [null/undefined, mạng chậm, kill app, double-submit...]
- **📱 Hướng dẫn kiểm thử thủ công** (bắt buộc khi có UI/Mobile/Integration):
  - **Môi trường & điều kiện:** [thiết bị/trình duyệt, màn hình, tài khoản]
  - **Bước 1:** [thao tác] → *Kỳ vọng:* [kết quả]
  - **Bước 2:** [thao tác với chỗ đã fix] → *Kỳ vọng:* [hành vi đúng]
  - **Bước 3:** [lưu/submit/đối chiếu dữ liệu] → *Kỳ vọng:* [dữ liệu đúng]
  - **Ngoại lệ:** [hủy giữa chừng/mất mạng/đổi tham số] → *Kỳ vọng:* [xử lý an toàn]

#### 🎨 4. Designer / UX (Visual & Interaction)
- **Tác động UI/UX:** [ảnh chụp 2 breakpoint nếu có đổi UI; layout/màu/spacing giữ nguyên hay đổi gì]

#### 🤝 5. Khách hàng (Business Impact)
- **Tóm tắt:** [1–2 câu không thuật ngữ: người dùng cuối thấy gì khác]
