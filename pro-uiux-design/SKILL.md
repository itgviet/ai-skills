---
name: pro-uiux-design
version: 3.0.0
author: itgviet
last_updated: 2026-09-27
description: >-
  Universal professional human-centered UI/UX design standards and execution protocol.
  Enforces modern design tokens, platform-native design languages (Apple HIG, Microsoft Fluent, Material 3),
  anti-AI-cliché aesthetics, strict SVG iconography rules, optical hierarchy, micro-interactions, and accessible responsive layouts.
---

# SKILL: Professional UI/UX Design System & Execution Protocol (`pro-uiux-design`)

## 🎯 Mục đích & Triết lý Thiết kế

Skill **`pro-uiux-design`** (v3.0.0) quy định bộ tiêu chuẩn giao diện người dùng (UI) và trải nghiệm người dùng (UX) chuẩn sản phẩm thương mại thế giới. Triết lý cốt lõi gồm 5 trụ cột:

1. **Anti-AI-Cliché & Anti-Emoji Aesthetics:** CẤM dùng Emoji hệ thống (`⚡`, `📁`, `🖥️`, `📤`, `📄`) làm icon chính. BẮT BUỘC dùng hệ thống **Vector SVG Icons** đồng bộ (Lucide / Feather / SF Symbols / Heroicons).
2. **Human-Centered & Platform-Native:** Tôn trọng đặc tính của từng nền tảng (Apple Human Interface Guidelines trên iOS/macOS, Microsoft Fluent Design trên Windows 11, Material 3 trên Android).
3. **Precision Iconography & Geometry:** Nét stroke icon mỏng tinh tế (1.5px - 2.0px), viewBox 24x24px, bo góc stroke mượt mà (`stroke-linecap="round"`).
4. **Precision Information Density:** Bố cục chặt chẽ, chuẩn hóa 8pt grid system.
5. **Resilient Multi-State Engineering:** Mỗi component đều có đủ 5 trạng thái bắt buộc: `Default`, `Hover/Active`, `Shimmer/Loading`, `Empty`, và `Error/Retry`.

---

## 🛑 1. Ma Trận Đối Chiếu: AI-Cliché UI vs. Professional Human UI

| Tiêu chí | ❌ AI-Cliché UI (CẤN TRÁNH TUYỆT ĐỐI) | ✅ Professional Human UI (TIÊU CHUẨN BẮT BUỘC) |
| :--- | :--- | :--- |
| **Iconography (Biểu tượng)** | Dùng Unicode Emoji ngẫu nhiên (`⚡`, `📁`, `🖥️`, `📤`, `📄`). Icon to nhỏ không đồng nhất. | **Crisp Vector SVG System:** SVG monochrome stroke 1.5px/2px (Lucide/SF Symbols), viewBox 24x24px, container 36px/40px chuẩn hóa. |
| **Bảng màu (Palette)** | Dark mode đen xì (`#000000`), chữ hồng/xanh neon phát sáng tràn lan. | **Semantic Slate & Zinc Colors:** Base Surface `#0B0F17` / `#151D2A`, Accent Blue `#3B82F6` tinh tế, độ tương phản WCAG 2.1 AA (≥ 4.5:1). |
| **Độ nổi & Layering** | Drop-shadow đen sì mờ đục (`0 20px 40px rgba(0,0,0,0.5)`), viền phát sáng chói mắt. | **Subtle Borders & Layering:** Viền mỏng 1px (`rgba(255,255,255,0.08)` hoặc `#E2E8F0`), Ambient Shadow cực mỏng (`0 1px 3px rgba(0,0,0,0.05)`). |
| **Typography** | Font size chọn đại, thiếu letter-spacing, không có nhịp điệu dòng (line-height). | **Optical Typographic Hierarchy:** Tỉ lệ Major Third (1.25), Tight tracking (`-0.02em`) cho Title, Line-height 1.2 cho Title và 1.5 cho Body text. |
| **Spacing & Grid** | Paddings ngẫu nhiên (11px, 13px), căn giữa tất cả mọi thứ (Center text overload). | **Strict 8pt Grid System:** Khoảng cách chuẩn hóa 4px, 8px, 12px, 16px, 24px, 32px, 48px. Lùi dòng theo hướng đọc tự nhiên (F/Z pattern). |
| **Bo góc (Geometry)** | Bo góc quá đà (`border-radius: 30px`) gây lãng phí diện tích hiển thị. | **Modern Geometry:** Corner Radius vừa vặn (6px - 8px cho Button/Input, 10px - 14px cho Card/Modal, 999px chỉ dùng cho Pill/Badge). |

---

## 🎨 2. Quy Chuẩn SVG Iconography (Vector Icon Standards)

### 2.1 Quy tắc Icon (Icon System Rules)
1. **Không Dùng Emoji:** Tất cả emoji trên giao diện web và app đều phải thay thế bằng icon Vector SVG stroke chuẩn.
2. **Stroke Width & Cap:** Tất cả SVG icons sử dụng `stroke-width="2"` hoặc `1.5`, `stroke-linecap="round"` và `stroke-linejoin="round"`.
3. **Container Padding:** Icon được bọc trong Container hình vuông 36x36px hoặc 40x40px với background tinted 10% primary opacity (`rgba(59, 130, 246, 0.1)`).

### 2.2 Thư viện SVG Standard Snippets
```html
<!-- Lightning / Power Icon -->
<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
</svg>

<!-- Folder Sync Icon -->
<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
</svg>

<!-- Screen Share Monitor Icon -->
<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
  <line x1="8" y1="21" x2="16" y2="21"></line>
  <line x1="12" y1="17" x2="12" y2="21"></line>
</svg>

<!-- Upload Tray Icon -->
<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
  <polyline points="17 8 12 3 7 8"></polyline>
  <line x1="12" y1="3" x2="12" y2="15"></line>
</svg>
```

---

## 🏛️ 3. Hệ Thống Token Thiết Kế (Design System Tokens)

### 3.1 Semantic Color Palette Tokens

```dart
abstract class AppDesignTokens {
  // --- DARK MODE SURFACES ---
  static const Color darkBaseBackground    = Color(0xFF0B0F17); // Deep Slate
  static const Color darkCardSurface       = Color(0xFF151D2A); // Elevated Surface
  static const Color darkInteractiveHover  = Color(0xFF1E293B); // Hover Surface
  static const Color darkSubtleBorder      = Color(0x14FFFFFF); // 8% White Stroke

  // --- LIGHT MODE SURFACES ---
  static const Color lightBaseBackground   = Color(0xFFF8FAFC); // Cool Off-White
  static const Color lightCardSurface      = Color(0xFFFFFFFF); // Pure White Panel
  static const Color lightInteractiveHover = Color(0xFFF1F5F9); // Light Gray Hover
  static const Color lightSubtleBorder     = Color(0xFFE2E8F0); // Crisp Light Border

  // --- BRAND ACCENTS ---
  static const Color primaryBlue           = Color(0xFF3B82F6); // Electric Royal Blue
  static const Color primaryBlueHover      = Color(0xFF2563EB); // Darker Blue
  static const Color primaryIndigo         = Color(0xFF6366F1); // Indigo Accent

  // --- FEEDBACK & STATUS TOKENS ---
  static const Color statusSuccess         = Color(0xFF10B981); // Emerald Green
  static const Color statusWarning         = Color(0xFFF59E0B); // Amber Yellow
  static const Color statusError           = Color(0xFFEF4444); // Rose Red
}
```

---

## 📋 4. Quy Trình Kiểm Thử Tự Động UI/UX (Self-Audit Protocol)

Trước khi nghiệm thu bất kỳ giao diện nào do AI sinh ra, AI **PHẢI TỰ CHẠY CHECKLIST 10 ĐIỂM**:

- [ ] **1. Anti-Emoji Check:** ĐÃ THAY THẾ toàn bộ Emoji unicode bằng Vector SVG stroke icons chuẩn.
- [ ] **2. Anti-AI Colors:** Không có gradient chói mắt bừa bãi, không có shadow đen mờ đục đè lên đĩa.
- [ ] **3. Semantic Colors:** Màu nền, card surface, text color và icon color tuân thủ đúng bảng màu Semantic Tokens.
- [ ] **4. Contrast Ratio:** Chữ và nền đạt độ tương phản tối thiểu **4.5:1** (Chuẩn WCAG 2.1 AA).
- [ ] **5. Grid & Padding:** Tất cả paddings, margins và gaps đều chia hết cho **4px/8px**.
- [ ] **6. Typography Scale:** Text size tuân thủ bảng Typographic Hierarchy.
- [ ] **7. 5-State Support:** Component đã xử lý đủ 5 trạng thái (`Default`, `Hover/Active`, `Shimmer/Loading`, `Empty`, `Error`).
- [ ] **8. Touch Target:** Nút bấm trên mobile đạt tối thiểu 44x44px.
- [ ] **9. Hover Feedback:** Nút bấm và card có hiệu ứng hover và press scale 0.98 mượt mà.
- [ ] **10. Localization Ready:** Không hardcode text hiển thị, 100% đi qua i18n localization keys.
