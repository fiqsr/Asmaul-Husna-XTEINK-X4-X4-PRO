import os
import sys
import json
import struct
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load data
with open('asmaul_husna.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f"Loaded {len(items)} Asmaul Husna items.")

# Fonts
win_fonts = 'C:\\Windows\\Fonts'
f_cover_ar = ImageFont.truetype(os.path.join(win_fonts, "tahomabd.ttf"), 64)
f_cover_title = ImageFont.truetype(os.path.join(win_fonts, "segoeuib.ttf"), 38)
f_cover_sub = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 24)
f_cover_meta = ImageFont.truetype(os.path.join(win_fonts, "segoeuib.ttf"), 16)
f_cover_sumber = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 14)

f_item_no = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 14)
f_item_ar = ImageFont.truetype(os.path.join(win_fonts, "tahomabd.ttf"), 46)
f_item_latin = ImageFont.truetype(os.path.join(win_fonts, "segoeuib.ttf"), 24)
f_item_arti = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 19)
f_page_num = ImageFont.truetype(os.path.join(win_fonts, "segoeuib.ttf"), 17)

f_penutup_ar = ImageFont.truetype(os.path.join(win_fonts, "tahomabd.ttf"), 34)
f_penutup_arti = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 16)
f_penutup_meta = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 13)

def render_arabic(text, font, max_width=432):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

def render_cover():
    img = Image.new("L", (480, 800), 255)
    draw = ImageDraw.Draw(img)
    
    # 1. Arabic Title at Y = 214
    ar_bidi = render_arabic("الأسماء الحسنى", f_cover_ar)
    bb_ar = draw.textbbox((0, 0), ar_bidi, font=f_cover_ar)
    w_ar = bb_ar[2] - bb_ar[0]
    draw.text((480 - 54 - w_ar, 214), ar_bidi, fill=0, font=f_cover_ar)
    
    # 2. Nama at Y = 350
    title = "Asma'ul Husna"
    bb_t = draw.textbbox((0, 0), title, font=f_cover_title)
    w_t = bb_t[2] - bb_t[0]
    draw.text((480 - 54 - w_t, 350), title, fill=0, font=f_cover_title)
    
    # 3. Arti at Y = 405
    sub = "99 Nama-Nama Agung Allah"
    bb_s = draw.textbbox((0, 0), sub, font=f_cover_sub)
    w_s = bb_s[2] - bb_s[0]
    draw.text((480 - 54 - w_s, 405), sub, fill=0, font=f_cover_sub)
    
    # 4. Meta at Y = 550
    meta = "99 Asma • Teks Arab, Latin & Arti"
    bb_m = draw.textbbox((0, 0), meta, font=f_cover_meta)
    w_m = bb_m[2] - bb_m[0]
    draw.text((480 - 54 - w_m, 550), meta, fill=0, font=f_cover_meta)
    
    # 5. Sumber at Y = 592
    sumber_lines = [
        "Sumber Data: Asmaul Husna API",
        "Repository: haikelz/asmaul-husna-api",
        "Format XTC Khusus Perangkat Xteink X4",
        "v 1.0 - 2026"
    ]
    cur_y = 592
    for sl in sumber_lines:
        bb = draw.textbbox((0, 0), sl, font=f_cover_sumber)
        w = bb[2] - bb[0]
        draw.text((480 - 54 - w, cur_y), sl, fill=0, font=f_cover_sumber)
        cur_y += 20
        
    return img

def render_content_page(page_items, page_num):
    img = Image.new("L", (480, 800), 255)
    draw = ImageDraw.Draw(img)
    
    # Margin
    left = 24
    right = 480 - 24
    
    y = 26
    for i, item in enumerate(page_items):
        if i > 0:
            draw.line([(left, y), (right, y)], fill=0, width=1)
            y += 16
            
        # Asma number top right
        no_str = f"Asma {item['urutan']} / 99"
        bb_no = draw.textbbox((0, 0), no_str, font=f_item_no)
        w_no = bb_no[2] - bb_no[0]
        draw.text((right - w_no, y), no_str, fill=60, font=f_item_no)
        y += 22
        
        # Arabic text right aligned
        ar_bidi = render_arabic(item['arab'], f_item_ar)
        bb_ar = draw.textbbox((0, 0), ar_bidi, font=f_item_ar)
        w_ar = bb_ar[2] - bb_ar[0]
        draw.text((right - w_ar, y), ar_bidi, fill=0, font=f_item_ar)
        y += (bb_ar[3] - bb_ar[1]) + 14
        
        # Latin text left aligned
        draw.text((left, y), item['latin'], fill=0, font=f_item_latin)
        bb_lat = draw.textbbox((0, 0), item['latin'], font=f_item_latin)
        y += (bb_lat[3] - bb_lat[1]) + 4
        
        # Arti left aligned
        # Handle long text wrap if needed
        arti_text = item['arti']
        if len(arti_text) > 42:
            # simple wrap
            words = arti_text.split()
            line1, line2 = "", ""
            for w in words:
                if len(line1 + " " + w) <= 40:
                    line1 = (line1 + " " + w).strip()
                else:
                    line2 = (line2 + " " + w).strip()
            draw.text((left, y), line1, fill=0, font=f_item_arti)
            y += 22
            draw.text((left, y), line2, fill=0, font=f_item_arti)
            y += 22
        else:
            draw.text((left, y), arti_text, fill=0, font=f_item_arti)
            bb_art = draw.textbbox((0, 0), arti_text, font=f_item_arti)
            y += (bb_art[3] - bb_art[1]) + 18
            
    # Page number at bottom
    p_str = str(page_num)
    bb_p = draw.textbbox((0, 0), p_str, font=f_page_num)
    w_p = bb_p[2] - bb_p[0]
    draw.text(((480 - w_p) // 2, 755), p_str, fill=0, font=f_page_num)
    
    return img

def render_penutup():
    img = Image.new("L", (480, 800), 255)
    draw = ImageDraw.Draw(img)
    
    # Centered Ayat Quran
    ar_verse = "وَلِلَّهِ الْأَسْمَاءُ الْحُسْنَىٰ فَادْعُوهُ بِهَا"
    ar_bidi = render_arabic(ar_verse, f_penutup_ar)
    bb_ar = draw.textbbox((0, 0), ar_bidi, font=f_penutup_ar)
    w_ar = bb_ar[2] - bb_ar[0]
    draw.text(((480 - w_ar) // 2, 280), ar_bidi, fill=0, font=f_penutup_ar)
    
    # Divider
    draw.line([(180, 350), (300, 350)], fill=0, width=1)
    
    # Translation
    lines = [
        "“Hanya milik Allah asmaaul husna,",
        "maka bermohonlah kepada-Nya",
        "dengan menyebut asmaaul husna itu.”",
        "",
        "QS. Al-A'raf: 180"
    ]
    cur_y = 380
    for l in lines:
        if not l:
            cur_y += 10
            continue
        bb = draw.textbbox((0, 0), l, font=f_penutup_arti)
        w = bb[2] - bb[0]
        draw.text(((480 - w) // 2, cur_y), l, fill=0, font=f_penutup_arti)
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
        draw.text(((480 - w) // 2, cur_y), n, fill=60, font=f_penutup_meta)
        cur_y += 20
        
    return img

def image_to_xtg(pil_img):
    width, height = 480, 800
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
    buf[4] = 1 # version 1
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

# Main build process
all_pages = []

# Page 0: Cover
print("Rendering Cover...")
cover_img = render_cover()
all_pages.append(cover_img)

# Content pages: 3 items per page (33 pages)
for p_idx in range(0, 99, 3):
    chunk = items[p_idx:p_idx+3]
    page_num = (p_idx // 3) + 1
    p_img = render_content_page(chunk, page_num)
    all_pages.append(p_img)

# Penutup page
print("Rendering Penutup...")
penutup_img = render_penutup()
all_pages.append(penutup_img)

print(f"Total pages rendered: {len(all_pages)}")

# Convert each page to XTG
xtg_blobs = [image_to_xtg(img) for img in all_pages]
print(f"Generated {len(xtg_blobs)} XTG blobs (each {len(xtg_blobs[0])} bytes)")

# Build XTC
xtc_bytes = build_xtc(xtg_blobs)
output_xtc = "Asmaul-Husna.xtc"
with open(output_xtc, "wb") as f:
    f.write(xtc_bytes)

print(f"SUCCESS! Created {output_xtc} ({len(xtc_bytes) / 1024:.1f} KB)")
