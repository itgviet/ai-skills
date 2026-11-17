# Gắn chủ chi phí và số $ lên sơ đồ

Đọc khi sơ đồ phải ghi "khối này thuộc ai, tốn bao nhiêu" (đối chiếu spec quản lý chi phí, review tối ưu).

## Chủ chi phí (owner)

Mỗi khối thuộc đúng một chủ:

| Chủ | Cách nhận | Ví dụ #8882 |
|---|---|---|
| môi trường (`production` / `stage` / `dev`) | tag `Name` theo naming policy (`isx-prod-*`, `isx-stage-*`), bucket của môi trường | VPC isx-prod, Batch stage |
| nhóm dùng chung (`pool:<key>`) + danh sách môi trường dùng | tài nguyên phục vụ nhiều môi trường | máy dev-stage chung (stage + dev); GuardDuty / Config / CloudWatch (cả tài khoản) |
| ngoài phạm vi (`account_only:<item>`) | hạ tầng cũ, sản phẩm khác, Savings Plan chưa dùng | máy SG cũ, WordPress |

Tài nguyên không khớp quy tắc nào → ghi "**chưa rõ chủ**" và đưa vào danh sách khác biệt. Không đoán theo loại máy: ở #8882, stage Batch cũng dùng g6 nên đoán theo loại máy là tính nhầm vào khách.

## Số $

- Lấy **AmortizedCost** theo tag `Name` × `USAGE_TYPE` (dòng có tag) và `SERVICE` × `USAGE_TYPE` lọc `Name ABSENT` (dòng không tag). Hai lời gọi này không chồng nhau, cộng lại đúng hoá đơn.
- S3 không có tag `Name` theo dòng chi phí: chia theo GB của từng bucket (CloudWatch `BucketSizeBytes`).
- Tổng tài khoản = Σ amortized + **Savings Plan chưa dùng** (unblended − amortized) = Σ unblended.
- **Không** cộng phí cam kết Savings Plan vào "cố định" khi đã dùng amortized, vì phần đã dùng của nó nằm sẵn trong chi phí các máy. Chỉ ghi chú "Savings Plan $X/giờ tới <ngày>, đã nằm trong chi phí máy".
- Ghi tháng và ngày đo trên sơ đồ ("$ amortized tháng 10/2026, đo 17/11"). Cost Explorer tính theo ngày UTC.
- Kiểm: Σ $ các khung L1 = tổng tài khoản (± 0,01). Không khớp → tìm dòng rơi ngoài khung trước khi xuất bản.

## Phí truyền dữ liệu

Luồng liên vùng (`APN1-APS1-*`) hoặc ra Internet có phí: vẽ cạnh `kind: cost` (nét đứt đỏ) và ghi $ nếu đo được.
