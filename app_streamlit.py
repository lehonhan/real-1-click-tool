
import streamlit as st
import csv, tempfile, os, subprocess, sys
from pathlib import Path
from PIL import Image

st.set_page_config(page_title="1-Click Province Poster Generator", layout="wide")
st.title("REAL 1-CLICK TOOL — Ảnh + text chuẩn dữ liệu")
st.write("Chọn tỉnh/thành, tải ảnh nền MAP không chữ nếu có, bấm Generate.")

data_path = Path("data/34_tinh_data.csv")
rows = list(csv.DictReader(open(data_path, encoding="utf-8-sig")))
names = [r["display_title"] for r in rows]
province = st.selectbox("Tỉnh/thành", names)
uploaded = st.file_uploader("Ảnh nền MAP không chữ (tùy chọn)", type=["png","jpg","jpeg","webp"])

map_path = None
if uploaded:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    tmp.write(uploaded.read()); tmp.close()
    map_path = tmp.name

if st.button("GENERATE 1 CLICK", type="primary"):
    cmd = [sys.executable, "generate_one_click.py", "--province", province, "--data", str(data_path), "--outdir", "output"]
    if map_path:
        cmd += ["--map-image", map_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    st.code(result.stdout + result.stderr)
    # Display current province outputs: MAP, LANDMARKS, FOOD, then COMMUNES pages
    import re, zipfile, io
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", province)
    outs = sorted(Path("output").glob(f"{safe}_*.png"))

    if outs:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
            for fp in outs:
                z.write(fp, arcname=fp.name)
        st.success(f"Đã tạo {len(outs)} ảnh cho {province}.")
        st.download_button("Tải tất cả ảnh PNG (.zip)", zip_buffer.getvalue(), file_name=f"{safe}_output.zip")
    else:
        st.warning("Chưa thấy file output. Hãy bấm Generate lại hoặc xem log phía trên.")

    for fp in outs:
        st.subheader(fp.name)
        st.image(str(fp), caption=fp.name, use_container_width=True)
        st.download_button("Tải ảnh " + fp.name, open(fp, "rb"), file_name=fp.name)
