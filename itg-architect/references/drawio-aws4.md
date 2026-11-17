# draw.io: bộ icon AWS (mxgraph.aws4)

Đọc khi thêm service mới vào `model.json` hoặc khi icon hiển thị thành ô màu trơn.

## Ba kiểu shape

| Kiểu | Style chính | Dùng cho |
|---|---|---|
| **Nhóm** (group) | `shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.<group>;container=1;` | AWS Cloud, Region, VPC, Subnet |
| **Resource icon** (ô vuông màu + glyph trắng) | `shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.<res>;fillColor=<màu nhóm>;strokeColor=#ffffff;` | Service (EC2, S3, SQS…) |
| **Icon tài nguyên con** (glyph không nền) | `shape=mxgraph.aws4.<shape>;fillColor=<màu>;strokeColor=none;` | NAT, endpoint, users… |

## Nhóm

| `type` trong model | grIcon | strokeColor | fillColor | Ghi chú |
|---|---|---|---|---|
| `aws_cloud` | `group_aws_cloud_alt` | `#232F3E` | none | |
| `region` | `group_region` | `#00A4A6` | none | `dashed=1`, chữ `#147EBA` |
| `vpc` | `group_vpc2` | `#8C4FFF` | none | chữ `#AAB7B8` |
| `subnet_private` | `group_security_group` | `#00A4A6` | `#E6F6F7` | (khung xanh nhạt) |
| `subnet_public` | `group_security_group` | `#7AA116` | `#F2F6E8` | |
| `box` | (rounded rect) | tuỳ | tuỳ | khung logic: "Global", "Dùng chung tài khoản" |

## Màu theo nhóm service (chuẩn AWS 2021+)

Compute `#ED7100` · Storage `#7AA116` · Database `#C925D1` · Networking `#8C4FFF` · App integration `#E7157B` · Security `#DD344C` · Management `#E7157B` · ML/AI `#01A88D` · Dev tools `#C925D1`.

## Bảng service đã dùng

✅ = đã render kiểm trên viewer.diagrams.net (17–18/11/2026). ◻ = tên theo thư viện aws4, **chưa render kiểm**: phải nhìn ảnh ở bước 7 trước khi tin.

| `service` | Kiểu | Tên | Màu | |
|---|---|---|---|---|
| ec2 | resIcon | `ec2` | compute | ✅ |
| batch | resIcon | `batch` | compute | ✅ |
| ecr | resIcon | `ecr` | compute | ✅ (không phải `elastic_container_registry`) |
| lambda | resIcon | `lambda` | compute | ✅ |
| ecs | resIcon | `ecs` | compute | ◻ |
| fargate | resIcon | `fargate` | compute | ◻ |
| ebs | resIcon | `elastic_block_store` | storage | ✅ |
| s3 | resIcon | `s3` | storage | ✅ |
| efs | resIcon | `elastic_file_system` | storage | ◻ |
| rds | resIcon | `rds` | database | ◻ |
| dynamodb | resIcon | `dynamodb` | database | ✅ |
| elasticache | resIcon | `elasticache` | database | ◻ |
| sqs | resIcon | `sqs` | integration | ✅ (không phải `simple_queue_service`) |
| sns | resIcon | `sns` | integration | ◻ |
| eventbridge | resIcon | `eventbridge` | integration | ✅ |
| step_functions | resIcon | `step_functions` | integration | ◻ |
| api_gateway | resIcon | `api_gateway` | networking | ✅ |
| cloudfront | resIcon | `cloudfront` | networking | ✅ |
| route_53 | resIcon | `route_53` | networking | ✅ |
| nat | shape | `nat_gateway` | networking | ✅ |
| vpc_endpoint | shape | `endpoints` | networking | ✅ |
| waf | resIcon | `waf` | security | ✅ |
| guardduty | resIcon | `guardduty` | security | ✅ |
| kms | resIcon | `key_management_service` | security | ✅ |
| secrets_manager | resIcon | `secrets_manager` | security | ◻ |
| iam | resIcon | `identity_and_access_management` | security | ◻ |
| cognito | resIcon | `cognito` | security | ✅ |
| config | resIcon | `config` | management | ✅ |
| cloudwatch | resIcon | `cloudwatch_2` | management | ✅ |
| systems_manager | resIcon | `systems_manager` | management | ◻ |
| cost_explorer | resIcon | `cost_explorer` | storage (xanh lá) | ✅ |
| bedrock | resIcon | `bedrock` | ml | ✅ |
| codebuild | resIcon | `codebuild` | devtools | ✅ |
| users | shape | `users` | `#232F3E` | ✅ |

Thêm service mới: thêm vào bảng này **và** vào `SERVICES` trong `scripts/drawio_render.py`, render thử, rồi mới đổi ◻ thành ✅.

## Nhãn và URL xem trước

- `html=1`: xuống dòng bằng `<br>` (script tự đổi `\n` thành `<br>`).
- URL xem trước: `https://viewer.diagrams.net/?lightbox=1&nav=1#R<payload>`, với `payload = base64(deflateRaw(encodeURIComponent(xml)))` rồi URL-encode. Phần sau `#` chỉ xử lý trong trình duyệt, không gửi lên máy chủ. Nếu sơ đồ có thông tin nhạy cảm thì vẫn nên mở bằng draw.io desktop thay vì link.
