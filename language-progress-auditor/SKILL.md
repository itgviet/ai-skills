---
name: language-progress-auditor
description: "Dùng khi cần đánh giá hoặc điều chỉnh lộ trình học ngoại ngữ (EN/JA cho kỹ sư IT): xếp cấp độ độc lập 1–4, cập nhật STUDY_TRACKER.md, lên lịch ôn lỗi theo chu kỳ 1-3-7-14 ngày, tăng tốc hoặc giảm tải theo lịch dự án. Dùng khi người dùng hỏi \"mình tiến bộ tới đâu\", \"đánh giá tháng này\", \"đang release, giảm bài\". Buổi luyện tập thực tế → it-language-coach."
---

# Language Progress Auditor — đánh giá và điều chỉnh lộ trình 6 tháng

Đo tiến độ học EN/JA của kỹ sư, lên lịch ôn lỗi, và tăng/giảm tải theo lịch dự án. Buổi luyện thực tế do `it-language-coach` làm.

Dữ liệu: `D:\Study\LearnLanguage` — `STUDY_TRACKER.md` (dashboard: năng lực, lịch sử buổi, sổ lỗi), `LEARNER_PROFILE.md`, `ROADMAP.md`, `daily_logs/sprint_XX/session_NN.md`.

## Gotchas

- Repo học có bản sao riêng của skill ở `.agents/skills/language-progress-auditor/`; nếu đổi quy trình, báo người dùng để đồng bộ hai bản.
- Ngày bắt đầu lộ trình: **2026-10-05** (trong `STUDY_TRACKER.md`); tính mốc 3 tháng/6 tháng từ ngày này.
- Lịch học thực tế chủ yếu là audio trên xe thứ 2–6 (xem `LEARNER_PROFILE.md`); buổi chat có thể cách nhau nhiều ngày (05/10 → 18/10). Đánh giá theo số buổi và lỗi lặp lại, không phạt vì khoảng trống ngày.
- `STUDY_TRACKER.md` chỉ là dashboard; chi tiết từng buổi để trong `daily_logs/sprint_XX/` (sprint 2 tuần) để file tracker không phình.

## Thang độc lập

| Level | Tên | Nhận diện |
|:---:|---|---|
| 1 | Cần mớm lời | cần gợi ý từ khóa hoặc bản dịch mới trả lời được |
| 2 | Tự nói nhưng ngắc ngứ | trả lời được, sai thì/trợ từ, còn dịch trong đầu |
| 3 | Đúng chuẩn công việc | trôi chảy, đúng ngữ pháp và ngữ cảnh IT, từ vựng còn đơn giản |
| 4 | Tự nhiên | phản xạ tự nhiên, collocation/idiom công sở IT chuẩn, tự tin |

## Mục tiêu 6 tháng

| Ngôn ngữ | Tiêu chí | Mốc 3 tháng | Mốc 6 tháng |
|---|---|---|---|
| EN | Daily standup & scrum | Level 3 (không nhìn note) | Level 4 (tranh luận PR, kiến trúc) |
| EN | Âm đuôi `-ed`, `-s` | tự sửa 70% | 90%, nối âm & IPA chuẩn |
| EN | Nghe họp kỹ thuật | 60% ý chính | 85% chi tiết |
| JA | Katakana IT trong tài liệu | đọc lướt từ quen | đọc trôi chảy spec |
| JA | Từ vựng | 100 Katakana + 30 Kanji IT | 250+ Katakana + 80 Kanji IT |
| JA | Hō-Ren-Sō | Level 2–3 (mẫu báo cáo cơ bản) | Level 3 (chủ động báo cáo, Q&A) |

## Quy trình

1. **Định vị**: đọc `STUDY_TRACKER.md` và 2–3 nhật ký buổi gần nhất; chấm level hiện tại cho từng tiêu chí, có dẫn chứng (câu học viên đã nói).
2. **Lịch ôn**: với mỗi lỗi trong sổ lỗi, ôn lại sau 1 → 3 → 7 → 14 ngày; qua mốc 14 ngày không sai → đánh dấu đã thuộc (`[x]`).
3. **Điều chỉnh nhịp**:
   - Đạt Level 3–4 ba buổi liên tiếp → tăng độ khó (tranh luận kiến trúc, đàm phán deadline).
   - Học viên báo đang crunch/release → chế độ tối giản: mỗi buổi một mẫu câu then chốt.
4. **Cập nhật** bảng năng lực và sổ lỗi trong `STUDY_TRACKER.md`; báo cáo ngắn: level hiện tại so với mốc, 3 lỗi lặp nhiều nhất, đề xuất cho 2 tuần tới.
