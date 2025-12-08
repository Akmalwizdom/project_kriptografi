# Prompt: Refactoring UI/UX untuk Aplikasi Web Enkripsi Video

## Peran
Bertindaklah sebagai **Senior UI/UX Designer** dan **Frontend Developer** ahli Tailwind CSS.

---

## Konteks Proyek
Saya memiliki aplikasi web enkripsi video (Flask) dengan file template HTML yang sudah ada.

### Kondisi Saat Ini
- **Desain saat ini** menggunakan background biru terang (`#016bb8`) dengan teks kuning pucat (`#fee3b3`)
- **Masalah yang dihadapi:**
  - Meskipun kontrasnya tinggi, warna ini **terlalu saturasi (menyolok)** untuk penggunaan jangka panjang
  - Membuat **mata cepat lelah**
  - **Hierarki visual datar** karena hanya mengandalkan border (garis tepi) tanpa kedalaman (shadow/layer)

---

## Tugas
**Refactor kode HTML dan Tailwind CSS** pada template saya untuk meningkatkan **Keterbacaan (Readability)** dan **User Experience (UX)**.

---

## Panduan Style Baru

### 1. Palet Warna (Modern Tech Theme)
- **Background utama:** Ubah menjadi **Deep Navy/Slate** (contoh: `bg-slate-900` atau `#0f172a`) agar lebih elegan dan mengurangi silau
- **Accent Color:** Gunakan warna biru `#319fe8` dan emas `#fec972` **hanya sebagai aksen** (tombol, ikon, link aktif), **bukan warna dominan**
- **Teks utama:** Ubah menjadi **Off-White/Light Gray** (`#f8fafc`) untuk kenyamanan membaca

### 2. Prinsip UI (Card & Depth)
- **Ganti gaya "Border Only"** pada Card menjadi gaya **Glassmorphism** atau **Soft Surface**
- **Gunakan:**
  ```css
  bg-white/5 backdrop-blur-sm border border-white/10 shadow-xl rounded-2xl
  ```
- **Whitespace:** Berikan jarak (padding/margin) yang lebih lega agar desain tidak terasa padat

### 3. Interaktivitas (Hover & Focus)

#### Button
- Buat tombol memiliki **efek lift** saat di-hover:
  ```css
  hover:-translate-y-1 hover:shadow-lg
  ```
- Pastikan ada **indikator visual jelas** saat tombol ditekan:
  ```css
  active:scale-95
  ```

#### Input Form
- Tambahkan `focus:ring` dan **transisi warna border** yang halus saat user mengetik

### 4. Tipografi
- **Saran:** Import font **Google Fonts** (seperti 'Inter' atau 'Outfit') agar terlihat lebih modern daripada font bawaan sistem

---

## Deliverables
Tolong berikan **kode revisi lengkap** untuk file:
1. `base.html`
2. `index.html`
3. `upload.html`

dengan menerapkan prinsip-prinsip di atas.