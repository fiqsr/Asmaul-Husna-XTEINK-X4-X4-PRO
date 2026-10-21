# Generator Asma'ul Husna untuk Xteink X4

Generator ini dibuat untuk merender 99 Asma'ul Husna ke format `.xtc` (dan `.epub`) yang dioptimalkan langsung untuk layar e-ink **Xteink X4** (480 × 800 piksel).

Format dan alur generator mengadaptasi proyek [xteink-x4-quran-indonesia](https://github.com/andidewanto/xteink-x4-quran-indonesia) oleh Andi Dewanto.

## Cara Menjalankan

### Opsi 1: Menggunakan Web Generator (Browser)

Buka langsung file `index.html` di browser Anda (Google Chrome, Edge, Firefox):

```bash
# Atau jalankan server lokal:
python -m http.server 8000
# Buka http://127.0.0.1:8000
```

1. Anda dapat melihat pratinjau langsung 35 halaman pada kanvas 480 × 800 px.
2. Gunakan tombol **Prev** dan **Next** untuk berpindah halaman.
3. Tekan tombol **EXPORT .XTC** di pojok kanan atas untuk merender seluruh halaman menjadi berkas biner `Asmaul-Husna.xtc`.

### Opsi 2: Menggunakan CLI Python (`generate.py`)

Jika Anda ingin menghasilkan berkas `.xtc` secara instan tanpa browser:

```bash
python generate.py
```

Skrip ini akan langsung merender 35 halaman (Cover, 33 Halaman Isi @ 3 Asma, dan Halaman Penutup) menggunakan Pillow dan mengekspornya ke `../xtc/Asmaul-Husna.xtc`.

## Spesifikasi Format `.xtc`

- **Resolusi Kanvas:** 480 × 800 px.
- **Konversi 1-bit:** Ambang batas luminans 160 (`terang = R*0.299 + G*0.587 + B*0.114`).
- **Blok XTG:** Header 22 byte (`XTG\0`, lebar 480, tinggi 800, panjang data 48000 byte) + 48000 byte bitmap data per halaman.
- **Kontainer XTC:** Magic `XTC\0`, header 56 byte, tabel indeks per halaman (16 byte per entri), diikuti urutan blob data XTG.
