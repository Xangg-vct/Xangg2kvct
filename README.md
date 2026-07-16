# ECU PINOUT TOOL

App desktop tra cứu pinout ECU theo hãng xe / dòng ECU, mô phỏng theo giao diện
"MEDC17 EGPT PINOUT TOOL": cây danh mục bên trái, ảnh connector + nhãn chú
thích chân bên phải, hỗ trợ zoom/pan ảnh.

## 1. Chạy trên máy (Windows/Mac/Linux)

Cần Python 3.9+ (Windows tải tại https://www.python.org/downloads, nhớ tick
"Add Python to PATH" lúc cài).

```bash
pip install pillow
python main.py
```

## 2. Cấu trúc project

```
pinout_tool/
├─ main.py                # code chính, không cần sửa khi thêm dữ liệu
├─ data/
│  ├─ pinouts.json        # danh sách hãng xe / dòng ECU / vị trí pin
│  └─ images/              # ảnh connector ECU (bạn tự bỏ vào)
└─ README.md
```

## 3. Thêm hãng xe / dòng ECU / ảnh pinout mới

Không cần sửa `main.py`. Chỉ cần:

1. Bỏ ảnh connector (png/jpg) vào `data/images/`.
2. Mở `data/pinouts.json`, thêm một model mới vào brand tương ứng
   (hoặc thêm cả brand mới):

```json
"FAL": {
  "label": "FAL",
  "models": {
    "MED17.3.3": {
      "title": "BOSCH_MED17.3.3_IROM_TC1793_EGPT_FAL",
      "version": "v.02.00",
      "subtitle": ["ECU CONNECTOR / CONNETTORE ECU / CONNECTEUR ECU"],
      "image": "images/FAL_MED17_3_3.png",
      "pins": [
        { "x": 0.79, "y": 0.20, "label": "PIN 5, 86 = +12V", "color": "#e74c3c" }
      ]
    }
  }
}
```

- `x`, `y`: toạ độ **tỉ lệ** (0.0 → 1.0) theo chiều rộng/cao ảnh gốc, không
  phải pixel — nhờ vậy nhãn luôn đúng vị trí dù ảnh to/nhỏ khác nhau. Cách xác
  định nhanh: mở ảnh trong Paint/GIMP, xem toạ độ pixel con trỏ, rồi chia cho
  chiều rộng/cao ảnh.
- `color`: mã màu hex cho chấm tròn + nhãn (ví dụ đỏ = nguồn, xanh dương =
  tín hiệu, xanh lá = CAN...).
- Nếu chưa có ảnh, app vẫn chạy bình thường và hiện khung placeholder báo
  đường dẫn ảnh còn thiếu.

Sau khi sửa `pinouts.json`, vào app bấm **File → Tải lại dữ liệu** (hoặc
phím **F5**) — không cần khởi động lại chương trình.

## 4. Đóng gói thành file .exe chạy trên Windows (không cần cài Python)

Trên máy Windows đã cài Python + pillow:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "data;data" --name "ECU_Pinout_Tool" main.py
```

File `.exe` sẽ nằm trong thư mục `dist/`. Copy cả file `.exe` này đi là chạy
được, không cần cài Python trên máy khác — nhưng nếu bạn cập nhật
`pinouts.json`/ảnh sau này, cần đóng gói lại (hoặc để `data/` bên cạnh file
.exe và sửa `main.py` để đọc từ thư mục đó thay vì bundle cứng — có thể yêu
cầu mình chỉnh nếu bạn cần workflow này).

## 5. Các chức năng đã có

- Tìm kiếm nhanh brand/model ở ô "Tìm" phía trên cây danh mục.
- Zoom bằng lăn chuột hoặc nút +/-, kéo chuột để pan ảnh, nút "Reset view".
- Placeholder tự động khi ảnh chưa có.
- Đổi dữ liệu không cần build lại code (F5 để tải lại).
- **In ra PDF**: nhấn `Ctrl+P`, hoặc menu File → "In ra PDF...", hoặc nút
  "In PDF (Ctrl+P)" ở thanh dưới. File PDF chứa tiêu đề, phiên bản, subtitle,
  ảnh connector và toàn bộ nhãn pin — được vẽ lại độc lập với mức zoom/pan
  đang xem trên màn hình, nên luôn nét và đúng vị trí.
- **Nút gạt sáng/tối**: nút bên phải thanh công cụ dưới cùng (🌙/☀) đổi toàn
  bộ giao diện (cây danh mục, banner tiêu đề, khung ảnh) giữa chế độ sáng và
  tối, không cần khởi động lại app.

## 6. Việc bạn cần làm tiếp theo

Gửi mình (hoặc tự thêm theo hướng dẫn mục 3):
- Ảnh connector ECU cho từng dòng máy.
- Toạ độ + nhãn từng chân (pin) cần chú thích.
- Danh sách đầy đủ các hãng/dòng ECU nếu khác với khung mẫu hiện tại (hiện
  đã dựng sẵn 25 hãng như trong ảnh bạn gửi, riêng FAL có 4 dòng mẫu, trong
  đó MED17.3.3 có sẵn 6 pin mẫu để bạn thấy cách hoạt động).

## 7. Quản lý phiên bản & đăng bản mới lên GitHub

Project đã có sẵn:
- `APP_VERSION` khai báo trong `main.py`.
- App tự kiểm tra bản mới trên GitHub Releases mỗi khi mở lên (menu
  **Help → Kiểm tra bản cập nhật...** để kiểm tra thủ công).
- File `.github/workflows/build.yml` — tự động build `.exe` và đăng Release
  khi bạn gắn tag phiên bản (không cần tự chạy PyInstaller).

Xem hướng dẫn từng bước chi tiết (tạo tài khoản, tạo repo, đưa code lên,
ra bản mới) tại file **`HUONG_DAN_GITHUB.md`** đi kèm.
