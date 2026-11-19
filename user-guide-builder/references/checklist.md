# Checklist chất lượng trang hướng dẫn

Mỗi dòng là một lỗi đã gặp thật ở hướng dẫn InsightScanX.

## Ghim và ô
- [ ] Số ghim = số bước; ghim chỉ đúng phần tử bước đó nói tới.
- [ ] Ghim không che chữ người đọc cần (nhãn nút, tiêu đề cột quan trọng); kiểm cả 390 lẫn 1280.
- [ ] Ô không cắt ngang chữ/icon, không chạm nhãn form, không chạm ô bên cạnh ở 390.
- [ ] Ô trên nền tối nhìn thấy được (`.on-dark`).
- [ ] Không có hai ô cho cùng một bước, trừ khi bước đó nói tới hai thứ.
- [ ] Viền focus xanh của chính app không bị nhầm thành ô của hướng dẫn (nếu dễ nhầm, chụp lại khi không focus).

## Khung cắt và ảnh
- [ ] Không cắt đôi hàng, nút, icon (kể cả nửa icon thanh bên ở góc).
- [ ] Hộp thoại không lộ chữ của trang phía sau.
- [ ] Ảnh minh họa/ghép đúng quy tắc nghiệp vụ, ghi "Ảnh minh họa".
- [ ] Ảnh vẽ không khuyết góc, không vệt màu lạ (soi phóng to 3×).
- [ ] Ảnh căn trái thống nhất; không lặp cùng một ảnh ở hai thẻ liền nhau nếu tránh được.
- [ ] Dữ liệu demo không tên thật, danh mục/ví dụ hợp ngữ cảnh luồng.

## Chữ
- [ ] Bước không có ảnh (không có ảnh chụp thật cho bước đó): ghi đủ tên nút/ô bằng `.ui`, không vẽ màn hình giả, không ghim.
- [ ] Bước mở đầu bằng hành động; điều kiện để sau.
- [ ] Tên nút đúng chữ trên app, thống nhất cả trang; chỉ tô kiểu `.ui` cho đúng tên nút.
- [ ] Không câu tự nói về trang, không ghi chú review lẫn vào bài.
- [ ] Không khẳng định điều ảnh không cho thấy; không lặp từ trong một câu ("máy… máy").
- [ ] Cùng một quy tắc viết giống nhau ở mọi chỗ (ví dụ góc hướng máy vào marker).
- [ ] Người đọc có cả quản lý: viết hoa chữ đầu câu, không thuật ngữ hạ tầng (AWS, bucket…).
- [ ] Ví dụ trong câu và sơ đồ đổi theo luồng đang chọn.

## Trang
- [ ] Đánh số chương/mục liên tục ở mọi luồng; mục lục và tìm kiếm trả đúng số mục.
- [ ] Không tràn ngang ở 360–414 px; bìa vừa màn hình đầu ở 12 cỡ (`check_guide.cjs cover`).
- [ ] Tương phản chữ ≥ 4,5:1 (`check_guide.cjs contrast`), kể cả chữ trên bìa.
- [ ] Không phần tử sai luồng (`check_guide.cjs flows`); liên kết không trỏ tới phần tử bị ẩn.
- [ ] Bản in/PDF: không chồng hình, ảnh crop in đủ, FAQ mở hết.
- [ ] Ảnh online khớp ảnh local (`asset_manifest.py --published`).
