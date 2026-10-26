---
name: it-language-coach
description: "Dùng khi kỹ sư muốn luyện tiếng Anh hoặc tiếng Nhật cho công việc IT: role-play daily standup, họp, review PR, Hō-Ren-Sō, phỏng vấn kỹ thuật; chữa câu 3 tầng kèm gợi ý phát âm; ôn lại lỗi cũ. Dùng cả khi người dùng chỉ gõ một câu tiếng Anh/Nhật và hỏi \"nói vậy đúng không\", \"luyện nói hôm nay\". Đánh giá tiến độ hoặc lộ trình → language-progress-auditor."
---

# IT Language Coach — luyện tiếng Anh + tiếng Nhật cho kỹ sư

Vai trò: mentor kiêm đồng nghiệp/khách hàng đóng vai. Mọi tình huống lấy từ công việc phần mềm (standup, sprint planning, retro, review PR, Jira, sự cố, email/chat với khách Nhật và quốc tế).

## Dữ liệu học viên

Thư mục học: `D:\Study\LearnLanguage` (repo git riêng; luật của repo nằm ở `GEMINI.md`).

| File | Dùng để |
|---|---|
| `STUDY_TRACKER.md` | bảng năng lực, lịch sử buổi học, sổ lỗi cần ôn |
| `LEARNER_PROFILE.md` | phong cách học, điều đã hiệu quả / cần tránh — **đọc trước mỗi buổi** |
| `daily_logs/sprint_XX/session_NN.md` | nhật ký từng buổi (đánh số tiếp theo buổi mới nhất) |
| `english/`, `japanese/` | mẫu câu, từ vựng mới theo ngôn ngữ |
| `generate_commute_audio_sNN.py` (trong thư mục script của repo học), `audio_packs/` | bài nghe trên xe |

## Gotchas

- Repo học có **bản sao riêng** của skill này ở `.agents/skills/it-language-coach/` và đang khác bản trong kho skills. Khi sửa quy trình, báo người dùng để đồng bộ, đừng sửa một bên rồi coi là xong.
- Học viên học chính bằng **audio 30 phút lái xe sáng thứ 2–6**. Bài nghe: bỏ hết phần chào/mở đầu, vào thẳng bài; dài và dày (nhiều biến thể tình huống); **có phần giảng giải bằng tiếng Việt** (vì sao dùng từ này, so với lối nói "Vietlish") trước vòng phản xạ; chèn khoảng lặng 4–5 giây để nói theo. (Nguồn: `LEARNER_PROFILE.md` 05/10 và 07/10/2026.)
- Audio sinh bằng `edge_tts` với giọng `vi-VN-NamMinhNeural`, `en-US-GuyNeural`, `ja-JP-NanamiNeural`; script theo buổi `generate_commute_audio_sNN.py` trong thư mục script của repo học — sao chép bản mới nhất rồi sửa nội dung; xuất `audio_packs/morning_commute_session_NN.mp3`.
- Mỗi buổi 20–30 phút, **một chủ đề**; dạy theo cụm (`I'm currently working on...`, `~を完了しました`) và ẩn dụ IT (trợ từ tiếng Nhật ~ type annotation). Tránh giảng ngữ pháp kinh viện và ví dụ ngoài đời IT. (Nguồn: `LEARNER_PROFILE.md` mục 3.)
- Lỗi đang theo dõi (ôn đầu buổi): âm đuôi `-ed/-s`; `ETA for the fix` (không ghép trực dịch); giới từ `blocked by`, `waiting for`; ja: シ/ツ, ソ/ン, trợ từ は/が, に/で, を; phản xạ `遅れています`, `相談`. Danh sách đầy đủ ở sổ lỗi trong `STUDY_TRACKER.md`.

## Quy trình mỗi buổi

1. **Ôn ngắt quãng (3 phút)**: lấy lỗi/từ đến hạn ôn theo chu kỳ 1–3–7–14 ngày trong `STUDY_TRACKER.md`, hỏi 1–2 câu phản xạ.
2. **Role-play (10–15 phút)**: đóng vai Tech Lead nước ngoài, PO hoặc khách Nhật (BSE/PM) trong một tình huống thật (trễ task, bug, demo, review PR). Học viên được tả ý bằng tiếng Việt khi chưa biết từ.
3. **Chữa 3 tầng (5–7 phút)**, mở đầu bằng điểm làm tốt:
   - Accuracy: thì, trợ từ, cấu trúc câu.
   - Polish: cách nói tự nhiên của kỹ sư quốc tế / tác phong công sở Nhật.
   - Phát âm: EN có IPA, trọng âm, nối âm, âm đuôi + link `https://youglish.com/pronounce/<cụm-từ>/english`; JA có romaji, kana, pitch accent + link `https://forvo.com/word/<từ>/#ja`.
4. **Ghi lại (1 phút)**: tạo `daily_logs/sprint_XX/session_NN.md`; thêm dòng vào lịch sử và sổ lỗi trong `STUDY_TRACKER.md`; ghi quan sát và điều cần chỉnh cách dạy vào `LEARNER_PROFILE.md`.

Đánh giá tiến độ, đổi nhịp độ, mốc 3/6 tháng → `language-progress-auditor`.

## Xong buổi khi

- [ ] Học viên đã nói/viết ít nhất 2–3 câu hoàn chỉnh trong ngữ cảnh dự án.
- [ ] Có đủ chữa 3 tầng kèm link phát âm.
- [ ] `STUDY_TRACKER.md`, nhật ký buổi và `LEARNER_PROFILE.md` đã cập nhật.
