# [RULE-GIT-001] Git Workflow, Branch Isolation & Commit Standards

> **Unit ID**: `RULE-GIT-001` | **Category**: `GIT` | **Status**: ACTIVE | **Scope**: GLOBAL

---

## 🎯 1. Nguyên tắc Bất di Bất dịch: Branch Isolation (Cô lập Nhánh)

> [!CAUTION]
> **CẤM SỬA CHUNG / CẤM COMMIT ĐÈ BUG KHÔNG LIÊN QUAN VÀO NHÁNH HIỆN TẠI:**
> Khi đang làm việc trên một branch (ví dụ: `fix/bug-A` hoặc `feat/feature-X`), nếu phát hiện lỗi mới hoặc người dùng yêu cầu sửa một vấn đề KHÔNG LIÊN QUAN đến mục tiêu ban đầu của branch hiện tại:
> 
> 1. **TUYỆT ĐỐI KHÔNG** "tiện tay" sửa code hoặc commit vào branch hiện tại.
> 2. **BẮT BUỘC TÁCH NHÁNH MỚI:**
>    - `git stash` hoặc commit hoàn tất công việc dở dang trên branch hiện tại.
>    - Chuyển về nhánh base ổn định: `git checkout develop && git pull origin develop` (hoặc `staging`/`main` theo quy chuẩn dự án).
>    - Tạo branch mới tinh từ base: `git checkout -b <prefix>/<ticket-or-topic>`.
>    - Thực thi fix độc lập, verify độc lập và merge/tạo PR độc lập.

---

## 🌿 2. Quy ước Đặt tên Branch (Branch Naming Standards)

Tất cả các nhánh mới phải tuân thủ nghiêm ngặt cú pháp: `<type>/<ticket-id>-<short-description>` hoặc `<type>/<short-description>`.
Tên nhánh dùng chữ thường (lowercase) và dấu gạch nối (`kebab-case`), không dấu, không khoảng trắng:

| Loại nhánh (Prefix) | Mục đích sử dụng | Base Branch | Ví dụ hợp lệ |
| :--- | :--- | :--- | :--- |
| **`fix/`** | Sửa bug thường trong quá trình dev/staging | `develop` | `fix/duplicate-scan`, `fix/ISX-8087-view-comment` |
| **`hotfix/`** | Sửa bug nghiêm trọng/crash trên Production | `production` / `staging` | `hotfix/quota-init-crash`, `hotfix/token-expired` |
| **`feat/`** | Thêm tính năng mới, module mới | `develop` | `feat/mep-extraction`, `feat/multi-room-merge` |
| **`refactor/`** | Tái cấu trúc mã nguồn không đổi hành vi | `develop` | `refactor/upload-pipeline`, `refactor/auth-service` |
| **`perf/`** | Tối ưu hóa hiệu năng, giảm memory/CPU/lag | `develop` | `perf/pointcloud-cache`, `perf/mesh-rendering` |
| **`test/`** | Bổ sung unit test, integration test, E2E | `develop` | `test/scans-api-coverage`, `test/monkey-test` |
| **`chore/`** | Cập nhật dependency, config, CI/CD, script | `develop` | `chore/bump-podspec`, `chore/docker-compose-update` |

---

## 📝 3. Quy ước Commit Code (Conventional Commits Standards)

Mọi commit message phải tuân thủ cấu trúc **Conventional Commits**:

```text
<type>(<scope>): <subject in present tense>

[Optional body: Giải thích ngắn gọn TẠI SAO làm thay đổi này và các tác động chính]

[Optional footer: Closes #123, Refs: ISX40-7974]
```

### 3.1. Các Loại Type Bắt buộc:
- `fix`: Sửa lỗi cho người dùng hoặc hệ thống.
- `feat`: Tính năng mới cho người dùng.
- `refactor`: Sửa code không đổi tính năng, không sửa bug.
- `perf`: Cải thiện hiệu năng.
- `test`: Thêm hoặc sửa test cases.
- `style`: Định dạng code (whitespace, semicolons, import sort), không đổi logic.
- `chore`: Tác vụ bảo trì, build tooling, dependency.
- `docs`: Sửa tài liệu hướng dẫn, Markdown.

### 3.2. Tiêu chuẩn Scope:
Scope phải chỉ rõ module hoặc component bị tác động (viết thường):
- Backend: `fix(scans): ...`, `feat(auth): ...`, `refactor(process_jobs): ...`
- Mobile: `fix(scan): ...`, `feat(viewer): ...`, `style(theme): ...`

### 3.3. Ví dụ Commit Chuẩn:
```bash
# Sửa bug:
git commit -m "fix(scans): resolve duplicate scan on interrupted upload and refresh-urls contract"

# Thêm tính năng:
git commit -m "feat(viewer): add point cloud density slider and color presets"

# Tối ưu hiệu năng:
git commit -m "perf(mesh): optimize mesh viewer performance with three-mesh-bvh cleanup"
```

---

## 🛡️ 4. Quy trình Trước khi Merge / Pull Request (Pre-Merge Protocol)

Trước khi merge vào `develop`, `staging`, hoặc `production`:
1. **Kiểm tra trạng thái sạch:** Không commit file rác, file `.env`, file log cá nhân, `node_modules`, `__pycache__`.
2. **Rebase/Pull mới nhất:** Kéo thay đổi mới nhất từ base branch vào nhánh làm việc để tránh conflict (`git pull origin develop`).
3. **Verify 100% Pass:** Tất cả unit tests và linter phải xanh hoàn toàn trước khi tạo PR hoặc push merge.

---

## 🤖 5. Quy Chuẩn Cô Lập Nhánh Cho AI Subagents & Lệnh Deploy (Agent Isolation Gate)

1. **Bắt buộc tạo Branch riêng cho mỗi Task:**
   - Khi nhận bất kỳ task/bug nào từ Feedback Hub hoặc backlog, AI Supervisor/Subagent **BẮT BUỘC** phải tạo nhánh riêng:
     ```bash
     git checkout -b <type>/<ticket-id>-<short-description>
     ```
   - Tuyệt đối cấm code hoặc commit thẳng vào nhánh chính (`main`, `master`, `production`).
2. **Không tự ý Merge / Deploy (Human-In-The-Loop Barrier):**
   - Sau khi hoàn thành code trên branch, chạy test và tạo ảnh evidence, AI chuyển trạng thái sang `pending_deploy` và **DỪNG LẠI (HARD STOP)**.
   - Chỉ khi User xác nhận rõ ràng ở lượt trao đổi tiếp theo (ví dụ: "merge và deploy đi"), AI mới được phép merge branch vào nhánh chính và thực thi lệnh deploy.

