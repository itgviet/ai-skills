# Prompt giao review độc lập

Giao cho một agent mới (không dùng agent đã viết trang), chạy nền. Điền phần `<…>`; giữ danh sách "đã chấp nhận" cập nhật
sau mỗi vòng để vòng sau không báo lại.

```text
Review a <language> one-page user guide (static HTML) as a strict QC reviewer, to decide whether it is finished at a
professional level. File: <absolute path to page.html> (open via file:// with Playwright; module <path or "playwright">,
chromium.launch({channel:'msedge'}), goto waitUntil 'domcontentloaded' timeout 90000; set every img.loading='eager',
wait ~2.5 s; set `.topbar` position static and hide the fixed back-to-top button before element screenshots).
Flow picker: click `.flow-switch [data-pick="<flow>"]` for each of: <flows>. Save screenshots in <dir> and open them
yourself; screenshot each figure on its own, deviceScaleFactor 2 at 390 so small pins are legible.
Run screenshots in the foreground and keep the run under ~12 minutes.

Go card by card (every `.card` with an h3) in ALL flows at 1280 and 390. Check each figure: pin number = step number and
points at the element the step names; boxes don't cut text/icons or overlap; pins don't cover text the reader needs;
crops don't cut UI elements in half; captions match the picture; diagrams readable. Check text: clear natural
<language>, no contradictions with pictures, consistent names for the same control, steps start with the action, no
redundant or meta sentences, consecutive numbering, nothing clipped or overflowing.

Already accepted, do not report: <list from earlier rounds>.

Do not edit files. Report under 400 words: first say which cards/widths/flows you actually opened; then findings with
severity (major/minor), card id, width, flow, problem, concrete fix (coordinates or exact wording). If nothing a careful
professional editor would fix remains, say "CLEAN" explicitly.
```

## Xử lý kết quả

- Reviewer có thể sai (ví dụ nhầm viền focus của app là ô). Xác minh từng mục bằng ảnh chụp/mã nguồn trước khi sửa;
  mục không phải lỗi → giải thích ngắn và thêm vào "đã chấp nhận".
- Reviewer chỉ phủ một phần trang → giao một vòng nữa cho đúng phần còn thiếu, đừng coi là sạch.
- Điểm dừng: 2 vòng liền không lỗi lớn và lỗi nhỏ đều đã sửa/chấp nhận, hoặc người dùng chốt.
