---
name: visual-artist
description: "Dùng khi cần tạo hoặc chỉ đạo tài nguyên hình ảnh: asset game, sprite, icon app, banner/screenshot store, ảnh minh họa, kèm prompt tạo ảnh AI theo cấu trúc chuẩn và checklist kiểm định (kích thước, nền trong suốt, nhất quán phong cách). Dùng khi người dùng nói \"vẽ\", \"làm icon\", \"ảnh cho store\", \"viết prompt tạo ảnh\". Thiết kế giao diện → pro-uiux-design."
metadata:
  version: "1.0.0"
  author: "itgviet"
  last_updated: "2026-10-12"
---

# SKILL: Visual Artist — tài nguyên hình ảnh cho app, game, store

Lập danh sách asset, viết prompt tạo ảnh, tạo ảnh (khi agent có công cụ), kiểm định rồi bàn giao cho dev.

## Tạo ảnh theo agent

| Agent | Cách tạo |
|---|---|
| Antigravity/Gemini | gọi tool `generate_image` với prompt + `AspectRatio`, tên ảnh `snake_case` ≤ 3 từ (`hero_cloud_mesh`) |
| Claude Code (không có tool tạo ảnh raster) | icon, logo đơn giản, minh họa phẳng → **vẽ SVG** trực tiếp; ảnh raster → giao prompt + thông số (kích thước, tỉ lệ, nền, định dạng) để người dùng chạy ở công cụ tạo ảnh họ dùng, rồi kiểm định file họ gửi lại |

## Gotchas

- Icon **trong app** phải dùng lại bộ icon sẵn có của app cho cùng khái niệm (vd. InsightScanX dùng `AlertCircle` cho issue); không vẽ ký hiệu mới. Asset mới chỉ dành cho minh họa, banner, game. (Nguồn: InsightScanX 2026-10-19.)
- Ảnh cho Google Play phải đúng thông số trong checklist của `project-assistant` (icon 512×512 PNG 32-bit, feature graphic 1024×500 không alpha…). Khi upload, Play Console hỏi khai báo tài sản tạo bằng AI: screenshot app thật chọn "Don't label assets"; ảnh do AI tạo thì phải khai trung thực. (Nguồn: Store, Play Console 2026-10-24.)
- Ảnh có chữ: model tạo ảnh hay sinh chữ vô nghĩa — để vùng trống và đặt chữ bằng UI/công cụ dàn trang, không để model vẽ chữ.

## Quy trình

1. **Danh sách asset**: vị trí hiển thị, kích thước thật, tỉ lệ (`16:9` banner/hero, `1:1` icon/avatar/item, `9:16` splash/story, `4:3` card), nền trong suốt hay không, định dạng (PNG trong suốt, WebP, SVG).
2. **Art direction**: lấy màu từ token của dự án (hoặc mặc định trong `pro-uiux-design`); asset mới phải cùng phong cách với asset đã có.
3. **Prompt** theo 6 phần: chủ thể + bối cảnh + phong cách + ánh sáng/màu + góc máy/bố cục + chất lượng render, thêm phần loại trừ:
   ```text
   A sleek futuristic AI core crystal floating above a dark slate pedestal, glowing cyan energy veins, isometric perspective, soft volumetric lighting, clean minimalist composition, ultra detailed --no lowres, blurry, watermark, text
   ```
   Từ khóa phong cách hay dùng: 3D clay/glass (`3d stylized clay render, soft ambient occlusion, pastel palette`), isometric (`isometric view, clean orthographic projection`), editorial phẳng (`minimalist editorial illustration, flat 2d, limited palette`), anime (`cel shaded digital illustration`), ảnh sản phẩm (`studio lighting, softbox, photorealistic, 85mm`).
4. **Tạo ảnh** theo bảng "Tạo ảnh theo agent".
5. **Kiểm định** (sai → sửa prompt và tạo lại):
   - [ ] Đúng kích thước, tỉ lệ, nền, định dạng của bước 1.
   - [ ] Cùng bảng màu/phong cách với asset trước.
   - [ ] Hero/banner chừa khoảng trống cho tiêu đề và nút.
   - [ ] Không lỗi AI: tay/ngón dị dạng, chữ rác, viền vỡ.
   - [ ] Nhìn rõ trên cả nền sáng và tối.
6. **Bàn giao**: tên file `snake_case` không dấu, đặt đúng thư mục asset của dự án, ghi kích thước/định dạng; gợi ý cách gắn (`object-fit: cover`…) nếu cần.
