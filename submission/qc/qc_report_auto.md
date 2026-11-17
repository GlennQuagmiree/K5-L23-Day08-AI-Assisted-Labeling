# Báo cáo QC tự động (nháp)

> **Gợi ý** do script tính từ phiếu kiểm; không tự xác minh độ đúng của nhãn hay tính độc lập của người kiểm.

## Mẫu
- 8 ảnh (3 ca khó + 5 ngẫu nhiên), 213 đối tượng.
- taxonomy v1.1

## Số đo
| Chỉ số | Giá trị | Mẫu số |
|---|---|---|
| Lỗi **theo đối tượng** | 6/213 = 2.8% | 213 đối tượng trong mẫu |
| **Ảnh có lỗi** (dùng cho ngưỡng) | 4/8 = 50.0% | 8 ảnh trong mẫu |
| Máy: accepted / edited / deleted | 429/505 = 85.0% / 22/505 = 4.4% / 50/505 = 9.9% | 505 box nguồn |
| Máy: added | 89/540 = 16.5% | 540 đối tượng sau duyệt |
| Bắt lỗi bẫy | 8/12 = 66.7% | 12 bẫy |

## Top 3 loại lỗi
| Loại lỗi | Số lỗi | Ảnh ví dụ |
|---|---|---|
| sai_lop | 3 | img_008.jpg |
| sai_vi_tri_kich_thuoc | 2 | img_005.jpg, img_010.jpg |
| bo_sot | 1 | img_018.jpg |

**Lỗi hệ thống**: 'sai_lop' lặp lại -> sửa quy tắc / recipe, không chỉ sửa từng ảnh.

## Giới hạn thống kê
- 4 ảnh lỗi trong 8 ảnh mẫu: cận trên 95% (Wilson) của tỉ lệ ảnh lỗi thật là **78%**. Ngưỡng 2% không thể được **chứng minh** bằng mẫu nhỏ như vậy: hãy nói rõ giới hạn này trong báo cáo.

## Gợi ý quyết định
**REWORK**

- ảnh có lỗi 50.0% > 2%
- lỗi hệ thống: 'sai_lop' chiếm 3/6 lỗi
- bắt bẫy 67% < 80% -> lô duyệt chưa đáng tin

Cây quyết định: Hold (guideline chưa rõ / dữ liệu hỏng) -> Rework (> ngưỡng, lỗi lặp, bắt bẫy / nhất quán thấp) -> Release.
