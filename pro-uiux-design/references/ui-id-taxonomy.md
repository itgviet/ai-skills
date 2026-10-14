# [RULE-UI-002] Universal UI Component ID Taxonomy & Master Screen Registry Governance

> **Unit ID**: `RULE-UI-002` | **Category**: `UIUX` | **Scope**: `Global (All Front-end Projects: Web, Mobile, Desktop, Extension)` | **Status**: ACTIVE

---

## 1. Nguyên Tắc Cốt Lõi: Đặt ID & Test-ID Minh Bạch (Zero-Anonymous UI Mandate)

Mọi thành phần giao diện hiển thị cho người dùng (Màn hình chính, Lớp phủ, Ngăn kéo dưới, Hộp thoại Popup, Thông báo Toast, Nút bấm trọng yếu) **bắt buộc phải có ID duy nhất và thuộc tính `data-testid` rõ ràng**.
Tuyệt đối không được để các màn hình, popup, dialog hoặc nút bấm hoạt động ẩn danh mà không có định danh kỹ thuật chuẩn.

### Bảng Quy Chuẩn Định Danh Toàn Cầu (Universal UI ID Taxonomy):

| Loại thành phần UI | Tiền tố chuẩn (Prefix) | Ví dụ cụ thể | Mục đích sử dụng |
| :--- | :--- | :--- | :--- |
| **Màn hình / Tab chính** | `screen-*` hoặc `tab-*` | `screen-dashboard-home`, `tab-analytics` | Định tuyến view, theo dõi Screen View Analytics |
| **Lớp phủ toàn màn hình** | `overlay-*` | `overlay-pin-lock`, `overlay-splash` | Chắn tương tác, khóa bảo mật, Splash screen |
| **Ngăn kéo đáy (Bottom Sheet)**| `sheet-*` | `sheet-quick-entry`, `sheet-filter` | Trượt lên nhập dữ liệu nhanh, filter |
| **Hộp thoại nổi (Modal Popup)** | `modal-*` | `modal-transfer-funds`, `modal-confirm` | Hộp thoại tương tác tập trung |
| **Thông báo nổi (Toast)** | `toast-*` | `toast-undo-container`, `toast-system` | Phản hồi thao tác thời gian ngắn (< 6s) |
| **Hộp thoại xác nhận / Prompt** | `dialog-*` | `dialog-factory-reset`, `dialog-confirm` | Cảnh báo rủi ro, xác nhận 2 bước |
| **Nút bấm hành động trọng yếu** | `btn-*` | `btn-fab-quick-entry`, `btn-export-csv` | Bộ chọn E2E Test (Automation Selector) |
| **Trường nhập liệu / Form** | `input-*` | `input-search`, `input-calc-screen` | Input form, màn hình máy tính mini |

---

## 2. Quy Định Bắt Buộc: Bảng Tổng Hợp Master Registry (`ui_screen_registry.md`)

Mọi ứng dụng có giao diện người dùng (UI) bắt buộc phải duy trì một tệp tài liệu tổng hợp tập trung tại:
👉 `docs/specs/<app_or_module_id>/ui_screen_registry.md`

Tệp này là **Single Source of Truth** cho toàn bộ cấu trúc giao diện của ứng dụng, bao gồm 6 mục:
1. **Danh sách Màn hình / Views**: ID, Mục đích, Trạng thái mặc định, Điều kiện kích hoạt.
2. **Danh sách Lớp phủ (Overlays)**: ID, Điều kiện xuất hiện (Trigger), Cơ chế gỡ bỏ (Dismiss).
3. **Danh sách Ngăn kéo & Hộp thoại (Sheets & Modals)**: ID, Nút kích hoạt, Dữ liệu truyền vào, Hành động đóng/xác nhận.
4. **Danh sách Thông báo & Hộp thoại cảnh báo (Toasts & Dialogs)**: ID, Thời gian tồn tại (Timeout), Hành động kèm theo (Undo, Dismiss).
5. **Ma trận Bộ chọn Tương tác Trọng yếu (E2E Key Selectors)**: Cung cấp `id` và `data-testid` để các framework kiểm thử (CDP, Playwright, Puppeteer, Appium, Cypress) bắt trúng phần tử 100%.
6. **Sơ đồ Chuyển dịch Trạng thái (Navigation State Diagram)**: Biểu đồ Mermaid mô tả quan hệ chuyển hướng giữa Home ⇄ Modal ⇄ Sheet ⇄ Toast ⇄ Tab.

---

## 3. Quy Trình Kiểm Toán & Nghiệm Thu (Audit Gate)

- Trong mọi đợt kiểm thử QA, Code Review hoặc Release Gate: Kiểm tra xem có bất kỳ màn hình, modal hoặc popup mới nào được tạo mà chưa được cấp ID chuẩn hoặc chưa được ghi nhận vào `ui_screen_registry.md` hay không.
- Nếu phát hiện UI "ẩn danh": Đánh dấu **FAIL Quality Gate** và yêu cầu bổ sung ID trước khi merge code.
