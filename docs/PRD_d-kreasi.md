# D-KREASI — Digital Creative Platform

**Product Requirements Document**
*Digital Creative Platform by PakDe Group*

---

## Document Information

| Item | Value |
|---|---|
| Product | D-KREASI |
| Version | 1.0 |
| Status | Draft / Initial Product |
| Owner | PakDe Group |
| Initial Services | Undangan Digital & Website Bisnis |
| AI | AI Assistant tersedia di D-KREASI dan masing-masing website jasa |

D-KREASI menjadi homebase berbagai kreasi digital dari kreator PakDe Group.

---

## 1. Product Overview

D-KREASI adalah platform digital creative milik PakDe Group yang menjadi homebase untuk berbagai layanan dan kreasi digital dari kreator PakDe Group.

Pada tahap awal, D-KREASI memiliki dua layanan utama: **Undangan Digital** dan **Website Bisnis**. Layanan lain ditampilkan sebagai *Coming Soon* dan dapat ditambahkan di masa depan.

### Konsep Utama

D-KREASI bukan pengganti dua website jasa yang sudah direncanakan. D-KREASI berfungsi sebagai website utama/homebase, sedangkan setiap jasa tetap memiliki website/subdomain khusus dengan alur dan AI Assistant masing-masing.

| Layer | Fungsi | AI |
|---|---|---|
| D-KREASI Home | Homebase dan pilihan seluruh layanan | AI Assistant umum |
| Undangan Digital | Website jasa khusus undangan | AI Assistant khusus undangan |
| Website Bisnis | Website jasa khusus pembuatan website bisnis | AI Assistant khusus website bisnis |
| Website Customer | Hasil website bisnis milik customer | AI chatbot khusus bisnis customer |

---

## 2. Product Goal

- Menjadi homebase layanan digital PakDe Group.
- Memudahkan customer memilih layanan sesuai kebutuhan.
- Menyediakan sistem berbasis template yang dapat digunakan kembali.
- Mempercepat proses pembuatan produk digital.
- Menyediakan AI Assistant pada D-KREASI dan masing-masing website jasa.
- Membangun fondasi yang dapat dikembangkan menjadi lebih banyak produk digital.

---

## 3. Target User

| User | Kebutuhan |
|---|---|
| Pemilik bisnis / UMKM | Membutuhkan website profesional untuk bisnis. |
| Perusahaan | Membutuhkan website company profile atau platform bisnis. |
| Personal / Creator | Membutuhkan website personal brand. |
| Calon pengantin / keluarga | Membutuhkan undangan digital. |
| Event / organisasi | Membutuhkan undangan atau website sesuai kebutuhan acara. |
| Internal PakDe Group | Mengelola customer, template, package, order, dan project. |

---

## 4. Brand & Visual Identity

| Item | Value |
|---|---|
| Brand | D-KREASI |
| Positioning | Digital Creative Platform by PakDe Group |
| Primary | `#0C3685` |
| Blue | `#0B64D4` |
| Bright Blue | `#1698F6` |
| Soft Blue | `#68A5D6` |
| White | `#FEFEFE` |

Arah visual mengikuti referensi desain yang telah ditentukan, dengan penyesuaian branding D-KREASI dan penambahan AI Assistance.

---

## 5. Information Architecture

```
D-KREASI HOME
  → [Undangan Digital] [Website Bisnis] [Lainnya / Coming Soon]
  → masing-masing masuk ke website/subdomain jasa khusus
```

---

## 6. D-KREASI Homepage Requirements

- Navbar dan identitas D-KREASI.
- Hero section yang menjelaskan D-KREASI sebagai homebase kreasi digital PakDe Group.
- AI Assistant button.
- Service cards untuk Undangan Digital dan Website Bisnis.
- Card Lainnya / Coming Soon.
- Section pendukung seperti penjelasan layanan, kreasi/portfolio, CTA, dan footer.

| Service | Description | Action |
|---|---|---|
| Undangan Digital | Undangan digital untuk berbagai kebutuhan acara. | Explore Undangan |
| Website Bisnis | Website profesional untuk berbagai kategori bisnis. | Explore Website |
| Lainnya | Kreasi digital lainnya yang sedang dipersiapkan. | Coming Soon |

---

## 7. AI Assistant — D-KREASI

AI Assistant di D-KREASI berfungsi sebagai asisten umum yang membantu pengunjung memahami pilihan layanan sebelum masuk ke website jasa.

- Menjelaskan layanan D-KREASI.
- Menanyakan kebutuhan customer.
- Merekomendasikan layanan yang sesuai.
- Menjawab pertanyaan umum.
- Mengarahkan customer ke website jasa yang relevan.

> **Contoh:** customer mengatakan ingin membuat website untuk bengkel. AI mengarahkan customer ke layanan Website Bisnis.

---

## 8. Service 1 — Undangan Digital

Undangan Digital merupakan website jasa khusus yang dibuka setelah customer memilih layanan Undangan Digital dari D-KREASI.

**Flow:**

```
CATEGORY → TEMPLATE → PACKAGE → ISI DATA → REVIEW → ORDER → UNDANGAN DIGITAL
```

### Kategori Awal

| Category | Contoh |
|---|---|
| Pernikahan | Wedding / akad / resepsi |
| Khitan | Undangan khitan |
| Ulang Tahun | Birthday |
| Anniversary | Anniversary |
| Aqiqah | Aqiqah |
| Graduation | Wisuda / kelulusan |
| Event | Acara umum |
| Lainnya | Kategori yang dikembangkan kemudian |

### Template

Setiap kategori memiliki beberapa template/theme. Template dibuat sebagai master template yang dapat digunakan oleh banyak customer dengan data, foto, warna, dan informasi yang berbeda.

### Package

Customer memilih package setelah memilih template. Struktur package awal dapat berupa **Basic, Standard, Premium, dan Custom**. Detail fitur dan harga ditentukan pada tahap product pricing.

### AI Assistant — Undangan Digital

- Membantu memilih kategori undangan.
- Merekomendasikan template.
- Menjelaskan package dan fitur.
- Menjawab FAQ.
- Membantu customer memahami proses pemesanan.

---

## 9. Service 2 — Website Bisnis

Website Bisnis merupakan website jasa khusus yang mempertahankan konsep layanan website yang telah dirancang sebelumnya, tetapi sekarang berada di bawah D-KREASI.

**Flow:**

```
CATEGORY → TEMPLATE → PACKAGE → MODULE → BUSINESS DATA → AI DATA → ORDER → WEBSITE + AI + SEO
```

### Kategori Awal

| Category | Contoh Template |
|---|---|
| F&B | F01 Modern Restaurant; F02 Premium Cafe; F03 Minimal Catering; F04 Bakery & Dessert; F05 Food Product |
| Beauty | B01 Elegant Salon; B02 Luxury Beauty; B03 Modern Barbershop; B04 Beauty Clinic; B05 Minimal Spa |
| Automotive | A01 Professional Workshop; A02 Modern Car Wash; A03 Auto Dealer; A04 Body Repair; A05 Automotive Detailing |
| Company | C01 Corporate; C02 Modern Contractor; C03 Industrial; C04 Agency; C05 Distributor |
| Property | Template bisnis property |
| Education | Template bisnis pendidikan |
| Professional Service | Template jasa profesional |
| Personal Brand | Template personal brand |
| Retail | Template retail |
| Healthcare | Template healthcare |

### Package

| Package | Scope |
|---|---|
| STATIC | Landing Page Statis + AI + Basic/Technical SEO |
| STARTER | AI Landing Page + Basic SEO |
| BUSINESS | AI Business Website + Standard SEO |
| PROFESSIONAL | AI Website + Admin + SEO lebih lengkap |
| CUSTOM | AI Custom Business Platform + SEO sesuai kebutuhan |

Semua package Website Bisnis **wajib** memiliki AI chatbot. SEO tetap menjadi komponen terpisah yang membantu website lebih siap ditemukan melalui search engine.

### Modules

- Booking
- Admin Dashboard
- Product Management
- Service Management
- Member Area
- E-Commerce
- Payment
- CRM
- Customer Portal
- Blog
- Analytics
- WhatsApp API
- Advanced AI

### Login & Authentication

Login tidak wajib untuk semua website. Login digunakan sesuai module:

- **Admin Dashboard** membutuhkan admin login.
- **Member Area** membutuhkan member login.
- Website publik biasa tidak wajib memiliki login.

---

## 10. Business AI Chatbot

Selain AI Assistant pada website jasa Website Bisnis, setiap website bisnis customer memiliki AI chatbot sendiri.

- AI menggunakan informasi bisnis milik customer tersebut.
- Data dapat mencakup nama bisnis, produk, harga, layanan, jam buka, lokasi, FAQ, promo, dan kontak.
- AI dapat menjawab pertanyaan pengunjung dan membantu mengarahkan customer.
- Data antar customer harus terpisah dan tidak boleh tercampur.

> **Contoh:** pada website Bengkel ABC, AI dapat menjawab jam buka, layanan, lokasi, harga, atau FAQ berdasarkan data Bengkel ABC.

---

## 11. SEO

SEO membantu website lebih siap ditemukan oleh calon customer melalui mesin pencari seperti Google.

### Level SEO

| Package | Level SEO |
|---|---|
| STATIC | Optimasi dasar / technical SEO |
| STARTER | Basic SEO |
| BUSINESS | SEO standar |
| PROFESSIONAL | SEO lebih lengkap |
| CUSTOM | SEO sesuai kebutuhan |

D-KREASI **tidak menjanjikan ranking #1 Google**. Contoh tujuan SEO: website bengkel dioptimalkan agar lebih siap ditemukan saat calon customer mencari layanan seperti "bengkel mobil Malang".

---

## 12. Reusable Template System

Template merupakan master design yang dapat digunakan oleh banyak customer. Customer mendapatkan tampilan dasar yang sama, tetapi seluruh isi dapat disesuaikan.

Manfaat:

- Development lebih cepat.
- Design lebih konsisten.
- Lebih mudah membuat banyak variasi.
- Lebih efisien untuk pengembangan skala besar.

---

## 13. Order Flow

### Undangan Digital

```
D-KREASI → Undangan Digital → Category → Template → Package → Data → Review → Order
```

### Website Bisnis

```
D-KREASI → Website Bisnis → Category → Template → Package → Module → Business Data → AI Data → Review → Order
```

---

## 14. Internal Project Workflow

```
NEW ORDER → BRIEF RECEIVED → ANALYSIS → DESIGN → FRONTEND DEVELOPMENT
→ BACKEND DEVELOPMENT → AI DEVELOPMENT → INTEGRATION → QA → CLIENT REVIEW
→ REVISION → APPROVAL → DEPLOYMENT → COMPLETED
```

---

## 15. Internal D-KREASI Admin

- Customer Management
- Order Management
- Project Management
- Category Management
- Template Management
- Package Management
- Module Management
- PIC / Developer Assignment
- Deadline & Status Tracking
- Revision Tracking
- QA / Deployment
- Portfolio / Demo Management

---

## 16. MVP Scope

| Area | MVP |
|---|---|
| D-KREASI Home | Homepage, service cards, AI Assistant, Coming Soon, CTA |
| Undangan Digital | Category, template, package, data, order, AI Assistant |
| Website Bisnis | Category, template, package, module, business data, AI data, order, AI chatbot, basic SEO |
| Admin | Minimal management untuk customer, template, package, dan order |

MVP dapat dikembangkan bertahap. Detail harga, payment gateway, jumlah template awal, dan fitur lanjutan belum menjadi keputusan final dalam PRD ini.

---

## 17. Future Development

- Menambah kategori dan template.
- Menambah package dan module.
- Online payment.
- Customer dashboard.
- Project tracking.
- Automated deployment.
- Advanced AI.
- CRM dan WhatsApp integration.
- Analytics.
- Menambahkan layanan digital baru pada card Lainnya.

---

## 18. Success Metrics

| Area | Metric |
|---|---|
| Traffic | Jumlah visitor D-KREASI dan masing-masing website jasa |
| Engagement | Interaksi AI dan template yang dilihat |
| Conversion | Jumlah inquiry dan order |
| Delivery | Waktu pengerjaan project |
| Quality | Jumlah revisi dan hasil QA |
| Customer | Customer satisfaction |

---

## 19. Key Product Principles

- D-KREASI adalah homebase, bukan pengganti website jasa.
- Undangan Digital dan Website Bisnis tetap menjadi website/subdomain terpisah.
- Kedua website jasa tetap memiliki AI Assistant masing-masing.
- Website bisnis customer juga memiliki AI chatbot khusus berdasarkan data bisnis customer.
- Template harus dirancang reusable.
- AI dan SEO adalah komponen berbeda: AI membantu pengunjung, SEO membantu discoverability.
- Fitur customer mengikuti package dan module yang dipilih.
- Produk baru dapat ditambahkan ke D-KREASI tanpa mengubah struktur utama.

---

## 20. Gambaran Sementara Website

Bagian ini pada dokumen asli berisi screenshot referensi desain sementara (bukan final), yang menampilkan:

- **Hero section** dengan headline ajakan membuat undangan & website bisnis, tombol CTA, dan statistik singkat.
- **Section "Solusi Digital Serba Praktis"** dengan tiga service card: Undangan Digital Interactive, Landing Page Bisnis / UMKM, dan Layanan Kreatif Mendatang (Coming Soon).
- **Section "Kenapa Harus Percayakan Ke Kami?"** berisi keunggulan layanan dan ilustrasi alur pemesanan.
- **Section "Hasil Karya Terbaru Kami"** (showcase & portofolio) dengan filter Semua Karya, Tema Undangan, dan Website Bisnis.
- Tombol **Ask Gemini / AI Assistant** yang mengambang di halaman.

> Catatan: Referensi tampilan menggunakan nama "KreasiPulse" dan tema gelap sebagai gambaran sementara. Branding final mengikuti identitas D-KREASI (Bagian 4).

---

## 21. Final Product Architecture

```
                        D-KREASI HOME
                              ↓
                AI ASSISTANT + SERVICE SELECTION
                              ↓
   [ UNDANGAN DIGITAL ]   [ WEBSITE BISNIS ]   [ LAINNYA ]
            ↓                     ↓                  ↓
    SUBDOMAIN JASA #1     SUBDOMAIN JASA #2     COMING SOON
            ↓                     ↓
       AI ASSISTANT          AI ASSISTANT
            ↓                     ↓
        CATEGORY              CATEGORY
            ↓                     ↓
        TEMPLATE              TEMPLATE
            ↓                     ↓
         PACKAGE               PACKAGE
            ↓                     ↓
           DATA                MODULE
                                  ↓
                      BUSINESS DATA + AI DATA
                                  ↓
                        WEBSITE + AI + SEO
```

---

*D-KREASI — Digital Creative Platform by PakDe Group | PRD v1.0*
