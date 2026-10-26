---
name: pro-uiux-design
description: "Dùng khi thiết kế hoặc chỉnh giao diện (web, Android/iOS, Flutter, Compose) cần trông chuyên nghiệp: design token màu/khoảng cách/typography, Material 3, icon SVG, layout responsive, UI ID theo taxonomy, và tự kiểm tra để tránh kiểu UI \"AI-cliché\". Dùng cả khi người dùng chỉ nói \"màn này xấu quá\", \"làm lại UI\", \"thêm dark mode\". Ảnh minh họa hoặc asset game → visual-artist."
metadata:
  version: "3.0.0"
  author: "itgviet"
  last_updated: "2026-09-27"
---

# [SKILL-DEV-002] Pro UI/UX Design — giao diện chuyên nghiệp, không "AI-cliché"

Chuẩn giao diện cho web, Android/iOS, Flutter, Compose. Ưu tiên: (1) design system của dự án nếu đã có, (2) quy ước nền tảng (Material 3 trên Android, Apple HIG trên iOS/macOS, Fluent trên Windows), (3) mặc định trong skill này.

## Gotchas

- **Dùng lại icon/badge sẵn có của app** cho cùng một khái niệm, kể cả trong mockup; không tự vẽ ký hiệu mới. Trước khi làm mockup, grep component hiện có. (Nguồn: InsightScanX CMS 2026-10-19 — mockup dùng ⚠ trong khi app dùng `AlertCircle` cho issue ở mọi nơi.)
- Mọi màn hình, overlay, sheet, modal, toast, dialog, nút quan trọng, input phải có `id`/`data-testid` theo tiền tố `screen-* tab-* overlay-* sheet-* modal-* toast-* dialog-* btn-* input-*` (RULE-UI-002). App có UI phức tạp duy trì `docs/specs/<module>/ui_screen_registry.md`. Đọc [references/ui-id-taxonomy.md](references/ui-id-taxonomy.md) khi đặt ID hoặc tạo registry màn hình.
- Vùng chạm trên Android: tối thiểu **48dp** (Material 3, mục kiểm của audit Google Play cho SafeBudget); iOS 44pt.
- Token màu trong [references/tokens-and-icons.md](references/tokens-and-icons.md) chỉ là mặc định khi dự án chưa có palette; không thay palette của dự án đang chạy.

## Mặc định khi dự án chưa có design system

| Mục | Tránh | Dùng |
|---|---|---|
| Icon | Emoji (`⚡ 📁 🖥️`) làm icon, icon lệch cỡ | SVG stroke 1.5–2px, viewBox 24, `stroke-linecap="round"` (Lucide/Feather/SF Symbols); container 36–40px |
| Màu | Nền `#000000`, chữ neon, gradient tràn lan | Nền slate (`#0B0F17`/`#151D2A` tối, `#F8FAFC` sáng), 1 màu nhấn; tương phản chữ ≥ 4.5:1 (WCAG AA) |
| Độ nổi | Bóng đen đậm, viền phát sáng | Viền 1px (`rgba(255,255,255,0.08)` / `#E2E8F0`), bóng rất nhẹ |
| Chữ | Cỡ tùy hứng | Thang tỉ lệ 1.25; line-height 1.2 tiêu đề, 1.5 thân bài; tiêu đề tracking `-0.02em` |
| Khoảng cách | 11px, 13px, căn giữa mọi thứ | Lưới 4/8: 4, 8, 12, 16, 24, 32, 48 |
| Bo góc | 30px khắp nơi | 6–8px nút/input, 10–14px card/modal, 999px chỉ cho pill/badge |

Snippet SVG và bảng token Dart: [references/tokens-and-icons.md](references/tokens-and-icons.md) — đọc khi cần viết icon hoặc file token.
App quản lý chi tiêu/ngân sách: đọc [references/finance-app-ux.md](references/finance-app-ux.md) (kiến trúc 4 tab, drill-down, undo).

## Trạng thái và tương tác

- Mỗi component có đủ: Default, Hover/Pressed, Loading (shimmer), Empty, Error kèm Retry.
- Không có phần tử "chết": thứ gì trông bấm được thì phải phản hồi khi bấm.
- Hành động nhạy cảm (xóa, reset) có dialog xác nhận hoặc toast kèm **Hoàn tác**.

## Tự kiểm trước khi bàn giao

- [ ] Không còn emoji làm icon; icon trùng khái niệm dùng đúng icon sẵn có của app.
- [ ] Màu, nền, chữ theo token (của dự án, hoặc mặc định ở trên); tương phản ≥ 4.5:1.
- [ ] Padding/margin/gap chia hết cho 4.
- [ ] Đủ 5 trạng thái cho component có dữ liệu.
- [ ] Vùng chạm ≥ 48dp (Android) / 44pt (iOS).
- [ ] ID/`data-testid` đúng tiền tố RULE-UI-002.
- [ ] Mọi nút/thẻ đều có hành vi thật; dữ liệu lưu thật, không mock (khi đang làm code, không phải mockup).
- [ ] Chụp màn hình cả light và dark (nếu app có dark mode) và tự xem lại trước khi báo xong.
