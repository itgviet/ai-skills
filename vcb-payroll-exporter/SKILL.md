---
name: vcb-payroll-exporter
description: "Dùng khi cần chuyển bảng lương hoặc danh sách chi trả (Excel, CSV, PDF, ảnh, text) thành file lô chuyển tiền Vietcombank (.xlsx theo mẫu lomau.xlsx): tên người hưởng in hoa không dấu, giữ số 0 đầu số tài khoản, map ngân hàng hưởng sang mã Citad, đối chiếu tổng tiền. Dùng khi người dùng nói \"xuất file lô VCB\", \"chuyển lương qua Vietcombank\", \"file chi lương\"."
compatibility: "Cần Python 3.9+ và openpyxl (pip install openpyxl)."
---

# VCB Payroll Exporter Skill

Chuyển bảng lương (Excel, CSV, JSON — hoặc ảnh/PDF/text sau khi trích xuất) thành **file lô chuyển tiền Vietcombank (`.xlsx`)** đúng mẫu `lomau.xlsx`. Đây là lệnh chi tiền thật: sai một số tài khoản hay một số tiền là chuyển nhầm lương, nên mọi bước đều có kiểm tra và người dùng duyệt trước khi giao file.

Đường dẫn trong skill tính từ thư mục skill. Tham số đầy đủ: `python scripts/convert_payroll.py --help`.

## ⚠️ Gotchas

- **Số tiền có dấu phân cách nghìn** (`7.500.000`, `7,500,000`, `7 500 000 đ`) được `parse_amount()` hiểu là VND nguyên, nên `15.000` là mười lăm nghìn, không phải 15 đồng. Chuỗi mơ hồ (vd. `1.5.00`) đọc ra 0 và `--dry-run` cảnh báo; số có phần lẻ cũng bị cảnh báo vì VND không có xu. Vẫn đối chiếu tổng tiền với file nguồn.
- **Số 0 đầu số tài khoản mất ngay trong file nguồn** nếu cột tài khoản trong Excel là kiểu Number — script không khôi phục được. Hỏi người dùng hoặc đối chiếu lại khi số tài khoản ngắn bất thường; CSV được đọc nguyên dạng text nên giữ số 0.
- **Ngân hàng không có trong `resources/bank_mapping.json` vẫn được ghi Loại 2 với tên thô** thay vì mã Citad 8 số — VCB sẽ từ chối dòng đó. Bảng mapping hiện có 97 ngân hàng (không phải 165 như bản cũ ghi). Gặp cảnh báo "không tìm được mã Citad": hỏi người dùng mã đúng hoặc bổ sung alias vào `bank_mapping.json`, không đoán.
- **Không có tài khoản trích nợ mặc định.** Hàm `convert_payroll_to_vcb` còn giá trị mặc định cũ trong code; CLI bắt buộc `--debit-account` để không bao giờ trích nhầm tài khoản. Hỏi người dùng nếu chưa biết.
- **Chỉ đọc `.json`, `.csv`, `.xlsx`.** `.xls` (Excel 97) không đọc được — nhờ người dùng lưu lại thành `.xlsx` hoặc `.csv`. Ảnh/PDF: tự trích xuất thành CSV trước rồi cho người dùng xem bảng trích xuất.
- **Tên cột đầu vào phải đúng** `name`, `account_no`, `bank`, `amount` (tùy chọn `description`, `cus_ref`), viết thường. Bảng lương gốc thường có cột kiểu "Họ tên", "STK" — đổi tên cột khi tạo file CSV trung gian.
- **Nội dung lệnh tự động thêm ` - <TÊN KHÔNG DẤU>`** và bỏ dấu toàn bộ; đừng tự thêm tên vào `description` nữa kẻo bị lặp.
- **Console Windows (cp1252) làm script lỗi khi in tiếng Việt**: CLI đã tự chuyển stdout sang UTF-8; nếu gọi hàm trực tiếp từ Python khác thì đặt `PYTHONIOENCODING=utf-8`.
- **Thiếu `openpyxl`** → script thoát mã 3 kèm hướng dẫn (`pip install openpyxl` hoặc `uv run scripts/convert_payroll.py`). Không tự cài package khi chưa hỏi người dùng. `--dry-run` với CSV/JSON chạy được không cần openpyxl.

## 🔄 Quy trình

Progress:
- [ ] 1. Trích xuất bảng lương thành CSV trung gian với 4 cột bắt buộc (giữ số tài khoản dạng text, số tiền là số nguyên).
- [ ] 2. Chạy thử: `python scripts/convert_payroll.py --input <file.csv> --dry-run` → JSON gồm `rows`, `total_amount`, `warnings`, `records`.
- [ ] 3. Nếu có `warnings`: sửa dữ liệu nguồn và chạy lại bước 2. Chỉ dùng `--allow-warnings` khi người dùng đã xem từng cảnh báo và đồng ý.
- [ ] 4. **Đối chiếu với file nguồn trước khi giao**: số dòng và tổng tiền trong JSON phải khớp tổng của bảng lương gốc; liệt kê cho người dùng các dòng chuyển ngoài VCB (Loại 2) kèm mã Citad.
- [ ] 5. Người dùng xác nhận tài khoản trích nợ và tổng tiền → xuất file:
  `python scripts/convert_payroll.py --input <file.csv> --output File_Lo_VCB_<thang>.xlsx --debit-account <STK công ty>`
- [ ] 6. Báo lại đường dẫn file, số dòng, tổng tiền. Không gửi file hay đăng lên ngân hàng thay người dùng.

Mã thoát: `0` OK · `1` lỗi đọc/ghi · `2` còn cảnh báo (file chưa được ghi) · `3` thiếu openpyxl.

Gọi từ Python (khi đã có `records`): `from convert_payroll import summarize, convert_payroll_to_vcb` — luôn chạy `summarize(records)` và xử lý `warnings` trước khi gọi `convert_payroll_to_vcb(records, output_path, debit_account)`.

## 📐 Định dạng cột file lô VCB

| Cột | Tên cột VCB | Định dạng | Giá trị |
|---|---|---|---|
| A | `STT` | Number (giữa) | 1, 2, 3… |
| B | `CUS REF\n( KH tùy chọn)` | Text | `cus_ref` hoặc tự sinh từ `2000000014` |
| C | `Loại hình chuyển tiền \n(Select)` | Number (giữa) | `1` trong VCB, `2` ngoài VCB, `3` tiền mặt (script không sinh Loại 3) |
| D | `Tài khoản trích nợ\n(Text)` | Text `@` | `--debit-account` |
| E | `Tài khoản người hưởng\n(Text)` | Text `@` | giữ nguyên số 0 đầu |
| F | `Tên người hưởng\n(Text)` | Text | in hoa, không dấu |
| G–J | Địa chỉ, Số CMT, Ngày cấp, Nơi cấp | Text | để trống (chỉ dùng cho Loại 3) |
| K | `Tên Ngân hàng hưởng\n(Text)` | Text `@` | Loại 1 → `Vietcombank`; Loại 2 → mã Citad 8 số |
| L | `Số tiền\n(số)` | Number `#,##0` | số tiền |
| M | `Loại tiền chuyển\n(Text)` | Text | `VND` |
| N | `Phí\n(Select)` | Text | `B ` (phí trong, mặc định — có khoảng trắng cuối) hoặc `O ` |
| O | `Nội dung lệnh\n(Text)` | Text | không dấu, kết thúc bằng ` - <TÊN>` |

Hàng 1 là header nền xám `#D9D9D9`, wrap text. Script **không** sinh khối chú thích (legend) ở cuối file — nếu ngân hàng yêu cầu, nói rõ với người dùng thay vì khẳng định file đã có.

Mã Citad hay gặp (đầy đủ trong `resources/bank_mapping.json`): MB `01311001`, Techcombank `01310005`, TPBank `01358001`, BIDV `01202002`, Sacombank `79303001`, Agribank `01204001`, VietinBank `01201001`, VPBank `01309001`, ACB `79307001`, HDBank `79321001`. VCB/Vietcombank/Ngoại Thương → Loại 1.

## ✅ Tiêu chí nghiệm thu

- [ ] `--dry-run` không còn cảnh báo (hoặc người dùng đã duyệt từng cảnh báo).
- [ ] Số dòng và tổng tiền khớp bảng lương gốc, đã báo cho người dùng.
- [ ] Cột D, E, K là Text; cột L là Number có phân cách nghìn.
- [ ] Mọi dòng Loại 2 có mã Citad 8 số.
