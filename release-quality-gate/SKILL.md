---
name: release-quality-gate
description: "Dùng khi chuẩn bị phát hành hoặc nghiệm thu một bản build: lập bộ test case chuẩn IEEE 829/ISTQB (JSON), gộp bằng chứng từ test tự động, sinh portal HTML để QA chạy và ghi kết quả, rồi đưa quyết định Go/No-Go. Dùng khi người dùng nói \"chuẩn bị release\", \"UAT\", \"test plan\", \"ship được chưa\". Review code → techlead-auditor; chính sách store → store-policy-compliance."
compatibility: "Cần Node.js 18+ (chỉ dùng module có sẵn)."
---


# Universal Release Quality Gate & Interactive Portal Protocol

Lập bộ test case cho một đợt phát hành, sinh portal HTML một file để QA chạy và ghi kết quả, rồi ra quyết định Go/No-Go. Dùng được cho mọi stack (web, API, mobile, microservice).

## Gotchas

Các điểm dưới đây kiểm tra trực tiếp từ `scripts/generate_portal.js`:

- **Không có `--help`**: tham số lạ bị bỏ qua và script vẫn chạy với dữ liệu mẫu, ghi `Release_Quality_Gate_Portal.html` vào thư mục hiện tại. Luôn truyền `--input` và `--output`.
- **Tham số phải dạng `--name=value`** (`--input=./testcases.json`). Dạng có dấu cách (`--input ./testcases.json`) không được nhận và script âm thầm dùng `templates/sample_cases.json`.
- **File evidence không tồn tại thì bị bỏ qua không báo**; evidence JSON lỗi chỉ in `[WARN]`. Sau khi sinh portal, kiểm tra trạng thái các case đã đổi đúng chưa.
- **localStorage thắng dữ liệu mới:** trạng thái đã lưu trong trình duyệt (key theo `projectName` + `version`) ghi đè `status`/`actual`/`evidence` của bản portal vừa sinh. Sinh lại portal với evidence mới mà cùng project/version thì QA vẫn thấy kết quả cũ → bấm nút reset trên portal hoặc tăng `version`.
- **Không hoàn toàn offline:** portal tải Tailwind, FontAwesome và Google Fonts từ CDN; máy không có mạng sẽ mở được nhưng mất style.
- **Script không tự đính kèm ảnh chụp màn hình;** muốn có bằng chứng ảnh thì ghi đường dẫn ảnh (ví dụ `e2e/screenshots/home.png`) vào trường `evidence`.
- **Case ghi dữ liệu (mutation) không chạy trên Prod** — gắn `environment` là `Local`/`Staging`; cần chạy trên Prod thì qua `production-safety-guardrail` trước.

## Quy tắc Go/No-Go (đúng như portal tính)

`READY FOR PRODUCTION RELEASE` khi đồng thời: mọi case `priority: "P0"` hoặc `isBlocker: true` đều `PASSED`, không case nào `FAILED`, và tỷ lệ PASSED ≥ 90% tổng số case. Ngược lại hiển thị `RELEASE BLOCKED`. Case `BLOCKED`/`UNTESTED` không tính là fail nhưng kéo tỷ lệ pass xuống.

## Quy trình

| Bước | Ai làm | Việc | Đầu ra |
|---|---|---|---|
| 1. Lập ma trận | QA lead / agent | Đọc tính năng/API trong repo (và spec `docs/specs/<app_id>/` nếu có), soạn test case P0–P3 | `testcases.json` |
| 2. Sinh portal | Dev / CI | Chạy script (xem dưới) | `Release_Quality_Gate.html` |
| 3. Kiểm thử | QA + automation | Chạy test tự động, gộp evidence, test tay trên portal | Trạng thái + bằng chứng |
| 4. Go/No-Go | QA lead + tech lead | Đọc huy hiệu trên portal | Không còn P0 tồn đọng, pass ≥ 90% |
| 5. Lưu vết | Release manager | Xuất CSV / In PDF, đính vào release tag hoặc task OneTech | Biên bản nghiệm thu |

## Chạy script

Đường dẫn tính từ thư mục skill; chạy từ thư mục gốc dự án để file output nằm trong dự án.

```bash
node <skill-dir>/scripts/generate_portal.js --input=./testcases.json --output=./Release_Quality_Gate.html
node <skill-dir>/scripts/generate_portal.js --input=./testcases.json --evidence=./reports/test-results.json --output=./Release_Quality_Gate.html
```

`<skill-dir>`: Claude Code `~/.claude/skills/release-quality-gate` · Antigravity `~/.gemini/config/skills/release-quality-gate`.

Định dạng evidence được nhận: mảng `[...]`, hoặc `{"results": [...]}`, hoặc `{"cases": [...]}`. Mỗi phần tử khớp theo `id` của test case, dùng các trường: `status` (hoặc `passed: true/false`), `actual` (hoặc `response`), `evidence` (hoặc `detail`, hoặc `durationMs`). Output của Jest/PyTest/Playwright cần chuyển sang dạng này trước.

## Schema `testcases.json`

Ví dụ đầy đủ: `templates/sample_cases.json` (đọc khi soạn bộ case mới).

```json
{
  "projectName": "Tên dự án",
  "version": "1.2.0",
  "releaseDate": "2026-10-01",
  "targetDomain": "https://staging.example.com",
  "checklistSections": [
    { "id": "infra", "title": "Hạ tầng & DevOps",
      "items": [ { "id": "CHK-01", "name": "DB migration đã chạy", "env": "prod", "checked": false } ] }
  ],
  "testCases": [
    { "id": "AUTH-01", "module": "Authentication", "priority": "P0", "isBlocker": true,
      "title": "Đăng nhập Google OAuth", "preconditions": "Tài khoản Google hợp lệ",
      "steps": "1. Bấm Đăng nhập Google\n2. Chọn email", "expected": "Vào trang chính < 2s",
      "actual": "", "status": "UNTESTED", "environment": "Staging", "evidence": "" }
  ]
}
```

`status`: `PASSED` · `FAILED` · `BLOCKED` · `UNTESTED`. `priority`: `P0`–`P3`.

## Dùng portal

Lọc theo ô tìm kiếm, priority, môi trường, module; đổi trạng thái và ghi chú trực tiếp (tự lưu vào trình duyệt). `Backup JSON`/`Restore JSON` để chuyển phiên test sang máy khác. `Xuất CSV` là UTF-8 BOM nên Excel mở không lỗi tiếng Việt. `In / Xuất PDF` ẩn thanh công cụ để làm biên bản.
