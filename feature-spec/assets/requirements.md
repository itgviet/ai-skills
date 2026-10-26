# Requirements Spec: [Tên tính năng]

## 1. Bối cảnh & Mục tiêu (PM)
- **Bối cảnh:** [vấn đề kinh doanh / kỹ thuật cần giải quyết]
- **Vai trò người dùng:** [ai dùng tính năng này]
- **Mục tiêu:**
  - [ ] Goal 1
- **Ngoài phạm vi (Out of Scope):**
  - Item 1 — [lý do]

## 2. Repo & module bị ảnh hưởng
- **Repo/Package A:** [thay đổi]
- **Cross-repo dependencies:** [shared types, API contract...]

## 3. Thuật ngữ
- **Term A:** [định nghĩa]

## 4. Yêu cầu chức năng (Dev)
- **FR-01:** Hệ thống SHALL [hành vi cụ thể]

## 5. Yêu cầu phi chức năng
- **NFR-01:** [hiệu năng / bảo mật / offline...]

## 6. UI/UX & Localization (Designer)
- **UX-01:** Màn hình & luồng bị ảnh hưởng (UI ID theo RULE-UI-002: `screen-*`, `btn-*`, `input-*`...).
- **UX-02:** Trạng thái: Default, Loading, Empty, Error, Disabled, Offline.
- **L10N-01:** Mọi text hiển thị đi qua hệ thống localization, không hardcode.

## 7. Acceptance Criteria (QA)
- **AC-01:** Given [bối cảnh], When [hành động], Then [kết quả]
- **AC-UI-01:** Given [trạng thái màn hình], When [render], Then [text & UI đúng theo i18n key]
