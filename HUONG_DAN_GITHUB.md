# Hướng dẫn: dùng GitHub làm nơi đăng version phần mềm

Mục tiêu cuối cùng:
- Có 1 trang GitHub chứa toàn bộ mã nguồn.
- Mỗi khi ra bản mới, bạn chỉ cần "gắn tag" version (vd `v1.1.0`) → GitHub
  **tự động build** file `.exe` và đăng lên mục **Releases**.
- App bạn đang dùng sẽ **tự kiểm tra** xem có bản mới hơn không mỗi khi mở lên.

Làm theo đúng thứ tự các bước dưới đây, không cần biết dòng lệnh phức tạp —
dùng **GitHub Desktop** (phần mềm có giao diện, kéo-thả) là đủ.

---

## Bước 1 — Tạo tài khoản GitHub

1. Vào https://github.com/signup
2. Đăng ký bằng email, đặt username (username này bạn sẽ cần nhớ, vd:
   `nguyenvana123`).
3. Xác nhận email.

## Bước 2 — Tạo Repository (kho chứa code)

1. Đăng nhập GitHub, bấm nút xanh **"New"** (hoặc vào
   https://github.com/new).
2. Điền:
   - **Repository name**: ví dụ `pinout-tool` (không dấu, không cách).
   - **Public** (để ai cũng tải được bản .exe) hoặc **Private** (chỉ mình
     bạn/người được mời thấy) — tuỳ bạn.
   - Tick **"Add a README file"**.
3. Bấm **Create repository**.
4. Ghi lại đường dẫn dạng: `https://github.com/<username>/pinout-tool`

## Bước 3 — Cài GitHub Desktop (để đưa code lên mà không cần gõ lệnh)

1. Tải tại: https://desktop.github.com
2. Cài đặt, đăng nhập bằng tài khoản GitHub vừa tạo ở Bước 1.

## Bước 4 — Đưa toàn bộ project lên GitHub

1. Mở GitHub Desktop → **File → Clone repository**.
2. Chọn đúng repo `pinout-tool` bạn vừa tạo → chọn thư mục lưu về máy (vd
   `Documents/GitHub/pinout-tool`) → **Clone**.
3. Copy toàn bộ file trong thư mục `pinout_tool` (main.py, README.md,
   data/, .gitignore, .github/...) mà mình gửi bạn, dán đè vào đúng thư mục
   vừa clone ở bước trên (giữ nguyên cấu trúc thư mục con).
4. Quay lại GitHub Desktop, bạn sẽ thấy danh sách file thay đổi hiện ra bên
   trái. Ở góc dưới trái, gõ nội dung ví dụ: `Bản đầu tiên` vào ô "Summary",
   rồi bấm **Commit to main**.
5. Bấm **Push origin** ở thanh trên cùng để đẩy code lên GitHub.
6. Vào lại trang `https://github.com/<username>/pinout-tool` trên trình
   duyệt để xác nhận code đã lên đó.

## Bước 5 — Gắn đúng username/repo vào code (để app tự kiểm tra bản mới)

1. Mở file `main.py` bằng IDLE hoặc Notepad.
2. Tìm 2 dòng gần đầu file:
   ```python
   GITHUB_OWNER = "your-github-username"   # <-- doi thanh username GitHub cua ban
   GITHUB_REPO = "pinout-tool"             # <-- doi thanh ten repo cua ban
   ```
3. Sửa thành đúng username và tên repo bạn vừa tạo, ví dụ:
   ```python
   GITHUB_OWNER = "nguyenvana123"
   GITHUB_REPO = "pinout-tool"
   ```
4. Lưu file, rồi lặp lại Bước 4 (commit + push) để đẩy thay đổi này lên
   GitHub.

## Bước 6 — Ra bản mới bằng cách "gắn tag" (GitHub tự build file .exe)

Mỗi khi bạn sửa code xong và muốn ra bản mới:

1. Mở file `main.py`, tìm dòng:
   ```python
   APP_VERSION = "1.0.0"
   ```
   Sửa thành số phiên bản mới, ví dụ `"1.1.0"`. Lưu lại.
2. Commit + Push thay đổi này lên GitHub (như Bước 4).
3. Trong GitHub Desktop, vào menu **History**, chuột phải vào commit vừa
   push → **Create Tag...** → gõ đúng dạng `v1.1.0` (nhớ chữ **v** ở đầu,
   khớp với số bạn vừa sửa trong `APP_VERSION`).
4. Bấm **Push origin** thêm 1 lần nữa để đẩy tag lên.
5. Vào tab **Actions** trên trang GitHub của bạn
   (`https://github.com/<username>/pinout-tool/actions`) — bạn sẽ thấy 1
   quy trình đang chạy tên **"Build and Release Windows EXE"**. Đợi khoảng
   2-3 phút cho nó chạy xong (dấu tích xanh).
6. Sau khi xong, vào tab **Releases**
   (`https://github.com/<username>/pinout-tool/releases`) — sẽ thấy bản
   `v1.1.0` mới với file `ECU_Pinout_Tool.exe` đính kèm sẵn, sẵn sàng để
   chia sẻ link tải cho người dùng.

Từ giờ, mỗi lần ra bản mới bạn chỉ lặp lại đúng 6 bước này (sửa số version →
commit/push → gắn tag → push tag) — không cần cài PyInstaller hay tự build
file .exe trên máy mình nữa, GitHub làm hộ.

## Bước 7 — Cách app tự báo cho người dùng khi có bản mới

Đây là tự động, không cần làm gì thêm:
- Mỗi khi mở app, sau ~1.5 giây, app sẽ âm thầm hỏi GitHub xem bản mới nhất
  trong mục Releases là bản nào.
- Nếu bản đó mới hơn `APP_VERSION` đang chạy, app hiện hộp thoại hỏi người
  dùng có muốn mở trang tải về không.
- Người dùng cũng có thể tự bấm kiểm tra bất cứ lúc nào qua menu
  **Help → Kiểm tra bản cập nhật...**
- Nếu không có mạng, app im lặng bỏ qua (không làm phiền), trừ khi người
  dùng chủ động bấm kiểm tra thủ công.

## Lưu ý quan trọng

- Số trong `APP_VERSION` (trong `main.py`) và tên tag bạn gắn trên GitHub
  (`v1.1.0`) phải khớp nhau (chỉ khác chữ `v` ở đầu tag).
- Tag phải theo đúng dạng `v<số>.<số>.<số>` (ví dụ `v1.0.0`, `v1.2.3`,
  `v2.0.0`) để quy trình tự động trên GitHub nhận diện và chạy.
- Nếu để repo **Private**, người dùng cần đăng nhập GitHub mới tải được file
  ở mục Releases. Nếu muốn ai cũng tải được không cần tài khoản, để repo
  **Public**.
