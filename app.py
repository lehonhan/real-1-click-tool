
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
    outs = sorted(Path("output").glob(f"*{province.replace(' ','_')}*.png"))
    if not outs:
        outs = sorted(Path("output").glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)[:3]
    for p in outs:
        st.image(str(p), caption=p.name, use_container_width=True)
        st.download_button("Tải ảnh " + p.name, open(p, "rb"), file_name=p.name)
