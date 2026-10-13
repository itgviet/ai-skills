---
name: production-safety-guardrail
description: "Production safety guardrail & HITL circuit-breaker: detect high-risk feedback/tasks (data loss, DB mutation, auth, billing), enforce hard stops, impact assessment, and zero-destructive execution across all projects."
metadata:
  icon: shield-alert
---

# [SKILL-SEC-001] Production Safety Guardrail & Circuit-Breaker Protocol

Skill này thiết lập **Hàng rào Bảo vệ An toàn Production Toàn diện (Defense-in-Depth)** và cơ chế **Cắt Cầu Dao Khẩn Cấp (Circuit-Breaker)** áp dụng chung cho mọi dự án phần mềm (`cafenhatsinh`, `nhatsinhsite`, `issx`, `dtg` và các dự án tương lai).

Mục tiêu cốt lõi: **Bảo vệ toàn vẹn 100% dữ liệu sống (Production Data), hạ tầng và bảo mật, ngăn chặn mọi nguy cơ agent tự động xóa, phá hủy hoặc gây lỗi nghiêm trọng từ các yêu cầu/feedback chưa được kiểm soát.**

---

## 🧭 1. Ma Trận Phân Loại Rủi Ro (Risk Triage Matrix)

Mọi yêu cầu từ khách hàng hoặc task phát triển trước khi thực thi BẮT BUỘC phải được phân loại theo ma trận sau:

| Cấp Độ Rủi Ro | Dấu Hiệu Nhận Diện / Từ Khóa Nhạy Cảm | Hành Vi Bắt Buộc Của Agent |
| :--- | :--- | :--- |
| 🟢 **Tier 1: Low Risk (An toàn)** | • Sửa giao diện UI/UX, CSS, Typography, Responsive, Icon, Màu sắc.<br>• Sửa chính tả, nhãn nút bấm, tooltip.<br>• Tối ưu template in ấn (Bill 80mm/58mm/KDS Ticket). | • Tự động tạo branch `feat/` hoặc `fix/`.<br>• Code, test trên môi trường giả lập (Emulator).<br>• Tiến hành quy trình chuẩn bị deploy bình thường. |
| 🟡 **Tier 2: Medium Risk (Cần thận trọng)** | • Thêm trường mới (non-breaking) vào data model.<br>• Thêm bộ lọc, sắp xếp, tìm kiếm nâng cao.<br>• Cải tiến logic tính toán hiển thị (không lưu trữ). | • Phải viết Unit Test & Integration Test kiểm chứng 100%.<br>• Chụp bằng chứng (evidence) trước/sau khi sửa.<br>• Báo cáo supervisor nghiệm thu trước khi merge. |
| 🔴 **Tier 3: Critical Risk (NGUY HIỂM CAO)** | • **Xóa dữ liệu:** `xóa`, `delete`, `drop`, `truncate`, `purge`, `reset`, `hủy toàn bộ`.<br>• **Cấu trúc DB:** Xóa collection/table, đổi kiểu dữ liệu, migration làm mất data cũ.<br>• **Bảo mật & Phân quyền:** Thay đổi `firestore.rules`, logic đăng nhập/session, cấp quyền Admin.<br>• **Thanh toán & Doanh thu:** Cấu hình tài khoản ngân hàng, VietQR, chiết khấu, đối soát số dư.<br>• **Hạ tầng Live:** Xóa bucket Storage, xóa index, can thiệp cấu hình domain/hosting. | **🛑 KÍCH HOẠT HARD STOP NGAY LẬP TỨC!**<br>• **CẤM TUYỆT ĐỐI** tự ý sửa code hoặc chạy lệnh ghi/xóa.<br>• Lập Báo cáo Đánh giá Tác động (Impact Assessment).<br>• Kích hoạt Human-in-the-Loop: Chờ User phê duyệt trực tiếp. |

---

## 🛑 2. Quy Trình Cắt Cầu Dao (Hard Stop Circuit-Breaker Protocol)

Khi phát hiện yêu cầu thuộc nhóm **🔴 Tier 3 (Critical Risk)**, Agent bắt buộc phải thực thi nghiêm ngặt 3 bước sau:

### Bước 1: Khóa Mọi Hành Động Ghi / Sửa (Immediate Freeze)
* Dừng ngay lập tức việc gọi các công cụ chỉnh sửa code (`write_to_file`, `replace_file_content`) hoặc lệnh terminal có khả năng làm thay đổi hệ thống.
* Không checkout branch tự động thực thi.

### Bước 2: Soạn Báo Cáo Đánh Giá Tác Động (Impact Assessment Report)
Xuất ngay thông báo báo động cho User trên hội thoại hiện tại theo mẫu chuẩn:

```markdown
🚨 [CẢNH BÁO RỦI RO CAO - CẦN PHÊ DUYỆT TRỰC TIẾP]
- Dự án bị ảnh hưởng: [Tên dự án & Workspace path]
- Nguồn yêu cầu: [Mã Ticket / Feedback Hub / User Prompt]
- Yêu cầu gốc: "... [trích dẫn yêu cầu] ..."
- Nhận diện rủi ro: [Xóa dữ liệu / Đổi Schema / Can thiệp Thanh toán / Lỗ hổng Bảo mật]
- Tác động tiềm ẩn:
  * [Mất mát dữ liệu gì? Dữ liệu có thể phục hồi không?]
  * [Khách hàng hoặc quán bị ảnh hưởng thế nào nếu lỗi xảy ra?]
- Phương án an toàn đề xuất:
  * Giải pháp 1 (Khuyên dùng): Áp dụng Soft-Delete / Thêm mã PIN xác thực / Giữ nguyên dữ liệu lịch sử.
  * Giải pháp 2: Tạo bản sao lưu (Backup snapshot) trước khi thực hiện.
  * Giải pháp 3: Từ chối yêu cầu và giải thích lý do an toàn cho khách.
```

### Bước 3: Đặt Câu Hỏi Xác Nhận (HITL Guardrail via `ask_question`)
Khóa luồng chờ User đưa ra quyết định qua popup lựa chọn trực tiếp:
* **Lựa chọn 1 (Khuyên dùng):** Thực hiện theo phương án an toàn (Soft-Delete / Bảo vệ dữ liệu).
* **Lựa chọn 2:** Tạm dừng và làm rõ thêm yêu cầu với khách hàng.
* **Lựa chọn 3:** Từ chối yêu cầu do vi phạm chính sách toàn vẹn dữ liệu.

---

## 🛡️ 3. Bộ Quy Tắc An Toàn Dữ Liệu Bất Khả Xâm Phạm (Zero-Destructive Rules)

### Quy tắc 1: Cấm Xóa Vật Lý (Soft Delete Only)
* **TUYỆT ĐỐI KHÔNG** dùng lệnh xóa vĩnh viễn dữ liệu nghiệp vụ (`deleteDoc`, `DROP TABLE`, `DELETE FROM ...`, `rm -rf`).
* Mọi thao tác "xóa" đều phải chuyển thành cập nhật cờ trạng thái:
  ```typescript
  // ĐÚNG (An toàn):
  await updateDoc(orderRef, { isDeleted: true, deletedAt: Date.now(), deletedBy: userId });

  // SAI (Cấm tuyệt đối):
  // await deleteDoc(orderRef);
  ```

### Quy tắc 2: Cách Ly Môi Trường Emulator Triệt Để
* Mọi script kiểm thử, seed dữ liệu mẫu, E2E test **chỉ được phép trỏ vào Local Emulator** (`localhost:8080`, `localhost:9099`).
* Phải có guardrail trong script kiểm tra URL trước khi ghi dữ liệu:
  ```python
  if "firebaseio.com" in db_url or "googleapis.com" in db_url:
      raise SecurityError("CRITICAL: Cố gắng ghi vào Production DB đã bị chặn!")
  ```

### Quy tắc 3: Giới Hạn Quyền Triển Khai (Least Privilege Deployment)
* Khi deploy tự động, chỉ cấp quyền deploy tài nguyên tĩnh (Static CDN Hosting):
  `firebase deploy --only hosting`
* Mọi thay đổi liên quan đến `firestore.rules`, `storage.rules`, hoặc `functions` bắt buộc phải có lệnh chỉ định riêng và được User duyệt thủ công.

---

## 💬 4. Mẫu Giao Tiếp Giữ Chân Khách Hàng (Customer Communication Template)

Để khách hàng không bị sốt ruột khi ticket bị giữ lại thẩm định an toàn, Supervisor tự động gửi phản hồi chính thức lên cổng Feedback Hub:

> *"Đội ngũ kỹ thuật ITG đã tiếp nhận yêu cầu của Quý khách. Do yêu cầu này liên quan trực tiếp đến cấu trúc dữ liệu và an toàn vận hành của hệ thống, chúng tôi đang tiến hành thẩm định giải pháp an toàn cùng Trưởng dự án/Quản trị viên để đảm bảo không làm gián đoạn hoạt động kinh doanh. Kỹ sư phụ trách sẽ cập nhật tiến độ sớm nhất tới Quý khách."*

---

## 🎯 Tiêu Chí Nghiệm Thu (Acceptance Criteria)
- [ ] Mọi ticket/task mới đều được gắn nhãn Risk Tier (Low / Medium / Critical) trước khi code.
- [ ] 100% các yêu cầu xóa dữ liệu, đổi schema, đụng chạm auth/payment đều kích hoạt Hard Stop.
- [ ] Không có bất kỳ lệnh xóa vật lý (Hard Delete) nào lọt vào source diff.
- [ ] User luôn là người quyết định cuối cùng trước khi bất kỳ thay đổi rủi ro nào được triển khai.
