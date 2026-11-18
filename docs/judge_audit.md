
# Judge Audit — Lab 9 LogiX-VN

## 1. Mục tiêu và phương pháp

Đánh giá độ tin cậy của hai LLM judge bằng cách so sánh nhãn judge với nhãn human trên dữ liệu replay công khai.

- Positive class: FAIL (phát hiện câu trả lời không đạt).
- Số mẫu: 100 cho mỗi judge.
- Ngưỡng: Cohen's kappa >= 0.6; Precision >= 0.8; Recall >= 0.7.
- Judge verdict được phát lại từ CSV, không gọi API thật.
- Nhãn human là chuẩn tham chiếu cho phép đo calibration.

Lệnh thực hiện:

```bash
python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5
python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5
```

## 2. Kết quả calibration

| Tiêu chí | n | Kappa | Precision | Recall | Đạt floors? | Quyết định |
|---|---:|---:|---:|---:|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | Có | Cho phép dùng với giám sát |
| helpful | 100 | 0.375 | 1.000 | 0.300 | Không | Loại khỏi release gate |

### Confusion matrix

| Judge | TP | FP | FN | TN |
|---|---:|---:|---:|---:|
| tone_ok | 24 | 4 | 6 | 66 |
| helpful | 9 | 0 | 21 | 70 |

TP = judge phát hiện đúng FAIL.

FP = judge báo FAIL trong khi human đánh giá PASS.

FN = judge bỏ sót FAIL, đánh giá PASS.

TN = judge xác nhận đúng PASS.

### Hiệu chỉnh Rogan-Gladen

| Judge | Observed failure rate | Corrected failure rate |
|---|---:|---:|
| tone_ok | 0.28 | 0.30 |
| helpful | 0.09 | 0.30 |

Công thức:

p_corrected = (p_observed + specificity - 1) / (sensitivity + specificity - 1)

Kết quả cho thấy judge helpful chỉ quan sát được 9% câu trả lời bị lỗi, trong khi nhãn human cho biết tỷ lệ là 30%.

Rogan-Gladen là phép hiệu chỉnh thống kê dựa trên sensitivity và specificity đo được, không phải bằng chứng rằng judge đã nhận diện đúng từng lỗi riêng lẻ.

## 3. Audit thủ công 10 trường hợp bất đồng

Các nhận định được đối chiếu với nhãn human và ghi chú đi kèm trong CSV.

| # | Case | Judge | Human | Ai đúng? | Phân tích và hành động sửa rubric |
|---|---|---|---|---|---|
| 1 | H-008 | PASS | FAIL | Human | Xưng "em", dùng "nha" quá suồng sã với khách theo rubric. Cần nêu rõ chuẩn xưng hô CSKH, không đồng nhất thân thiện với chuyên nghiệp. |
| 2 | H-017 | PASS | FAIL | Human | Judge không xét ngữ cảnh xưng "bạn" với khách lớn tuổi. Bổ sung quy tắc xưng hô theo ngữ cảnh khách hàng, không chỉ dựa vào cảm giác thân thiện. |
| 3 | H-029 | PASS | FAIL | Human | "Không cần nhắn thêm" mang tính ra lệnh. Rubric cần kiểm tra toàn bộ câu, đặc biệt các mệnh lệnh thiếu lịch sự. |
| 4 | H-042 | FAIL | PASS | Human | Câu trả lời ngắn nhưng đủ ý và lịch sự. Không bắt buộc phải xin lỗi trong mọi trường hợp. |
| 5 | H-051 | FAIL | PASS | Human | Từ "refund" được quy chuẩn CSKH LogiX cho phép. Rubric cần cho phép thuật ngữ tiếng Anh được chấp nhận. |
| 6 | HL-015 | PASS | FAIL | Human | Reply báo 55.000đ, ledger ghi 40.000đ. Không thể đánh giá tính đúng đắn chỉ từ độ trôi chảy của reply; dùng code đối chiếu ledger. |
| 7 | HL-016 | PASS | FAIL | Human | Reply báo 55.000đ, ledger ghi 35.000đ. Lời xin lỗi dài không bù được lỗi tiền; thêm điều kiện kiểm tra số tiền bằng code. |
| 8 | HL-020 | PASS | FAIL | Human | Reply báo 90.000đ, ledger ghi 120.000đ. Lỗi sai số tiền phải được đánh giá là FAIL bất kể giọng điệu. |
| 9 | HL-028 | PASS | FAIL | Human | Reply báo 50.000đ, ledger ghi 35.000đ. Judge bị ảnh hưởng bởi lời xin lỗi lịch sự; tách correctness khỏi tone. |
| 10 | HL-035 | PASS | FAIL | Human | Reply báo 50.000đ, ledger ghi 35.000đ. Không chấp nhận lời khẳng định hoàn tiền nếu không khớp ledger; sử dụng deterministic grader. |

## 4. Kết luận và quyết định sử dụng

### Tone judge: PASS calibration

- Kappa = 0.757, vượt floor 0.6.
- Precision = 0.857, vượt floor 0.8.
- Recall = 0.800, vượt floor 0.7.
- Tuy nhiên vẫn bỏ sót 6 lỗi và báo nhầm 4 lần trong 100 mẫu.

Quyết định: có thể sử dụng cho đánh giá tone trong phạm vi đã calibration, kết hợp giám sát và audit định kỳ. Không dùng để quyết định tiền hoặc approval.

### Helpfulness judge: FAIL calibration

- Kappa = 0.375, thấp hơn floor 0.6.
- Precision = 1.000 nhưng recall chỉ đạt 0.300.
- Judge bỏ sót 21 trong tổng số 30 lỗi thực tế.
- Nhiều false negative liên quan đến số tiền trong reply không khớp ledger.

Quyết định: loại khỏi release gate. Không sử dụng judge này làm tiêu chí blocking khi chưa cải thiện rubric và calibration trên bộ dữ liệu mới.

Đề xuất sửa: tách đánh giá tone khỏi tính đúng đắn nghiệp vụ; dùng code grader cho ledger, refund amount, approval và các tác động tài chính.

## 5. Rủi ro và bằng chứng còn thiếu

- Hai bộ dữ liệu chỉ gồm 100 mẫu mỗi bộ.
- Đây là judge replay, không phải đánh giá live.
- Dữ liệu calibration công khai, chưa có held-out set độc lập.
- Kappa, precision và recall có thể thay đổi khi phân phối lỗi thay đổi.
- Nhãn human vẫn cần quy trình kiểm tra nhất quán giữa nhiều người đánh giá.
- Nếu không xác định được kappa thì calibration phải FAIL, không được tự động cho qua.

Cần bổ sung dữ liệu mới, kiểm tra bất đồng giữa người gán nhãn và calibration lại trước khi thay đổi quyết định dùng judge cho release gate.
