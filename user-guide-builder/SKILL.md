---
name: user-guide-builder
description: "Dùng khi cần làm hoặc chỉnh trang hướng dẫn sử dụng cho người dùng cuối của một app/web (user guide, help page, tài liệu hướng dẫn khách hàng): một trang HTML gồm các thẻ việc có bước đánh số, ảnh chụp màn hình có ghim số và ô khoanh, chọn theo luồng/vai trò, in ra PDF được, rồi kiểm tra tự động và review theo vòng tới khi sạch. Dùng cả khi người dùng chỉ nói \"làm trang hướng dẫn cho app X\", \"ghi chú lên ảnh chụp màn hình\", \"hướng dẫn này chưa chuyên nghiệp\", \"đánh số bước cho rõ\", \"cập nhật bản hướng dẫn lên server review\". Không dùng cho tài liệu kỹ thuật cho dev (kiến trúc, API, schema) → tech-doc-generator; sơ đồ đơn lẻ → archify; ảnh minh họa/asset vẽ mới → visual-artist; dịch sang ngôn ngữ khác → cultural-localization-strategist."
compatibility: "Cần Python 3.10+, Node 18+ và Playwright (msedge hoặc chrome). Deploy review cần ssh + docker trên máy đích."
metadata:
  version: "1.0.0"
  author: "itgviet"
  last_updated: "2026-11-19"
---

# [SKILL-DEV-006] User Guide Builder

Làm trang hướng dẫn sử dụng một trang (HTML) cho người dùng cuối: thẻ việc có bước đánh số, ảnh chụp thật có ghim/ô
chính xác, lọc theo luồng, rồi kiểm tra tự động + review độc lập theo vòng. Đầu ra là một trang HTML kèm `assets/`,
xuất bản dạng Artifact và (khi người dùng yêu cầu) lên server review. Rút từ hướng dẫn InsightScanX (61 bản, 23 vòng review).

## Gotchas

- **Xuất bản Artifact chỉ gửi HTML.** Ảnh mới hoặc đã sửa phải truyền trong `files`, nếu không bản online thiếu ảnh hoặc giữ
  ảnh cũ trong khi ảnh chụp kiểm tra (đọc từ đĩa) vẫn đẹp. Trước khi báo xong: `python scripts/asset_manifest.py <page> --published <listing>`.
- **Tên nút lấy từ file ngôn ngữ của app** (vi.json, Localizable.strings), không đoán theo ảnh. Mỗi nút một tên trong cả trang
  ("nút xuất" ở bước 1 thì bước 3 cũng "nút xuất"). Câu khẳng định điều ảnh không cho thấy (màu tô, đơn vị mm…) → kiểm tra mã nguồn,
  không xác minh được thì viết trung tính.
- **Không bịa màn hình.** Ảnh thiếu → ghép từ giao diện thật và mã nguồn, ghi "Ảnh minh họa" trong chú thích. Ảnh vẽ phải đúng
  quy tắc nghiệp vụ (ví dụ hai marker trên hai mặt vuông góc, không phải hai mặt song song).
- **Dữ liệu demo:** chụp trên môi trường dev/local với dữ liệu mẫu. Upload lên stage/prod tốn tiền: hỏi trước. Tên người là
  "Nhân viên A/B/C", tên dự án chung chung, không địa chỉ thật.
- **Không có câu tự nói về trang** ("ảnh dưới cho thấy…", "trang này…"). Ghi chú review đặt trong hộp nội bộ, không lẫn vào bài.
- **Bước bắt đầu bằng hành động** ("Bấm…", "Chọn…"), không "Để…, bạn…" hay "Nếu…". Điều kiện đặt sau: "Nhờ Quản trị duyệt máy nếu app hiện…".
- **Ghim/ô ở khổ điện thoại (390 px):** ảnh web chỉ còn ~340 px nên ô sát nhau sẽ chạm, ghim che chữ. Luôn chụp kiểm ở 390 lẫn 1280.
  Ô trên nền tối dùng `.on-dark`; ảnh form dùng `.form` để giữ khoảng đệm; chỗ chật dùng điểm ghim cố định `n:box:@x,y`.
- **`data-crop` cắt theo ranh giới hàng/cột**, đo trên ảnh gốc (vẽ thước % lên ảnh), không cắt đôi nút hay hàng. Hộp thoại: đo mép
  hộp thoại thật (pixel sáng) rồi chừa ~0,5%. Ảnh gốc tự bị cắt ở mép phải thì chấp nhận, đừng cắt thêm.
- **Sơ đồ SVG trên điện thoại** co lại tới chữ 5–6 px: cho cuộn ngang với `min-width` thay vì co.
- **Python in tiếng Việt trên Windows:** `python -X utf8`. Patch file bằng script Python (raw string) thay vì heredoc bash
  (bash ăn mất `\`). Thay chuỗi luôn `assert s.count(a) == 1` để không thay nhầm.
- **Trang dạng fragment lên nginx** phải thêm `<!doctype html><meta charset="utf-8">` (script deploy đã làm), nếu không lỗi font.
- **Chỉ đồng bộ server review khi người dùng bảo.** Review lặp dễ không dừng: dừng khi 2 vòng liền không còn lỗi lớn hoặc khi người dùng chốt.

## Quy trình

Progress:
- [ ] 1. Khảo sát: luồng người dùng (ví dụ MEP / Khảo sát), vai trò, file ngôn ngữ của app, ảnh chụp có sẵn, môi trường chụp được phép.
      Hỏi người dùng nếu chưa rõ luồng hoặc nơi xuất bản.
- [ ] 2. Dàn ý: chương → thẻ việc. Mỗi thẻ: tiêu đề động từ, `card-meta` (web/app · thời gian · vai trò), các bước, Kết quả,
      Nếu có sự cố, "Tiếp theo". Mẫu: [assets/card-template.html](assets/card-template.html).
- [ ] 3. Chụp ảnh (dev/local, dữ liệu demo). Ảnh web 1920×1200, ảnh điện thoại 600×1302, lưu dạng webp trong thư mục ảnh của dự án (cạnh trang: `img/<lang>/` bên trong thư mục assets của dự án).
- [ ] 4. Viết thẻ + ghi chú ghim/ô (`data-hp`, `data-crop`). Dựng trang: copy [assets/reference-isx/make_guide.py](assets/reference-isx/make_guide.py)
      làm khung, hoặc nhúng [assets/guide-runtime.css](assets/guide-runtime.css) + [assets/guide-runtime.js](assets/guide-runtime.js) vào trang có sẵn.
      Đọc [references/authoring.md](references/authoring.md) trước khi đặt ghim lần đầu hoặc khi đổi mã luồng.
- [ ] 5. Kiểm tra tự động, sửa tới khi sạch (trừ mục đã chấp nhận):
      `node scripts/check_guide.cjs marks|flows|contrast|cover --page <page.html>`.
- [ ] 6. Tự chụp từng hình ở 390 và 1280 (`node scripts/check_guide.cjs shots --page <p> --width 390 --flow <f> --dpr 3 --out <dir/x> <selector…>`)
      và tự mở ảnh ra xem; test DOM xanh không chứng minh ghim không che chữ.
- [ ] 7. Review độc lập theo vòng: giao agent mới prompt trong [references/review-prompt.md](references/review-prompt.md) kèm danh sách
      "đã chấp nhận". Xác minh từng phát hiện bằng ảnh/mã nguồn trước khi sửa (reviewer có thể sai). Sửa → bước 5.
- [ ] 8. Xuất bản: Artifact (kèm `files` cho ảnh đổi) → `asset_manifest.py --published` sạch. Server review khi người dùng yêu cầu:
      `bash scripts/deploy_review.sh --page <p> --host <user@host> --dir <folder> --port <n>`.

Checklist chất lượng đầy đủ: [references/checklist.md](references/checklist.md) (đọc ở bước 5–7).

## Đầu ra

```markdown
Bản <N> đã lên <artifact URL> [và <server>:<port>].
Đã sửa: <từng mục, bằng chữ của người đọc hướng dẫn>.
Kiểm tra: marks/flows/contrast/cover <kết quả>; đã chụp kiểm <các hình> ở 390 và 1280.
Không sửa: <mục> — <lý do>.
Chưa làm / chưa kiểm: <…>.
```

## Tham khảo

- Đọc [references/authoring.md](references/authoring.md) khi viết ghim/ô/crop, thêm luồng mới, hoặc chuyển runtime sang dự án khác.
- Đọc [references/checklist.md](references/checklist.md) trước khi tự review hoặc trả lời reviewer.
- Đọc [references/review-prompt.md](references/review-prompt.md) khi giao review cho agent độc lập.
- [assets/reference-isx/](assets/reference-isx/) là bản InsightScanX hoàn chỉnh (generator + nội dung), dùng làm ví dụ, không chạy trực tiếp
  được vì phụ thuộc khung trang `src/` của dự án đó.
