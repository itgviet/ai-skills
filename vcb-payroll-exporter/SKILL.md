---
name: vcb-payroll-exporter
description: >-
  Skill tự động chuyển đổi bảng lương bất kỳ (Excel, CSV, Image, PDF, Text) sang File Excel Lô Chuyển Tiền Vietcombank (VCB Batch Transfer Format) khớp 100% định dạng mẫu (Loại hình chuyển tiền 1/2/3, mapping tự động mã ngân hàng CITAD/Napas, tài khoản trích nợ, định dạng text/number, và bảng chú thích).
---

# VCB Payroll Exporter Skill

Skill này tự động hóa toàn bộ quy trình tiếp nhận Bảng lương nhân viên (dạng Excel `.xlsx`, `.csv`, ảnh chụp màn hình, tệp PDF hoặc bảng Text) và xuất ra **File Lô Mẫu Vietcombank (`.xlsx`)** chuẩn 100% theo quy định ngân hàng Vietcombank.

## 📌 Điều Kiện Kích Hoạt (Triggering Conditions)
Kích hoạt skill này khi người dùng yêu cầu:
- Convert / chuyển đổi bảng lương sang file lô VCB / Vietcombank.
- Xuất file chuyển tiền ngân hàng Vietcombank theo mẫu `lomau.xlsx`.
- Mapping danh sách ngân hàng hưởng sang mã Citad / Napas / VCB.

## 📐 Quy Tắc Định Dạng Cột File Lô VCB (100% Specs)

| Cột | Tên Cột VCB | Định Dạng Cell | Quy Tắc Mapping Dữ Liệu |
|---|---|---|---|
| A | `STT` | Number (Center) | 1, 2, 3... (tăng dần từ 1) |
| B | `CUS REF\n( KH tùy chọn)` | Text (Left) | Mã NV, CUS REF hoặc tự sinh (`2000000014`...) |
| C | `Loại hình chuyển tiền \n(Select)` | Number (Center) | `1`: Trong VCB, `2`: Ngoài VCB, `3`: Tiền mặt |
| D | `Tài khoản trích nợ\n(Text)` | Text (Left) | Tài khoản công ty trích nợ (VD: `1000000015`) |
| E | `Tài khoản người hưởng\n(Text)` | Text (Left) | Số tài khoản người nhận (giữ nguyên số 0 ở đầu) |
| F | `Tên người hưởng\n(Text)` | Text (Left) | Tên chủ tài khoản nhận (Không dấu, in hoa) |
| G | `Địa chỉ người hưởng\n(Text)` | Text | Để trống (chỉ dùng cho Loại 3 - Tiền mặt) |
| H | `Số CMT\n(Text)` | Text | Để trống (chỉ dùng cho Loại 3 - Tiền mặt) |
| I | `Ngày cấp\n(Text)` | Text | Để trống (chỉ dùng cho Loại 3 - Tiền mặt) |
| J | `Nơi cấp\n(Text)` | Text | Để trống (chỉ dùng cho Loại 3 - Tiền mặt) |
| K | `Tên Ngân hàng hưởng\n(Text)` | Text | Nếu Loại 1 -> `Vietcombank`. Nếu Loại 2 -> Mã ngân hàng Citad (VD: `01311001` cho MB Bank) |
| L | `Số tiền\n(số)` | Number (`#,##0`) | Số tiền chuyển (dạng numeric) |
| M | `Loại tiền chuyển\n(Text)` | Text (Center) | Mặc định `VND` |
| N | `Phí\n(Select)` | Text (Center) | `O ` (Phí ngoài) hoặc `B ` (Phí trong) |
| O | `Nội dung lệnh\n(Text)` | Text (Left) | Nội dung chuyển khoản |

## 💡 Tra Cứu Tự Động Mã Ngân Hàng (Bank Code Mapping)

- **Trong Vietcombank**: Nếu tên ngân hàng là `Vietcombank`, `VCB`, `Ngoại Thương` -> Loại hình = `1`, Tên ngân hàng = `Vietcombank`.
- **Ngoài Vietcombank**: Nếu tên ngân hàng là ngân hàng khác -> Loại hình = `2`, Tên ngân hàng = **Mã ngân hàng (Bank Code)** từ cơ sở dữ liệu 165 ngân hàng `resources/bank_mapping.json`.
  - *MB Bank / Quân đội* -> `01311001`
  - *Techcombank / Kỹ thương* -> `01310005`
  - *TPBank / Tiên phong* -> `01358001`
  - *BIDV / Đầu tư và phát triển* -> `01202002`
  - *Sacombank / Sài Gòn thương tín* -> `79303001`
  - *Agribank / Nông nghiệp* -> `01204001`
  - *VietinBank / Công thương* -> `01201001`
  - *VPBank / Thịnh vượng* -> `01309001`
  - *ACB / Á Châu* -> `79307001`
  - *HDBank / Phát triển TPHCM* -> `79321001`
  - ... (toàn bộ 165 ngân hàng)

## 🔄 Các Bước Thực Thi (Workflow)

1. **Trích xuất dữ liệu Bảng lương**:
   - Nếu dữ liệu là file Excel/CSV: đọc các dòng dữ liệu.
   - Nếu dữ liệu là Ảnh/OCR/PDF: trích xuất các cột STT, Mã NV/Tên, Số tiền, STK, Ngân hàng, Nội dung.

2. **Khởi tạo và Chạy Script Converter**:
   Thực thi python script:
   ```bash
   python .gemini/skills/vcb-payroll-exporter/scripts/convert_payroll.py
   ```
   hoặc gọi hàm `convert_payroll_to_vcb(records, output_path)` trong Python.

3. **Tiêu Chí Nghiệm Thu (Acceptance Criteria)**:
   - [ ] File xuất ra đúng định dạng `.xlsx`.
   - [ ] Hàng 1 chứa đúng 15 tên cột chuẩn VCB với WrapText và Nền xám `#D9D9D9`.
   - [ ] Cột `Tài khoản trích nợ` và `Tài khoản người hưởng` là định dạng Text (`@`).
   - [ ] Cột `Số tiền` là định dạng Number có dấu phân cách hàng nghìn.
   - [ ] Ngân hàng Vietcombank hiển thị `1` và `Vietcombank`.
   - [ ] Ngân hàng ngoài hiển thị `2` và Mã ngân hàng Citad chính xác.
   - [ ] Có bảng chú thích (Legend block) ở cuối file theo chuẩn VCB.
