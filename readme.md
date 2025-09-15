# Toc6Tect

Toc6Tect adalah aplikasi berbasis website yang berfungsi untuk **mendeteksi komentar toxic pada platform YouTube**.  
Dengan aplikasi ini, pengguna maupun content creator dapat mengetahui tingkat kecenderungan toxic pada komentar di video mereka sehingga bisa mengambil keputusan lebih tepat terhadap interaksi yang ada.

---

## 🚀 Deskripsi Project

Aplikasi ini mengintegrasikan model **machine learning** yang telah dilatih untuk melakukan prediksi komentar toxic.  
Selain itu, Toc6Tect juga dilengkapi dengan bot **scraping YouTube** untuk mengambil komentar secara otomatis dari video yang dipilih.

🔹 **Sasaran aplikasi**:

- Content creator YouTube yang ingin memahami kualitas interaksi pada videonya.
- Peneliti atau pihak lain yang membutuhkan data mengenai komentar toxic di suatu video.

---

## ✨ Fitur Utama

1. **Prediksi Komentar Toxic**

   - Pengguna dapat melakukan prediksi komentar toxic pada video YouTube.
   - Cukup dengan input **URL video**, sistem akan melakukan scraping komentar dan menjalankan prediksi menggunakan model.
   - Hasil prediksi ditampilkan dalam antarmuka beserta **data statistik**.

2. **Histori Prediksi**
   - Pengguna yang memiliki akun terdaftar dapat menyimpan hasil prediksi.
   - Hasil prediksi yang tersimpan dapat dilihat kembali pada menu histori.

---

## 🛠️ Teknologi yang Digunakan

- **Frontend**: Next.js
- **Backend**: Node.js (Express)
- **Database**: PostgreSQL
- **Machine Learning Model**: Python (Scikit-learn / TensorFlow / PyTorch)
- **Scraping**: YouTube API / Custom bot

---
