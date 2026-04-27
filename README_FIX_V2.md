# Bản V2 FIX

Đã sửa:
- Trang xã/phường dễ đọc hơn: 36 mục/trang, chữ lớn hơn.
- Poster chính luôn xuất trước: `00_poster_full`.
- Tự xóa file cũ của tỉnh trước khi generate, tránh hiện nhầm trang cũ.
- Có nút tải tất cả ảnh dạng ZIP.
- Bổ sung `import re` để tránh lỗi NameError.

Cách cập nhật trên GitHub:
1. Giải nén file zip này.
2. Upload đè toàn bộ file lên repo cũ.
3. Commit changes.
4. Vào Streamlit Cloud → Reboot app.
