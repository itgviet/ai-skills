# Design tokens & SVG icon snippets mặc định

Đọc khi dự án **chưa có** design system riêng. Dự án đã có token/icon thì dùng của dự án.

## Icon SVG

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

## Token màu (Flutter/Dart)

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
