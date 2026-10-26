# Tài Liệu Kỹ Thuật Hệ Thống (System Architecture Document - SAD)
**Dự án**: [Tên dự án] | **Ngày xuất**: [YYYY-MM-DD] | **Commit**: [git short hash] | **Người lập**: [tên người/agent]

## 1. Tổng quan hệ thống & bối cảnh nghiệp vụ
- Mục đích dự án, đối tượng người dùng, phạm vi chức năng chính.

## 2. Công nghệ & Tech Stack
- Frontend, Backend, Database, Caching, Cloud/DevOps, thư viện bên thứ ba quan trọng (kèm version từ manifest).

## 3. Kiến trúc hệ thống & sơ đồ thành phần
- Sơ đồ component / C4 bằng Mermaid.
- Phân tầng logic (Controller → Service → Repository / Data Access).

## 4. Mô hình dữ liệu & ERD
- Sơ đồ `erDiagram` Mermaid các bảng/collection và quan hệ 1-N, N-N.
- Bảng mô tả các trường quan trọng.

## 5. Danh mục API
| Method | Path | Auth | Request | Response | Định nghĩa tại |
| :--- | :--- | :--- | :--- | :--- | :--- |

## 6. Luồng nghiệp vụ cốt lõi
- `sequenceDiagram` Mermaid cho các luồng phức tạp nhất (auth, checkout, đồng bộ dữ liệu...).

## 7. Bảo mật, xác thực & vận hành
- Cơ chế xác thực/phân quyền, CORS, rate limit, logging & monitoring.
- Build, test, deploy (CI/CD, Docker, cloud). Secret được tham chiếu từ đâu (chỉ ghi tên/đường dẫn, không ghi giá trị).

## 8. Chất lượng mã nguồn & nợ kỹ thuật
- Điểm tốt của kiến trúc hiện tại.
- Rủi ro (performance, security, anti-pattern) kèm file:dòng.
- Đề xuất cải tiến ngắn hạn / dài hạn.
