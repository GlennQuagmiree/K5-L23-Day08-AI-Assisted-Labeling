# Số đo review (det)

- Ảnh tính: 24 (batch); box máy: 548; đối tượng sau duyệt: 548; ngưỡng accepted: IoU >= 0.9
- Đã **loại 22 đối tượng nằm quanh các bẫy** khỏi bảng này: lỗi nhân tạo không phản ánh chất lượng máy.

## 1. Bốn trạng thái (hồ sơ lỗi mô hình)
| Trạng thái | Số | Tỉ lệ | Mẫu số |
|---|---|---|---|
| accepted (giữ nguyên) | 548 | 548/548 = 100.0% | 548 box máy |
| edited (sửa) | 0 | 0/548 = 0.0% | 548 box máy |
| deleted (xoá) | 0 | 0/548 = 0.0% | 548 box máy |
| added (vẽ thêm) | 0 | 0/548 = 0.0% | 548 đối tượng sau duyệt |

Trong số deleted + added, **0 trường hợp là đổi lớp** (máy gán sai lớp, box đúng chỗ): đó không phải máy bỏ sót. Số vật máy **sót thật** ≈ added − đổi lớp = 0.

### Theo lớp
| Lớp | accepted | edited | deleted | added |
|---|---|---|---|---|
| person | 293 | 0 | 0 | 0 |
| bicycle | 11 | 0 | 0 | 0 |
| motorbike | 161 | 0 | 0 | 0 |
| car | 56 | 0 | 0 | 0 |
| bus | 7 | 0 | 0 | 0 |
| truck | 3 | 0 | 0 | 0 |
| three_wheeler | 17 | 0 | 0 | 0 |

## 3. Ảnh bẫy
- Bắt được 10/12 = 83.3% (KTC 95%: 55–95%) (ngưỡng đạt: 80%). Chỉ 12 bẫy nên khoảng tin cậy rất rộng: đọc cùng danh sách bẫy lọt, đừng kết luận chỉ từ %.
  - wrong_class: 3/3
  - missing: 2/3
  - extra: 3/3
  - loose: 2/3
  - lọt: img_021.jpg (missing), img_018.jpg (loose)

## Gợi ý đọc số
- `deleted` cao → ngưỡng thấp hoặc ánh xạ nhãn sai; `added` cao → máy bỏ sót (xem lớp nào);
- `accepted` thấp (< 50%) → sửa mỗi box lâu hơn vẽ mới: đổi model/ngưỡng hoặc vẽ tay;
- bắt bẫy < 80% → duyệt lại lô, siết checklist (quét ảnh TRƯỚC khi nhìn nhãn máy).
