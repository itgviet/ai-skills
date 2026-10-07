---
name: context-compressor
description: >-
  [SKILL-COST-001] Context Compression & Token Savings Engine: Tự động cô đọng các đoạn log dài, file dữ liệu lớn hoặc lịch sử trao đổi thành bản tóm tắt siêu nhỏ trước khi truyền vào prompt để tiết kiệm 70-90% token.
---

# [SKILL-COST-001] Context Compression & Token Savings Engine

Skill này chịu trách nhiệm nén dữ liệu đầu vào (Terminal Logs, Git Diff lớn, File tài liệu dài) để bảo vệ ngân sách Token của Bạn.

## ⚙️ Các Bước Thực Thi Cô Đọng Ngữ Cảnh

1. **Log Sanitization**: Lọc bỏ các dòng thông tin thừa (Progress bars, successful build lines, verbose debug trace).
2. **Error Extraction**: Trích xuất duy nhất 15 dòng xung quanh vị trí Exception / Error Stacktrace.
3. **Structured Compression**: Chuyển đổi văn bản tự do thành dạng bảng hoặc JSON siêu gọn.
4. **Context Injection**: Nạp bản nén vào Context Window của Trợ lý thay vì văn bản thô ban đầu.
