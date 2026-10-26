---
name: project-assistant
description: "Dùng cho việc vận hành dự án không phải viết code: checklist trước khi publish Google Play, bàn giao asset từ artist sang dev, đối chiếu PRD với phần đã làm, soát chính tả/i18n văn bản, viết báo cáo nhanh cho chủ studio. Dùng khi người dùng nói \"check lại trước khi publish\", \"tóm tắt tình hình dự án\", \"soát lại text\". Duyệt chính sách store → store-policy-compliance; test plan và Go/No-Go → release-quality-gate."
metadata:
  version: "1.0.0"
  author: "itgviet"
  last_updated: "2026-10-12"
---

# SKILL: Project Assistant — vận hành dự án, checklist, báo cáo

Việc "keo dán" không phải viết code: checklist trước khi publish, bàn giao asset, đối chiếu PRD với phần đã làm, soát text/i18n, báo cáo ngắn cho chủ studio.

## Gotchas

- **Play Console: "Save as draft" không đưa thay đổi listing vào review.** Sửa listing (mọi ngôn ngữ) → **Next** → khai báo tài sản AI ("Don't label assets" cho screenshot app thật) → **Save** (trạng thái "Changes ready to send for review") → Publishing overview → Submit. Trước khi submit, xem Publishing overview có dòng "Change app name / description / Phone screenshots", không chỉ "Add language". (Nguồn: SafeBudget 1.0.7 lên store với listing cũ, 19/10/2026.)
- **Thay screenshot theo ngôn ngữ**: panel asset đóng khi chuyển ngôn ngữ; mỗi ngôn ngữ bấm "Add assets" rồi upload đúng 5 file của ngôn ngữ đó (upload nhiều ngôn ngữ một lượt sẽ gắn hết vào ngôn ngữ đang mở), sau đó sắp lại thứ tự. (Nguồn: Store 24/10/2026.)
- Trang privacy policy của app Store: chuẩn bị trong `ItgVietSite/itgviet/public/<slug>/`, commit ở đó rồi mới deploy Firebase Hosting; deploy là hành động công khai, cần người dùng đồng ý. (Nguồn: APP-002, 2026-10-24.)
- Task/bug tạo trên OneTech: tiêu đề tiếng Anh `[Module] Short title`, mô tả tiếng Việt 3 phần (Hiện trạng/Lỗi – Tác động/Nguyên nhân – Đề xuất). (Nguồn: `$ITGVIET_HOME/memory/user_preferences.md`.)

## Checklist 1 — Google Play pre-flight

- [ ] Tên app ≤ 30 ký tự, mô tả ngắn ≤ 80 ký tự, không nhồi từ khóa.
- [ ] Mô tả đầy đủ nêu rõ tính năng, có thông tin liên hệ.
- [ ] Icon 512×512 PNG 32-bit, không tự bo góc, < 1024 KB.
- [ ] Feature graphic 1024×500, JPG hoặc PNG 24-bit (không alpha).
- [ ] Screenshot 4–8 ảnh mỗi ngôn ngữ, đúng ngôn ngữ, không mờ.
- [ ] Privacy Policy URL trả HTTP 200, nhắc đúng các SDK đang dùng (AdMob, Crashlytics…).
- [ ] Data Safety khớp SDK trong code (chi tiết → `store-policy-compliance`).
- [ ] `versionCode` tăng so với bản trước, `versionName` đúng.
- [ ] Publishing overview liệt kê đủ các thay đổi listing (xem Gotchas).

## Checklist 2 — Bàn giao asset (artist → dev)

- [ ] Raster: PNG nén hoặc WebP; icon vector: SVG có viewBox đúng.
- [ ] Tên file `snake_case`, không dấu, không khoảng trắng (`ic_action_search.png`, `bg_hero_home.webp`).
- [ ] Đủ mật độ (mdpi → xxxhdpi) hoặc dùng vector.
- [ ] Đặt đúng thư mục asset của dự án (`res/drawable/`, `src/assets/images/`…).

## Checklist 3 — PRD vs phần đã làm

- [ ] Mỗi màn hình trong PRD có view/screen tương ứng.
- [ ] Thông báo lỗi thân thiện, có nút thử lại.
- [ ] Nút Back Android ở màn hình con không thoát app đột ngột.
- [ ] Không còn placeholder (`TODO`, `lorem`, `Test string`) hay lỗi encoding trong chuỗi i18n.

## Báo cáo nhanh cho chủ studio

```markdown
**Tóm tắt tiến độ: [Module / App]**
- Đã xong: [2–3 ý chính]
- Đang làm: [việc + người phụ trách]
- Checklist: [Pass hết / còn X mục: ...]
- Cần quyết định: [1 câu hỏi cụ thể, nếu có]
```

Phối hợp: story/AC → `pm-decomposer`; asset → `visual-artist`; code → `dev-executor`; biên bản test, Go/No-Go → `release-quality-gate`; chính sách store → `store-policy-compliance`.
