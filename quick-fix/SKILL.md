---
name: quick-fix
description: "Dùng khi người dùng báo lỗi, crash, sai hiển thị, sai dữ liệu hoặc nhờ sửa/refactor nhỏ trong phạm vi khoảng 1–5 file (\"fix giúp\", \"sao lại lỗi\", \"bug\", \"chỉnh lại chỗ này\"), kể cả khi không nói chữ bug: khóa scope, tìm nguyên nhân gốc, sửa, tự review, chạy build/test theo stack và báo cáo bàn giao. Tính năng mới hoặc thay đổi kiến trúc → feature-spec; task đã có spec → dev-executor."
metadata:
  version: "3.0.0"
  author: "itgviet"
  last_updated: "2026-10-07"
---

# SKILL: Universal Quick Fix & Rapid Improvement Protocol (v3.0.0)

Quy trình cho sửa lỗi, chỉnh hành vi, tinh chỉnh UI và refactor nhỏ trên mọi tech stack, không cần spec đầy đủ.

## Gotchas

- **Branch isolation (RULE-GIT-001):** trước khi sửa, chạy `git branch --show-current`. Nếu nhánh đang thuộc bug/feature khác: stash hoặc commit việc dở → `git checkout develop && git pull origin develop` → `git checkout -b fix/<ticket-id>-<topic>`. Vì commit đè lên nhánh của việc khác làm lẫn hai thay đổi, không review/revert riêng được.
- **Windows/PowerShell:** máy chạy Windows; lệnh PowerShell dùng cmdlet chuẩn (`Get-ChildItem`, `Select-String`), không dùng alias Unix — đã từng gây lỗi cú pháp/timeout (reflexion_log REFLECT-2026-001).
- **Log build dài:** lọc trước khi đọc (`... | Select-String "BUILD|ERROR|FAIL"` hoặc skill `context-compressor`), vì log gradle/npm hàng trăm dòng làm loãng context (RULE-PERF-001).
- **Không giấu lỗi:** không dùng try-catch rỗng hay trả dummy fallback để test xanh (RULE-ENG-001) — lỗi sẽ quay lại ở production và khó lần hơn.
- **Secret:** keystore, service-account JSON, `.env` production nằm ở `D:\SecureVault\<Project>\`, project trỏ tới bằng đường dẫn tuyệt đối trong config đã gitignore. Khi build lỗi vì thiếu secret, sửa đường dẫn config, không copy secret vào repo.
- **Test DOM pass ≠ UI đúng:** `expect(btn).toBeInTheDocument()` chỉ chứng minh phần tử tồn tại, không chứng minh layout không vỡ. Đổi UI thì phải chụp ảnh và tự mở ảnh ra xem (Phase 4).
- **UI POS/Mobile (cafenhatsinh):** breakpoint cần kiểm là Mobile 360–390px, Tablet 768px, POS 1336px. Thêm nút vào container có sẵn thì cộng chiều rộng ở breakpoint nhỏ nhất; không nhét ≥ 3 nút chữ dài trên một hàng < 320px — thao tác phụ (In, Sửa, Hủy) dùng icon button 24×24 trong vùng chạm 28–36px kèm `title`/`aria-label`; mỗi vùng chỉ 1 primary action; nút Hủy/Xóa màu đỏ không đặt sát nút chính vì dễ chạm nhầm trên màn cảm ứng.

## Ma trận Quyết định Scope

Kiểm tra trước khi làm; nếu rơi vào cột phải thì dừng và chuyển sang `feature-spec`.

| Tiêu chí | ✅ `quick-fix` | 🛑 `feature-spec` |
| :--- | :--- | :--- |
| Số file thay đổi | 1–5 file | > 5 file hoặc nhiều layer |
| Bản chất | Fix bug, sửa logic, UI tweak, UX nhỏ | Tính năng mới, màn hình mới |
| DB / Schema | Không migration | Có migration / đổi schema |
| API contract | Giữ nguyên hoặc mở rộng tương thích ngược | Breaking change |
| Rủi ro | Cục bộ hoặc 2 bên (cross-repo fix) | Tái cấu trúc toàn hệ thống |

Thao tác xóa/sửa dữ liệu thật, deploy production, auth, thanh toán → chạy `production-safety-guardrail` trước.

## Quy trình 6 bước

### Phase 1 — Triage & khóa scope
1. Phân loại: 🐛 bug fix · 🔧 code repair (type/lint/import/deprecation) · 🎨 UI/UX tweak · ♻️ micro refactor (< 100 dòng).
2. Liệt kê file được phép sửa và file không được đụng.
3. Kiểm tra branch (xem Gotchas).
4. Chọn chế độ: 1 repo → **Solo**; ≥ 2 repo hoặc lỗi phân tán Client–Server → **Swarm**. Đọc `references/multi-repo-swarm.md` khi chọn Swarm.
5. Yêu cầu mập mờ hoặc có nhiều cách giải: dừng và hỏi người dùng 1–3 câu, mỗi câu kèm phương án `(Recommended)`, vì sửa theo đoán sai tốn gấp đôi thời gian. Yêu cầu rõ thì tóm tắt scope 1–2 dòng rồi làm tiếp.

### Phase 2 — Tìm nguyên nhân gốc
- Đọc log/stack trace và đọc file liên quan thực tế (không đoán từ tên file).
- Ghi ra 3 dòng: **Hiện tượng** · **Nguyên nhân gốc** (file:dòng, hàm) · **Rủi ro lan** (module nào khác bị ảnh hưởng).

### Phase 3 — Sửa code
- Minimal diff: chỉ sửa dòng cần để xử lý nguyên nhân gốc.
- Theo đúng naming, indent, import pattern của dự án.
- Không để lại `console.log`/`print()`, comment rác, import thừa.
- Swarm: chốt contract ở Phase 2 rồi giao việc cho worker từng repo.

### Phase 4 — Tự phản biện
Chưa tuyên bố xong ngay sau khi sửa. Solo: tự đóng vai reviewer soi `git diff`; Swarm: critic độc lập review.
1. Đối chiếu từng yêu cầu của người dùng/ticket → đã đáp ứng chưa, có bỏ sót không.
2. Soát diff: log thừa, null/KeyError/ReferenceError, leak.
3. Contract: schema backend khớp model client không; có đổi hành vi tính năng khác không.
4. Biên & bất đồng bộ: double-call/retry (idempotency), kill app, mạng yếu, ngắt giữa chừng.
5. Có đổi UI: chụp ảnh (Playwright) ở ít nhất POS/Desktop 1280–1336px và Mobile 390px, rồi mở từng ảnh ra xem (Claude Code: `Read` file ảnh · Antigravity: `view_file`). Kiểm: rớt dòng làm lệch chiều cao card, nút dính chùm, primary CTA có nổi bật, Mobile có tràn ngang. Chỉ gửi ảnh cho khách khi chính mình đã thấy ổn.

### Phase 5 — Kiểm thử tự động
Phát hiện stack và chạy lệnh tương ứng; Swarm thì chạy song song từng repo.

| Stack | Build / type-check | Lint | Test |
| :--- | :--- | :--- | :--- |
| Node / TS / React / Next / Vue | `npm run type-check` hoặc `tsc --noEmit` | `npm run lint` | `npm test` / `npx vitest` |
| Python | `mypy .` / `pyright` | `ruff check .` | `pytest` |
| Java / Kotlin / Android | `./gradlew compileJava` / `mvn compile` | `./gradlew checkstyle` | `./gradlew test` / `mvn test` |
| C# / .NET | `dotnet build` | `dotnet format --verify-no-changes` | `dotnet test` |
| Go | `go build ./...` | `go vet ./...` | `go test ./...` |
| Rust | `cargo check` | `cargo clippy` | `cargo test` |
| iOS / Swift | `xcodebuild build` | `swiftlint` | `xcodebuild test` |
| PHP | `vendor/bin/phpstan` | `vendor/bin/phpcs` | `php artisan test` / `phpunit` |

Ưu tiên script có sẵn trong `package.json`/`Makefile`/CI của dự án hơn bảng trên. Lệnh fail (exit ≠ 0): đọc log lỗi, sửa nguyên nhân, chạy lại tới khi xanh. Không báo hoàn thành khi chưa chạy (learned_patterns RULE-001); nếu không chạy được (thiếu thiết bị, thiếu secret) thì nói rõ bước nào chưa verify.

Tác vụ có UI/Mobile/Integration: viết thêm hướng dẫn kiểm thử thủ công (môi trường, các bước đánh số, kỳ vọng từng bước, ca ngoại lệ) trong báo cáo.

### Phase 6 — Báo cáo bàn giao
Dùng mẫu `assets/report-template.md` (5 góc nhìn: quản lý, dev, QC, UX, khách hàng). Mọi kết quả test trong báo cáo phải là lệnh đã chạy thật kèm output tóm tắt.
