# REAL 1-CLICK TOOL — ONLINE DEPLOY VERSION

## Cách đưa lên chạy online miễn phí bằng Streamlit Community Cloud

### Bước 1 — Tạo GitHub repo
1. Vào GitHub.com
2. Tạo repository mới, ví dụ: `real-1-click-tool`
3. Upload toàn bộ file trong thư mục này lên repo

### Bước 2 — Deploy lên Streamlit
1. Vào share.streamlit.io
2. Đăng nhập bằng GitHub
3. Chọn `New app`
4. Repository: chọn repo vừa upload
5. Main file path: `app.py`
6. Bấm Deploy

### Bước 3 — Dùng tool online
Sau khi deploy, Streamlit sẽ cho bạn 1 link dạng:
`https://ten-app.streamlit.app`

Bạn chỉ cần:
1. Mở link
2. Chọn tỉnh/thành
3. Upload ảnh nền MAP không chữ nếu có
4. Bấm GENERATE 1 CLICK
5. Tải ảnh PNG

## Ghi chú
- Tool dùng dữ liệu 34 tỉnh và 3.321 xã/phường đã nằm trong `data/34_tinh_data.csv`
- Nếu muốn cập nhật dữ liệu, thay file CSV trong thư mục `data`
- Ảnh nền nên là ảnh không chữ để text tiếng Việt được overlay chuẩn 100%

## Chạy local
```bash
pip install -r requirements.txt
streamlit run app.py
```
