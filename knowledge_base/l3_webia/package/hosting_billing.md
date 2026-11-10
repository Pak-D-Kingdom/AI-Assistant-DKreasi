# Panduan Tagihan & Perpanjangan Hosting WEBIA

WEBIA menyediakan infrastruktur hosting berkinerja tinggi yang terintegrasi langsung dengan setiap website bisnis yang dibangun. Dokumen ini menjelaskan kebijakan penagihan, siklus faktur, dan tata cara pembayaran hosting.

## 1. Siklus Penagihan & Periode Awal
- Setiap pemesanan paket website bisnis WEBIA (Pixel, Pulse, Nexus, atau Infinity) sudah mencakup masa aktif hosting awal (periode aktif pertama).
- Setelah periode awal berakhir, layanan hosting dilanjutkan dengan siklus penagihan rutin (bulanan atau tahunan) agar website klien tetap dapat diakses publik secara online 24/7.
- Tanggal siklus tagihan dihitung berdasarkan tanggal aktivasi awal layanan website klien (`activation_date`).

## 2. Faktur Tagihan (Hosting Invoice) & Jatuh Tempo
- Faktur tagihan baru diterbitkan secara otomatis oleh sistem saat tanggal siklus penagihan tiba.
- **Batas Waktu Pembayaran (Due Date)**: Setiap invoice memiliki batas waktu pembayaran selama **7 hari kalender** sejak diterbitkan.
- **Status Invoice**:
  * `unpaid`: Faktur telah terbit dan menunggu pembayaran klien sebelum jatuh tempo.
  * `paid`: Faktur telah berhasil diverifikasi dan dibayarkan (layanan otomatis aktif normal).
  * `overdue`: Pembayaran telah melewati batas tanggal jatuh tempo.
  * `cancelled`: Faktur dibatalkan oleh admin atau digantikan dengan faktur baru.

## 3. Notifikasi Pengingat Otomatis
Sistem WEBIA mengirimkan notifikasi pengingat pembayaran ke akun klien pada momen-momen berikut:
1. Saat faktur tagihan pertama kali terbit (`issued`).
2. Tiga hari sebelum jatuh tempo (`due_in_3_days`).
3. Satu hari sebelum jatuh tempo (`due_tomorrow`).
4. Pada hari H batas jatuh tempo (`due_today`).
5. Tiga hari setelah melewati jatuh tempo (`overdue_3_days`).
6. Tujuh hari setelah melewati jatuh tempo jika belum terbayar (pemberitahuan penangguhan / `suspended`).

## 4. Kebijakan Suspensi & Pemulihan Layanan (Grace Period)
- **Toleransi 7 Hari (Grace Period)**: Jika invoice belum dibayar setelah melewati batas jatuh tempo hingga lebih dari 7 hari, status layanan hosting akan diubah sementara menjadi `suspended`.
- **Aktivasi Kembali (Unsuspend)**: Klien tidak perlu khawatir kehilangan data website. Layanan hosting yang disuspend akan langsung dipulihkan secara otomatis segera setelah invoice tertunggak dibayarkan melalui portal pembayaran.

## 5. Cara Pembayaran Invoice via Midtrans
- Klien dapat melihat daftar tagihan dan membayar invoice melalui menu akun di **/hosting-invoices**.
- Klik tombol **Bayar Sekarang** pada invoice yang ingin diselesaikan.
- Sistem terintegrasi dengan Payment Gateway **Midtrans** yang mendukung:
  * QRIS (GoPay, ShopeePay, OVO, Dana)
  * Virtual Account Bank (BCA, Mandiri, BRI, BNI, Permata)
  * Kartu Kredit / Debit
- Verifikasi pembayaran berlangsung instan (real-time). Setelah berstatus `paid`, hosting langsung aktif kembali tanpa perlu konfirmasi manual.
