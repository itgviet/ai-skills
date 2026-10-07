---
name: techlead-auditor
description: >-
  Skill dành cho Tech Lead Agent: Tự động soi Git Diff/PR, kiểm tra lỗ hổng bảo mật OWASP, hiệu năng, kiến trúc SOLID và tạo báo cáo Code Review kèm đề xuất ADR.
---

# Tech Lead Auditor: Code Review & Security Gate

Skill này thực hiện quy trình kiểm tra chất lượng mã nguồn độc lập trước khi merge hoặc release.

## 🔍 Checklist Review 5 Tầng

1. **🔒 Security Audit**:
   - Quét mật khẩu hardcode, API Keys.
   - Kiểm tra SQL Injection, XSS, CSRF, insecure deserialization.
2. **⚡ Performance & Memory**:
   - Phát hiện các vòng lặp O(N^2) hoặc N+1 query.
   - Kiểm tra việc giải phóng tài nguyên (DB Connection, File Stream, Thread Locks).
3. **📐 Architecture & SOLID**:
   - Đảm bảo Single Responsibility (SoC).
   - Kiểm tra tính phụ thuộc ngược (Dependency Inversion).
4. **🧪 Test Coverage & Edge Cases**:
   - Kiểm tra coverage của business logic cốt lõi.
   - Đảm bảo có xử lý null pointer / undefined safety.
5. **📝 Architecture Decision Log (ADR)**:
   - Nếu phát hiện thay đổi cấu trúc DB hoặc thư viện lớn, tự động đề xuất viết file ADR lưu tại `docs/memory/adr/`.

## 📤 Báo Cáo Đầu Ra (Report Output)
Xuất báo cáo Markdown dạng scorecard (Điểm A/B/C/D) với các khuyến nghị cụ thể theo file & dòng code.
