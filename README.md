# HR Management Application

## Mô tả
Ứng dụng quản lý nhân sự dựa trên mô-đun SAP ERP HCM, sử dụng Python, Tkinter, và SQLite.

## Cài đặt
1. Cài đặt Python 3.9 hoặc cao hơn.
2. Cài đặt các thư viện:
```commandline
pip install -r requirements.txt
```
3. Chạy ứng dụng:
```commandline
python main.py
```
4. Đóng gói thành file .exe (tùy chọn):
```commandline
pyinstaller --onefile main.py
```
## Cấu trúc thư mục
- `src/ui/`: Chứa giao diện chính.
- `src/logic/`: Chứa logic xử lý cho từng chức năng.
- `src/db/`: Quản lý cơ sở dữ liệu.
- `main.py`: Tệp chạy ứng dụng.

## Chức năng
- Quản lý nhân viên (thêm, sửa, xóa, tìm kiếm).
- Ghi nhận chấm công.
- Quản lý hồ sơ ứng viên.
- Tạo báo cáo lương.
- Nhận và trả lời phản hồi.