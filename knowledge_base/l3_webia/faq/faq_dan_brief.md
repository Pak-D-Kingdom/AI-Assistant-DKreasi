# FAQ, SEO Disclaimer, Add-on & Panduan Pemesanan WEBIA

## 1. Alur Pemesanan Cepat & Aktivasi Website Bisnis (Guest Checkout Sistem Baru)
WEBIA menggunakan sistem **Guest Checkout & Auto-Provisioning Akun**, sehingga calon klien tidak perlu repot mendaftar akun terlebih dahulu:
1. **Pilih Paket & Template**: Klien memilih paket di `#paket-website` atau melihat koleksi template di `/webia/koleksi`.
2. **Checkout Langsung (Guest Checkout)**: Klien langsung mengisi formulir pemesanan di `/orders/create` (Nama, Email, No. WhatsApp, Pilihan Paket, dan Add-on jika ada).
3. **Pembayaran Otomatis**: Klien membayar melalui Payment Gateway Midtrans (QRIS, Virtual Account BCA/Mandiri/BRI/BNI, GoPay, Kartu Kredit) dengan verifikasi otomatis real-time, atau transfer manual.
4. **Pemberian Akun Otomatis via Email**: Begitu pesanan dibuat, sistem WEBIA otomatis membuatkan akun klien dan mengirimkan kredensial resmi (Email & Password login acak) langsung ke email pemesan.
5. **Pengisian Data Bisnis di Dashboard**: Klien masuk ke `/login` menggunakan akun yang dikirimkan ke email, membuka Dashboard (`/dashboard`), dan mengisi formulir Data Bisnis (Nama usaha, tagline, WhatsApp CS, alamat kota, Google Maps, deskripsi, dan Instagram).
6. **Live di Subdomain Klien**: Setelah tim memproses website dan mengonfigurasi AI Chatbot (L4), website resmi dapat diakses publik melalui tautan resmi `/s/{site_slug}` (lengkap dengan sub-halaman `/menu` atau `/reservasi`).

## 2. 5 Tahapan Timeline Pengerjaan Pesanan di Dashboard Klien
Klien dapat memantau progres pengerjaan website secara transparan melalui menu **Pesanan Saya** (`/orders/{id}`) dengan 5 tahapan visual:
1. **Pending**: Menunggu pembayaran dari klien.
2. **Paid**: Pembayaran berhasil diverifikasi oleh Midtrans atau bukti transfer diterima.
3. **In Progress**: Tim teknis WEBIA sedang menyusun website, integrasi tampilan mobile, dan konfigurasi AI Assistant.
4. **Review**: Klien memeriksa hasil pratinjau website dan mengajukan revisi jika diperlukan.
5. **Delivered**: Website telah selesai, domain/subdomain aktif di `/s/{site_slug}`, dan serah terima akun selesai.

## 3. 4 Pilihan Paket Add-on Resmi WEBIA (WebiaAddon)
Selain 4 paket website utama (Pixel, Pulse, Nexus, Infinity), klien dapat menambahkan modul Add-on resmi:
1. **SEO Optimization**: Optimasi teknis on-page, sitemap, meta tags, dan struktur data Google untuk meningkatkan visibilitas mesin pencari.
2. **Admin Dashboard**: Panel manajemen konten mandiri bagi klien yang ingin memperbarui produk/layanan dan artikel secara berkala.
3. **Custom Module**: Penambahan modul fungsional khusus sesuai alur unik bisnis klien (misal kalkulator tarif custom, booking spesifik).
4. **Integrasi Tambahan**: Integrasi ke layanan pihak ketiga atau API eksternal (CRM, logistik kurir, atau sistem eksternal).

## 4. Kebijakan Penting Mengenai SEO (Google Ranking)
- **Aturan PRD AI-L3-009**: Seluruh website WEBIA dibangun dengan kaidah teknis SEO yang bersih (struktur HTML semantik, meta tags, kecepatan muat tinggi, mobile-friendly).
- Namun, WEBIA **TIDAK PERNAH menjanjikan garansi ranking #1 Google secara instan**, karena posisi pencarian Google dipengaruhi oleh otoritas domain, usia website, persaingan industri, dan aktivitas konten klien di masa mendatang.

## 5. Komponen Business Brief yang Dibutuhkan dari Calon Klien
Untuk mempercepat pembuatan website, AI Assistant dapat membantu merangkum data berikut:
- Nama Brand / Usaha
- Kategori Usaha (F&B, Beauty, Laundry, Agriternak, Furniture, Bengkel, dll.)
- Alamat Lengkap & Link Google Maps
- Jam Operasional (Hari & Jam Buka)
- Daftar Layanan / Produk Unggulan & Kisaran Harga
- Nomor WhatsApp untuk Layanan Pelanggan (CS)
