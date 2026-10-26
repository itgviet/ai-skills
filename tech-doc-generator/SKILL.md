---
name: tech-doc-generator
description: "Dùng khi cần viết tài liệu kỹ thuật cho một codebase có sẵn: khảo sát tech stack, trích xuất schema DB và danh mục API, vẽ sơ đồ Mermaid (component, ERD, sequence), đánh giá nợ kỹ thuật, xuất docs/TECHNICAL_SYSTEM_DOCUMENTATION.md theo khung 8 chương. Dùng khi người dùng nói \"viết tài liệu hệ thống\", \"onboard người mới vào repo này\", \"reverse-engineer dự án\". Chỉ cần một sơ đồ tương tác → archify."
---

# [SKILL-LEAD-003] Tech Doc Generator: System & Source Code Reverse-Engineering Engine

Khảo sát một codebase có sẵn và xuất tài liệu kỹ thuật hệ thống (SAD) tại `docs/TECHNICAL_SYSTEM_DOCUMENTATION.md` của repo dự án.

## Gotchas

- **Không chép giá trị secret vào tài liệu.** File `.env`, keystore, service-account JSON chỉ ghi tên và nơi tham chiếu (secret của các dự án nằm ở `D:\SecureVault\<Project>\`); thấy secret nằm trong repo thì dừng và báo người dùng (RULE-SEC-001).
- **Mọi khẳng định phải truy được về code:** endpoint, bảng, luồng đều ghi file định nghĩa. Không đủ bằng chứng thì ghi "chưa xác định" thay vì suy đoán — tài liệu sai còn hại hơn thiếu.
- **Repo lớn:** đọc theo vùng (manifest, router, model, migration) thay vì đọc toàn bộ file lớn; lọc output dài trước khi đọc (RULE-PERF-001).
- **Tài liệu master:** nếu dự án có `SYSTEM_ARCHITECTURE_AND_USER_GUIDE.md` hoặc spec trong `docs/specs/<app_id>/`, đối chiếu và ghi chỗ lệch thay vì viết song song một nguồn sự thật mới (RULE-SDD-001).
- **Ghi commit hash** vào đầu tài liệu để người đọc biết tài liệu phản ánh phiên bản code nào.

## Quy trình 5 bước

1. **Bản đồ dự án:** ngôn ngữ, framework (từ `package.json`, `pyproject.toml`, `build.gradle`, `go.mod`...), cây thư mục và cách phân tầng, file môi trường, Dockerfile, CI/CD.
2. **Dữ liệu & API:** đọc Prisma/TypeORM/SQLAlchemy/Mongoose/migration SQL/Firestore rules → ERD Mermaid; liệt kê endpoint REST/GraphQL/gRPC (method, route, input, response, auth).
3. **Kiến trúc & luồng:** sơ đồ component; sequence diagram cho luồng cốt lõi; cơ chế xác thực/phân quyền (JWT, OAuth2, RBAC, Firestore rules).
4. **Sức khỏe mã nguồn:** điểm nghẽn hiệu năng (N+1, query không index, leak), lỗ hổng cơ bản (secret, thiếu validate input), nợ kỹ thuật và đề xuất refactor — mỗi mục có file:dòng.
5. **Xuất tài liệu:** viết `docs/TECHNICAL_SYSTEM_DOCUMENTATION.md` theo khung 8 chương trong `assets/sad-template.md` (đọc mẫu ở bước này). Bỏ chương không áp dụng thay vì điền chung chung.

Chỉ cần một sơ đồ tương tác (kiến trúc, ERD, sequence) thay vì cả bộ tài liệu → dùng skill `archify`.
