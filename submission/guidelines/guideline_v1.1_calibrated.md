# Label contract — Phố châu Á — BỔ SUNG v1.1 — 2A202603271 - Hà Huy Dũng

> Chỉ phần thay đổi so với v1.0 (`guideline/guideline_v1.0_label_contract.md`). Mỗi quy tắc có ảnh ví dụ và khớp một dòng trong `qc/calibration_decisions.csv`.

## 1. Câu hỏi mở đã chốt (từ mục 6 của v1.0)

| # | Câu hỏi | Quyết định | Ảnh ví dụ | `case_id` |
|---|---|---|---|---|
| 4 | Người ngồi trong xe ba bánh có mui, chỉ thấy thấp thoáng: ngưỡng "còn thấy ≥ 20%" có hợp lý? | **Giữ ngưỡng còn thấy ≥ 20%**; dùng dấu hiệu sau để hỗ trợ ước lượng: gán `person` khi thấy rõ **đầu + ít nhất một phần vai/thân**; chỉ thấy tóc, tay, bóng mờ sau kính → không gán. | img_012 (3 người lái dưới mui), img_020 (người sau kính chắn gió) | CAL-01 |
| 7 | Mức `conf` tối thiểu để chấp nhận box máy không cần sửa? | **Không đặt.** Box sai có conf cao (bán tải → truck 0.73) và box đúng có conf thấp (tuk-tuk → car 0.29). `conf` chỉ dùng để xếp thứ tự duyệt. | img_002, img_004 | CAL-06 |
| 3 (mask) | Mask xe có gồm người / vật chạm vào không? | Mask `three_wheeler` **không gồm** người lái, khách và xe khác chạm vào. Với SAM: luôn thêm click âm lên người lái và lên vật chạm xe. | img_013 (`masks/tuktuk_img013_sam21_unionbox_2neg.jpg`) | CAL-07 |

Chưa chốt (không có ảnh ví dụ trong lô để quyết): câu 1 (xe đạp điện), câu 2 (khối xe máy đỗ dày **gần** camera), câu 5 (kính xe trong mask ô tô), câu 6 (box chồng ảnh đêm). Giữ theo v1.0 và tick `can_review` nếu gặp.

## 2. Ca khó mới (từ lỗi của máy và box `can_review`)

| Ảnh | Tình huống | Máy làm gì (model nào) | Quyết định | Quy tắc mới (vào mục nào của v1.0) |
|---|---|---|---|---|
| img_036 | Người ngồi sau xe máy bị người lái che gần hết | YOLO26 thường bỏ sót | `person` riêng nếu thấy đầu (mũ) + một phần thân/chân | 4.1.4: người ngồi sau là `person` riêng, dùng tiêu chí CAL-01 (CAL-02) |
| img_030, img_007, img_016, img_015 | Xe máy 2 bánh / xe đạp | YOLOE gọi `three_wheeler` conf 0.28–0.39 | `motorbike` / `bicycle` | Mục 2, cột "Không gồm" của `three_wheeler`: **xe máy 2 bánh có thùng sau, xe đạp chở hàng** (CAL-03) |
| img_013, img_017 | Một tuk-tuk dài | YOLOE tách thành 2–3 box nửa xe; YOLO26 thêm `car` + `truck` chồng lên | Một box ôm cả mui + khoang + thân; xoá box nửa xe / trùng | 4.1.1: **một vật một box**, box phải chạm cả đầu và đuôi xe (CAL-04) |
| img_002 | Xe bán tải | YOLO26 `truck` 0.73 | `car` | Bảng ca khó: ví dụ cho "bán tải = car" đã có ở mục 2 (CAL-05) |
| img_004, img_017, img_023 | Tuk-tuk | YOLO26 `car` 0.29–0.39 | `three_wheeler` | Không đổi chữ (guideline đã đúng, lỗi máy); thêm ảnh ví dụ (CAL-05) |

Bảng ca khó (mục 5 v1.0), thêm dòng:

| Ca | Quyết định | Lý do |
|---|---|---|
| Người lái tuk-tuk dưới mui, thấy đầu + vai | `person` riêng, box phần nhìn thấy | CAL-01, img_012 |
| Xe máy 2 bánh chở thùng hàng | `motorbike` | CAL-03, img_030 |
| Máy ra 2 box cho một tuk-tuk | giữ một box ôm cả xe | CAL-04, img_013 |

## 3. Lịch sử thay đổi

| Phiên bản | Thay đổi | Lý do (ca nào, `case_id`) |
|---|---|---|
| v1.0 | Bản giảng viên | — |
| v1.1 | Tiêu chí "đầu + vai" hỗ trợ ước lượng ngưỡng 20% (4.1.2, 4.1.4); "không gồm" xe máy có thùng cho `three_wheeler` (mục 2); "một vật một box" (4.1.1); mask không gồm người / vật chạm (4.2.4); không đặt ngưỡng conf tự chấp nhận (mục 3) | CAL-01 … CAL-07 |

## 4. Bổ sung sau QC

| Quy tắc | Ảnh | Quyết định | Case |
|---|---|---|---|
| Xe đẩy hai bánh không thuộc taxonomy | img_008 | Không gán three_wheeler chỉ vì có hàng; giữ person người bán. | CAL-08 |
| Xe máy kéo moóc rời | img_034 | Gán phần motorbike; moóc rời không tự trở thành three_wheeler. Giữ can_review cho cấu hình khó. | CAL-09 |
| Giỏ, giá gắn cố định trên bicycle | img_031 | Box gồm phần kết cấu gắn cố định, không gồm người bán. Hàng rời nhô xa áp dụng 4.1.5. | CAL-10 |
| Xe máy đỗ gần, dày | img_026 | Vật rõ và cao ≥20 px phải gán riêng; ignore chỉ dùng cho cụm ≥5 vật nhỏ/mờ không tách được. | CAL-11 |
| Bẫy lọt | img_013, img_018, img_026, img_034 | Giữ điểm lần đầu, quét lại vật chưa có box và QC độc lập trước Release. | CAL-12 |

Bổ sung v1.1: CAL-08–CAL-12; không đổi taxonomy.rules.
