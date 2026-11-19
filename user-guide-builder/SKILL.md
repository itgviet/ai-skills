---
name: user-guide-builder
description: "Dùng khi cần làm hoặc chỉnh trang hướng dẫn sử dụng cho người dùng cuối của một app/web (user guide, help page, tài liệu hướng dẫn khách hàng): một trang HTML gồm các thẻ việc có bước đánh số, ảnh chụp màn hình có ghim số và ô khoanh, chọn theo luồng/vai trò, in ra PDF được, rồi kiểm tra tự động và review theo vòng tới khi sạch. Dùng cả khi người dùng chỉ nói \"làm trang hướng dẫn cho app X\", \"ghi chú lên ảnh chụp màn hình\", \"hướng dẫn này chưa chuyên nghiệp\", \"đánh số bước cho rõ\", \"cập nhật bản hướng dẫn lên server review\". Không dùng cho tài liệu kỹ thuật cho dev (kiến trúc, API, schema) → tech-doc-generator; sơ đồ đơn lẻ → archify; ảnh minh họa/asset vẽ mới → visual-artist; dịch sang ngôn ngữ khác → cultural-localization-strategist."
compatibility: "Cần Python 3.10+, Node 18+ và Playwright (msedge hoặc chrome). Deploy review cần ssh + docker trên máy đích."
metadata:
  version: "1.2.0"
  author: "itgviet"
  last_updated: "2026-11-19"
---

# [SKILL-DEV-006] User Guide Builder

Làm trang hướng dẫn sử dụng một trang (HTML) cho người dùng cuối của bất kỳ app nào: thẻ việc có bước đánh số, ảnh chụp
thật có ghim/ô chính xác, lọc theo luồng (vai trò hoặc loại công việc), in được. Đầu ra là `dist/index.html` + ảnh,
dựng bằng `scripts/build_guide.py` từ `guide.config.json` + `content.html` của dự án, rồi qua vòng kiểm tra → sửa → review
tới khi đạt. Rút từ hướng dẫn InsightScanX (62 bản, 23 vòng review) và hướng dẫn Smart Home Inspection (output kém mà kiểm tra
cũ vẫn cho qua: các luật về ảnh trong Gotchas và `check_guide pictures` sinh ra từ lần đó).

## Gotchas

- **Xuất bản Artifact chỉ gửi HTML.** Ảnh mới hoặc đã sửa phải truyền trong `files`, nếu không bản online thiếu ảnh hoặc giữ
  ảnh cũ trong khi ảnh chụp kiểm tra (đọc từ đĩa) vẫn đẹp. Trước khi báo xong: `python scripts/asset_manifest.py <page> --published <listing>`.
- **Tên nút lấy từ file ngôn ngữ của app** (vi.json, Localizable.strings…), không đoán theo ảnh. Mỗi nút một tên trong cả trang.
  Câu khẳng định điều ảnh không cho thấy (màu tô, đơn vị…) → kiểm tra mã nguồn; không xác minh được thì viết trung tính.
- **Không bịa màn hình.** Ảnh thiếu → ghép từ giao diện thật và mã nguồn, ghi "Ảnh minh họa". Ảnh vẽ phải đúng quy tắc nghiệp vụ của app.
- **Dữ liệu demo:** chụp trên môi trường dev/local với dữ liệu mẫu; upload lên stage/prod tốn tiền nên hỏi trước. Tên người
  "Nhân viên A/B/C", tên dự án/công ty chung chung, không địa chỉ thật.
- **Không có câu tự nói về trang** ("ảnh dưới cho thấy…", "trang này…"). Ghi chú review không lẫn vào bài.
- **Bước bắt đầu bằng hành động** ("Bấm…", "Chọn…"), điều kiện để sau. `build_guide.py` cảnh báo bước mở đầu bằng "Để", "Nếu".
- **Kiểm tra DOM xanh không chứng minh ghim không che chữ.** Luôn chụp từng hình ở 390 và 1280 (`check_guide.cjs shots`) và tự mở ảnh.
  Ở 390 ảnh web chỉ còn ~340 px: ô sát nhau sẽ chạm, ghim cạnh ô dễ đè chữ → dùng điểm ghim cố định `n:box:@x,y` vào khoảng trống.
- **Ảnh nguồn đã có số vẽ sẵn** (lấy từ tài liệu cũ, số cam ②③…): không phải ghim của trang. Ưu tiên xin ảnh gốc chưa vẽ
  rồi đặt `data-hp`; chỉ có ảnh đã vẽ thì gắn lớp `annotated`, đối chiếu **từng** số trong ảnh với số bước (build nhắc cho mỗi ảnh),
  và màn hình nào không có số vẽ sẵn vẫn phải có `data-hp`. Một hướng dẫn trước đây có 44 ảnh, không ghim nào, vẫn qua kiểm tra cũ.
- **Ảnh web cạnh danh sách bước chỉ còn ~1/3 cỡ thật** (khung ~480 px cho ảnh 1440–1920 px): chữ giao diện không đọc được. Crop vào
  vùng các bước dùng (≤ 50% bề ngang), hoặc đặt ảnh **dưới** danh sách bước (ngoài `.grid-2`) để nó chiếm hết bề ngang thẻ.
  `check_guide pictures` báo ảnh hiện dưới 45% cỡ thật.
- **Ảnh minh họa thật** (hiện trường, dụng cụ, bản vẽ giấy) dùng `figure.photo` trong `.photos`, chú thích "Ảnh minh họa: …"; không
  thêm `style=` hay `extraCss` để chỉnh cỡ (build báo lỗi `style` nội tuyến).
- **Không tự gán `width`/`height` cho ảnh**: build đọc kích thước thật từ file và sửa; chú thích không lặp lại `alt`.
- **`data-crop` cắt theo ranh giới hàng/cột** đo trên ảnh gốc, không cắt đôi nút/hàng; hộp thoại: đo mép thật rồi chừa ~0,5%.
- **Python in tiếng Việt trên Windows:** `python -X utf8`. Sửa file bằng Write/Edit hoặc script Python, không bằng heredoc bash
  (bash ăn mất `\` trong regex/`\n`). Thay chuỗi trong script luôn `assert s.count(a) == 1`.
- **Reviewer cũng sai và hay chỉ phủ một phần trang.** Xác minh từng phát hiện bằng ảnh/mã nguồn; báo cáo không ghi rõ đã mở
  những thẻ nào ở khổ/luồng nào thì giao tiếp phần còn thiếu.
- **Chỉ đồng bộ server review khi người dùng bảo.** Không đặt mục tiêu "review đến khi hoàn hảo" không có điểm dừng: dừng khi
  `check_guide.cjs all` PASS và 2 vòng review liền không còn lỗi lớn, hoặc khi người dùng chốt.

## Quy trình

Progress:
- [ ] 1. Khảo sát: luồng người dùng (vai trò / loại việc), file ngôn ngữ của app, ảnh có sẵn, môi trường chụp được phép, nơi xuất bản.
      Hỏi người dùng nếu chưa rõ luồng hoặc nơi xuất bản.
- [ ] 2. Khởi tạo: `python scripts/build_guide.py --init <thư mục hướng dẫn của dự án>` → `guide.config.json`, `content.html`, `img/`.
      Điền config (tên sản phẩm, màu thương hiệu, luồng). Dự án đã có trang riêng (như ISX) thì giữ trang đó, chỉ dùng bước 5–8.
- [ ] 3. Chụp ảnh (dev/local, dữ liệu demo): web 1920×1200, điện thoại 600×1302, webp/png trong `img/`. Ghi toạ độ % của
      các nút cần chỉ (vẽ thước % lên ảnh, hoặc lấy bounding box từ DOM của app).
- [ ] 4. Viết thẻ trong `content.html` theo [assets/card-template.html](assets/card-template.html): tiêu đề động từ, `card-meta`,
      bước, ảnh có `data-hp`/`data-crop`, Kết quả, Nếu có sự cố. Cú pháp: [references/authoring.md](references/authoring.md).
- [ ] 5. Build + kiểm cấu trúc: `python scripts/build_guide.py --config <cfg>`. Lỗi (id trùng, luồng lạ, ảnh thiếu, ghim không khớp
      bước, ảnh giao diện cạnh 2+ bước mà không có ghim, `style` nội tuyến) dừng build → sửa → build lại. Đọc từng cảnh báo
      (ảnh `annotated`, ảnh web rộng chưa crop, chú thích lặp `alt`) và xử lý hoặc ghi lý do.
- [ ] 6. Cổng tự động: `node scripts/check_guide.cjs all --page dist/index.html --accept guide.accept.json` → sửa tới khi `PASS`.
      Mục đúng là lựa chọn có chủ đích (hai nút liền nhau trong app…) → thêm vào `guide.accept.json` kèm `why`, không sửa bừa.
- [ ] 7. Tự xem: `node scripts/check_guide.cjs shots --page <p> --width 390 --flow <id> --out shots/390-<id> --sheet shots/390-<id>.png`
      (không truyền selector = mọi hình của luồng đó), rồi 1280; mở các tấm `--sheet` ra xem, phóng to chỗ nghi ngờ bằng `--dpr 3`
      + selector `.card:has(#<id>) figure`. Ghim che chữ, ô cắt chữ, crop cắt đôi → sửa → bước 5.
- [ ] 8. Review độc lập: giao agent mới prompt trong [references/review-prompt.md](references/review-prompt.md) kèm nội dung
      `guide.accept.json`. Xác minh từng phát hiện, sửa → bước 5. Dừng theo điểm dừng ở Gotchas.
- [ ] 9. Xuất bản: Artifact (kèm `files` cho ảnh) → `asset_manifest.py --published` sạch. Server review khi người dùng yêu cầu:
      `bash scripts/deploy_review.sh --page dist/index.html --host <user@host> --dir <folder> --port <n>`.

Checklist chất lượng: [references/checklist.md](references/checklist.md) (đọc ở bước 6–8).

## Đầu ra

```markdown
Bản <N> đã lên <artifact URL> [và <server>:<port>].
Đã sửa: <từng mục, bằng chữ của người đọc hướng dẫn>.
Kiểm tra: build <errors/warnings>; check_guide all <PASS/FAIL, n mục đã chấp nhận>; đã tự xem <các hình> ở 390 và 1280.
Không sửa: <mục> — <lý do>.
Chưa làm / chưa kiểm: <…>.
```

## Tham khảo

- [references/authoring.md](references/authoring.md): cú pháp ghim/ô/crop, luồng, đo toạ độ, config. Đọc trước khi viết thẻ đầu tiên.
- [references/checklist.md](references/checklist.md): checklist chất lượng, đọc trước khi tự review hoặc trả lời reviewer.
- [references/review-prompt.md](references/review-prompt.md): prompt giao review độc lập.
- [assets/template/](assets/template/): khung trang (`guide.css`, `guide.js`) và mẫu config/content mà `--init` chép ra.
- [assets/reference-isx/](assets/reference-isx/): bản InsightScanX hoàn chỉnh (generator riêng của dự án đó, nội dung 49 thẻ) để
  tham khảo cách viết; không chạy được ngoài dự án ISX.
