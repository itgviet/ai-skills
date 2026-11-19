# Viết thẻ, ghim, ô và khung cắt

## guide.config.json

| Khóa | Ý nghĩa |
|---|---|
| `lang`, `product`, `title`, `lede` | ngôn ngữ (`vi`/`en` có sẵn nhãn giao diện), tên sản phẩm, tiêu đề trang, câu giới thiệu ở bìa |
| `content`, `output` | file nội dung; file trang sinh ra (ảnh được chép theo sang cạnh nó) |
| `brand.primary`, `brand.soft` | màu chính (nút bước, ô, ghim, liên kết) và màu nền nhạt; kiểm tra tương phản bằng `check_guide.cjs contrast` |
| `flows` | `[{id, label, desc, icon}]`: luồng người đọc chọn ở bìa và thanh trên. Bỏ trống nếu trang chỉ có một luồng |
| `marks` | (tuỳ chọn) file JSON `{shotRef: [{n,x,y,w,h,px,py}]}` đo từ app thật, dùng với `data-ref` + `n:@m` |
| `labels`, `footer`, `extraCss`, `storageKey` | đổi nhãn giao diện, chân trang, CSS riêng của dự án, khóa lưu luồng đã chọn |

## Cú pháp `data-hp` (ghim theo bước)

Số ghim là số bước trong `ol.proc` của cùng thẻ (build báo lỗi nếu không khớp). Danh sách tách đôi thì dùng
`style="counter-reset:s <n>"` ở danh sách sau để số chạy tiếp.

| Dạng | Ý nghĩa |
|---|---|
| `n:x,y,w,h` | ô theo % ảnh gốc; số đặt bên tự chọn (`l`, hoặc `r` nếu ô sát mép trái) |
| `n:x,y,w,h:side` | `l r t b tl lb` — số đặt ở cạnh đó |
| `n:x,y,w,h:@px,py` | ô + số tại điểm cố định trong khoảng trống (chỗ chật, cạnh nào cũng che chữ) |
| `n:@m[:side]` | ô đo sẵn từ app (`marks`, khóa = `data-ref` của figure) |
| `n:x,y` | chỉ số, không ô |

Nhiều mục cách nhau `;`. Toạ độ luôn theo **ảnh gốc**, kể cả khi có `data-crop`. Ghim nằm trên ô của chính nó không bị
`check_guide marks` báo; ghim đè ô của bước khác thì bị báo.

## Lớp của figure

- `.shot` ảnh chụp; `.phone` ảnh điện thoại (trong `.phones` để xếp hàng, cuộn ngang trên màn hẹp); `.dialog` crop hộp thoại (rộng tối đa 420 px).
- `.form` giữ khoảng đệm của ô trên điện thoại (ô form sát nhãn sẽ chạm chữ nếu bỏ).
- `.on-dark` viền ô trắng + quầng màu chính, cho ô nằm **bên trong** vùng tối (nút trên thanh điều khiển đen). Ô **bao quanh**
  cả vùng tối (khung camera) có viền nằm trên nền sáng nên không cần; lớp này áp cho mọi ô của figure, nên figure có cả hai
  loại thì ưu tiên loại nhiều hơn và kiểm tra bằng ảnh.
- `data-crop="x0,y0,x1,y1"` hiện một phần ảnh; cần `width`/`height` thật trên `<img>` để giữ đúng tỉ lệ.
- `figure.diagram.wide` sơ đồ SVG giữ cỡ chữ đọc được trên điện thoại (cuộn ngang thay vì co lại).

## Đo để đặt ô/crop

1. Toạ độ chính xác nhất lấy từ DOM của app (bounding box ÷ kích thước viewport × 100) lúc chụp. Không có thì vẽ thước % lên
   ảnh (PIL: vạch mỗi 2%) rồi mở ra đọc.
2. Hộp thoại: tìm vùng pixel sáng (>235) giữa các hàng/cột giữa ảnh → mép hộp thoại; crop chừa ~0,4–0,6%.
3. Sau khi sửa: `check_guide.cjs shots` ở 390 và 1280 (dpr 2–3), ghép vào một tấm, tự xem. Ghim chỗ chật: thử `b`, `r`, `t`, `l`,
   rồi tới điểm cố định ở khoảng trống đã đo.

### Cỡ ghim so với khoảng trống

Ghim rộng 2,2% chiều rộng cửa sổ, trong khoảng 18–28 px (khoảng 28 px ở 1280), 15 px ở ≤640 px, 13–16 px với ảnh điện thoại. Ảnh web dày chữ
chụp nguyên màn thì gần như không còn chỗ trống đủ cho một ghim: **crop gần hơn** (`data-crop` chỉ lấy vùng cần chỉ) để chữ
to lên so với ghim, thay vì cố tìm điểm trống. Điểm ghim cố định cần một khoảng trống cỡ 3% × 4% ảnh gốc ở ảnh web toàn màn.

## Luồng

- Bìa và thanh trên có nút chọn luồng; chưa chọn thì hiện mọi thẻ. `data-flow="<id>"` trên chương, thẻ, figure, hàng bảng
  hoặc `<i class="fl">` → chỉ hiện ở luồng đó. Số chương/mục, mục lục và dòng "Tiếp theo" tính lại theo luồng đang chọn.
- Biến thể trong câu: `<i class="fl" data-flow="a">…</i><i class="fl" data-flow="b">…</i>`; khi chưa chọn luồng chỉ hiện biến thể
  của luồng đầu tiên trong config, để câu không dính hai cách nói.
- Ví dụ trong câu, sơ đồ và tên mẫu nên đổi theo luồng (người làm luồng B đọc ví dụ của luồng A sẽ thấy lạc).

## In / PDF

Khi in: thanh trên, mục lục, "Tiếp theo" ẩn; thẻ và hình không bị cắt ngang trang; `details` mở hết.
Kiểm tra bằng cách in ra PDF và mở từng trang (pymupdf), không chỉ xem trên màn hình.
