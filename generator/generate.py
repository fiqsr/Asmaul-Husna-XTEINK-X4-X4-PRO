import os
import sys
import json
import struct
import shutil
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import qrcode

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

# Reshapers
harakat_reshaper = arabic_reshaper.ArabicReshaper(
    configuration={
        'delete_harakat': False,
        'support_ligatures': True
    }
)

cover_reshaper = arabic_reshaper.ArabicReshaper(
    configuration={
        'delete_harakat': True,
        'support_ligatures': True
    }
)

def render_content_arabic(text):
    return get_display(harakat_reshaper.reshape(text))

def render_cover_arabic(text):
    return get_display(cover_reshaper.reshape(text))

# Fonts
f_cover_ar = ImageFont.truetype(os.path.join(win_fonts, "tahomabd.ttf"), 48)
f_cover_title = ImageFont.truetype(os.path.join(win_fonts, "segoeuib.ttf"), 34)
f_cover_sub = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 22)
f_cover_meta_bold = ImageFont.truetype(os.path.join(win_fonts, "segoeuib.ttf"), 16)
f_cover_meta = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 13)

# Info page fonts
f_info_head = ImageFont.truetype(os.path.join(win_fonts, "segoeuib.ttf"), 22)
f_info_sub = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 14)
f_info_sec = ImageFont.truetype(os.path.join(win_fonts, "segoeuib.ttf"), 14)
f_info_bold = ImageFont.truetype(os.path.join(win_fonts, "segoeuib.ttf"), 13)
f_info_reg = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 12)
f_info_url = ImageFont.truetype(os.path.join(win_fonts, "segoeuib.ttf"), 12)

# Content Fonts
f_no = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 13)
f_ar = ImageFont.truetype(amiri_path, 46)
f_latin = ImageFont.truetype(os.path.join(win_fonts, "segoeuib.ttf"), 22)
f_arti = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 16)
f_page_num = ImageFont.truetype(os.path.join(win_fonts, "segoeuib.ttf"), 16)

# Penutup Fonts
f_penutup_ar = ImageFont.truetype(amiri_path, 38)
f_penutup_arti = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 16)
f_penutup_meta = ImageFont.truetype(os.path.join(win_fonts, "segoeui.ttf"), 13)

def wrap_text(text, max_chars=36):
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
    right_x = 424

    # 1. Arabic Title (Tahoma Bold, right-aligned to right_x, Y = 240)
    ar_bidi = render_cover_arabic("الأسماء الحسنى")
    bb_ar = draw.textbbox((0, 0), ar_bidi, font=f_cover_ar)
    draw.text((right_x - (bb_ar[2] - bb_ar[0]), 240), ar_bidi, fill=0, font=f_cover_ar)

    # 2. Main Title: Asma'ul Husna (right-aligned, Y = 375)
    title = "Asma'ul Husna"
    bb_t = draw.textbbox((0, 0), title, font=f_cover_title)
    draw.text((right_x - (bb_t[2] - bb_t[0]), 375), title, fill=0, font=f_cover_title)

    # 3. Subtitle: 99 Nama-Nama Agung Allah (right-aligned, Y = 420)
    sub = "99 Nama-Nama Agung Allah"
    bb_s = draw.textbbox((0, 0), sub, font=f_cover_sub)
    draw.text((right_x - (bb_s[2] - bb_s[0]), 420), sub, fill=0, font=f_cover_sub)

    # 4. Bottom Right-aligned Metadata block with user's info
    meta_lines = [
        ("99 Asma • Teks Arab, Latin & Arti", f_cover_meta_bold, 563),
        ("Edisi Khusus Xteink X4 & X4 Pro", f_cover_meta, 594),
        ("Disusun oleh: fiqsr", f_cover_meta, 614),
        ("github.com/fiqsr", f_cover_meta, 635),
        ("v 1.0 - 2026", f_cover_meta, 656),
    ]

    for line, fn, y_pos in meta_lines:
        bb = draw.textbbox((0, 0), line, font=fn)
        draw.text((right_x - (bb[2] - bb[0]), y_pos), line, fill=0, font=fn)

    return img

def render_info_page():
    img = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(img)

    # Header
    head = "Informasi & Sumber Proyek"
    bb_h = draw.textbbox((0, 0), head, font=f_info_head)
    draw.text(((width - (bb_h[2] - bb_h[0])) // 2, 40), head, fill=0, font=f_info_head)

    sub = "Asma'ul Husna untuk Xteink X4 & X4 Pro"
    bb_s = draw.textbbox((0, 0), sub, font=f_info_sub)
    draw.text(((width - (bb_s[2] - bb_s[0])) // 2, 70), sub, fill=60, font=f_info_sub)

    # Divider
    draw.line([(32, 98), (width - 32, 98)], fill=120, width=1)

    # Sources & Attributions Block
    left_x = 42
    cur_y = 115

    sections = [
        ("Penyusun & Repositori", [
            ("Kompilasi & Desain:", "fiqsr (github.com/fiqsr)"),
            ("Format Target:", "Xteink X4 & X4 Pro (480×800 E-Ink)"),
        ]),
        ("Sumber Data & Referensi", [
            ("API Data:", "github.com/haikelz/asmaul-husna-api"),
            ("Harakat & Tasykil:", "github.com/adiman-dev/islamic-json"),
            ("Format & Arsitektur:", "github.com/andidewanto/xteink-x4-quran-indonesia"),
            ("Font Teks Arab:", "Amiri Font (SIL Open Font License)"),
        ])
    ]

    for sec_title, sec_items in sections:
        draw.text((left_x, cur_y), sec_title, fill=0, font=f_info_sec)
        cur_y += 22
        for lbl, val in sec_items:
            draw.text((left_x + 8, cur_y), lbl, fill=0, font=f_info_bold)
            bb_lbl = draw.textbbox((0, 0), lbl, font=f_info_bold)
            w_lbl = bb_lbl[2] - bb_lbl[0]
            draw.text((left_x + 8 + w_lbl + 8, cur_y + 1), val, fill=40, font=f_info_reg)
            cur_y += 19
        cur_y += 10

    # Divider before QR Code
    draw.line([(32, cur_y + 4), (width - 32, cur_y + 4)], fill=160, width=1)
    cur_y += 18

    # QR Code generation
    repo_url = "https://github.com/fiqsr/Asmaul-Husna-XTEINK-X4-X4-PRO"
    qr = qrcode.QRCode(
        version=1,
        box_size=5,
        border=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M
    )
    qr.add_data(repo_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("L")
    
    qr_size = 190
    qr_img = qr_img.resize((qr_size, qr_size), Image.NEAREST)
    qr_x = (width - qr_size) // 2
    qr_y = cur_y
    img.paste(qr_img, (qr_x, qr_y))

    # Border around QR Code
    draw.rectangle([(qr_x - 3, qr_y - 3), (qr_x + qr_size + 2, qr_y + qr_size + 2)], outline=180, width=1)

    cur_y += qr_size + 14

    # QR Code instruction / label
    qr_labels = [
        "Pindai QR code di atas untuk membuka repositori:",
        "github.com/fiqsr/Asmaul-Husna-XTEINK-X4-X4-PRO",
        "Dapatkan rilis .XTC & .EPUB terbaru atau bagikan proyek ini",
    ]
    for i, lbl in enumerate(qr_labels):
        fn = f_info_url if i == 1 else f_info_reg
        bb = draw.textbbox((0, 0), lbl, font=fn)
        w = bb[2] - bb[0]
        draw.text(((width - w) // 2, cur_y), lbl, fill=0 if i == 1 else 60, font=fn)
        cur_y += 18

    # Bottom footer
    ft = "Xteink X4 & X4 Pro E-Reader Edition • v 1.0 - 2026"
    bb_f = draw.textbbox((0, 0), ft, font=f_info_sub)
    draw.text(((width - (bb_f[2] - bb_f[0])) // 2, 762), ft, fill=80, font=f_info_sub)

    return img

def render_content_page(page_items, page_num):
    img = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(img)

    slot_tops = [16, 260, 504]
    slot_h = 244

    for i, item in enumerate(page_items):
        sy = slot_tops[i]

        # 1. Asma Number (100% FIXED Y: sy + 16)
        no_str = f"ASMA {item['urutan']} / 99"
        bb_no = draw.textbbox((0, 0), no_str, font=f_no)
        w_no = bb_no[2] - bb_no[0]
        draw.text(((width - w_no) // 2, sy + 16), no_str, fill=90, font=f_no)

        # 2. Arabic with Full Harakat (100% FIXED Y: sy + 44)
        ar_bidi = render_content_arabic(item['arab'])
        bb_ar = draw.textbbox((0, 0), ar_bidi, font=f_ar)
        w_ar = bb_ar[2] - bb_ar[0]
        draw.text(((width - w_ar) // 2, sy + 44), ar_bidi, fill=0, font=f_ar)

        # 3. Latin Name (100% FIXED Y: sy + 136)
        bb_lat = draw.textbbox((0, 0), item['latin'], font=f_latin)
        w_lat = bb_lat[2] - bb_lat[0]
        draw.text(((width - w_lat) // 2, sy + 136), item['latin'], fill=0, font=f_latin)

        # 4. Arti / Translation (100% FIXED Y: sy + 170)
        arti_lines = wrap_text(item['arti'], max_chars=36)
        cur_arti_y = sy + 170
        for line in arti_lines:
            bb_line = draw.textbbox((0, 0), line, font=f_arti)
            w_line = bb_line[2] - bb_line[0]
            draw.text(((width - w_line) // 2, cur_arti_y), line, fill=20, font=f_arti)
            cur_arti_y += 22

        # Symmetrical divider line between cards (at sy + 244)
        if i < 2:
            draw.line([(32, sy + slot_h), (width - 32, sy + slot_h)], fill=140, width=1)

    # Page number at bottom (Centered, FIXED Y: 764)
    p_str = str(page_num)
    bb_p = draw.textbbox((0, 0), p_str, font=f_page_num)
    w_p = bb_p[2] - bb_p[0]
    draw.text(((width - w_p) // 2, 764), p_str, fill=0, font=f_page_num)

    return img

def render_penutup():
    img = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(img)

    # Centered Ayat Quran with full harakat in Amiri
    ar_verse = "وَلِلَّهِ الْأَسْمَاءُ الْحُسْنَىٰ فَادْعُوهُ بِهَا"
    ar_bidi = render_content_arabic(ar_verse)
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
        "Asma'ul Husna untuk Xteink X4 & X4 Pro",
        "Disusun oleh fiqsr • github.com/fiqsr",
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

print("1. Rendering Rata Kanan Cover...")
cover_img = render_cover()
all_pages.append(cover_img)

print("2. Rendering Info & QR Code Page...")
info_img = render_info_page()
all_pages.append(info_img)

print("3. Rendering 33 Content Pages (Fixed Grid)...")
for p_idx in range(0, 99, 3):
    chunk = items[p_idx:p_idx+3]
    page_num = (p_idx // 3) + 1
    p_img = render_content_page(chunk, page_num)
    all_pages.append(p_img)

print("4. Rendering Penutup...")
penutup_img = render_penutup()
all_pages.append(penutup_img)

print(f"Total pages rendered: {len(all_pages)} (Expected 36)")

# Save preview images
preview_dir = "docs/preview"
os.makedirs(preview_dir, exist_ok=True)
cover_img.save(os.path.join(preview_dir, "00-sampul.png"))
info_img.save(os.path.join(preview_dir, "01-informasi.png"))
all_pages[2].save(os.path.join(preview_dir, "02-halaman-01.png")) # Page 1 of Asma (items 1-3)
all_pages[26].save(os.path.join(preview_dir, "03-halaman-73-75.png")) # Page 25 of Asma (items 73-75)
penutup_img.save(os.path.join(preview_dir, "04-penutup.png"))
print("Preview images saved.")

xtg_blobs = [image_to_xtg(img) for img in all_pages]
xtc_bytes = build_xtc(xtg_blobs)

with open("Asmaul-Husna.xtc", "wb") as f:
    f.write(xtc_bytes)

print(f"SUCCESS! Asmaul-Husna.xtc compiled ({len(xtc_bytes) / 1024:.1f} KB)")
