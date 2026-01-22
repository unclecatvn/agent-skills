---
name: odoo-code-review
description: Review Odoo code for correctness, security, performance, and Odoo 18 standards. Use when reviewing Odoo modules, diffs, or pull requests; produce a scored report with weighted criteria.
---

# Odoo Code Review (VN)

## Mục tiêu

Đánh giá thay đổi Odoo theo tiêu chí rõ ràng, phát hiện rủi ro, và chấm điểm
theo thang điểm có trọng số.

## Bắt buộc trước khi review

- Đọc `docs/skills/odoo/18.0/SKILL.md` và các guide liên quan nếu có thay đổi
  về model, field, view, controller, bảo mật, performance.
- Xác định phạm vi: module, file, và bối cảnh thay đổi.

## Quy trình review

1. **Scope**: xác định phạm vi thay đổi, mục tiêu, và rủi ro chính.
2. **Correctness & Bugs**: logic, edge cases, dữ liệu rỗng, quy trình.
3. **Odoo 18 Standards**: patterns đúng/anti-patterns.
4. **Security**: ACL, record rules, sudo, data exposure.
5. **Performance**: N+1, batch operations, read_group, prefetch.
6. **Testing**: test coverage, test plan, thiếu test.

## Checklist Odoo 18 (rút gọn)

- `Many2one` có `ondelete`
- `Monetary` có `currency_field`
- View list dùng `<list>` (không dùng `<tree>`)
- Hạn chế search trong loop (N+1)
- `@api.ondelete` thay cho override `unlink()` khi cần chặn xóa
- `search_read` khi cần dict output
- `read_group` cho aggregate

## Thang điểm (Weighted 1–10)

**Tiêu chí** (điểm 1–10):

- **Quality & Best Practices** (30%)
- **Potential Bugs / Correctness** (30%)
- **Performance** (20%)
- **Security** (20%)

**Cách tính điểm tổng**:

```
total = 0.3*quality + 0.3*bugs + 0.2*performance + 0.2*security
```

**Anchor chấm điểm**:

- **9–10**: xuất sắc, không có rủi ro đáng kể
- **7–8**: tốt, có vài vấn đề nhỏ
- **5–6**: trung bình, có rủi ro rõ ràng cần xử lý
- **3–4**: kém, có lỗi nghiêm trọng hoặc dễ gây regression
- **1–2**: rất kém, không thể merge

## Format báo cáo (bắt buộc)

```
## Kết luận nhanh
- [1–2 câu tóm tắt chính]

## Điểm tổng
- Tổng điểm: X.X/10
- Công thức: 0.3*Q + 0.3*B + 0.2*P + 0.2*S

## Điểm theo tiêu chí
- Quality & Best Practices: X/10 — [lý do ngắn]
- Potential Bugs / Correctness: X/10 — [lý do ngắn]
- Performance: X/10 — [lý do ngắn]
- Security: X/10 — [lý do ngắn]

## Phát hiện quan trọng (ưu tiên cao → thấp)
- [Mức độ] Mô tả ngắn + hệ quả + gợi ý fix
- Trích dẫn code: `path/file.py` (nêu đoạn mã nếu cần)

## Khuyến nghị
- [Cải thiện cụ thể, rõ ràng]

## Testing
- Đã chạy: [nếu có, nêu lệnh]
- Thiếu: [test còn thiếu hoặc chưa chạy]
```

## Quy tắc phản hồi

- Ưu tiên phát hiện lỗi và rủi ro trước, rồi mới đến đề xuất.
- Nếu không có vấn đề đáng kể, nêu rõ “Không có findings”.
- Trích dẫn đúng file và đoạn mã khi cần thiết.
- Ghi rõ giả định nếu thiếu thông tin (không suy đoán).
