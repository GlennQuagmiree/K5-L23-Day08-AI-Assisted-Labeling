# Báo cáo QC tự động (nháp)

> **Gợi ý** do script tính từ phiếu kiểm; không tự xác minh độ đúng của nhãn hay tính độc lập của người kiểm.

## Mẫu
- 8 ảnh (3 ca khó + 5 ngẫu nhiên), 206 đối tượng.
- taxonomy v1.1

## Số đo
| Chỉ số | Giá trị | Mẫu số |
|---|---|---|
| Lỗi **theo đối tượng** | 0/206 = 0.0% | 206 đối tượng trong mẫu |
| **Ảnh có lỗi** (dùng cho ngưỡng) | 0/8 = 0.0% | 8 ảnh trong mẫu |
| Nhãn nền đã rà: accepted / edited / deleted | 548/548 = 100.0% / 0/548 = 0.0% / 0/548 = 0.0% | 548 box nguồn |
| Nhãn nền đã rà: added | 0/548 = 0.0% | 548 đối tượng sau duyệt |
| Bắt lỗi bẫy | 10/12 = 83.3% | 12 bẫy |

## Top 3 loại lỗi
(không ghi nhận lỗi nào)

## Giới hạn thống kê
- 0 ảnh lỗi trong 8 ảnh mẫu: cận trên 95% (Wilson) của tỉ lệ ảnh lỗi thật là **32%**. Ngưỡng 2% không thể được **chứng minh** bằng mẫu nhỏ như vậy: hãy nói rõ giới hạn này trong báo cáo.

## Gợi ý quyết định
**RELEASE**

- ảnh lỗi 0.0% <= 2%, không lỗi hệ thống, bắt bẫy / nhất quán đạt (nếu đã đo)

Cây quyết định: Hold (guideline chưa rõ / dữ liệu hỏng) -> Rework (> ngưỡng, lỗi lặp, bắt bẫy / nhất quán thấp) -> Release.
