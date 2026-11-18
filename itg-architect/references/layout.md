# Bố cục sơ đồ: không đè chữ, không rối mũi tên

Đọc trước khi dựng `model.json` và trước bước kiểm hình. Rút ra từ #8916 (18/11/2026): 6 sơ đồ AWS (account, production,
stage, dev, access portal, legacy) đạt 0 nhãn đè nhau, 0 cạnh cắt qua nhãn khác, sau khi bản trước bị người dùng chê
"đè chữ, rối mũi tên".

## Dựng mô hình

- **Viết bằng toạ độ tuyệt đối** với `scripts/model_builder.py` (`Model.group / node / edge / p`). `points` của cạnh là toạ
  độ trang còn group / node là toạ độ trong khung cha; viết tay bằng toạ độ tương đối là nguồn lệch số chính.
- Lấy điểm neo bằng `M.p(id, fx, fy)` (vd. `M.p("cf", 0.25, 0)` = đỉnh, 1/4 bên trái), không cộng nhẩm.
- **Bố cục theo luồng:** tác nhân ngoài (users, partner, CI, on-prem) ở mép trái / phải; edge → vùng có app → vùng có
  hàng đợi / Batch / dữ liệu. Mỗi tầng là một hàng khung (`box`) có tiêu đề; node trong hàng **cùng y** để cạnh nối thẳng.
- **Chừa hành lang** 20–40 px giữa các khung (vd. giữa region SG và region Tokyo, giữa VPC và khung dưới). Mọi cạnh dọc / ngang
  dài đi trong hành lang, không cắt ngang khung khác.
- Hai cạnh đi chung một hành lang thì lệch nhau ≥ 20 px (vd. x = 920 và x = 940).

## Nhãn

- Nhãn node nằm **dưới** icon (11 px, ≈ 6 px mỗi ký tự). Khoảng cách tâm hai node cạnh nhau ≥ độ rộng nhãn dài nhất + 20 px.
  Nhãn dài thì xuống dòng bằng `<br>`, 2–4 dòng.
- **Không cho cạnh ra / vào ở đáy node** (`exit`/`entry` y = 1): cạnh sẽ đi xuyên nhãn của chính node đó. Dùng trái / phải / đỉnh.
- Hai cạnh vào cùng một phía của node: tách điểm vào `[0, 0.25]` và `[0, 0.75]`.
- **Nhãn khung (group label) nằm ở góc trên trái, chạy ngang.** Cạnh dọc đi vào khung qua đỉnh sẽ cắt nhãn khung → giữ nhãn khung
  ngắn (một ý), đưa chi tiết vào node / ghi chú, hoặc cho cạnh vào từ cạnh bên.
- **Nhãn cạnh nằm ở trung điểm đường gấp khúc.** Đặt đoạn dài nhất của cạnh ở chỗ trống. Nếu trung điểm rơi vào chỗ đông
  (cạnh nằm sát nhãn cạnh khác), bỏ nhãn cạnh và ghi thông tin vào nhãn node ("origin HTTP :80").
- Nhãn khung chú thích (box nhiều dòng, chữ đậm 12 px ≈ 7 px / ký tự): dòng dài nhất phải ngắn hơn bề rộng khung − 20 px.
- Đổi nội dung nhãn (dịch sang tiếng Anh, thêm số $) là đổi kích thước: **kiểm lại toàn bộ**. Ở #8916, bản dịch EN làm
  phát sinh 3 chỗ cạnh cắt nhãn mới.

## Cạnh

- Cạnh cắt cạnh chấp nhận được khi không tránh nổi; cạnh cắt nhãn thì không.
- Sơ đồ tổng (L1) chỉ giữ các luồng **vào** tài khoản; đường đi chi tiết (CloudFront → app, liên vùng) để ở L2.
  Một cạnh dài vắt ngang cả sơ đồ L1 gần như chắc chắn cắt nhãn.
- Màu / nét: xám = request / data; nét đứt = bất đồng bộ hoặc đang tắt; đỏ (`kind: cost`) = luồng tính phí đáng chú ý.

## Kiểm (bắt buộc, sau mỗi lần render)

1. `python scripts/preview_page.py <thư mục phục vụ>/p-<tên>.html <tên>.drawio` (cỡ thật, có sẵn `layout_check.js`).
2. Phục vụ thư mục qua http (Browser pane không chụp / chạy script được trang `file://`); mở trang, viewport ≈ 1100 × 572.
3. Chạy `__check()`: `ll` phải rỗng; mỗi dòng `el` phải là nhãn **của chính cạnh đó** (so chuỗi path với nhãn cạnh).
4. Chụp từng vùng bằng `__go(x, y)` + screenshot (≈ 4–9 ô mỗi sơ đồ) và tự xem: icon không thành ô trơn, chữ đọc được.
5. Không kiểm trên viewer.diagrams.net lightbox hoặc trang có `resize: true`: sơ đồ bị thu nhỏ, nhãn khung đo sai.
6. Sửa `model.json` → render → kiểm lại tới khi đạt.
