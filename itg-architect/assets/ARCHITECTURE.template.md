# <Hệ thống>: Kiến trúc hạ tầng

- Ngày khảo sát: <YYYY-MM-DD> · Profile / vùng: <profile chỉ đọc>, <regions> · Người lập: <tên>
- Nguồn khai báo: <Terraform roots>, <compose>, <tài liệu khác>
- Sơ đồ nguồn: `docs/architecture/*.drawio` (render từ `model.json` bằng skill itg-architect)

## 1. Tổng quan

<1 đoạn: số tài khoản AWS (linked / payer), vùng, môi trường, phần ngoài phạm vi. Tổng chi phí tháng gần nhất nếu có.>

## 2. Sơ đồ L1: toàn tài khoản

![L1](architecture/L1-account.png)

<Mỗi khung = một chủ: môi trường / dùng chung / ngoài phạm vi; ghi $/tháng.>

## 3. Sơ đồ L2: từng môi trường

### 3.1 <Production>

![L2 production](architecture/L2-production.png)

<Mạng (VPC, subnet, NAT, endpoint) · compute · luồng xử lý · lưu trữ · edge (CloudFront / WAF).>

### 3.2 <Stage> · 3.3 <Dev>

## 4. Bảng tài nguyên

| Tài nguyên | Loại | Vùng | Tag Name | Tag Environment | Chủ | $/tháng | Nguồn khai báo |
|---|---|---|---|---|---|---|---|
| <isx-prod-app> | EC2 t3.medium | ap-northeast-1 | isx-prod-app | prod | production | 23,21 | terraform/ec2.tf |

## 5. Luồng nghiệp vụ → chi phí

| Bước | Tài nguyên | Chủ / nhóm chi phí |
|---|---|---|
| <upload scan> | <S3 bucket môi trường> | <client_use / storage> |

## 6. IAM và quyền

| Role / user | Gắn vào | Môi trường | Quyền đáng chú ý | Nguồn |
|---|---|---|---|---|

## 7. Khác biệt giữa khai báo và thực tế · việc cần làm

| # | Khác biệt | Ảnh hưởng | Việc cần làm | Phụ trách |
|---|---|---|---|---|
| 1 | <tài nguyên tạo tay / thiếu tag / dùng chung nhiều môi trường> | | | |

## 8. Cách cập nhật tài liệu này

Chạy lại skill `itg-architect` (khảo sát → đối chiếu → sửa `model.json` → render → kiểm ảnh), cập nhật ngày khảo sát ở đầu file.
