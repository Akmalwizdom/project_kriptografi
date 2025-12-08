# Prompt: Refactoring UI untuk 4 File Template Sisa

## Konteks
anda telah berhasil memperbarui `base.html`, `index.html`, dan `upload.html` menggunakan tema baru (**Dark Mode**, **Slate-900**, **Glassmorphism**).

Sekarang, tolong bantu saya **menyamakan desain (refactor UI)** untuk **4 file sisa** agar konsisten dengan tema baru tersebut.

---

## File yang Perlu Diperbaiki

1. `templates/select_algorithm.html`
2. `templates/result_encrypt.html`
3. `templates/result_decrypt.html`
4. `templates/test_results.html` ⚠️ **Penting:** Chart.js perlu update warna

---

## Design System (Context dari `base.html` baru)

### Background
- **Body Background:** `bg-slate-900` (sudah ada di body base.html)

### Text
- **Utama:** `text-white` atau `text-slate-50`
- **Sekunder:** `text-slate-400`

### Container Card
- **Gunakan class custom:** `.glass-panel` (sudah ada di CSS base) untuk pembungkus konten utama
- **Style reference:**
  ```css
  bg-slate-900/60 backdrop-blur-md border border-white/10 shadow-2xl rounded-2xl
  ```

### Accent Colors
- **Blue:** `#319fe8` / `text-accent-blue`
- **Gold:** `#fec972` / `text-accent-gold`

### Font
- **Font family:** Gunakan font **'Outfit'** (sudah di-load di base)

---

## Instruksi Spesifik per Halaman

### 1. Select Algorithm (`select_algorithm.html`)
- **Kartu pilihan AES dan Blowfish:**
  - Ubah menjadi `.glass-panel` dengan efek hover
  - Class hover: `hover:border-accent-blue` atau `hover:border-accent-gold`
- **Icon SVG:**
  - Ganti menjadi style **outline** yang lebih halus
- **Layout:**
  - Pastikan responsif menggunakan **Grid**

---

### 2. Result Pages (`result_encrypt.html` & `result_decrypt.html`)

#### Struktur Umum
- **Informasi file:**
  - Bungkus dalam satu `.glass-panel` besar yang rapi

#### Button Styling
- **Tombol "Download":**
  - Gunakan style **Primary** (Gradient Blue)
- **Tombol Sekunder** (Kembali/Hapus Sesi):
  - Gunakan style **Ghost/Outline**
  - Class: `text-slate-400 hover:text-white`

#### Khusus `result_decrypt.html`
- **Container Video Preview:**
  - Pastikan terlihat elegan
  - Gunakan border tipis dan shadow

---

### 3. Test Results (`test_results.html`) ⚠️ **PENTING**

#### Tabel
- **Style:** Ubah menjadi **Modern Dark Table**
- **Header:**
  ```css
  bg-slate-800 text-slate-200
  ```
- **Row:**
  ```css
  border-b border-slate-700 hover:bg-slate-800/50
  ```

#### Chart.js Config 📊
- **Masalah saat ini:** Kode JS untuk Chart masih menggunakan warna lama (`#fee3b3`)
- **Yang perlu diubah:**
  - **Ticks, grid lines, label** → ubah menjadi warna `slate-400` atau `slate-500` agar terlihat di background gelap
  - **Grid lines** → harus samar menggunakan `rgba(255,255,255,0.1)`

---

## Deliverables

Berikan **kode lengkap** untuk keempat file tersebut yang sudah mewarisi:

```html
{% extends "base.html" %}
```

---

## Checklist Konsistensi

- [ ] Semua file menggunakan `.glass-panel` untuk container utama
- [ ] Warna teks konsisten (`text-white`, `text-slate-400`)
- [ ] Accent colors hanya untuk highlight (blue/gold)
- [ ] Button styling seragam (Primary gradient, Secondary ghost)
- [ ] Chart.js menggunakan palette dark mode
- [ ] Layout responsif dengan spacing yang lega
- [ ] Hover effects smooth dan konsisten