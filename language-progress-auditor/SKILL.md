---
name: language-progress-auditor
description: >-
  Hệ thống kiểm toán và đánh giá tiến độ học tập song ngữ IT (English & Japanese Progress Auditor): Định vị năng lực đầu vào (Baseline Calibration), sinh đề kiểm tra ngắt quãng (Spaced Quizzes), tính toán độ hiểu và tự động điều chỉnh tốc độ lộ trình (Dynamic Pacing) trong STUDY_TRACKER.md và ROADMAP.md.
---

# Language Progress Auditor: Dynamic Pacing & Milestone Evaluation

Skill này chịu trách nhiệm giám sát, đánh giá định lượng và thích ứng hóa lộ trình học tập 6 tháng cho kỹ sư phần mềm, đảm bảo học viên không bị bỏ lại phía sau hoặc học sai trọng tâm.

---

## 📌 CHỨC NĂNG CỐT LÕI (CORE CAPABILITIES)

1. **Baseline Calibration (Định vị đầu vào):**
   - Đo lường chính xác các chỉ số ban đầu theo thang đo **Cấp độ Độc lập (Autonomy Levels 1–4)**.
   - Ghi nhận chỉ số gốc vào `STUDY_TRACKER.md`.

2. **Spaced Repetition Engine (Thuật toán lặp lại ngắt quãng):**
   - Tự động quét `STUDY_TRACKER.md` tìm các điểm yếu (Mistakes log) và lên lịch kiểm tra lại theo chu kỳ Fibonacci:
     - Lần 1: Sau 24 giờ.
     - Lần 2: Sau 3 ngày.
     - Lần 3: Sau 7 ngày.
     - Lần 4: Sau 14 ngày (Nếu vượt qua $\rightarrow$ Đánh dấu "Mastered").

3. **Dynamic Pacing & Difficulty Calibration (Tự động điều chỉnh tiến độ):**
   - **Tăng tốc (Fast-track):** Khi đạt Level 3–4 liên tiếp trong 3 buổi $\rightarrow$ Đẩy nhanh vào các tình huống phức tạp (tranh biện kiến trúc hệ thống, đàm phán deadline).
   - **Hạ tải (De-escalation):** Khi học viên báo cáo đợt cao điểm dự án (Crunch time, Release phase) $\rightarrow$ Tự động chuyển sang chế độ "Survival 1-Min Mode" (chỉ 1 mẫu câu then chốt).

4. **Sprint-based Logging (Chống phình dữ liệu):**
   - Lưu trữ chi tiết từng buổi học theo từng Sprint 2 tuần: `daily_logs/sprint_01/`, `daily_logs/sprint_02/`.
   - File `STUDY_TRACKER.md` chỉ giữ vai trò Dashboard tổng quan, chứa metrics và danh sách lỗi đang theo dõi.

---

## 🎯 THANG ĐO CẤP ĐỘ ĐỘC LẬP (AUTONOMY LEVELS)

Thay vì đo số giây gõ bàn phím (không thực tế qua chat), hệ thống đánh giá theo mức độ độc lập phản xạ:

| Cấp độ | Tên cấp độ | Đặc điểm nhận diện |
| :---: | :--- | :--- |
| **Level 1** | **Dependent (Cần mớm lời)** | Cần gợi ý từ khóa hoặc cần dịch từ tiếng Việt sang thì mới hiểu và trả lời được. |
| **Level 2** | **Hesitant (Tự phản xạ có ngắc ngứ)** | Tự trả lời được nhưng câu cú còn lủng củng, dùng sai thì/trợ từ, còn dịch máy trong đầu. |
| **Level 3** | **Accurate & Functional (Đúng chuẩn công việc)** | Trả lời trôi chảy, đúng ngữ pháp và bối cảnh IT, diễn đạt tròn ý dù từ vựng còn đơn giản. |
| **Level 4** | **Native & Fluent (Tự nhiên như bản xứ)** | Phản xạ tự nhiên, dùng idiom/collocation công sở IT chuẩn mực, ngữ điệu tự tin. |

---

## 📊 BỘ CHỈ SỐ MỤC TIÊU 6 THÁNG

| Ngôn ngữ | Tiêu chí đánh giá | Mốc 3 tháng | Mốc 6 tháng |
| :--- | :--- | :--- | :--- |
| **English** | Daily Standup & Scrum Meeting | Đạt **Level 3** (Nói lưu loát không nhìn note) | Đạt **Level 4** (Tranh biện PR & kiến trúc) |
| **English** | Nhận diện & Sửa lỗi phát âm âm đuôi | Tự giác sửa được $70\%$ âm `-ed`, `-s` | Làm chủ $90\%$ nối âm & IPA chuẩn |
| **English** | Nghe hiểu cuộc họp kỹ thuật | Nắm được $60\%$ ý chính | Nắm được $85\%$ chi tiết kỹ thuật |
| **Japanese**| Nhận diện Katakana IT trong tài liệu | Đọc lướt tức thì các từ quen thuộc | Làm chủ toàn bộ từ Katakana trong Spec |
| **Japanese**| Vốn từ Katakana & Kanji IT cốt lõi | 100 từ Katakana + 30 Kanji IT | 250+ từ Katakana + 80 Kanji IT |
| **Japanese**| Giao tiếp công việc Hō-Ren-Sō | Đạt **Level 2–3** (Mẫu câu báo cáo cơ bản) | Đạt **Level 3** (Chủ động báo cáo & trao đổi Q&A) |
