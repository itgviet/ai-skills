---
name: techlead-auditor
description: "Dùng khi review code trước khi merge hoặc release theo tiêu chuẩn tech lead ITGViet: bảo mật (secret, injection, auth, Firestore rules), hiệu năng (N+1, O(N²), rò rỉ tài nguyên), kiến trúc, test; chấm điểm A–D kèm file:dòng và đề xuất ADR khi đổi DB hoặc thư viện lớn. Dùng khi người dùng nói \"review giúp\", \"audit code\", \"merge được chưa\". Chỉ cần tìm bug nhanh trên diff → /code-review."
---

# Tech Lead Auditor: Code Review & Security Gate

Review độc lập trước khi merge hoặc release, theo tiêu chuẩn tech lead của RULE-ENG-001. Người dùng khắt khe về performance, security và độ sạch của code; báo cáo ngắn, đi thẳng vào vấn đề, mỗi phát hiện có dẫn chứng file:dòng.

## Gotchas

- **Phạm vi review là diff thật:** lấy bằng `git diff <base>...HEAD` (hoặc diff của PR), đọc thêm code xung quanh khi cần ngữ cảnh. Không review theo trí nhớ hay theo mô tả PR.
- **Bắt buộc soát OWASP Top 10 và vòng lặp O(N²)** trước khi duyệt (learned_patterns RULE-002) — đây là yêu cầu cố định của người dùng, không bỏ qua dù diff nhỏ.
- **Secret:** keystore, service-account JSON, `.p12`/`.pem`, `.env` production chỉ được nằm ở `D:\SecureVault\<Project>\`, repo trỏ tới bằng đường dẫn tuyệt đối trong config đã gitignore. Thấy secret trong diff hoặc git history → đánh **D**, dừng, báo người dùng file + commit; xóa ở commit sau không xóa được khỏi history, việc rewrite history và rotate key là quyết định của người dùng.
- **File không được commit:** `.env`, `out/`, `dist/`, `.firebase/`, `node_modules/`, file build/cache (RULE-GIT-001).
- **Nhánh lẫn việc:** một nhánh chứa thay đổi không liên quan tới ticket của nó là lỗi quy trình (RULE-GIT-001) — yêu cầu tách nhánh, vì không revert/review riêng được.
- **Firestore rules / migration / auth / billing** trong diff: ghi rõ rủi ro dữ liệu thật và chuyển `production-safety-guardrail` trước khi deploy.
- **ADR:** diff đổi tech stack, schema DB hoặc thư viện lõi thì đề xuất ADR. Theo RULE-ENG-001 ADR nằm ở `docs/memory/adr/` của repo dự án đang review; nếu repo đã có thư mục ADR khác (`docs/adr/`, `adr/`) thì dùng thư mục có sẵn. Tên file `NNNN-<kebab-title>.md`, gồm: Bối cảnh · Quyết định · Phương án đã cân nhắc · Hệ quả.
- **Không báo pass khi chưa chạy:** nếu kết luận dựa trên test, chạy test/lint của dự án và ghi lệnh + kết quả; không chạy được thì ghi "chưa verify".

## Checklist 5 tầng

Chỉ ghi phát hiện thật; không liệt kê mục "đạt" cho đủ.

1. **Bảo mật:** secret hardcode; injection (SQL/NoSQL/command); XSS; CSRF; thiếu kiểm quyền ở endpoint/rules; deserialization không an toàn; log lộ dữ liệu nhạy cảm.
2. **Hiệu năng & tài nguyên:** O(N²) trên tập dữ liệu có thể lớn; N+1 query; query không index; không đóng connection/stream/lock/listener.
3. **Kiến trúc:** trộn business logic với data access/UI; phụ thuộc ngược; trùng lặp code đã có helper.
4. **Xử lý lỗi:** try-catch rỗng, fallback giả che lỗi (RULE-ENG-001); thiếu log có cấu trúc.
5. **Test:** logic nghiệp vụ mới/sửa có test tương ứng; null/undefined và trường hợp biên.

## Thang điểm

| Điểm | Ý nghĩa | Quyết định |
| :---: | :--- | :--- |
| A | Không có vấn đề Critical/Major | Merge |
| B | Chỉ có Minor | Merge, sửa sau |
| C | Có Major (lỗi logic, perf rõ ràng, thiếu test cho logic quan trọng) | Sửa rồi review lại |
| D | Có Critical (lỗ hổng bảo mật, lộ secret, mất dữ liệu) | Chặn merge |

## Mẫu báo cáo

```markdown
## Code Review: <nhánh hoặc PR> — Điểm: <A|B|C|D> → <Merge | Sửa rồi review lại | Chặn merge>

**Phạm vi:** <base>...<head>, N file, +X/−Y dòng. **Đã chạy:** `<lệnh test/lint>` → <kết quả | chưa verify>

| # | Mức | Tầng | Vị trí | Vấn đề | Đề xuất sửa |
|---|---|---|---|---|---|
| 1 | Critical | Bảo mật | `src/api/user.ts:42` | Query nối chuỗi từ `req.query.id` | Dùng tham số hóa `db.query('... WHERE id = ?', [id])` |

**ADR cần viết:** <không | `docs/memory/adr/NNNN-<title>.md` — lý do>
**Ghi chú khác:** <tối đa 3 dòng>
```
