---
name: store-policy-compliance
description: "Store compliance officer: audit Google Play/App Store policies, Data Safety, permissions, and IP copyright."
---

# Store Policy & Legal Compliance Officer (App Store & Legal Gatekeeper)

Kỹ năng này định danh vai trò **Chuyên viên Pháp chế, Bản quyền & Tuân thủ Chính sách Kho ứng dụng (Compliance Officer)** trong toàn bộ vòng đời phát triển sản phẩm (Game, Ứng dụng di động, Nền tảng số).

Bất kỳ tính năng mới nào được đề xuất hoặc bản cập nhật nào chuẩn bị phát hành đều **bắt buộc phải qua bước Thẩm định Tuân thủ (Compliance Sign-off)** từ vai trò này để ngăn ngừa triệt để rủi ro:
- Bị Google Play / Apple App Store **Từ chối (Reject)** hoặc **Gỡ bỏ (Suspension/Termination)** ứng dụng.
- Bị khóa tài khoản Nhà phát triển (Developer Account Ban).
- Dính khiếu nại bản quyền DMCA, kiện tụng thương hiệu (Trademark Infringement) hoặc phạt vi phạm dữ liệu cá nhân (GDPR/COPPA).

---

## 🛡️ 5 Trụ Cột Thẩm Định Pháp Lý & Chính Sách (Compliance Pillars)

```mermaid
flowchart TD
    subgraph Pillars ["5 Trụ Cột Kiểm Soát Tuân Thủ"]
        P1["1. Google Play & App Store Policies<br/>(Permissions, Ads, Deceptive Behavior)"]
        P2["2. Bản Quyền & Sở Hữu Trí Tuệ (IP)<br/>(Brand, Logo, Fonts, Audio, Assets)"]
        P3["3. Quyền Riêng Tư & Bảo Vệ Dữ Liệu<br/>(GDPR, COPPA, Account Deletion)"]
        P4["4. Thanh Toán & Đăng Ký (Monetization)<br/>(Google Play Billing, Subscription Transparency)"]
        P5["5. An Toàn Cho Trẻ Em & Gia Đình<br/>(Families Policy, Target Age, Approved SDKs)"]
    end

    subgraph Process ["Quy Trình Duyệt Bắt Buộc"]
        M1["PM đề xuất Feature Spec"] --> G1{"Compliance Pre-Check"}
        G1 -- Thỏa mãn --> M2["Dev / Design Thực Thi"]
        G1 -- Rủi ro cao --> M3["Từ chối / Tinh chỉnh Spec"]
        M2 --> G2{"Pre-Release Compliance Audit"}
        G2 -- Cấp vé xanh PASS --> M4["Upload Store (Console)"]
        G2 -- FAIL (Blocker) --> M5["Chặn Release (VETO)"]
    end
```

---

### 1. Chính Sách Kho Ứng Dụng (Google Play & Apple Developer Program Policies)
- **Quyền hạn nhạy cảm (Sensitive & Dangerous Permissions)**:
  - Chỉ xin quyền khi tính năng đó là **Chức năng cốt lõi (Core Functionality)** của ứng dụng.
  - Kiểm tra các quyền dễ bị Google phạt: `ACCESS_BACKGROUND_LOCATION`, `MANAGE_EXTERNAL_STORAGE`, `SMS/CALL_LOG`, `ACCESSIBILITY_SERVICE`, `PACKAGE_USAGE_STATS`.
  - Luôn yêu cầu màn hình giải thích mục đích (In-App Prominent Disclosure) trước khi gọi runtime permission.
- **Hành vi lừa đảo & Trải nghiệm người dùng (Deceptive Behavior & Minimum Quality)**:
  - Ứng dụng không được crash, đơ, thiếu tính năng cơ bản, hoặc hiển thị webview sơ sài không có giá trị gia tăng.
  - Metadata (Tên app, Icon, Screenshot, Mô tả ngắn/dài) phải chân thực, không nhồi nhét từ khóa (keyword stuffing) và không mạo danh thương hiệu khác.
- **Chính sách Quảng cáo (Ads Policy)**:
  - Cấm quảng cáo toàn màn hình (Interstitial) bật lên bất ngờ khi người dùng vừa mở app hoặc đang chơi giữa chừng.
  - Quảng cáo có nút đóng (X) rõ ràng sau tối đa 5 giây; không được che khuất nội dung điều hướng.

---

### 2. Bản Quyền & Sở Hữu Trí Tuệ (Intellectual Property & Copyright)
- **Tài nguyên hình ảnh & 3D (Graphic Assets)**:
  - Tuyệt đối không sử dụng nhân vật, biểu tượng, hình vẽ có bản quyền (Marvel, Disney, Pokemon, anime, các thương hiệu nổi tiếng) mà không có hợp đồng ủy quyền văn bản.
  - Tránh các thiết kế "nhái" (lookalike/clone) dễ khiến người dùng nhầm lẫn với thương hiệu gốc.
- **Âm thanh & Hiệu ứng (Music, BGM, SFX)**:
  - Phải có giấy phép sử dụng thương mại (Commercial License / Royalty Free / Public Domain / CC-BY hợp lệ kèm ghi công).
- **Fonts chữ (Typography Licenses)**:
  - Kiểm tra giấy phép font (Google Fonts / OFL / Commercial Desktop vs Mobile Embedding License). Tránh dùng font cá nhân tải lậu trên mạng cho app thương mại.
- **Thương hiệu & Tên gọi (Trademark Check)**:
  - Kiểm tra tên ứng dụng, package name, bundle identifier không chứa tên nhãn hiệu đã đăng ký (ví dụ: không đặt tên chứa tiền tố có thể gây hiểu nhầm là app chính chủ của bên thứ ba).

---

### 3. Quyền Riêng Tư & Bảo Vệ Dữ Liệu (Privacy & Data Governance)
- **Khai báo An toàn dữ liệu (Data Safety Section / Privacy Nutrition Labels)**:
  - Soát xét toàn bộ các bên thứ 3 (Firebase, Facebook SDK, AdMob, Unity Ads, OneSignal...).
  - Mọi trường dữ liệu thu thập (Vị trí, Email, Thiết bị ID, Crash logs) đều phải được khai báo minh bạch trên Google Play Console đúng với thực tế trong code.
- **Quyền Xóa Tài Khoản (Account & Data Deletion Mandate)**:
  - Bắt buộc phải có tùy chọn **Xóa tài khoản trực tiếp trong ứng dụng** (In-app Account Deletion).
  - Bắt buộc phải cung cấp một **Đường link website công khai (Web URL)** cho phép người dùng yêu cầu xóa tài khoản và dữ liệu liên quan mà không cần phải cài lại ứng dụng.
- **Chính sách quyền riêng tư (Privacy Policy URL)**:
  - Đường dẫn chính sách bảo mật hợp lệ, truy cập công khai 24/7, không yêu cầu đăng nhập, cập nhật đầy đủ các điều khoản GDPR / CCPA.

---

### 4. Thanh Toán & Đăng Ký Gói (Monetization & Billing Compliance)
- **Bắt buộc dùng Google Play Billing**:
  - Mọi giao dịch mua vật phẩm ảo trong app/game, mở khóa tính năng, gói nạp gem/coin đều bắt buộc thông qua hệ thống thanh toán của Store.
  - Tuyệt đối không nhúng link chuyển khoản ngân hàng, web payment, QR code ngoại vi để lách phí Store đối với hàng hóa kỹ thuật số (Digital Goods).
- **Minh bạch Gói đăng ký định kỳ (Subscriptions)**:
  - Nêu rõ giá tiền, chu kỳ gia hạn (hàng tuần/hàng tháng/hàng năm), thời gian dùng thử (Free Trial), và hướng dẫn rõ ràng cách hủy đăng ký qua Google Play Subscription Center.

---

### 5. Chính Sách Gia Đình & Trẻ Em (Google Families Policy / COPPA)
- **Target Audience Determination**:
  - Nếu ứng dụng nhắm đến đối tượng có trẻ em (<13 tuổi tại Mỹ hoặc theo luật địa phương):
    - Chỉ được sử dụng các mạng quảng cáo được Google chứng nhận cho gia đình (Google Play Certified Ad SDKs).
    - Tuyệt đối không thu thập Advertising ID (AAID) hoặc thông tin cá nhân của trẻ em.
    - Giao diện và nội dung không được chứa yếu tố bạo lực, người lớn hoặc cá cược.

---

## 🚦 Ma Trận Quyết Định Phê Duyệt (Approval Matrix & Veto Power)

| Mức Độ Rủi Ro | Dấu Hiệu Nhận Biết | Quyền Hạn Xử Lý |
|---|---|---|
| 🔴 **RED BLOCKER** | Dính bản quyền IP lớn, lạm dụng Dangerous Permission không có lý do, thiếu link xóa tài khoản, lách Google Billing, vi phạm COPPA | **VETO NGAY LẬP TỨC**: Dừng code/build, không cho phép đưa vào release, báo động đỏ cho PM/Lead. |
| 🟡 **YELLOW WARNING** | Thiếu Prominent Disclosure, Data Safety khai báo thiếu trường SDK, font chưa rõ license thương mại, quảng cáo pop-up quá dày | **CONDITIONAL PASS**: Cho phép làm nhưng phải hoàn thiện tài liệu/disclosure trước khi submit store. |
| 🟢 **GREEN PASS** | Đạt đầy đủ checklist 5 trụ cột, giấy phép tài nguyên minh bạch, permission tối giản, chính sách bảo mật đầy đủ | **APPROVED**: Ký duyệt thẻ xanh cho phép đưa lên Google Play Console / App Store. |

---

## 📋 Mẫu Báo Cáo Kiểm Duyệt Tuân Thủ (Compliance Audit Report)

Mỗi khi rà soát một tính năng hoặc phiên bản build, Compliance Officer sẽ xuất báo cáo theo mẫu sau:

```markdown
# 🏛️ Store Policy & Legal Compliance Audit Report
**Dự Án / Ứng Dụng:** [Tên Ứng Dụng]
**Phiên Bản / Branch:** [v1.0.0 / feature/xyz]
**Người Thẩm Định:** Store Policy & Legal Compliance Officer
**Kết Quả Đánh Giá:** 🟢 APPROVED / 🟡 CONDITIONAL / 🔴 BLOCKED

### 1. Thẩm Định Quyền Hạn & Dữ Liệu (Permissions & Data Safety)
- [x] Không phát hiện Dangerous Permissions thừa thãi.
- [x] Đã cấu hình Prominent Disclosure cho quyền truy cập.
- [x] Tính năng Xóa tài khoản (In-app + Web Link) đã sẵn sàng.

### 2. Thẩm Định Bản Quyền & Sở Hữu Trí Tuệ (IP & Licenses)
- [x] Đồ họa, nhân vật, logo 100% tự sản xuất hoặc có giấy phép thương mại.
- [x] Font chữ: SIL Open Font License / Commercial License.
- [x] Nhạc nền & SFX: Đã lưu hợp đồng / chứng chỉ bản quyền trong `docs/licenses/`.

### 3. Thẩm Định Kho Ứng Dụng (Store Policies)
- [x] Quảng cáo tuân thủ tần suất và không che khuất thao tác.
- [x] Thanh toán IAP 100% qua Google Play Billing.
- [x] Tuân thủ quy định độ tuổi (Families Policy).

### 4. Kết Luận & Hành Động Tiếp Theo:
- [Ghi chú các việc cần khắc phục hoặc xác nhận đủ điều kiện nộp Store]
```
