---
name: itg-architect
description: "Dùng khi cần vẽ hoặc cập nhật sơ đồ kiến trúc hệ thống đúng với thực tế đang chạy và đúng chuẩn AWS (icon, tên service, khung Cloud / Region / VPC / Subnet): khảo sát Terraform + compose + tài khoản AWS ở chế độ chỉ đọc, đối chiếu code với thực tế, dựng mô hình sơ đồ, xuất draw.io có icon AWS chính thức, kiểm tra hiển thị và viết tài liệu ARCHITECTURE.md; tuỳ chọn gắn chủ chi phí và số $ lên từng khối để đối chiếu cách tính chi phí. Dùng cả khi người dùng chỉ nói \"vẽ sơ đồ hạ tầng\", \"architecture diagram\", \"tài liệu infra\", \"sơ đồ AWS chuẩn icon\", \"hệ thống đang chạy những gì trên AWS\". Không dùng cho sơ đồ luồng / sequence / ERD giải thích code → archify hoặc tech-doc-generator; không dùng để thiết kế hạ tầng mới hay sửa Terraform."
compatibility: "Python 3.11+, boto3 (chỉ cho bước khảo sát AWS), AWS CLI v2 có profile chỉ đọc. Bước render không cần mạng; bước xem trước dùng viewer.diagrams.net."
metadata:
  version: "1.0.0"
  author: "itgviet"
  last_updated: "2026-11-17"
---

# [SKILL-LEAD-006] ITG Architect: sơ đồ kiến trúc đúng thực tế, chuẩn AWS

Biến "hệ thống đang chạy thật" thành một sơ đồ draw.io dùng icon AWS chính thức, kèm tài liệu `ARCHITECTURE.md`. Mỗi khối trên sơ đồ đều truy được về một tài nguyên thật (ARN / tên / tag) và một nguồn khai báo (Terraform root, hoặc ghi rõ "tạo tay").

Nguồn: phiên #8882 (InsightScanX, 17/11/2026): dựng sơ đồ theo chủ chi phí cho 1 tài khoản / 3 môi trường, đối chiếu với spec quản lý chi phí.

## Gotchas

- **Terraform không phải sự thật.** Ở #8882 có máy và role tạo tay ngoài Terraform: role `dev-onetech-insightscanx-role`, các máy SG. Còn có trường hợp **Django stage và dev chạy chung một EC2**, chỉ phát hiện khi `describe-instances` + đọc instance profile. Luôn đối chiếu với khảo sát thật (bước 3) trước khi vẽ.
- **Tag không đồng nhất.** `Environment` có 8 kiểu giá trị (`prod`, `production`, `production-legacy`, `staging`, `dev/stage`…). Gán môi trường theo quy tắc tên (tag `Name` / naming policy `isx-<env>-*`) + bucket, không đọc thẳng tag `Environment`. Tài nguyên không khớp quy tắc nào thì ghi "chưa rõ chủ", không đoán.
- **Linked account:** tag `Name` có thể đã được payer bật làm cost allocation tag còn `Environment` thì chưa, và linked account **không tự bật được**. Muốn có số $ theo khối thì nhóm Cost Explorer theo `Name`.
- **draw.io:** nhãn có `html=1` thì xuống dòng bằng `<br>`, `\n` không có tác dụng. Tên `resIcon` phải đúng chính xác (`sqs`, `ecr`; **không phải** `simple_queue_service`, `elastic_container_registry`). Sai tên thì icon thành ô màu trơn mà không báo lỗi. Chỉ dùng tên trong [references/drawio-aws4.md](references/drawio-aws4.md); `scripts/drawio_render.py` từ chối service lạ.
- **Phiên `aws login` hết hạn giữa chừng** (gặp ở #8882). Khi gặp thì dừng và nhờ người dùng chạy `aws login`, đừng thử profile khác. Cho boto3 dùng phiên này: `eval "$(aws configure export-credentials --profile <p> --format env)"; unset AWS_PROFILE`.
- **AWS CLI lỗi `charmap` khi in tag có ký tự Nhật/Việt** trên Windows. Dùng `python -X utf8 scripts/aws_inventory.py` thay vì CLI.
- **Git Bash đôi khi làm hỏng heredoc Python** (`unexpected EOF`). Viết script ra file rồi chạy.
- **Số $ trên sơ đồ:** dùng **AmortizedCost** (phí Savings Plan đã được chia vào máy). Không cộng thêm phí cam kết Savings Plan vào khối "cố định", vì như vậy là đếm hai lần (lỗi đã gặp ở #8882). Đọc [references/cost-overlay.md](references/cost-overlay.md) trước khi ghi $ lên sơ đồ.
- **Chỉ đọc.** Khảo sát chỉ dùng `describe` / `list` / `get`; không tạo, sửa hay xoá tài nguyên. Cost Explorer tốn $0,01/request: báo số request trước khi chạy.
- **Sơ đồ chia sẻ ra ngoài** (khách, đối tác): che account ID và ARN đầy đủ, không ghi IP / hostname nội bộ.

## Quy trình

Progress:
- [ ] 1. **Chốt mục đích và mức sơ đồ:** hỏi người dùng (1–3 câu, mỗi câu kèm phương án khuyên dùng):
  - người đọc là ai: dev / ops / sếp / khách;
  - mục đích: onboarding / đối chiếu chi phí / review bảo mật;
  - cần mức nào. Mặc định **2 mức**:
    - **L1** toàn tài khoản: khung theo môi trường + dùng chung + ngoài phạm vi;
    - **L2** mỗi môi trường một sơ đồ (mạng, compute, luồng xử lý, lưu trữ, edge).
- [ ] 2. **Gom nguồn khai báo:** liệt kê Terraform root (`terraform/*/`, `stage-*`, `services/*`), compose (`deploy/compose/*.yml`), settings ứng dụng, tài liệu cũ (`INVENTORY.md`, `*-summary.md`). Ghi lại Terraform root nào quản lý cái gì.
- [ ] 3. **Khảo sát thực tế (chỉ đọc):**
  - `python -X utf8 scripts/aws_inventory.py --profile <p> --regions ap-northeast-1,ap-southeast-1 --output inventory.json` (`--help` để xem tuỳ chọn).
  - Cần số $ theo khối thì thêm `--costs YYYY-MM` (1 request Cost Explorer, nhóm theo tag `Name`).
  - Hết phiên đăng nhập → dừng, nhờ người dùng `aws login`.
- [ ] 4. **Đối chiếu khai báo và thực tế:**
  - Lập bảng tài nguyên theo [assets/ARCHITECTURE.template.md](assets/ARCHITECTURE.template.md) §4. Mỗi dòng gồm: tài nguyên, loại, vùng, tag `Name` / `Environment`, **chủ** (môi trường / dùng chung / ngoài phạm vi), $/tháng, nguồn (Terraform root hoặc "tạo tay").
  - Liệt kê **khác biệt**: tài nguyên tạo tay, thiếu tag, tag sai, máy dùng chung nhiều môi trường. Đây là phần giá trị nhất của tài liệu.
- [ ] 5. **Dựng mô hình sơ đồ** (`model.json`, theo [assets/model.example.json](assets/model.example.json)): nhóm (aws_cloud → region → vpc → subnet / box), node (`service` lấy từ bảng icon), cạnh (nhãn luồng; `kind: cost` cho luồng có tính phí như truyền liên vùng). Mỗi node có `ref` trỏ về dòng trong bảng tài nguyên. Không vẽ tài nguyên không có trong bảng.
- [ ] 6. **Render:**
  - Mặc định: `python scripts/drawio_render.py model.json --out <tên>.drawio --url-file viewer_url.txt`.
  - Nếu skill **`deploy-on-aws:aws-architecture-diagram`** đã được cài (plugin AWS chính thức, xem mục Tham khảo) và người dùng muốn bố cục tự động, đưa bảng tài nguyên + `model.json` làm đầu vào cho skill đó. Không chép nội dung skill đó vào đây.
- [ ] 7. **Kiểm tra hiển thị (vòng lặp):**
  - Mở URL trong `viewer_url.txt` bằng trình duyệt, chụp ảnh và zom từng khung.
  - Kiểm: không có icon nào thành ô trơn; nhãn không đè nhau; mọi node có trong bảng tài nguyên; mọi cạnh có nhãn; tổng $ các khung L1 = tổng tài khoản (± 0,01).
  - Sai → sửa `model.json` → render lại → kiểm lại tới khi đạt.
- [ ] 8. **Viết `docs/ARCHITECTURE.md`** trong repo hạ tầng theo template, nhúng ảnh PNG / SVG xuất từ draw.io, link file `.drawio` nguồn. Ghi ngày khảo sát và profile / vùng đã dùng. Báo cáo cho người dùng: các file đã tạo, danh sách khác biệt, phần chưa kiểm được. Không commit thay người dùng.

## Đầu ra

```text
<repo-hạ-tầng>/docs/ARCHITECTURE.md          tài liệu (template assets/ARCHITECTURE.template.md)
<repo-hạ-tầng>/docs/architecture/model.json   mô hình sơ đồ (nguồn để render lại)
<repo-hạ-tầng>/docs/architecture/L1-account.drawio, L2-<env>.drawio
<repo-hạ-tầng>/docs/architecture/*.png        ảnh xuất từ draw.io để nhúng
(inventory.json để ngoài repo nếu có account ID / ARN; chỉ đưa vào repo bản đã che)
```

## Tham khảo

- Đọc [references/drawio-aws4.md](references/drawio-aws4.md) khi thêm service mới vào mô hình, hoặc khi icon hiển thị sai.
- Đọc [references/cost-overlay.md](references/cost-overlay.md) khi sơ đồ cần ghi chủ chi phí / số $.
- Skill bên thứ 3, **chỉ liên kết, không sao chép**:
  - `deploy-on-aws:aws-architecture-diagram`: plugin AWS chính thức (awslabs), tạo sơ đồ AWS dạng draw.io đã kiểm. Nguồn: <https://github.com/awslabs/agent-plugins/tree/main/plugins/deploy-on-aws>. Cài qua thư mục plugin của Claude ("Anthropic Directory" → `deploy-on-aws`).
  - `archify` (đã vendored trong kho): dùng cho sơ đồ giải thích dạng HTML tương tác (luồng, sequence, state). Không dùng icon AWS chính thức.
  - `aws-billing-and-cost-management` (vendored): khi cần phân tích chi phí sâu hơn mức gắn số lên sơ đồ.
- Liên quan trong ITGViet: `tech-doc-generator` (tài liệu codebase tổng thể), `production-safety-guardrail` (mọi thao tác ghi lên tài khoản thật).
