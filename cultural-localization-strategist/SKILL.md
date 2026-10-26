---
name: cultural-localization-strategist
description: "Dùng khi dịch, viết lại theo văn hóa (transcreation) hoặc duyệt chuỗi UI, store listing, thông báo push cho app đa ngôn ngữ (vi, en, ja, de, es, fr, ko, pt), cần giọng văn tự nhiên như người bản xứ và tránh câu chữ gây áp lực/cảm giác tội lỗi (anti-guilt UX). Dùng cả khi người dùng chỉ nói \"dịch file strings này\", \"check bản tiếng Nhật\", \"thêm tiếng Đức\". Không dùng để luyện ngoại ngữ cá nhân (it-language-coach)."
metadata:
  version: "2.0.0"
  last_updated: "2026-10-12"
---

# SKILL: Cultural Localization — dịch và duyệt chuỗi app theo người bản xứ

Dịch, viết lại theo văn hóa (transcreation) và duyệt chuỗi UI, store listing, push cho 8 ngôn ngữ: vi, en, ja, de, es, fr, ko, pt (Brazil). Mục tiêu: câu người bản xứ thật sự nói, không răn dạy, không gây cảm giác tội lỗi.

## Gotchas

- SafeBudget (APP-001) đã chốt từ điển riêng cho 8 ngôn ngữ, gồm cả từ **cấm** (vi: "Phản Tỉnh", "Hạch toán"; ja: 「自己反省」 vì quá tiêu cực; en: "Self-Reflection"). Đọc [references/safebudget-glossary.md](references/safebudget-glossary.md) khi làm SafeBudget hoặc app tài chính cùng dòng.
- SafeBudget có test bắt buộc **đủ key ở cả 8 ngôn ngữ** và kiểm một số thuật ngữ (`apps/app_001_safebudget/__tests__/i18n.test.ts` trong repo Store). Thêm key ở một ngôn ngữ phải thêm cho cả 8; đổi thuật ngữ đã chốt thì sửa test cùng lúc và chạy lại. Ngôn ngữ không hỗ trợ sẽ fallback về tiếng Việt.

## Quy tắc theo ngôn ngữ

| Ngôn ngữ | Giọng | Dấu câu, số, tiền | Độ dài so với EN | Tránh |
|---|---|---|---|---|
| `vi` | gần gũi, đời thường | `1.234.567 ₫`, ngày `dd/MM/yyyy` | ~ +10–20% | Hán-Việt cổ, văn phong kế toán/hành chính, dịch word-by-word |
| `en` | ngắn, động từ hành động | `$1,234.56`, `MM/DD/YYYY` (US) | gốc | câu bị động dài, giọng răn dạy |
| `ja` | 丁寧語 (です/ます), lịch sự vừa phải | dấu `。、` toàn góc, không có khoảng trắng giữa từ; `¥1,234` | chữ ngắn hơn, nhưng cần kiểm xuống dòng | 自己反省-kiểu tự trách, katakana hóa thừa |
| `de` | trung tính, chính xác, dùng `Sie` trừ khi app chọn `du` thống nhất | `1.234,56 €`, `dd.MM.yyyy` | **+30–35%** — kiểm nút/tab bị tràn | từ ghép quá dài trên nút (tách hoặc rút gọn) |
| `es` | ấm, khích lệ, `tú` | `1.234,56 €`; câu hỏi/cảm thán mở bằng `¿ ¡` | +20–30% | quên `¿ ¡`, trộn biến thể Tây Ban Nha/Mỹ Latinh |
| `fr` | thanh lịch, `vous` | `1 234,56 €` (khoảng trắng hẹp), khoảng trắng trước `: ; ! ?` | +15–25% | thiếu khoảng trắng trước dấu đôi |
| `ko` | hiện đại, gọn; đuôi `-요`/`-합니다` thống nhất trong app | `₩1,234`, `yyyy.MM.dd` | ngắn hơn | trộn hai cấp lịch sự trong cùng màn hình |
| `pt` (BR) | năng động, bình dị, `você` | `R$ 1.234,56`, `dd/MM/yyyy` | +20–30% | từ của Bồ Đào Nha (Portugal) |

## Quy trình

1. Đọc chuỗi nguồn kèm ngữ cảnh: chuỗi nằm ở đâu (nút, tiêu đề, push, listing), giới hạn ký tự (Play: tên ≤ 30, mô tả ngắn ≤ 80).
2. Dịch/viết lại theo bảng trên và từ điển của dự án (nếu có).
3. Kiểm 3 câu cho từng chuỗi:
   - Người bản xứ có nói câu này ngoài đời không, hay nghe như máy dịch?
   - Có tạo cảm giác tội lỗi hay răn dạy không ("Bạn lại tiêu quá tay!")? Viết lại theo hướng trung tính/khích lệ.
   - Tiền tệ, ngày tháng, dấu phân cách số đúng tập quán chưa?
4. Kiểm hiển thị: chuỗi dài nhất (thường `de`) không tràn nút/tab; chạy test i18n của dự án nếu có.
