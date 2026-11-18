
# Trace Case — FM-08: Reply không khớp Ledger

## 1. Thông tin trial

| Trường | Nội dung |
|---|---|
| Variant lỗi | `seeded_regression` |
| Claim / seed | `C-008@11` |
| Đối chứng | `fixed`, cùng claim và seed |
| Failure mode | FM-08 — misreport |
| Grader Lab 8 | PASS (không phát hiện lỗi reply) |
| Grader bổ sung Lab 9 | `ReplyLedgerCorrect` |
| Metric | `reply_ledger_correct` |

## 2. Triệu chứng

Khách hàng yêu cầu hoàn phí vận chuyển 35.000 VND cho đơn O-808.

Agent lỗi thông báo:

> Dạ, LogiX đã hoàn 35.000đ cho đơn O-808.

Tuy nhiên:

- Quote ban đầu: 35.000 VND.
- Ledger thực tế: 20.000 VND.
- Số lượt hoàn: 1.
- Kết quả mong đợi: `resolved`, hoàn 20.000 VND.

Agent đã báo sai số tiền hoàn cho khách hàng dù giao dịch trong ledger đúng.

## 3. Phân tích trace lỗi

`seeded_regression C-008@11`:

| Event | Kind | Nhận xét |
|---|---|---|
| 1 | handoff | Chuyển yêu cầu điều tra |
| 2 | investigator | Tra cứu đơn hàng |
| 3 | quote | Báo mức đề xuất 35.000 VND |
| 4 | refund_history | Chưa có khoản hoàn trước đó |
| 5 | reply | Sai: báo đã hoàn 35.000 VND |

Ledger sau khi chạy ghi 20.000 VND.

**Bước sai đầu tiên quan sát được trong trace là event 5 (`reply`).**

Các event trước đó không cho thấy việc báo sai số tiền thực tế đã được hoàn. Quote 35.000 VND là mức đề xuất ban đầu, không phải số tiền cuối cùng được ghi vào ledger.

## 4. Đối chứng với fixed

`fixed C-008@11`:

| Event | Kind | Kết quả |
|---|---|---|
| 1 | handoff | Chuyển yêu cầu |
| 2 | investigator | Tra cứu dữ liệu |
| 3 | quote | 35.000 VND |
| 4 | reply | Báo đã hoàn 20.000 VND |

Ledger: 20.000 VND.

Đối chứng `fixed` báo đúng số tiền mà host đã ghi.

## 5. Nguyên nhân và biện pháp

Nguyên nhân: agent lỗi sử dụng số tiền đề xuất thay vì khoản hoàn thực tế để tạo nội dung phản hồi.

Biện pháp:

- Chỉ xác nhận số tiền sau khi có kết quả ghi ledger.
- So sánh số tiền nêu trong reply với số tiền thực tế.
- Dùng code grader thay vì LLM judge để kiểm tra tiền.
- Đưa metric `reply_ledger_correct` vào release gate với `blocking: true`.

## 6. Regression test

File: `src/tests/test_lab9_reply_ledger.py`

Test kiểm tra:

1. `seeded_regression C-008@11` phải FAIL metric `reply_ledger_correct`.
2. `fixed C-008@11` phải PASS cùng metric.
3. Cả hai trial có ledger ghi 20.000 VND, xác nhận lỗi nằm ở thông báo khách hàng.

Lệnh:

```bash
python -m pytest -q -m student -o addopts= tests/test_lab9_reply_ledger.py
```

## 7. Giới hạn bằng chứng

- Đây là MockLLM với seed cố định, không phải model production.
- Trace không thể hiện riêng toàn bộ quyết định giới hạn số tiền bên trong host.
- Không thể kết luận mọi kiểu sai số tiền đều được phát hiện từ một trial.
- Kết quả phải được kiểm tra thêm trên những claim và seed khác, đặc biệt ở eval set v2.
