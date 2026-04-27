
import csv, os, argparse, textwrap, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920

def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "arial.ttf"
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size=size)
        except Exception:
            pass
    return ImageFont.load_default()

F_TITLE = font(92, True)
F_SUB = font(34, True)
F_H = font(34, True)
F_TEXT = font(24, False)
F_SMALL = font(20, False)
F_BOLD = font(24, True)

GOLD = (207, 168, 78)
DARK = (13, 48, 62)
PAPER = (247, 237, 213)
WHITE = (255, 255, 248)
INK = (32, 28, 23)

def read_data(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def find_province(rows, name):
    name_u = name.strip().upper()
    for r in rows:
        if name_u in r["display_title"].upper() or name_u in r["province_source_name"].upper():
            return r
    raise ValueError(f"Không tìm thấy tỉnh/thành: {name}")

def split_list(s):
    return [x.strip() for x in s.split(";") if x.strip()]

def fit_cover(img, box):
    bw, bh = box
    iw, ih = img.size
    scale = max(bw/iw, bh/ih)
    nw, nh = int(iw*scale), int(ih*scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    return img.crop(((nw-bw)//2, (nh-bh)//2, (nw+bw)//2, (nh+bh)//2))

def gradient_bg():
    img = Image.new("RGB", (W,H), (20,55,70))
    pix = img.load()
    for y in range(H):
        for x in range(W):
            t = y/H
            # top warm -> bottom teal
            r = int(245*(1-t)+13*t)
            g = int(216*(1-t)+54*t)
            b = int(150*(1-t)+68*t)
            pix[x,y] = (r,g,b)
    return img

def rounded_panel(draw, xy, fill, outline=GOLD, radius=22, width=3):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_text_shadow(draw, pos, text, fnt, fill, shadow=(0,0,0), anchor=None, stroke=0):
    x,y = pos
    draw.text((x+2,y+2), text, font=fnt, fill=shadow+(120,) if len(shadow)==3 else shadow, anchor=anchor, stroke_width=stroke)
    draw.text((x,y), text, font=fnt, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(80,60,30) if stroke else None)

def draw_column_list(draw, title, items, x, y, w, h, cols=1, color=WHITE, max_items=None):
    rounded_panel(draw, (x,y,x+w,y+h), fill=(8,55,72), radius=18)
    draw.text((x+24,y+18), title, font=F_H, fill=GOLD)
    items = items[:max_items] if max_items else items
    top = y+68
    col_w = (w-40)//cols
    rows_per_col = math.ceil(len(items)/cols)
    for i, item in enumerate(items):
        col = i//rows_per_col
        row = i%rows_per_col
        tx = x+24+col*col_w
        ty = top + row*28
        if ty < y+h-28:
            draw.text((tx,ty), f"{i+1}. {item}", font=F_SMALL, fill=color)

def draw_card_list(draw, title, items, x, y, w, h, cols=2):
    rounded_panel(draw, (x,y,x+w,y+h), fill=PAPER, outline=(220,190,125), radius=18)
    draw.text((x+w//2,y+24), title, font=F_H, fill=(98,74,35), anchor="ma")
    top = y+90
    gap = 10
    card_h = 34
    col_w = (w-40-(cols-1)*gap)//cols
    rows_per_col = math.ceil(len(items)/cols)
    for i, item in enumerate(items):
        col = i//rows_per_col
        row = i%rows_per_col
        cx = x+20+col*(col_w+gap)
        cy = top+row*(card_h+8)
        if cy+card_h > y+h-20: continue
        draw.rounded_rectangle((cx,cy,cx+col_w,cy+card_h), radius=8, fill=(255,252,239), outline=(220,205,170))
        draw.text((cx+10,cy+7), f"{i+1}. {item}", font=F_SMALL, fill=INK)

def make_poster(data, map_image=None, out="poster.png"):
    title = data["display_title"]
    communes = split_list(data["communes_visual_40"])
    old_units = split_list(data["old_units"])
    landmarks = split_list(data["landmarks"])
    foods = split_list(data["foods"])

    canvas = Image.new("RGB", (W,H), (246,238,218))
    draw = ImageDraw.Draw(canvas)

    # main map area
    if map_image and os.path.exists(map_image):
        img = Image.open(map_image).convert("RGB")
        map_area = fit_cover(img, (680, 790))
    else:
        map_area = gradient_bg().crop((0,0,680,790))
    canvas.paste(map_area, (0,0))
    # dark overlay for readability top
    overlay = Image.new("RGBA",(680,180),(0,0,0,70))
    canvas.paste(overlay,(0,0),overlay)

    # title
    draw_text_shadow(draw, (340,48), title, F_TITLE, (240,205,125), anchor="ma", stroke=1)
    draw_text_shadow(draw, (340,145), "FULL MAP 2026", F_SUB, WHITE, anchor="ma")

    # right commune panel
    draw_column_list(draw, "CÁC XÃ / PHƯỜNG", communes, 690, 10, 380, 780, cols=2, max_items=40)

    # lower panels on map
    draw_column_list(draw, "ĐƠN VỊ CŨ", old_units, 8, 650, 300, 250, cols=1, max_items=9)
    draw_column_list(draw, "ĐỊA DANH NỔI BẬT", landmarks, 320, 650, 350, 250, cols=2, max_items=18)

    # commune list slide style embedded
    draw_card_list(draw, f"DANH SÁCH XÃ / PHƯỜNG {title}", communes, 8, 920, 530, 520, cols=2)

    # landmarks mini panel
    rounded_panel(draw, (548,920,1072,1440), fill=(232,242,244), outline=(200,220,225), radius=18)
    draw.text((810,948), f"ĐỊA DANH NỔI BẬT {title}", font=F_H, fill=(32,68,90), anchor="ma")
    # Simple scenic placeholders
    grid_x, grid_y = 575, 1010
    card_w, card_h = 150, 120
    for idx, lm in enumerate(landmarks[:9]):
        col, row = idx%3, idx//3
        x = grid_x+col*165; y = grid_y+row*138
        draw.rounded_rectangle((x,y,x+card_w,y+card_h), radius=12, fill=(245,250,250), outline=(190,210,215))
        draw.ellipse((x+35,y+15,x+115,y+70), fill=(80,145,95))
        draw.rectangle((x+50,y+45,x+100,y+75), fill=(186,135,65))
        label = lm[:20] + ("…" if len(lm)>20 else "")
        draw.text((x+card_w//2,y+84), label.upper(), font=font(15, True), fill=(25,60,80), anchor="ma")

    # food section bottom
    rounded_panel(draw, (8,1460,1072,1910), fill=(250,238,215), outline=(220,190,125), radius=20)
    draw.text((540,1488), f"ẨM THỰC TRUYỀN THỐNG {title}", font=font(44, True), fill=(105,67,34), anchor="ma")
    draw.text((540,1540), "TINH HOA ĐỊA PHƯƠNG", font=F_SUB, fill=(145,94,43), anchor="ma")
    n = min(8, len(foods))
    card_w = (1040 - (n-1)*10)//n if n else 120
    for i, food in enumerate(foods[:8]):
        x = 22 + i*(card_w+10); y = 1595
        draw.rounded_rectangle((x,y,x+card_w,y+280), radius=15, fill=(255,249,234), outline=(220,205,170))
        # food icon
        draw.ellipse((x+18,y+18,x+card_w-18,y+118), fill=(230,190,130), outline=(180,120,60), width=3)
        draw.ellipse((x+35,y+35,x+card_w-35,y+100), fill=(165,85,45))
        draw.text((x+card_w//2,y+138), food.upper(), font=font(18, True), fill=INK, anchor="ma")
        desc = "Đặc sản địa phương,\nhương vị truyền thống."
        draw.multiline_text((x+card_w//2,y+168), desc, font=font(14, False), fill=(70,60,50), anchor="ma", align="center")

    canvas.save(out, quality=95)
    return out


def make_commune_slide(data, out="communes.png"):
    title = data["display_title"]
    communes = split_list(data["communes_full"])
    pages = []
    per_page = 36  # 3 columns x 12 rows, larger and easier to read
    for page_start in range(0, len(communes), per_page):
        items = communes[page_start:page_start+per_page]
        page_no = len(pages) + 1
        img = Image.new("RGB",(W,H),(247,237,213))
        d = ImageDraw.Draw(img)

        d.text((W//2,85), "DANH SÁCH XÃ / PHƯỜNG", font=font(56, True), fill=(135,101,48), anchor="ma")
        d.text((W//2,155), title, font=font(64, True), fill=(105,78,36), anchor="ma")
        d.text((W//2,220), f"THÔNG TIN CẬP NHẬT 2026 — TRANG {page_no}", font=font(26, True), fill=(120,95,55), anchor="ma")

        x, y, w, h = 58, 285, 964, 1500
        rounded_panel(d, (x,y,x+w,y+h), fill=PAPER, outline=(220,190,125), radius=24, width=3)

        cols = 3
        gap_x = 18
        gap_y = 16
        card_w = (w - 60 - (cols-1)*gap_x) // cols
        card_h = 54
        top = y + 42
        left = x + 30

        for i, item in enumerate(items):
            col = i % cols
            row = i // cols
            cx = left + col * (card_w + gap_x)
            cy = top + row * (card_h + gap_y)
            d.rounded_rectangle((cx,cy,cx+card_w,cy+card_h), radius=12, fill=(255,252,239), outline=(215,198,160), width=2)
            d.text((cx+14, cy+14), f"{page_start+i+1}. {item}", font=font(22, True), fill=INK)

        d.text((W//2,1830), "DỮ LIỆU XÃ / PHƯỜNG ĐƯỢC CHÈN BẰNG TEXT THẬT — KHÔNG PHẢI AI TỰ VIẾT", font=font(20, True), fill=(130,100,60), anchor="ma")

        page_out = out.replace(".png", f"_{page_no}.png")
        img.save(page_out, quality=95)
        pages.append(page_out)
    return pages



def make_map_slide(data, map_image=None, out="map.png"):
    title = data["display_title"]
    landmarks = split_list(data["landmarks"])
    img = Image.new("RGB", (W,H), (20,55,70))
    if map_image and os.path.exists(map_image):
        bg = fit_cover(Image.open(map_image).convert("RGB"), (W,H))
        img.paste(bg, (0,0))
    else:
        bg = gradient_bg()
        img.paste(bg, (0,0))
    d = ImageDraw.Draw(img)
    d.rectangle((0,0,W,260), fill=(0,0,0,80))
    draw_text_shadow(d, (W//2,60), title, F_TITLE, (240,205,125), anchor="ma", stroke=1)
    draw_text_shadow(d, (W//2,160), "FULL MAP 2026", F_SUB, WHITE, anchor="ma")
    # Landmark legend panel
    rounded_panel(d, (60, 1360, W-60, 1850), fill=(8,55,72), radius=24)
    d.text((W//2,1390), "ĐỊA DANH NỔI BẬT", font=F_H, fill=GOLD, anchor="ma")
    for i, lm in enumerate(landmarks[:12]):
        col = i % 2
        row = i // 2
        x = 100 + col*460
        y = 1450 + row*55
        d.text((x,y), f"• {lm}", font=F_BOLD, fill=WHITE)
    img.save(out, quality=95)
    return out

def make_landmark_slide(data, out="landmarks.png"):
    title = data["display_title"]
    landmarks = split_list(data["landmarks"])
    img = Image.new("RGB",(W,H),(232,242,244))
    d = ImageDraw.Draw(img)
    d.text((W//2,75), f"CÁC ĐỊA DANH NỔI BẬT", font=font(54, True), fill=(32,68,90), anchor="ma")
    d.text((W//2,145), title, font=font(62, True), fill=(32,68,90), anchor="ma")
    grid_x, grid_y = 70, 250
    card_w, card_h = 290, 250
    gap_x, gap_y = 35, 40
    for idx, lm in enumerate(landmarks[:12]):
        col, row = idx%3, idx//3
        x = grid_x+col*(card_w+gap_x); y = grid_y+row*(card_h+gap_y)
        d.rounded_rectangle((x,y,x+card_w,y+card_h), radius=20, fill=(248,252,252), outline=(190,210,215), width=2)
        # simple 3D island placeholder
        d.ellipse((x+70,y+40,x+220,y+140), fill=(72,140,88))
        d.rectangle((x+105,y+95,x+185,y+145), fill=(186,135,65))
        d.polygon([(x+95,y+95),(x+145,y+55),(x+195,y+95)], fill=(120,75,45))
        d.text((x+card_w//2,y+170), lm.upper(), font=font(22, True), fill=(25,60,80), anchor="ma")
        d.text((x+card_w//2,y+205), "Địa danh tiêu biểu", font=font(17, False), fill=(70,90,100), anchor="ma")
    img.save(out, quality=95)
    return out

def make_food_slide(data, out="food.png"):
    title = data["display_title"]
    foods = split_list(data["foods"])
    img = Image.new("RGB",(W,H),(250,238,215))
    d = ImageDraw.Draw(img)
    d.text((W//2,75), f"ẨM THỰC TRUYỀN THỐNG {title}", font=font(46, True), fill=(105,67,34), anchor="ma")
    d.text((W//2,135), "TINH HOA ĐỊA PHƯƠNG", font=F_SUB, fill=(145,94,43), anchor="ma")
    start_y = 230
    card_h = 185
    for i, food in enumerate(foods[:8]):
        y = start_y + i*(card_h+20)
        if y+card_h > H-60: break
        d.rounded_rectangle((70,y,1010,y+card_h), radius=24, fill=(255,249,234), outline=(220,205,170), width=2)
        d.ellipse((105,y+25,265,y+160), fill=(230,190,130), outline=(180,120,60), width=3)
        d.ellipse((135,y+55,235,y+130), fill=(165,85,45))
        d.text((310,y+45), food.upper(), font=font(34, True), fill=INK)
        d.text((310,y+95), "Hương vị địa phương, giàu bản sắc và dễ nhớ.", font=font(24, False), fill=(70,60,50))
    img.save(out, quality=95)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--province", required=True, help="Tên tỉnh/thành, ví dụ: Huế")
    ap.add_argument("--data", default="data/34_tinh_data.csv")
    ap.add_argument("--map-image", default=None, help="Ảnh nền map/diorama không chữ, tùy chọn")
    ap.add_argument("--outdir", default="output")
    args = ap.parse_args()
    rows = read_data(args.data)
    data = find_province(rows, args.province)
    outdir = Path(args.outdir); outdir.mkdir(exist_ok=True, parents=True)
    safe = re.sub(r"[^A-Za-z0-9_-]+","_",data["display_title"])
    for old_file in outdir.glob(f"{safe}_*.png"):
        try:
            old_file.unlink()
        except Exception:
            pass
    map_slide = outdir/f"{safe}_01_MAP.png"
    landmark_slide = outdir/f"{safe}_02_LANDMARKS.png"
    food_slide = outdir/f"{safe}_03_FOOD.png"
    communes = outdir/f"{safe}_04_COMMUNES.png"

    make_map_slide(data, args.map_image, str(map_slide))
    make_landmark_slide(data, str(landmark_slide))
    make_food_slide(data, str(food_slide))
    commune_pages = make_commune_slide(data, str(communes))

    print("DONE")
    print(map_slide)
    print(landmark_slide)
    print(food_slide)
    for p in commune_pages:
        print(p)

if __name__ == "__main__":
    main()
