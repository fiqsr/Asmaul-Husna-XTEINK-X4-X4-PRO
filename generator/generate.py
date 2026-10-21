import os
import sys
import json
import struct
import shutil
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load full harakat dataset
with open('asmaul_husna_full_harakat.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

# Save to asmaul_husna.json as well
with open('asmaul_husna.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

width, height = 480, 800
amiri_path = "Amiri-Regular.ttf"
win_fonts = 'C:\\Windows\\Fonts'

# Fonts
f_cover_ar = ImageFont.truetype(amiri_path, 56)
f_cover_title = ImageFont.truetype(os.path.join(win_fonts, "segoeuib.ttf"), 34)
f_cover_sub = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 20)
f_cover_meta = ImageFont.truetype(os.path.join(win_fonts, "segoeuib.ttf"), 15)
f_cover_sumber = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 13)

f_no = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 13)
f_ar = ImageFont.truetype(amiri_path, 48)
f_latin = ImageFont.truetype(os.path.join(win_fonts, "segoeuib.ttf"), 23)
f_arti = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 17)
f_page_num = ImageFont.truetype(os.path.join(win_fonts, "segoeuib.ttf"), 17)

f_penutup_ar = ImageFont.truetype(amiri_path, 38)
f_penutup_arti = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 16)
f_penutup_meta = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 13)

reshaper = arabic_reshaper.ArabicReshaper(
    configuration={
        'delete_harakat': False,
        'support_ligatures': True
    }
)

def render_arabic(text, font=None):
    reshaped = reshaper.reshape(text)
    return get_display(reshaped)

def wrap_text(text, max_chars=38):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        if len(cur + " " + w) <= max_chars:
            cur = (cur + " " + w).strip()
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def render_cover():
    img = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(img)

    # 1. Arabic Title with full harakat: الْأَسْمَاءُ الْحُسْنَىٰ (Centered horizontally, Y = 220)
    ar_bidi = render_arabic("الْأَسْمَاءُ الْحُسْنَىٰ", f_cover_ar)
    bb_ar = draw.textbbox((0, 0), ar_bidi, font=f_cover_ar)
    w_ar = bb_ar[2] - bb_ar[0]
    draw.text(((width - w_ar) // 2, 220), ar_bidi, fill=0, font=f_cover_ar)

    # 2. Main Title: Asma'ul Husna (Centered, Y = 360)
    title = "Asma'ul Husna"
    bb_t = draw.textbbox((0, 0), title, font=f_cover_title)
    w_t = bb_t[2] - bb_t[0]
    draw.text(((width - w_t) // 2, 360), title, fill=0, font=f_cover_title)

    # 3. Subtitle: 99 Nama-Nama Agung Allah (Centered, Y = 405)
    sub = "99 Nama-Nama Agung Allah"
    bb_s = draw.textbbox((0, 0), sub, font=f_cover_sub)
    w_s = bb_s[2] - bb_s[0]
    draw.text(((width - w_s) // 2, 405), sub, fill=0, font=f_cover_sub)

    # 4. Bottom Right-aligned Metadata block
    right_x = width - 48
    meta_lines = [
        ("99 Asma • Teks Arab, Latin & Arti", f_cover_meta, 560),
        ("Sumber Data: Asmaul Husna API", f_cover_sumber, 592),
        ("Repository: haikelz/asmaul-husna-api", f_cover_sumber, 612),
        ("Format XTC Khusus Perangkat Xteink X4", f_cover_sumber, 632),
        ("v 1.0 - 2026", f_cover_sumber, 652),
    ]

    for l, fn, y_pos in meta_lines:
        bb = draw.textbbox((0, 0), l, font=fn)
        w = bb[2] - bb[0]
        draw.text((right_x - w, y_pos), l, fill=0, font=fn)

    return img

def render_content_page(page_items, page_num):
    img = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(img)

    slot_starts = [24, 268, 512]
    slot_height = 236

    for i, item in enumerate(page_items):
        sy = slot_starts[i]

        # 1. Asma number (Centered, subtle)
        no_str = f"ASMA {item['urutan']} / 99"
        bb_no = draw.textbbox((0, 0), no_str, font=f_no)
        w_no = bb_no[2] - bb_no[0]
        draw.text(((width - w_no) // 2, sy), no_str, fill=90, font=f_no)

        # 2. Arabic with FULL HARAKAT (Amiri font, Centered!)
        ar_bidi = render_arabic(item['arab'], f_ar)
        bb_ar = draw.textbbox((0, 0), ar_bidi, font=f_ar)
        w_ar = bb_ar[2] - bb_ar[0]
        ar_y = sy + 22
        draw.text(((width - w_ar) // 2, ar_y), ar_bidi, fill=0, font=f_ar)

        # 3. Latin (Centered, Bold)
        lat_y = ar_y + (bb_ar[3] - bb_ar[1]) + 14
        bb_lat = draw.textbbox((0, 0), item['latin'], font=f_latin)
        w_lat = bb_lat[2] - bb_lat[0]
        draw.text(((width - w_lat) // 2, lat_y), item['latin'], fill=0, font=f_latin)

        # 4. Arti (Centered, properly word-wrapped, NO truncation!)
        arti_lines = wrap_text(item['arti'], max_chars=38)
        cur_arti_y = lat_y + (bb_lat[3] - bb_lat[1]) + 8
        for line in arti_lines:
            bb_line = draw.textbbox((0, 0), line, font=f_arti)
            w_line = bb_line[2] - bb_line[0]
            draw.text(((width - w_line) // 2, cur_arti_y), line, fill=20, font=f_arti)
            cur_arti_y += 22

        # Symmetrical divider line between items
        if i < 2:
            div_y = sy + slot_height - 6
            draw.line([(32, div_y), (width - 32, div_y)], fill=120, width=1)

    # Page number at bottom (Centered)
    p_str = str(page_num)
    bb_p = draw.textbbox((0, 0), p_str, font=f_page_num)
    w_p = bb_p[2] - bb_p[0]
    draw.text(((width - w_p) // 2, 762), p_str, fill=0, font=f_page_num)

    return img

def render_penutup():
    img = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(img)

    # Centered Ayat Quran with full harakat
    ar_verse = "وَلِلَّهِ الْأَسْمَاءُ الْحُسْنَىٰ فَادْعُوهُ بِهَا"
    ar_bidi = render_arabic(ar_verse, f_penutup_ar)
    bb_ar = draw.textbbox((0, 0), ar_bidi, font=f_penutup_ar)
    w_ar = bb_ar[2] - bb_ar[0]
    draw.text(((width - w_ar) // 2, 275), ar_bidi, fill=0, font=f_penutup_ar)

    # Divider
    draw.line([(180, 345), (300, 345)], fill=0, width=1)

    # Translation
    lines = [
        "“Hanya milik Allah asmaaul husna,",
        "maka bermohonlah kepada-Nya",
        "dengan menyebut asmaaul husna itu.”",
        "",
        "QS. Al-A'raf: 180"
    ]
    cur_y = 375
    for l in lines:
        if not l:
            cur_y += 10
            continue
        bb = draw.textbbox((0, 0), l, font=f_penutup_arti)
        w = bb[2] - bb[0]
        draw.text(((width - w) // 2, cur_y), l, fill=0, font=f_penutup_arti)
        cur_y += 24

    # Bottom notes
    cur_y = 650
    notes = [
        "Asma'ul Husna untuk Xteink X4",
        "API: haikelz/asmaul-husna-api",
        "Format Project: andidewanto/xteink-x4-quran-indonesia",
        "Selesai Dibaca • 99 Asma"
    ]
    for n in notes:
        bb = draw.textbbox((0, 0), n, font=f_penutup_meta)
        w = bb[2] - bb[0]
        draw.text(((width - w) // 2, cur_y), n, fill=60, font=f_penutup_meta)
        cur_y += 20

    return img

def image_to_xtg(pil_img):
    byte_stride = width // 8
    data = bytearray(byte_stride * height)
    pixels = pil_img.load()
    for y in range(height):
        row_offset = y * byte_stride
        for x in range(width):
            if pixels[x, y] >= 160:
                data[row_offset + (x >> 3)] |= (1 << (7 - (x & 7)))

    header = bytearray(22)
    header[0:4] = b"XTG\x00"
    header[4:6] = struct.pack("<H", width)
    header[6:8] = struct.pack("<H", height)
    header[10:14] = struct.pack("<I", len(data))
    return header + data

def build_xtc(xtg_blobs):
    total = len(xtg_blobs)
    idx_start = 56
    data_start = idx_start + total * 16
    total_size = data_start + sum(len(b) for b in xtg_blobs)

    buf = bytearray(total_size)
    buf[0:4] = b"XTC\x00"
    buf[4] = 1
    buf[6:8] = struct.pack("<H", total)
    buf[12:16] = struct.pack("<I", 1)
    buf[24:32] = struct.pack("<Q", idx_start)
    buf[32:40] = struct.pack("<Q", data_start)

    cursor = data_start
    for i, blob in enumerate(xtg_blobs):
        entry = idx_start + i * 16
        buf[entry:entry+8] = struct.pack("<Q", cursor)
        buf[entry+8:entry+12] = struct.pack("<I", len(blob))
        buf[entry+12:entry+14] = struct.pack("<H", 480)
        buf[entry+14:entry+16] = struct.pack("<H", 800)
        buf[cursor:cursor+len(blob)] = blob
        cursor += len(blob)

    return buf

# Main Generation
all_pages = []

print("Rendering Symmetrical Cover...")
cover_img = render_cover()
all_pages.append(cover_img)

for p_idx in range(0, 99, 3):
    chunk = items[p_idx:p_idx+3]
    page_num = (p_idx // 3) + 1
    p_img = render_content_page(chunk, page_num)
    all_pages.append(p_img)

print("Rendering Symmetrical Penutup...")
penutup_img = render_penutup()
all_pages.append(penutup_img)

print(f"Total pages rendered: {len(all_pages)}")

# Save preview images
preview_dir = "docs/preview"
os.makedirs(preview_dir, exist_ok=True)
cover_img.save(os.path.join(preview_dir, "00-sampul.png"))
all_pages[1].save(os.path.join(preview_dir, "01-halaman.png"))
all_pages[4].save(os.path.join(preview_dir, "02-halaman.png")) # Page 4 (Items 10-12)
penutup_img.save(os.path.join(preview_dir, "03-penutup.png"))
print("Preview images saved.")

xtg_blobs = [image_to_xtg(img) for img in all_pages]
xtc_bytes = build_xtc(xtg_blobs)

with open("Asmaul-Husna.xtc", "wb") as f:
    f.write(xtc_bytes)

print(f"SUCCESS! Asmaul-Husna.xtc compiled ({len(xtc_bytes) / 1024:.1f} KB)")
