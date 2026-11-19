# Viết thẻ, ghim, ô và khung cắt

## Cú pháp `data-hp` (ghim theo bước)

Số ghim là số bước trong danh sách `ol.proc` phía trên hình. Danh sách bị tách đôi (ví dụ trước/sau hộp thoại) thì
dùng `style="counter-reset:s <n>"` ở danh sách sau để số chạy tiếp.

| Dạng | Ý nghĩa |
|---|---|
| `n:x,y,w,h` | ô theo % ảnh gốc; số đặt bên tự chọn (`l` nếu ô không sát mép trái, ngược lại `r`) |
| `n:x,y,w,h:side` | `l r t b tl tr bl lb …` — số đặt ở cạnh đó |
| `n:x,y,w,h:@px,py` | ô + số tại điểm cố định (khi cạnh nào cũng che chữ) |
| `n:@m[:side]` | ô đo sẵn trên app thật (`marks.js`, khóa = `data-ref` của figure) |
| `n:x,y` | chỉ số, không ô |

Nhiều mục cách nhau `;`. Toạ độ luôn theo **ảnh gốc**, kể cả khi có `data-crop`.

## Lớp của figure

- `.shot` ảnh chụp; `.phone` ảnh điện thoại (ghim nhỏ 16 px, 13 px ở ≤640); `.dialog` crop hộp thoại.
- `.form` giữ khoảng đệm của ô trên điện thoại (ô form sát nhãn sẽ chạm chữ nếu bỏ).
- `.on-dark` viền ô trắng + quầng navy, cho ô nằm trên thanh điều khiển đen.
- `.phones` hàng ảnh điện thoại, cuộn ngang trên màn hẹp.
- `data-crop="x0,y0,x1,y1"` hiện một phần ảnh. Từ bản ISX 61 crop chạy cả khi figure không có `data-hp`.

## Đo để đặt ô/crop

1. Vẽ thước % lên ảnh gốc rồi mở ra xem (PIL: kẻ vạch mỗi 2%, ghi số). Đặt ô theo mép thật của nút/hàng.
2. Hộp thoại: tìm vùng pixel sáng (>235) giữa các hàng/cột giữa ảnh → mép hộp thoại; crop chừa ~0,4–0,6%.
3. Sau khi sửa: `check_guide.cjs shots` ở 390 và 1280 (dpr 3), ghép các ảnh vào một tấm và tự xem.
   Ghim chỗ chật: thử lần lượt `b`, `r`, `t`, `l`, rồi tới điểm cố định ở khoảng trống đã đo.

## Luồng (flow)

- `html[data-flow]` do nút `.flow-switch [data-pick="<id>"]` đặt; phần tử có `data-flow="<id>"` khác luồng bị ẩn.
- Biến thể trong câu: `<i class="fl" data-flow="a">…</i><i class="fl" data-flow="b">…</i>` (span trực tiếp trong `li>div` sẽ thành block).
- Chưa chọn luồng: chỉ hiện biến thể của luồng đầu, nếu không câu bị dính hai cách nói.
- Bộ chọn ẩn phải lặp `[data-flow]` nhiều lần để thắng các quy tắc `.chapter .card .grid-2 > figure.shot`.

## Chuyển runtime sang dự án khác

`assets/guide-runtime.js|css` còn cứng hai mã luồng của ISX. Khi dùng cho dự án mới, sửa:
- JS: `TAG = { mep: …, ks: … }` → mã + nhãn luồng của dự án; `KEY = 'isx-flow-2'` → khóa riêng của dự án.
- CSS: các bộ chọn `html[data-flow="mep"] … [data-flow="ks"]` và `.pill.mep/.pill.ks`; bỏ các quy tắc chỉ ISX dùng
  (`.zones`, `.ifc-flow`, `.il-flange`, `.fdg`) nếu trang không có các sơ đồ đó.
- Token màu `--brand`, `--mark`, `--tip-*` theo thương hiệu dự án; trang hướng dẫn theo app chỉ có light mode thì ghim
  `data-theme="light"` và `color-scheme: light`.

## In / PDF

Khi in: chương/thẻ `display:block`, `break-inside: avoid`, ảnh crop in nguyên ảnh, `.next` ẩn, `details` mở hết.
Kiểm tra PDF bằng cách in ra và mở từng trang (fitz/pymupdf), không chỉ xem trên màn hình.
