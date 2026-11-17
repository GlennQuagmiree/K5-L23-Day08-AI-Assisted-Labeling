# Thông tin học viên

- Họ và tên: Hà Huy Dũng
- MSHV: 2A202603271
- Lớp (L2 / L3 / khác): L2
- Tài khoản GitHub: hdung25
- Repo bài nộp (URL): https://github.com/hdung25/K5-L2-Day08-HaHuyDung-2A202603271-AI-Assisted-Labeling
- Commit chốt bài (hash): aa9f68d983f65c701c522d8079db490bef1a49d8 (bản nội dung sau rework; commit sau chỉ cập nhật dòng này)
- Máy: Windows 11 Home, GPU NVIDIA GeForce RTX 3050 Laptop 4 GB (CUDA, torch 2.6.0+cu124), Python 3.11.9
- CVAT (Docker): v2.74.1 (Docker Desktop, WSL2)

## Kết quả tóm tắt

- Nội dung bài làm: thử nghiệm mô hình, chọn ngưỡng theo lớp, xử lý nhãn trên CVAT, so sánh mask, bổ sung guideline và đánh giá QC. Phạm vi công cụ hỗ trợ và giới hạn đánh giá được trình bày tại REPORT mục 8.

- Lượt review đầu: accepted 429/505 = 85,0%; edited 22/505 = 4,4%; deleted 50/505 = 9,9%; added 89/540 = 16,5%.
- So với 69 vật tham chiếu: máy có precision 51/72 = 70,8%; recall 51/69 = 73,9%. Tập tham chiếu không phải gold gán tay độc lập.
- Bắt bẫy lần đầu: 8/12 = 66,7%; lượt kiểm tra lại với seed mới: 10/12 = 83,3% (chốt nhãn trước khi mở đáp án).
- Thời gian: tạo nhãn tham chiếu 5,94/4 = 1,49 phút/ảnh; review 13,14/24 = 0,55 phút/ảnh; nghỉ 0 phút. Không phải phép đo thao tác thủ công độc lập.
- QC trước sửa: 4/8 ảnh lỗi = 50,0%; 6/213 đối tượng lỗi = 2,8%. Bản sửa 4 ảnh ban đầu được lưu tại qc/rework/qc_fixed_before_rework.json; qc_fixed.json hiện là bản cuối đủ 24 ảnh.
- Bản cuối sau rà toàn lô và kiểm tra lại: 24 ảnh, 571 hình (559 vật + 12 ignore_region).
- QC sau sửa, seed 73: 0/8 ảnh và 0/206 đối tượng có lỗi được ghi nhận; cùng quy trình kiểm, chưa có người kiểm độc lập.
- **Quyết định hiện tại: Release sau rework**, theo ngưỡng quan sát của lượt kiểm tra lại. Kết quả Rework lần đầu và giới hạn mẫu nhỏ được giữ trong REPORT mục 7.
