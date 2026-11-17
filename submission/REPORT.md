# Báo cáo Day 08 — 2A202603271 - Hà Huy Dũng

> Mọi con số kèm **mẫu số** và nguồn. Máy: RTX 3050 Laptop 4 GB (CUDA), CVAT v2.74.1 (Docker).

## 1. Model và recipe (Part 2–3)

| Lớp | Model + cỡ | Ngưỡng | Vì sao (dẫn `run_id` trong `model_log.csv`) |
|---|---|---|---|
| person / bicycle / motorbike / car / bus / truck | YOLO26-m, imgsz 1024 | 0.3 (mặc định) | Sweep trên gold (r12): **không lớp nào** đạt recall 90% với ngưỡng ≤ 0.5 (person tối đa 23/35 = 66%, motorbike 9/12 = 75%, car 5/8 = 62%, bicycle 5/6 = 83%) → script giữ mặc định. Ở 0.3 precision/recall: person 0.66/0.66, motorbike 0.73/0.67, car 0.63/0.63, bicycle 0.80/0.67. bus chỉ 1 vật (< 5), truck 0 vật → không chọn ngưỡng riêng. YOLOE kém ở lớp COCO (r05: 17 motorbike so với 55 của YOLO26 trên pilot). |
| three_wheeler | YOLOE-26l, 5 prompt: `tuk-tuk, cyclo, cargo tricycle, three-wheeled vehicle, auto rickshaw` | **0.5** | Sweep (r13): recall 7/7 = 100% ở mọi ngưỡng 0.1–0.5, precision 7/8 = 0.875 ở 0.3 và 0.5 nhưng chỉ 7/19 = 0.37 ở 0.1. Pilot (r04, r09) cho cùng kết luận: mọi box thừa (xe máy img_030 0.30/0.36, img_007 0.38, img_016 0.39; xe đạp img_015 0.30) đều < 0.4. Prompt mặc định 3 chữ (r03) sót hàng xích lô ở img_007 và 1 xích lô ở img_032 (r09 tìm đủ 4). |

- Lệnh `merge_prelabels.py` đã dùng:
  `python scripts/merge_prelabels.py work/prelabel/final_yoloel_c005/pre.coco.json work/prelabel/final_y26m_c005/pre.coco.json --thr "three_wheeler=0.5" --conf 0.3 --iou 0.6 --split "batch,gold" --out work/prelabel/merged_review/pre.coco.json`
  → 28 ảnh, 591 box (person 311, motorbike 153, car 65, three_wheeler 33, bicycle 14, truck 9, bus 6). Bẫy: `inject_traps.py --student 2A202603271`.
- **Phiên bản SAM chọn: SAM 2.1-b** (`sam2.1_b.pt`). Lý do đo được (r07, `work/mask_measure.py`): trên img_013 với 3 click âm, MobileSAM (SAM 1) sụp còn 23% diện tích box (mất nửa xe), SAM 2.1 giữ 41%; với box + 2 click âm, SAM 2.1 tách người lái tốt hơn (mask phủ 34% box người lái so với 40% của MobileSAM) và biên ít loang lổ hơn. Tốc độ gần bằng (1.72 vs 1.54 s/ảnh), 160 MB vừa GPU 4 GB, không cần quyền như SAM 3.
- **Lỗi không sửa được bằng ngưỡng:** YOLO26 gọi tuk-tuk là `car` (img_004 0.29, img_017 0.39, img_023 0.29), xích lô là `bicycle` (img_032 0.38), xe bán tải là `truck` (img_002 0.73), và **không ra box xe nào** cho tuk-tuk xanh ở img_002. Đây là lỗi **từ vựng** (80 lớp COCO không có xe ba bánh), nên tăng/giảm ngưỡng chỉ làm mất cả box. Sửa bằng model open-vocabulary (YOLOE) + merge cho `three_wheeler` thắng `car/truck` khi IoU ≥ 0.6, và còn lại thì người duyệt đổi lớp. Lỗi YOLOE **tách một tuk-tuk thành 2–3 box** (img_013, img_008) cũng không sửa bằng ngưỡng vì các box nửa xe có conf 0.83–0.97.
- **Điểm cao mà sai / điểm thấp mà đúng:** bán tải → `truck` 0.73 (img_002, sai lớp); box nửa xe tuk-tuk img_013 0.94 (sai hình); tuk-tuk → `car` 0.29 (img_004: đúng vật, sai lớp, điểm thấp); xích lô img_032 `three_wheeler` 0.27 (đúng, điểm rất thấp).
- **So sánh model mạnh hơn (đo thêm, không dùng cho lô vì pre-label đã nạp CVAT):** YOLO26-l imgsz 1280 trên gold ở ngưỡng 0.3 (`work/qc/sweep_y26l1280.*`): recall motorbike 10/12 = 0.83 (m: 0.67), car 7/8 = 0.88 (m: 0.63), person 24/35 = 0.69 (m: 0.66), nhưng precision giảm (person 0.52 vs 0.66, motorbike 0.53 vs 0.73) và chậm 2.8 s/ảnh vs 0.16. Lần sau sẽ dùng bản l-1280 cho motorbike/car (recall quan trọng hơn: xoá box thừa nhanh hơn vẽ box sót).
- **Giới hạn:** ngưỡng chọn và precision/recall chấm trên **cùng 4 ảnh gold** → số đo lạc quan; three_wheeler chỉ 7 vật, bus 1, truck 0 → ngưỡng là ước lượng thô. 12/35 người gold máy không bao giờ ra (nhỏ, ngồi trong xe, bị che), nên `added` ở batch sẽ không nhỏ.

## 2. Hồ sơ lỗi mô hình

Nguồn: `qc/review_stats.json` và `.md`, tính trên bản review lần đầu `labels/batch_reviewed.json`, trước sửa QC. Script loại 25 đối tượng gần vị trí bẫy khỏi thống kê chất lượng máy.

| Trạng thái | Số | Tỉ lệ | Mẫu số |
|---|---:|---:|---|
| accepted | 429 | 85,0% | 505 box máy |
| edited | 22 | 4,4% | 505 box máy |
| deleted | 50 | 9,9% | 505 box máy |
| added | 89 | 16,5% | 540 đối tượng sau duyệt |

Accepted + edited + deleted = 501, thấp hơn 505 vì 4 box không ghép nằm trong vùng ignore không được tính deleted, trong khi mẫu số của script vẫn giữ chúng. Có 8 trường hợp đổi lớp được tính deleted + added; số sót ước tính là 89 − 8 = 81, không phải cả 89 đều là bỏ sót.

`three_wheeler` cần can thiệp nhiều: 8 accepted, 7 edited, 9 deleted, 5 added; ví dụ một tuk-tuk bị tách thành hai nửa ở img_013, img_017. Xe đẩy hàng hai bánh ở img_008 còn bị nhận nhầm sau lần review đầu và chỉ được sửa trong QC. Person có 37 added, motorbike có 29 added, phản ánh khó khăn với người bị che và xe nhỏ.

So với 4 ảnh tham chiếu: **51 TP, 21 FP, 18 FN**, precision **51/72 = 70,8%**, recall **51/69 = 73,9%**. Mẫu số recall là 69 vật, không gồm 2 ignore_region. Tập tham chiếu không phải gold gán tay độc lập; ngưỡng còn được chọn trên chính tập này nên số đo không phải ước lượng tổng quát hóa.

## 3. Thiên kiến tự động hóa và ảnh bẫy

Nguồn: `qc/review_stats.md`, chấm sau khi đã xuất bản review lần đầu. Không mở trực tiếp `traps_key.json`; chỉ truyền đường dẫn cho script chấm sau export.

Tôi sử dụng Codex để xem ảnh và hỗ trợ sửa nhãn. Vì vậy, điểm bắt bẫy dưới đây đo **quy trình review có AI hỗ trợ**, không đo khả năng tự review của riêng tôi. Không dùng kết quả này để suy ra mức thiên kiến tự động hóa của cá nhân tôi.

- Bắt **8/12 = 66,7%**, thấp hơn yêu cầu ít nhất 10/12. Theo loại: loose 2/3, wrong_class 2/3, missing 1/3, extra 3/3.
- Bẫy lọt theo script: img_034 (wrong_class), img_026 (loose), img_018 và img_013 (missing).
- Accepted 85,0% nhưng bẫy chỉ 66,7% cho thấy giữ nhiều box không chứng minh review tốt. Việc tìm vật chưa có box yếu hơn phát hiện box thừa; cụm xe đỗ và phần người bị che cần lượt quét riêng.
- **Bẫy đo quy trình có AI hỗ trợ, không đo riêng mắt người.** Review 24 ảnh được làm bằng quy trình có công cụ/AI hỗ trợ (mục 8) trong 13,14 phút (0,55 phút/ảnh, nghỉ 0 phút), nhanh hơn nhiều so với ~3 phút/ảnh của checklist. Ba bẫy lọt thuộc loại máy *không vẽ* (missing ×2) hoặc lệch nhỏ (loose), đúng hai điểm yếu kinh điển của thiên kiến tự động hóa: "máy không vẽ thì không kiểm" và "lệch vài pixel khó thấy". Bẫy extra (box thừa) bắt 3/3, tức là quy trình xoá tốt nhưng tìm vật sót kém, khớp với `added` của người/xe máy còn cao (37 / 29). Kết luận: một bộ duyệt thứ hai cũng tự động không thay được bước 0 (quét ảnh khi ẩn nhãn) của người.
- Giữ nguyên điểm lần đầu để đánh giá quy trình. Các sửa QC không được dùng để thay điểm này bằng kết quả đẹp hơn. Khoảng tin cậy 95% của 8/12 rất rộng, khoảng 39–86%.

## 4. Máy có đáng dùng không?

Nguồn `time_log.csv`: tạo nhãn tham chiếu và nhập/xuất CVAT **5,94 phút / 4 ảnh = 1,49 phút/ảnh**; review và nhập/xuất **13,14 phút / 24 ảnh = 0,55 phút/ảnh**, nghỉ 0 phút. Đồng hồ gồm thao tác file và CVAT. Đây là quy trình hỗ trợ; **không phải phép đo tốc độ gán tay hoặc review thủ công độc lập**. Không dùng tỉ số khoảng 2,71 lần để khẳng định máy nhanh hơn con người. Hai tập ảnh khác nhau và làm gold trước cũng tạo hiệu ứng quen cảnh.

Kết luận: pre-label hữu ích như bản nháp cho các lớp COCO và gợi ý xe ba bánh, nhưng lô này chưa đạt điều kiện phát hành. Không dùng conf hay accepted làm tiêu chí tự chấp nhận.

Ba quy tắc kiểm tra được cho lần tiếp theo:
1. Quét ảnh khi chưa hiện box, lập số đếm người và xe trước khi so với nhãn; mỗi ảnh phải có mục đối chiếu số đếm.
2. Đi đủ bốn bước bỏ sót → thừa → sai lớp → hình học, đặc biệt kiểm toàn bộ xe chở hàng và box chồng; giữ danh sách sửa theo ảnh.
3. Tách lượt QC khỏi lượt sửa, lấy 3 ca khó + 5 ảnh ngẫu nhiên seed 42; chỉ xét Release khi số liệu đạt các ngưỡng gốc, không sửa ngưỡng để đạt.

## 5. Mask SAM cho 3 vật (Part 5)

Prompt = box từ máy (YOLOE r10) + click âm đặt tại tâm box `person` của YOLO26 (r11). Số đo phủ: `work/mask_measure.py` (tỉ lệ pixel mask trong box người lái).

| Ảnh | SAM (phiên bản) | Số click | Mask gồm người lái / hàng hoá? | Lỗi quan sát | File trong `masks/` |
|---|---|---|---|---|---|
| img_013 | SAM 2.1-b | box YOLOE gốc, 0 click | — | Box YOLOE [339,62,950,630] chỉ phủ **nửa trước** tuk-tuk → mask mất nửa sau (lỗi lan từ detector) | (đã thay, số đo trong model_log r07) |
| img_013 | SAM 2.1-b | box hợp 2 box YOLOE, 0 click | **Có**: phủ 54% box người lái, tràn sang xe máy đỏ đỗ sau | sai 4.2.4 (hai vật chạm nhau phải tách) | `tuktuk_img013_sam21_unionbox_0click.jpg` |
| img_013 | SAM 2.1-b | box hợp + **2 click âm** (người lái, xe máy) | Mức phủ box người lái giảm còn 34%; chưa có mask chuẩn người để khẳng định đã tách sạch | mask phủ cả mui + thân + bánh, 1 polygon | `tuktuk_img013_sam21_unionbox_2neg.jpg` |
| img_013 | MobileSAM (SAM 1) | box hợp + 2 click âm | người lái 40% | biên loang lổ ở khung mui; với 3 click âm mask sụp còn 23% box | `tuktuk_img013_mobilesam_unionbox_2neg.jpg` |
| img_004 | SAM 2.1-b | box YOLOE, 0 click | không thấy người lái trong box | fill 72% box, 0% ngoài box | `tuktuk_img004_sam21_box.jpg` |
| img_017 | SAM 2.1-b | box YOLOE, 0 click | — | fill 68% box | `tuktuk_img017_sam21_box.jpg` |
| img_023 | SAM 2.1-b | box YOLOE, 0 click | — | fill 51% box | `tuktuk_img023_sam21_box.jpg` |

- **Đối chiếu guideline 4.2:** 4.2.4 ("hai vật chạm nhau, mỗi vật một polygon") giúp quyết định click âm lên xe máy; nhưng 4.2 **không nói** người ngồi **trong** xe là vật "phía trước" → đã thêm vào v1.1 (CAL-07). 4.2.2 (lỗ < 5% không vẽ) khớp với SAM: khoang khách hở ở img_013 vẫn được tô liền.
- **Quy tắc rút ra:** (1) mask chỉ đúng khi box đúng: kiểm box ôm cả xe trước khi chạy SAM; (2) luôn click âm lên người lái và vật chạm xe; (3) không thêm quá 2 click âm với MobileSAM (sụp mask).
- *(Tuỳ chọn)* Interactor SAM trong CVAT: không thử (CVAT Docker chưa cài serverless/Nuclio).

## 6. Calibration

Có **12 quyết định** trong `qc/calibration_decisions.csv` (CAL-01 đến CAL-12), từ ca can_review, câu hỏi mở, lỗi mô hình và bẫy lọt. Nội dung tương ứng nằm trong `guidelines/guideline_v1.1_calibrated.md`.

- CAL-01, CAL-02: 7 ca can_review trong gold, gồm 6 ca người dưới mui ở img_012/img_020 và 1 ca người trên xe máy ở img_036. Giữ ngưỡng che khuất của v1.0; dấu hiệu đầu + vai/thân hỗ trợ ước lượng, không phải thay đổi ngưỡng diện tích.
- CAL-03 đến CAL-07: phân biệt xe ba bánh với xe hai bánh, một xe một box, không có ngưỡng conf tự chấp nhận, tách người và xe lân cận khỏi mask.
- CAL-08: xe đẩy hai bánh bán hàng img_008 không thuộc taxonomy; không suy đoán bánh thứ ba từ hàng chở.
- CAL-09: motorbike kéo moóc img_034: gán phần xe máy, không nhập moóc rời thành three_wheeler; giữ can_review cho cấu hình khó.
- CAL-10, CAL-11: giỏ gắn cố định trên bicycle img_031; xe đỗ gần ở img_026 vẫn gán riêng khi thấy rõ, chỉ ignore phần cụm nhỏ/mờ không tách được.
- CAL-12: bẫy lọt là lỗi quy trình; phải quét lại vật chưa có box và kiểm bốn ảnh bẫy lọt trước một lượt QC độc lập.

Không đổi các ngưỡng trong `taxonomy.json.rules`. Các ví dụ giúp cụ thể hóa v1.0; số đo lần đầu được giữ để truy nguyên.

## 7. QC và quyết định

Nguồn: `qc/qc_sample.csv`, `qc/qc_review.csv`, `qc/qc_report_auto.md`.

Mẫu **8/24 ảnh**, gồm 3 ca khó + 5 ảnh ngẫu nhiên seed 42, **213 đối tượng** trước sửa QC. Phiếu ghi 6 lỗi trên 4 ảnh: **6/213 = 2,8% theo đối tượng**, **4/8 = 50,0% theo ảnh**. Không so 2,8% theo đối tượng với ngưỡng 2% theo ảnh.

Tôi dùng Codex để kiểm ảnh mẫu và ghi phiếu QC. Đây là lượt kiểm có hỗ trợ, không phải lượt kiểm độc lập do tôi tự thực hiện bằng mắt.

| Lỗi | Số | Ví dụ |
|---|---:|---|
| Sai lớp | 3 | img_008: ba xe đẩy hàng hai bánh bị gán three_wheeler |
| Sai vị trí/kích thước | 2 | img_005 thiếu vai phải; img_010 thiếu dải mui xanh bên trái |
| Bỏ sót | 1 | img_018: motorbike dưới người lái gần (418,495) |

Không phát hiện lỗi thêm trong lượt QC ở img_003, img_009, img_021, img_035; điều đó không chứng minh ảnh hoàn toàn sạch. Cận trên Wilson 95% của tỉ lệ ảnh lỗi là **78%**; mẫu nhỏ, có chọn ca khó và cùng quy trình thực hiện nhãn lẫn QC nên không đại diện độc lập cho cả lô.

Đã sửa 6 lỗi trong `labels/qc_fixed.json` (4 ảnh). `build_release.py` thay 4 ảnh này để tạo `release/final_det.coco.json`: **24 ảnh, 562 hình**, gồm 550 vật và 12 ignore_region. `batch_reviewed.json` vẫn là bản xuất CVAT lần đầu: 564 hình. Số QC trên đây thuộc bản trước sửa; không diễn giải thành tỉ lệ lỗi còn lại sau sửa.

Script kiểm được cấu trúc COCO, số ảnh, lớp, biên ảnh và việc ghép box; không chứng minh box ôm sát vật, không tìm được mọi vật cùng bị bỏ sót, không xác nhận một người đã quét đủ 15 giây.

**Quyết định: Rework — 2026-11-17.** Không có ảnh hỏng được ghi nhận; các quy tắc phát sinh đã được bổ sung nên không chọn Hold. Chưa chọn Release vì lượt đầu chỉ bắt 8/12 bẫy và QC phát hiện lỗi trên 4/8 ảnh. Các sửa cục bộ đã có, nhưng cần rà lại toàn lô, ưu tiên img_013, img_018, img_026, img_034, rồi QC độc lập trước khi đổi quyết định.

## 8. Ghi chú thực hiện

- **Khai báo sử dụng AI:** tôi sử dụng Claude Code (Anthropic) và Codex (OpenAI) để hỗ trợ thực hiện bài. Claude hỗ trợ chuẩn bị môi trường, chạy mô hình, đo mask và soạn bản nháp log, guideline, calibration, báo cáo. Codex xem ảnh gốc, tạo tọa độ box gold bằng Python, nhập và xuất nhãn qua CVAT; sau đó xem ảnh và pre-label để sửa nhãn batch, kiểm mẫu QC, lưu các sửa QC và chỉnh báo cáo. Tôi không mô tả những thao tác này là tự vẽ hoặc tự review thủ công độc lập.
- **Phạm vi cho phép:** theo thông tin tôi đã cung cấp trong trao đổi, giảng viên cho phép sử dụng AI và gửi ảnh bộ dữ liệu cho AI. Tôi khai rõ phạm vi công cụ đã tham gia để người đọc đánh giá đúng kết quả.
- **Tình trạng gold:** Codex tạo nhãn từ ảnh gốc trước khi xem dự đoán detector trên bốn ảnh đó, rồi nhập CVAT và xuất COCO. Tuy không sao chép pre-label của detector, nhãn vẫn do AI hỗ trợ tạo nên **không phải gold gán tay độc lập**. Precision/recall trong bài là phép so với tập tham chiếu này, không phải phép đánh giá trên gold sạch theo quy trình gán tay của RULES.
- **Cách kiểm tra đã thực hiện:** đối chiếu ảnh gốc và overlay trong quy trình hỗ trợ; chạy `validate_labels.py` và `check_submission.py`; lấy số liệu bằng các script gốc. Các kiểm tra cấu trúc đã chạy thành công, nhưng không thay thế việc tôi tự kiểm ảnh và xác nhận nhãn độc lập.
- **Thời gian và người kiểm:** mốc trong `time_log.csv` đo quy trình hỗ trợ gồm thao tác file và CVAT, không phải thời gian tôi tự gán hoặc tự duyệt. Phiếu QC ghi Codex là công cụ thực hiện lượt kiểm này. Nhãn sau QC được lưu riêng để giữ lịch sử lần review đầu.
- Máy Windows 11, RTX 3050 Laptop 4 GB, torch 2.6.0+cu124; CVAT v2.74.1 chạy Docker. Detector được chạy trên GPU; không dùng dự đoán trong `data/cache/` làm kết quả thay thế.
- Dùng các script gốc để validate, quét ngưỡng, chấm review, lấy mẫu QC và dựng bản tổng hợp; không sửa tay các file thống kê sinh tự động.
- Lần sau: dành lượt riêng cho vật chưa có box và cho xe chở hàng; kiểm box trước khi dùng SAM; chưa nộp bản này như một lô đã đạt chuẩn Release.
