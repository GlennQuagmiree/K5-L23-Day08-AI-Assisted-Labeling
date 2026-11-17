# Kiểm tra lại sau rework

Đây là lượt kiểm tra bổ sung, không thay thế số đo lần đầu ở thư mục `qc/` phía trên.

| Lượt | Nguồn nhãn | Điểm bẫy | QC theo ảnh | Quyết định |
|---|---|---|---|---|
| Đầu | `labels/batch_reviewed.json` | 8/12 | 4/8 ảnh lỗi | Rework |
| Kiểm tra lại | `reviewed_blind.coco.json` trước sửa sau chấm | 10/12 | Bản cuối: 0/8 ảnh lỗi được ghi nhận | Release theo ngưỡng quan sát |

## Trình tự thực hiện

1. Đối chiếu ảnh gốc và overlay của đủ 24 ảnh. Lưu 24 chỉnh sửa trên 9 ảnh tại `../rework/edits.json`; bản nền trước rà là `../rework/baseline.coco.json`.
2. Chạy `inject_traps.py` với seed **2026111701** trên `labels/batch_reworked.json`. Bộ bẫy có đủ 12 lỗi, mỗi loại 3. Không mở key và không dùng phép so sánh nhãn với bản nền trong khi duyệt.
3. Duyệt đủ 24 ảnh, ghi `edits_blind.json`, xuất `reviewed_blind.coco.json` và chốt SHA-256 trong `protocol.json` trước khi chấm. Ghi nhận 11 chỉnh sửa trong lượt duyệt này; một bổ sung là box person trùng, đã bỏ ở bước sau.
4. Chạy script chấm: **10/12 = 83,3%**; wrong_class 3/3, extra 3/3, missing 2/3, loose 2/3. Hai bẫy lọt: car ở img_021 và box motorbike ở img_018. Giữ nguyên file nhãn đã chốt và điểm này.
5. Sau khi chấm, sửa hai bẫy lọt và bỏ person trùng ở img_018; lưu riêng `edits_after_grading.json` và log. Khôi phục các cờ `can_review` đã bị bước cài bẫy đặt về false, không thay điểm conf. Bản cuối là `labels/batch_rechecked.json`, cũng được lưu làm `labels/qc_fixed.json` để dựng release.
6. Lấy mẫu QC từ bản cuối bằng seed **73**, 3 ca khó + 5 ảnh ngẫu nhiên. Đối chiếu 8 ảnh có 206 đối tượng; chưa ghi nhận lỗi còn lại trong lượt kiểm này. Script đề xuất Release theo các ngưỡng gốc.

Box thừa trên phần nhà ở img_033 (ID **516** trong bộ bẫy mới) đã được xóa; xem dòng xóa trong `change_log_blind.json`. ID được đánh lại khi dựng COCO cuối nên cần đối chiếu cả tên ảnh và vị trí box, không chỉ ID.

## Giới hạn

Lượt này dùng cùng các ảnh đã quen và cùng quy trình hỗ trợ, chưa có người kiểm độc lập. QC sau sửa quan sát 0/8 không chứng minh tỉ lệ lỗi thật dưới 2% (cận trên Wilson 95% khoảng 32%). Đây là quyết định phát hành trong phạm vi bài thực hành theo số đo quan sát, không phải chứng nhận bộ nhãn sạch tuyệt đối.

Nhãn nền của lượt bẫy mới đã được rà, vì vậy accepted 100% trong output `review_stats.md` không đo chất lượng detector. Hồ sơ lỗi mô hình phải đọc ở `../review_stats.*` của lượt đầu. Bộ gold và thời gian lượt đầu không được biến thành phép đo gán tay độc lập qua các lượt sửa này.

## Tái lập và kiểm tra

Chạy từ thư mục gốc repo:

```powershell
python scripts/rebuild_recheck.py --check
python scripts/validate_labels.py submission/release/final_det.coco.json --expect batch
python scripts/review_stats.py --pre submission/qc/recheck/pre_traps.coco.json --final submission/qc/recheck/reviewed_blind.coco.json --key submission/qc/recheck/traps_key.json --splits batch --out submission/qc/recheck/review_stats
python scripts/qc_report.py --sample submission/qc/recheck/qc_sample.csv --review submission/qc/recheck/qc_review.csv --stats submission/qc/recheck/review_stats.json --profile-label "Nhãn nền đã rà" --out submission/qc/recheck/qc_report_auto.md
python scripts/check_submission.py
```

`rebuild_recheck.py --check` chỉ đối chiếu các chỉnh sửa đã ghi và dấu kiểm file. Nếu cần dựng lại nhãn từ các chỉnh sửa, chạy không có `--check`, sau đó chạy `python scripts/build_release.py`. Đây là tái lập các quyết định đã lưu, không phải một lượt review hoặc chấm bẫy mới.
