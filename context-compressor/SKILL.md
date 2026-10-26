---
name: context-compressor
description: "Dùng khi phải đọc log build/test/CI, output terminal hoặc stack trace rất dài (hàng trăm tới hàng nghìn dòng) để tìm lỗi: chạy script lọc giữ lại dòng lỗi kèm ngữ cảnh quanh exception, bỏ progress bar, dòng thành công và dòng lặp, rồi chỉ đọc bản đã lọc. Dùng cả khi người dùng chỉ dán/đưa file log và hỏi \"sao lỗi\", \"build fail\". Không dùng để tóm tắt tài liệu nghiệp vụ hay hội thoại."
compatibility: "Cần Python 3.9+ (chỉ stdlib)."
---

# [SKILL-COST-001] Context Compression — lọc log trước khi đọc

Log build/test/CI dài làm tốn context và che mất dòng lỗi thật. Thay vì đọc cả file, chạy script lọc rồi chỉ đọc phần còn lại. Đường dẫn tính từ thư mục skill.

## Cách dùng

```bash
python scripts/filter_log.py build.log                 # file log
<lệnh build> 2>&1 | python scripts/filter_log.py -C 8   # hoặc đọc từ stdin
python scripts/filter_log.py ci.log --pattern "OrderServiceTest"   # thêm regex riêng
```

- stdout: các dòng lỗi kèm ngữ cảnh (mặc định ±15 dòng), mỗi dòng có số dòng gốc; `...` đánh dấu đoạn bị lược.
- stderr: một dòng tóm tắt — tổng số dòng, số dòng khớp lỗi, dòng lỗi đầu tiên.
- Không thấy lỗi → in 40 dòng cuối (`--tail`). Output tối đa 200 dòng (`--max-lines`).

## Quy trình

1. Log ngắn (< ~200 dòng) thì đọc thẳng, không cần script.
2. Log dài: chạy `filter_log.py`, đọc kết quả, bắt đầu từ **lỗi đầu tiên** — các lỗi sau thường là hệ quả.
3. Cần thêm ngữ cảnh quanh một chỗ cụ thể: đọc trực tiếp đoạn đó trong file gốc theo số dòng thay vì tăng `-C` cho toàn bộ log.
4. Khi báo lại người dùng, trích nguyên văn dòng lỗi chính kèm số dòng, không dán cả bản đã lọc.

## Gotchas

- Dòng như `0 errors`, `failed: 0` được coi là không lỗi; nhưng tên test/biến chứa chữ `error` vẫn có thể khớp — đọc tóm tắt rồi phán đoán, đừng tin số "dòng khớp lỗi" tuyệt đối.
- Dòng trùng liên tiếp và progress bar (`45%`, `[====>  ]`, `Downloading…`) bị bỏ; nếu đang điều tra chính việc tải gói bị treo, đọc log gốc.
- Script tự nhận UTF-8 (có/không BOM) và UTF-16 có BOM (file do PowerShell `>` ghi ra); encoding khác (cp1258…) sẽ hiện `�` — khi đó chuyển file sang UTF-8 trước.
