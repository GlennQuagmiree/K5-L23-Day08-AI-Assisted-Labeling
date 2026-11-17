# Thông tin học viên

- Họ và tên: Hà Huy Dũng
- MSHV: 2A202603271
- Lớp (L2 / L3 / khác): L2
- Tài khoản GitHub: hdung25
- Repo bài nộp (URL): https://github.com/hdung25/K5-L2-Day08-HaHuyDung-2A202603271-AI-Assisted-Labeling
- Commit chốt bài (hash): 2605449f048cb4aa8c87a40e1c05e8fa53e539bd (nội dung bài; commit sau chỉ điền dòng này)
- Máy: Windows 11 Home, GPU NVIDIA GeForce RTX 3050 Laptop 4 GB (CUDA, torch 2.6.0+cu124), Python 3.11.9
- CVAT (Docker): v2.74.1 (Docker Desktop, WSL2)

## Kết quả tóm tắt

- Cách thực hiện: tôi sử dụng Claude Code cho phần chuẩn bị, chạy mô hình và soạn nháp; Codex tạo nhãn tham chiếu, hỗ trợ review và QC. Chi tiết khai báo tại REPORT mục 8; không coi đây là gán tay hoặc review thủ công độc lập.

- Lượt review đầu: accepted 429/505 = 85,0%; edited 22/505 = 4,4%; deleted 50/505 = 9,9%; added 89/540 = 16,5%.
- So với 69 vật tham chiếu: máy có precision 51/72 = 70,8%; recall 51/69 = 73,9%. Tập tham chiếu không phải gold gán tay độc lập.
- Bắt bẫy lần đầu: 8/12 = 66,7%.
- Thời gian: tạo nhãn tham chiếu 5,94/4 = 1,49 phút/ảnh; review 13,14/24 = 0,55 phút/ảnh; nghỉ 0 phút. Không phải phép đo thao tác thủ công độc lập.
- QC trước sửa: 4/8 ảnh lỗi = 50,0%; 6/213 đối tượng lỗi = 2,8%. Đã lưu sửa 4 ảnh trong labels/qc_fixed.json.
- Bản tổng hợp sau sửa QC: 24 ảnh, 562 hình (550 vật + 12 ignore_region).
- **Quyết định: Rework.** Điểm bẫy lần đầu và QC chưa đạt ngưỡng; cần lượt rà toàn lô và QC độc lập trước Release.
