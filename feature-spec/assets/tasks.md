# Execution Task Plan: [Tên tính năng]

## Tracking Table
| Task ID | Tên task | Trạng thái | Checkpoint | Scope Lock (files) |
| :--- | :--- | :--- | :--- | :--- |
| T-01 | Setup schema & entities | ⏳ pending | Checkpoint 1 | `src/models/*` |
| T-02 | Implement API service | ⏳ pending | Checkpoint 1 | `src/services/*` |
| T-03 | Build UI screen & i18n | ⏳ pending | Checkpoint 2 | `src/ui/*`, `locales/*` |
| T-04 | Integration test | ⏳ pending | Checkpoint 3 | `tests/*` |

## Ma trận truy vết kiểm thử
| AC | Task | Test / bằng chứng |
| :--- | :--- | :--- |
| AC-01 | T-02 | `tests/...` |

## Execution rules & commit strategy
- Làm theo thứ tự checkpoint; dừng báo cáo ở mỗi checkpoint.
- 1 task = 1 commit logic (`feat(scope): ...`).
- Chỉ sửa file trong Scope Lock; phát sinh file mới thì cập nhật spec trước.
