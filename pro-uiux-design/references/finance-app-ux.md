# UX cho app tài chính cá nhân (mẫu SafeBudget / Kakeibo)

Đọc khi thiết kế app quản lý chi tiêu/ngân sách (dòng app Store của ITGViet như SafeBudget). Không áp cho app khác.

Các phần nên có:

1. **Kiến Trúc Điều Hướng Chuẩn (Standard 4-Tab Bar):**
   - **Tab 1: Sổ Thu Chi (Dashboard & Feed):** Danh sách giao dịch, lọc theo ngày/ví/hũ, tìm kiếm nhanh, nút thêm nhanh.
   - **Tab 2: Phân Tích & Báo Cáo (Analytics & Charts):** Biểu đồ tỷ lệ Vector SVG động, cơ cấu chi tiêu, cảnh báo vượt hạn mức, xuất file báo cáo.
   - **Tab 3: Phương Pháp Luận / Chuyên Mục Sâu (Methodology / Reflection):** Nội dung giá trị thực tiễn (như 4 câu hỏi Kakeibo, đánh giá hành vi chi tiêu).
   - **Tab 4: Cài Đặt & Trung Tâm Dữ Liệu (Settings & Vault):** Khóa bảo mật PIN, quản lý ví, sao lưu/khôi phục, đổi đơn vị tiền tệ, chính sách quyền riêng tư và xóa sạch dữ liệu.
2. **Chi Tiết Hóa Dữ Liệu (Drill-Down Detail):**
   - Khi bấm vào bất kỳ danh mục/hũ/ví nào, phải mở ra Modal hoặc màn hình con hiển thị danh sách các khoản chi của riêng mục đó kèm nút điều chỉnh ngân sách.
3. **Thao Tác Tức Thì Kèm Phục Hồi (Immediate Action & Reversible UX):**
   - Mọi hành động nhạy cảm (Xóa giao dịch, Khởi tạo lại) đều phải có Dialog xác nhận hoặc Toast thông báo kèm nút "HOÀN TÁC" (Undo).
4. **Không Để Lại Thành Phần "Chết":**
   - Bất kỳ nút, icon hay thẻ nào xuất hiện trên màn hình đều phải có phản hồi khi người dùng chạm vào (Active state, Modal, Drawer, hoặc Action sheet).
