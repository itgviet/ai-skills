---
name: store-policy-compliance
description: "Dùng khi rà soát tuân thủ trước khi gửi app lên Google Play/App Store, hoặc khi tính năng chạm tới quyền Android/iOS, Data Safety/Privacy label, quảng cáo, in-app purchase/subscription, đối tượng trẻ em (Families/COPPA), bản quyền font, nhạc, hình ảnh, asset. Kết luận Approve/Conditional/Reject kèm lý do. Dùng cả khi người dùng hỏi \"app bị reject vì...\", \"thêm quyền này có sao không\", \"dùng font này được không\"."
---

# Store Policy & Legal Compliance — duyệt tuân thủ trước khi lên store

Thẩm định một tính năng (khi còn là spec) hoặc một bản build (trước khi submit) theo chính sách Google Play / App Store và bản quyền tài nguyên, rồi kết luận APPROVED / CONDITIONAL / BLOCKED kèm lý do.

Ví dụ biên bản thật đã làm: `D:\itgviet\Store\docs\audits\COMPLIANCE_AUDIT_APP_001.md` (SafeBudget, 25 tiêu chí) — đọc khi cần mẫu chi tiết cho app Store của ITGViet.

## Gotchas

- App có **AdMob** dù "không thu thập dữ liệu": vẫn phải khai `com.google.android.gms.permission.AD_ID` trong manifest và trong Data Safety khai *Device or other IDs* do Google Mobile Ads SDK thu thập cho *Advertising or marketing* và *Fraud prevention*. Khai "No data collected" là sai. (Nguồn: audit SafeBudget APP-001.)
- App offline, không có tài khoản: không cần luồng xóa tài khoản, nhưng phải có chức năng **xóa toàn bộ dữ liệu** trong app và nêu trong privacy policy. App có tài khoản: cần xóa tài khoản trong app **và** một URL web công khai để yêu cầu xóa. (Nguồn: audit APP-001, tiêu chí 9.)
- Quảng cáo trả thưởng phải do người dùng chủ động chọn, nói rõ được gì, và từ chối không làm mất chức năng cơ bản. (Nguồn: audit APP-001, tiêu chí 4.)
- Listing sửa bằng "Save as draft" không vào review — xem Gotchas của `project-assistant` trước khi kết luận "đã nộp".

## Checklist thẩm định

**1. Quyền & hành vi**
- [ ] Mỗi quyền nguy hiểm gắn với chức năng cốt lõi; soi kỹ `ACCESS_BACKGROUND_LOCATION`, `MANAGE_EXTERNAL_STORAGE`, SMS/Call log, `ACCESSIBILITY_SERVICE`, `PACKAGE_USAGE_STATS`, `RECORD_AUDIO`, `CAMERA`.
- [ ] Có màn hình giải thích (prominent disclosure) trước khi xin quyền runtime nhạy cảm.
- [ ] Metadata (tên, icon, screenshot, mô tả) đúng sự thật, không nhồi từ khóa, không mượn thương hiệu khác.
- [ ] Interstitial không bật ngay khi mở app hay giữa thao tác; có nút đóng rõ.

**2. Bản quyền & thương hiệu**
- [ ] Hình, nhân vật, logo tự làm hoặc có giấy phép thương mại; không nhái thương hiệu nổi tiếng.
- [ ] Nhạc/SFX: giấy phép thương mại, royalty-free, public domain hoặc CC-BY kèm ghi công.
- [ ] Font: OFL/Google Fonts hoặc giấy phép cho phép **nhúng vào app** (giấy phép desktop không đủ).
- [ ] Tên app, package/bundle id không chứa nhãn hiệu của bên khác.
- [ ] Giấy phép được lưu trong repo dự án (thư mục licenses) để đối chiếu.

**3. Dữ liệu & quyền riêng tư**
- [ ] Data Safety / Privacy Nutrition Label khớp với mọi SDK trong code (Firebase, AdMob, Crashlytics, Facebook SDK…).
- [ ] Privacy policy URL công khai, không cần đăng nhập, nêu đúng SDK và quyền xóa dữ liệu.
- [ ] Xóa dữ liệu/tài khoản theo Gotchas ở trên.

**4. Thanh toán**
- [ ] Hàng hóa số (mở khóa tính năng, gói, coin) đi qua Google Play Billing / Apple IAP; không link chuyển khoản, web payment hay QR ngoài.
- [ ] Subscription ghi rõ giá, chu kỳ, dùng thử, cách hủy.

**5. Trẻ em & gia đình**
- [ ] Đã xác định đối tượng; nếu có trẻ em (< 13 tại Mỹ hoặc theo luật địa phương): chỉ dùng ad SDK được chứng nhận cho Families, không thu Advertising ID hay thông tin cá nhân của trẻ, nội dung không bạo lực/người lớn/cờ bạc.

## Kết luận

| Mức | Dấu hiệu | Xử lý |
|---|---|---|
| BLOCKED | Vi phạm IP, quyền nguy hiểm không lý do, thiếu cơ chế xóa dữ liệu/tài khoản, lách billing, vi phạm COPPA | Dừng release, báo PM/Lead |
| CONDITIONAL | Thiếu disclosure, Data Safety thiếu SDK, font chưa rõ giấy phép, quảng cáo dày | Được làm tiếp nhưng phải sửa trước khi submit |
| APPROVED | Đạt cả 5 nhóm | Được submit |

## Mẫu báo cáo

```markdown
# Store Policy & Legal Compliance Audit
**App:** [tên] · **Phiên bản/branch:** [v1.0.0 / feature/xyz] · **Kết quả:** APPROVED / CONDITIONAL / BLOCKED

## 1. Quyền & dữ liệu
- [x/ ] ... (bằng chứng: file:dòng, ảnh màn hình Console)
## 2. Bản quyền tài nguyên
- [x/ ] ...
## 3. Chính sách store (quảng cáo, billing, độ tuổi)
- [x/ ] ...
## 4. Kết luận & việc cần làm
- ...
```
