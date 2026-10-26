---
name: skill-factory
description: "Dùng khi muốn biến một quy trình lặp lại của team ITGViet (checklist, báo cáo, SOP, script) thành skill mới trong kho skills dùng chung cho Claude và Gemini: kiểm tra trùng trong unit_registry.json, đặt tên, viết SKILL.md theo chuẩn agentskills.io, đăng ký Unit ID và chạy validator. Dùng khi người dùng nói \"tạo skill\", \"đóng gói quy trình này\", \"lần sau tự làm vậy\". Đo và tối ưu description bằng eval → anthropic-skills:skill-creator."
compatibility: "Ghi skill vào kho skills của workspace ITGVietAssistant ($ITGVIET_HOME, mặc định D:\\ITGVietAssistant)."
---

# [SKILL-FACTORY-001] Skill Factory — chuẩn tạo skill của ITGViet

Biến một quy trình đã làm thành công ít nhất 2 lần (RULE-META-001) thành skill dùng chung cho Claude Code và Gemini/Antigravity.
Chuẩn gốc: [agentskills.io/specification](https://agentskills.io/specification) và [best practices](https://agentskills.io/skill-creation/best-practices).

Kho skills: `$ITGVIET_HOME/skills/` (repo `itgviet/ai-skills`). `~/.claude/skills` và `~/.gemini/config/skills` là junction tới thư mục này, nên một skill viết ở đây chạy được ở cả hai agent.

## Gotchas

- `unit_registry.json` **không đầy đủ**: nhiều skill đang dùng (onetech-workspace-manager, production-safety-guardrail, rnd-loop, các skill ngôn ngữ/đồ họa/compliance…) chưa có Unit ID trong đó. Kiểm tra trùng phải xem cả danh sách thư mục `$ITGVIET_HOME/skills/*/SKILL.md`, không chỉ registry.
- Có hai bản memory: `$ITGVIET_HOME/docs/memory/` (bản master theo CLAUDE.md của workspace) và `$ITGVIET_HOME/memory/` (junction `~/.claude/shared-memory`, chứa `rnd_playbook.md`). Đăng ký Unit ID vào `docs/memory/unit_registry.json`.
- Skill đọc dữ liệu workspace phải ghi đường dẫn dạng `$ITGVIET_HOME/...`. Đường dẫn tương đối kiểu `docs/memory/...` hay `skills/<x>/scripts/...` sẽ hỏng khi người dùng đang mở một dự án khác (NhatSinhCafe, Store…).
- Không dùng tên tool riêng của một agent làm bước bắt buộc (`ask_question`, `write_to_file`, `generate_image`, `view_file`, `run_command`). Viết theo hành động ("hỏi người dùng và chờ trả lời") và nếu cần thì thêm một dòng ánh xạ (Claude Code: `AskUserQuestion`; Antigravity: `ask_question`).
- Thư mục `synced/` và `.trash/` trong kho là của Claude app (đã gitignore), không tạo skill trong đó.
- Skill vendored (aws-*, amazon-bedrock, archify, find-skills, playwright-cli, launch-with-aws, signing-in-to-aws) không sửa tay, vì lần cập nhật sau sẽ ghi đè.

## Quy trình

Progress:
- [ ] 1. Xác nhận nhu cầu: quy trình đã lặp ≥ 2 lần, có bước/quy ước mà agent sẽ làm sai nếu không được dặn. Agent đã tự làm tốt thì không cần skill.
- [ ] 2. Kiểm tra trùng: liệt kê `$ITGVIET_HOME/skills/*/SKILL.md` + đọc description; tra `docs/memory/unit_registry.json`. Gần trùng → sửa skill cũ thay vì tạo mới.
- [ ] 3. Gom nguồn thật: transcript phiên làm thành công, các lần người dùng sửa, runbook, script đã dùng, lỗi đã gặp. Không viết từ kiến thức chung.
- [ ] 4. Tạo thư mục và `SKILL.md` từ [assets/SKILL.template.md](assets/SKILL.template.md).
- [ ] 5. Viết `<skill-dir>/evals/evals.json` (2–3 case) và `<skill-dir>/evals/trigger_queries.json` (~20 câu).
- [ ] 6. Validate: `python _tools/validate_skills.py <skill-dir>` (chạy từ `$ITGVIET_HOME/skills`). Lỗi → sửa → chạy lại tới khi sạch.
- [ ] 7. Đăng ký Unit ID, cập nhật tài liệu master (RULE-DOC-001), báo lại cho người dùng tên skill + Unit ID.

## Frontmatter

```yaml
---
name: jira-sprint-report          # = tên thư mục; a-z0-9 và '-', ≤ 64 ký tự, không '--', không đầu/cuối '-'
description: "Dùng khi ... (ý định người dùng, từ khóa VI + EN). Dùng cả khi người dùng chỉ nói \"...\". Không dùng cho ... → <skill-khác>."
compatibility: "Cần Python 3.11+ và ..."   # chỉ khi thật sự có yêu cầu môi trường; ≤ 500 ký tự
metadata:                          # mọi khóa ngoài spec để ở đây, giá trị là chuỗi
  version: "1.0.0"
  author: "itgviet"
  last_updated: "2026-10-26"
---
```

- Chỉ dùng các khóa của spec: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. `version`/`author`/`last_updated` để trong `metadata`.
- `description` ≤ 1024 ký tự, mở đầu bằng "Dùng khi…", tả **ý định người dùng** chứ không tả cơ chế bên trong; liệt kê cả cách nói gián tiếp; kết bằng ranh giới với skill gần giống (near-miss). Description là thứ duy nhất agent đọc để quyết định kích hoạt, nên đây là phần đáng đầu tư nhất.

## Thân SKILL.md

- Dưới 500 dòng và khoảng 5.000 token. Chi tiết dài → `references/`, template dài → `assets/`, kèm câu nói rõ **khi nào** đọc ("Đọc `references/<lỗi-api>.md` khi API trả về khác 200"). Chỉ tham chiếu sâu một cấp.
- Chỉ viết điều agent không tự biết: quy ước dự án, đường dẫn, lệnh cụ thể, lỗi đã gặp. Bỏ phần giảng giải khái niệm chung.
- Mục `## Gotchas` đặt gần đầu, mỗi dòng là một lần người dùng đã phải sửa hoặc một sự thật trái với giả định thông thường. Khi người dùng sửa agent trong lúc dùng skill → thêm vào đây.
- Chọn sẵn một cách mặc định, chỉ nhắc phương án khác như lối thoát; không đưa danh sách lựa chọn ngang hàng.
- Khuôn đầu ra cụ thể (template) thay cho mô tả định dạng bằng lời.
- Việc nhiều bước: checklist; việc có thể hỏng: vòng validate (làm → chạy validator → sửa → chạy lại); thao tác hàng loạt/phá hủy: plan → validate với nguồn chuẩn → execute.
- Giải thích lý do ("vì…") thay vì viết in hoa `BẮT BUỘC`/`TUYỆT ĐỐI`.

## Script trong `scripts/`

- Gọi bằng đường dẫn tương đối từ gốc skill (`python scripts/<tên>.py`), không dùng đường dẫn tuyệt đối `D:` hay `skills/<x>/...`.
- Có `--help` ngắn kèm ví dụ; không hỏi tương tác (agent không trả lời được prompt TTY); thiếu tham số → báo lỗi nói rõ cần gì.
- Dữ liệu ra stdout dạng JSON/CSV; tiến trình và cảnh báo ra stderr; mã thoát khác nhau cho từng loại lỗi.
- Lệnh ghi/xóa/gửi ra ngoài có `--dry-run`; thao tác nguy hiểm cần cờ xác nhận rõ (`--confirm`).
- Khai báo dependency: Python dùng khối PEP 723 (`# /// script`) và kiểm tra import với thông báo cài đặt rõ ràng; ghi yêu cầu runtime trong `compatibility`.
- Output lớn: mặc định tóm tắt hoặc giới hạn, có `--limit`/`--offset` hoặc `--output <file>`.

## Eval

`<skill-dir>/evals/evals.json` — bắt đầu 2–3 case, thêm assertion sau khi xem kết quả chạy đầu:

```json
{
  "skill_name": "<name>",
  "evals": [
    {"id": 1, "prompt": "câu yêu cầu thật, có đường dẫn/ngữ cảnh", "expected_output": "mô tả kết quả đúng",
     "files": ["<skill-dir>/evals/files/<input>"], "assertions": ["kiểm chứng được, cụ thể"]}
  ]
}
```

`<skill-dir>/evals/trigger_queries.json` — khoảng 20 câu, nửa nên kích hoạt, nửa không; câu "không" nên là **near-miss** (chung từ khóa nhưng cần skill khác):

```json
[{"query": "...", "should_trigger": true}, {"query": "...", "should_trigger": false}]
```

Chạy mỗi case có skill và không có skill (hoặc bản cũ) để so. Đo và tối ưu tỉ lệ kích hoạt của description → dùng `anthropic-skills:skill-creator` (tự chia train/validation, chạy lặp).

## Đăng ký Unit ID

Thêm vào mảng `units` của `$ITGVIET_HOME/docs/memory/unit_registry.json`, đúng cấu trúc các mục hiện có:

```json
{"unit_id": "SKILL-<PIL>-<NNN>", "pillar_id": "PIL-<SUP|DEV|LEAD|PM|META|COST>", "type": "SKILL",
 "name": "<name>", "path": "skills/<name>/SKILL.md", "status": "ACTIVE"}
```

Lấy số `<NNN>` kế tiếp trong cùng pillar; thêm Unit ID vào `owned_skills` của pillar trong `docs/memory/pillars_registry.json`; nếu là thay đổi cấu trúc lớn thì cập nhật `docs/SYSTEM_ARCHITECTURE_AND_USER_GUIDE.md`. Không commit thay người dùng.
