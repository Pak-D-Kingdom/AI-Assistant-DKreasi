# AI SPRINT BACKLOG — D-KREASI & WEBIA

**Versi:** 1.0 (Draft)
**Pemilik:** AI Engineering, PakDe Group
**Acuan:** PRD D-KREASI v1.0, PRD WEBIA v1.0, PRD AI D-KREASI & WEBIA v1.0

---

## 1. Cara Membaca Dokumen Ini

- Setiap layer (**L1, L2, L3, L4**) punya **sprint sendiri** dan dapat dikerjakan **independen**. Dokumen ini **tidak menentukan layer mana yang dikerjakan lebih dulu**; urutan antar layer diputuskan tim.
- Di dalam satu layer, sprint berurutan (Sprint 1 → 2 → 3 → ...) karena tiap sprint membangun hasil sebelumnya.
- **Shared AI Core** (Bagian 3) adalah fondasi bersama. Task yang bergantung pada Core ditandai `[Core]`, sehingga tim bisa melihat dependensinya tanpa harus mengurutkan layer.
- **Asumsi panjang sprint:** 2 minggu (silakan ubah). Estimasi memakai ukuran **S / M / L** (kasar), bukan story point final.
- Format ID task: `L1-S1-01` = Layer 1, Sprint 1, task 01. Core: `CORE-S1-01`.

### Legenda

| Tanda | Arti |
|---|---|
| `[Core]` | Bergantung pada task Shared AI Core |
| `[BE]` `[FE]` `[PRD]` | Butuh dukungan Backend / Frontend / Product |
| `[BLOCKED]` | Menunggu keputusan atau dokumen eksternal |
| S / M / L | Ukuran kasar (kecil / sedang / besar) |

### Definition of Done (berlaku untuk semua task)

- Kode ter-review dan ter-merge.
- Perilaku sesuai requirement di PRD AI.
- Lolos evaluation set yang relevan (tidak ada regresi).
- Tidak melanggar guardrail (tidak mengarang fakta, tidak bocor lintas tenant).
- Log dan error tertangani.
- Dokumentasi singkat (konfigurasi, prompt version, cara uji) diperbarui.

---

## 2. Ringkasan Sprint per Layer

| Layer | Nama | Jumlah Sprint | Sifat |
|---|---|---|---|
| Core | Shared AI Core | 3 | Fondasi bersama |
| L1 | AI Assistant D-KREASI | 4 | Routing dan rekomendasi layanan |
| L2 | AI Assistant Undangan Digital | 3 | **Placeholder**, menunggu PRD Undangan |
| L3 | AI Assistant Website Bisnis (Sales AI) | 4 | Rekomendasi paket, template, modul, brief |
| L4 | AI Business Chatbot | 6 | Multi-tenant, paling kompleks |

---

## 3. SHARED AI CORE

Fondasi yang dipakai semua layer. Dikerjakan sebagian atau seluruhnya sesuai kebutuhan layer yang dimulai tim.

### Sprint CORE-1 — Orchestration & LLM Gateway

**Goal:** Ada pipeline dasar: pesan masuk → konfigurasi layer → LLM → respons.

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| CORE-S1-01 | Tetapkan keputusan teknis: model LLM, framework, vector DB (Open Questions #1, #2) | M | `[BLOCKED]` keputusan technical lead |
| CORE-S1-02 | Bangun LLM Gateway (abstraction layer provider) | M | Agar provider mudah diganti |
| CORE-S1-03 | Bangun Orchestrator: terima pesan, pilih konfigurasi layer/tenant, panggil LLM | L | |
| CORE-S1-04 | Bangun Prompt/Persona Manager dengan versioning | M | System prompt per layer/tenant |
| CORE-S1-05 | Endpoint chat API (streaming) + rate limiting dasar | M | `[BE]` |
| CORE-S1-06 | Logging dasar percakapan (layer, tenant, waktu, latency, error) | S | |

**Exit criteria:** pesan uji menghasilkan respons lewat gateway dengan persona berbeda per layer.

### Sprint CORE-2 — Retrieval/RAG & Tenant Boundary

**Goal:** Retrieval aman dengan batas tenant/layer.

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| CORE-S2-01 | Desain skema knowledge chunk (`tenant_id`/layer, tipe, status, versi) | M | Selaras PRD AI §15 |
| CORE-S2-02 | Pipeline ingest: validasi → chunking → embedding → index | L | |
| CORE-S2-03 | Retrieval service dengan **filter tenant/layer wajib** | L | |
| CORE-S2-04 | Aturan **default deny**: query tanpa tenant/layer ditolak | S | Kritis |
| CORE-S2-05 | Ambang relevansi (threshold) untuk deteksi "tidak ada jawaban" | M | Dasar fallback |
| CORE-S2-06 | Mekanisme re-index saat knowledge berubah | M | |
| CORE-S2-07 | Namespace cache (respons/embedding) per tenant/layer | S | |

**Exit criteria:** retrieval hanya mengembalikan data milik tenant/layer yang diminta; query tanpa identitas ditolak.

### Sprint CORE-3 — Guardrail, Fallback, Handoff & Evaluasi

**Goal:** AI terkendali, terukur, dan aman.

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| CORE-S3-01 | Guardrail input: deteksi prompt injection, permintaan membuka system prompt | M | |
| CORE-S3-02 | Guardrail output: validasi jawaban terhadap konteks retrieval (anti-halusinasi) | L | |
| CORE-S3-03 | Alur fallback standar (info tidak ada → klarifikasi/handoff) + pencatatan | M | |
| CORE-S3-04 | Tool Registry + izin tool per layer | M | |
| CORE-S3-05 | Tool handoff WhatsApp (ambil kontak dari CTA knowledge) | M | `[BE]` |
| CORE-S3-06 | Evaluation harness: runner golden / unanswerable / adversarial set | L | |
| CORE-S3-07 | Dashboard internal: usage, token, latency, error, fallback rate | M | `[BE][FE]` |
| CORE-S3-08 | Alert: lonjakan error, lonjakan biaya, anomali lintas tenant | S | |

**Exit criteria:** guardrail aktif, fallback berfungsi, evaluation harness dapat dijalankan otomatis.

---

## 4. L1 — AI ASSISTANT D-KREASI

**Tujuan:** asisten umum di homepage D-KREASI untuk menjelaskan layanan, menanyakan kebutuhan, merekomendasikan, dan mengarahkan ke website jasa.
**Sumber:** PRD D-KREASI §7 · Requirement: AI-L1-001 s.d. 006

### Sprint L1-1 — Knowledge & Persona

**Goal:** Assistant memahami layanan D-KREASI.

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L1-S1-01 | Susun knowledge layanan: Undangan Digital, Website Bisnis, Coming Soon | M | `[PRD]` konten dari tim product |
| L1-S1-02 | Susun FAQ umum D-KREASI dan PakDe Group | M | |
| L1-S1-03 | Rancang persona/tone L1 (sopan, ringkas, bahasa Indonesia) | S | `[Core]` |
| L1-S1-04 | Ingest knowledge L1 ke retrieval (namespace layer L1) | M | `[Core]` |
| L1-S1-05 | Aturan: layanan Coming Soon tidak dijanjikan ketersediaannya | S | AI-L1-006 |

**Acceptance:** L1 menjawab pertanyaan layanan dan FAQ sesuai knowledge; Coming Soon dijelaskan apa adanya.

### Sprint L1-2 — Intent Detection & Routing

**Goal:** Kebutuhan customer diarahkan ke layanan yang benar.

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L1-S2-01 | Definisikan intent: butuh undangan, butuh website bisnis, belum jelas, di luar scope | M | |
| L1-S2-02 | Pertanyaan klarifikasi untuk kebutuhan ambigu (maks 1 pertanyaan per giliran) | M | |
| L1-S2-03 | Tool routing: arahkan ke subdomain Undangan Digital / Website Bisnis | M | `[Core]` Tool Registry, `[FE]` tombol/link |
| L1-S2-04 | Contoh uji: "website untuk bengkel" → Website Bisnis | S | Dari PRD |
| L1-S2-05 | Tangani kebutuhan yang tidak cocok kedua layanan (jujur, tawarkan human support) | S | |

**Acceptance:** routing tepat pada routing set; kebutuhan ambigu memicu klarifikasi, bukan tebakan.

### Sprint L1-3 — Widget, Integrasi Homepage & Handoff

**Goal:** Assistant tampil dan dapat dipakai di homepage.

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L1-S3-01 | Integrasi AI Assistant button + chat widget di homepage | M | `[FE]` |
| L1-S3-02 | Welcome message dan suggested prompts (mis. "Saya butuh undangan", "Saya punya usaha") | S | |
| L1-S3-03 | Handoff ke human/WhatsApp bila AI tidak bisa membantu | M | `[Core]` |
| L1-S3-04 | Penanganan error/timeout LLM dengan pesan jelas | S | |
| L1-S3-05 | Responsif mobile, tablet, desktop (uji bersama FE) | S | `[FE]` |

**Acceptance:** alur lengkap pengunjung → chat → diarahkan ke website jasa berjalan di semua device.

### Sprint L1-4 — Evaluasi, Tuning & Rilis

**Goal:** Kualitas L1 terukur dan siap rilis.

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L1-S4-01 | Bangun routing set dan golden Q&A L1 | M | `[Core]` harness |
| L1-S4-02 | Uji unanswerable dan adversarial (prompt injection, minta data internal) | M | |
| L1-S4-03 | Tuning prompt dan threshold berdasarkan hasil evaluasi | M | |
| L1-S4-04 | Pasang metrik: conversations, routing accuracy, handoff rate | S | |
| L1-S4-05 | Checklist rilis dan dokumentasi operasional | S | |

**Acceptance:** lolos gate rilis (routing accuracy dan hallucination sesuai ambang yang disepakati, lihat Open Question #3).

---

## 5. L2 — AI ASSISTANT UNDANGAN DIGITAL (PLACEHOLDER)

> **Status:** Detail menunggu **PRD Undangan Digital**. Sprint di bawah dibuat berdasarkan lima requirement tingkat tinggi dari PRD D-KREASI §8 dan struktur layer yang sama. Task bertanda `[BLOCKED]` tidak boleh dimulai sebelum PRD Undangan tersedia.

**Tujuan:** membantu memilih kategori, merekomendasikan template, menjelaskan package dan fitur, FAQ, dan proses pemesanan.
**Requirement:** AI-L2-001 s.d. 005

### Sprint L2-1 — Knowledge & Persona

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L2-S1-01 | Kumpulkan knowledge kategori undangan (Pernikahan, Khitan, Ulang Tahun, Anniversary, Aqiqah, Graduation, Event, Lainnya) | M | `[PRD]` |
| L2-S1-02 | Susun knowledge template per kategori | M | `[BLOCKED]` daftar template belum ada |
| L2-S1-03 | Susun knowledge package (Basic, Standard, Premium, Custom) dan fitur | M | `[BLOCKED]` detail fitur dan harga belum final |
| L2-S1-04 | FAQ dan proses pemesanan undangan | M | `[BLOCKED]` PRD Undangan |
| L2-S1-05 | Persona/tone L2 (hangat, sesuai konteks acara) | S | `[Core]` |
| L2-S1-06 | Ingest knowledge L2 (namespace layer L2) | M | `[Core]` |

**Acceptance:** L2 menjawab pertanyaan kategori, template, package, dan proses order sesuai knowledge.

### Sprint L2-2 — Rekomendasi & Alur Order

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L2-S2-01 | Logika rekomendasi kategori dari kebutuhan acara pengguna | M | |
| L2-S2-02 | Rekomendasi template berdasarkan kategori dan preferensi | M | `[BLOCKED]` data template |
| L2-S2-03 | Penjelasan perbandingan package dan arahan ke alur order (Category → Template → Package → Data → Review → Order) | M | `[BLOCKED]` struktur package final |
| L2-S2-04 | Tool arahkan pengguna ke langkah order yang relevan | M | `[Core]` `[FE]` |
| L2-S2-05 | Larangan menyebut harga/fitur yang belum final | S | Guardrail |

**Acceptance:** rekomendasi masuk akal pada recommendation set; AI tidak menyebut harga/fitur yang belum final.

### Sprint L2-3 — Integrasi, Evaluasi & Rilis

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L2-S3-01 | Integrasi widget di website/subdomain Undangan Digital | M | `[FE]` |
| L2-S3-02 | Handoff ke human/WhatsApp | S | `[Core]` |
| L2-S3-03 | Bangun golden Q&A, unanswerable, adversarial set L2 | M | |
| L2-S3-04 | Tuning prompt dan threshold | M | |
| L2-S3-05 | Metrik, checklist rilis, dokumentasi | S | |
| L2-S3-06 | **Review ulang cakupan L2** setelah PRD Undangan final (ada tidaknya AI untuk tamu undangan, Open Question #9) | S | `[BLOCKED]` |

**Acceptance:** lolos gate rilis; cakupan L2 diselaraskan dengan PRD Undangan.

---

## 6. L3 — AI ASSISTANT WEBSITE BISNIS (SALES AI)

**Tujuan:** membantu prospect memahami paket, template, kategori, modul, proses order; merekomendasikan paket; membantu menyusun business brief.
**Sumber:** PRD WEBIA §11.1 · Requirement: AI-L3-001 s.d. 010

### Sprint L3-1 — Knowledge Katalog & Persona

**Goal:** Sales AI memahami seluruh katalog produk.

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L3-S1-01 | Susun knowledge Category Catalog (10 kategori awal + subkategori + kebutuhan tipikal) | M | PRD WEBIA §6.2 |
| L3-S1-02 | Susun knowledge Template (mis. F01–F05, B01–B05, A01–A05, C01–C05) | M | |
| L3-S1-03 | Susun knowledge 5 Package (Static, Starter, Business, Professional, Custom) + level SEO | M | |
| L3-S1-04 | Susun knowledge Module/Add-On + kebutuhan autentikasi | M | PRD WEBIA §9 |
| L3-S1-05 | FAQ dan proses order, workflow project | M | `[PRD]` |
| L3-S1-06 | Aturan harga: tidak menyebut angka sampai pricing final | S | Open Question #5 |
| L3-S1-07 | Persona/tone Sales AI dan ingest (namespace layer L3) | M | `[Core]` |

**Acceptance:** L3 menjawab pertanyaan katalog dengan benar; tidak menyebut harga yang belum final.

### Sprint L3-2 — Rekomendasi Paket, Template & Modul

**Goal:** Rekomendasi cerdas berdasarkan kebutuhan prospect.

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L3-S2-01 | Alur kualifikasi prospect: jenis bisnis, kebutuhan (admin? booking? online store?), skala | M | Maks 1 pertanyaan per giliran |
| L3-S2-02 | Logika rekomendasi paket memakai Recommendation Matrix PRD WEBIA §7.6 (baseline, bukan pembatas) | L | AI-L3-002 |
| L3-S2-03 | Rekomendasi template berdasarkan kategori | M | |
| L3-S2-04 | Rekomendasi modul sesuai kategori (Salon → Booking, Online Course → Member, Retail → E-commerce) | M | AI-L3-004 |
| L3-S2-05 | Jalur ke paket Custom bila kebutuhan tidak cocok kategori | S | AI-L3-010 |
| L3-S2-06 | Penjelasan jujur soal SEO (tanpa jaminan ranking) | S | AI-L3-009 |
| L3-S2-07 | Penjelasan upsell berdasarkan kebutuhan, bukan memaksa (jalur Static → Custom) | S | |

**Acceptance:** rekomendasi lolos recommendation set; AI tidak menjanjikan ranking.

### Sprint L3-3 — Business Brief, Order & Handoff

**Goal:** Membantu prospect sampai siap order.

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L3-S3-01 | Alur percakapan penyusunan business brief (nama bisnis, kategori, deskripsi, jam operasional, kontak, sosial media) | L | PRD WEBIA §13.2 |
| L3-S3-02 | Keluaran brief terstruktur yang dapat diteruskan ke form checkout | M | `[BE][FE]` |
| L3-S3-03 | Panduan pengisian AI Configuration (produk, layanan, FAQ, kebijakan) agar knowledge L4 berkualitas | M | Menghubungkan L3 → L4 |
| L3-S3-04 | Tool arahkan ke demo/order/human support | M | `[Core]` |
| L3-S3-05 | Integrasi widget di website jasa Website Bisnis | M | `[FE]` |
| L3-S3-06 | Handoff ke human/WhatsApp | S | `[Core]` |

**Acceptance:** prospect dapat dibantu dari pertanyaan awal hingga brief terstruktur dan diarahkan ke order.

### Sprint L3-4 — Evaluasi, Guardrail & Rilis

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L3-S4-01 | Golden Q&A katalog, unanswerable (SLA/harga/kebijakan yang tak ada), adversarial set | M | |
| L3-S4-02 | Uji khusus: AI tidak mengarang harga, fitur, SLA, atau kebijakan | M | AI-L3-008 |
| L3-S4-03 | Recommendation set: profil prospect → paket/template/modul | M | |
| L3-S4-04 | Tuning prompt dan threshold | M | |
| L3-S4-05 | Metrik: conversations, rekomendasi diterima, AI-assisted conversion, handoff rate | S | |
| L3-S4-06 | Checklist rilis dan dokumentasi | S | |

**Acceptance:** lolos gate rilis; tidak ada kasus mengarang harga/fitur/SLA pada uji.

---

## 7. L4 — AI BUSINESS CHATBOT

**Tujuan:** chatbot di setiap website customer yang menjawab berdasarkan data bisnis tenant.
**Sumber:** PRD WEBIA §10, §11.2–11.5 · Requirement: AI-L4-001 s.d. 009, AI-ISO-001 s.d. 008

> L4 paling kompleks dan wajib ada di **semua paket**. Karena itu sprint-nya lebih banyak, dan **uji isolasi tenant adalah gate wajib**.

### Sprint L4-1 — Tenant Model & Knowledge Schema

**Goal:** Fondasi data dan identitas tenant.

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L4-S1-01 | Rancang skema knowledge tenant: Business, Product, Service, FAQ, Promotion, Policy, CTA | M | PRD WEBIA §11.3 |
| L4-S1-02 | Tenant resolution server-side (domain/website → `tenant_id`), tidak dari input pengunjung | L | `[BE]` AI-ISO-002 |
| L4-S1-03 | Skema status knowledge (draft/approved), versi, masa berlaku (mis. promo kedaluwarsa) | M | |
| L4-S1-04 | Validasi data AI Configuration dari checkout | M | `[BE]` |
| L4-S1-05 | Struktur knowledge dasar per kategori (template isian: F&B → menu, Beauty → layanan+durasi, dst.) | M | |
| L4-S1-06 | Dokumentasikan kontrak data tenant bersama Backend | S | `[BE]` |

**Acceptance:** data tenant tersimpan terstruktur, tenant ter-resolve di server, entri punya status dan versi.

### Sprint L4-2 — Ingest, Retrieval & Isolasi Tenant

**Goal:** Retrieval aman dan terisolasi.

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L4-S2-01 | Pipeline ingest knowledge tenant ke index dengan metadata `tenant_id` | L | `[Core]` |
| L4-S2-02 | Retrieval dengan filter/namespace tenant wajib + default deny | L | `[Core]` Kritis |
| L4-S2-03 | Hanya knowledge berstatus approved yang terindeks/dijawab | S | PRD WEBIA §29 |
| L4-S2-04 | Re-index otomatis saat harga/jam buka/promo/kebijakan berubah | M | |
| L4-S2-05 | Namespace cache per tenant | S | `[Core]` |
| L4-S2-06 | **Uji isolasi tenant awal**: Tenant A tak bisa mengambil data Tenant B | L | Gate |

**Acceptance:** uji isolasi lulus 100%; perubahan knowledge tercermin setelah re-index.

### Sprint L4-3 — Chatbot Core: Jawaban, Fallback & Handoff

**Goal:** Chatbot menjawab dari data tenant, jujur saat tidak tahu.

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L4-S3-01 | Prompt L4: jawab hanya dari konteks retrieval tenant | L | AI-L4-001 |
| L4-S3-02 | Jawaban produk/layanan/harga/jam buka/lokasi/promo/kebijakan/FAQ | M | |
| L4-S3-03 | Rekomendasi produk/layanan dari knowledge | M | AI-L4-002 |
| L4-S3-04 | Fallback saat info tidak ada: jujur + klarifikasi/handoff, tanpa mengarang | L | AI-L4-006 |
| L4-S3-05 | Handoff WhatsApp memakai CTA knowledge tenant (nomor tidak dikarang) | M | AI-HO-004 |
| L4-S3-06 | Pencatatan fallback event per tenant untuk perbaikan knowledge | M | |
| L4-S3-07 | Jawab promo hanya bila masih berlaku | S | |

**Acceptance:** chatbot menjawab akurat dari data tenant; fallback dan handoff berfungsi pada unanswerable set.

### Sprint L4-4 — Widget, Branding & Integrasi Paket

**Goal:** Chatbot tersedia dan berbrand di semua paket.

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L4-S4-01 | Widget chat embeddable untuk website customer (terisolasi dari halaman) | L | `[FE]` AI-NFR-010 |
| L4-S4-02 | Branding per tenant: nama, tone, bahasa, warna | M | AI-L4-007 |
| L4-S4-03 | Integrasi ke template website di seluruh paket (Static → Custom) | L | `[FE][BE]` AI-L4-008 |
| L4-S4-04 | Konfigurasi AI per paket/tenant (fitur aktif sesuai module entitlement) | M | |
| L4-S4-05 | Aturan: AI tidak menawarkan fitur modul yang tidak aktif | S | |
| L4-S4-06 | Responsif mobile/tablet/desktop; error state yang jelas + opsi WhatsApp | M | `[FE]` |

**Acceptance:** widget tampil dan berfungsi di semua paket, dengan branding dan pesan error yang sesuai.

### Sprint L4-5 — Modul: Lead, Booking & Knowledge Management

**Goal:** Kemampuan lanjutan sesuai modul (PRD WEBIA fase 2).

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L4-S5-01 | Lead capture oleh AI (nama, kontak, kebutuhan) bila modul tersedia | M | `[BE]` AI-L4-003 |
| L4-S5-02 | Dukungan Booking bila Booking module aktif | L | `[BE]` AI-L4-005 |
| L4-S5-03 | AI Knowledge Management untuk customer admin (CRUD knowledge, status, preview jawaban) | L | `[BE][FE]` FR-020, Professional ke atas |
| L4-S5-04 | Permission pengelolaan knowledge sesuai role | M | `[BE]` |
| L4-S5-05 | Alur update knowledge oleh tim internal untuk paket tanpa admin | M | Open Question #12 |
| L4-S5-06 | Event analytics AI bila modul Analytics aktif | S | |

**Acceptance:** lead/booking hanya berfungsi bila modul aktif; admin dapat mengelola knowledge sesuai permission.

### Sprint L4-6 — Hardening, Evaluasi & Rilis

**Goal:** Aman, terukur, siap produksi.

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L4-S6-01 | Golden Q&A, unanswerable, adversarial set L4 per kategori | L | |
| L4-S6-02 | Uji adversarial: prompt injection, minta data tenant lain, minta system prompt | L | AI-ISO |
| L4-S6-03 | **Uji isolasi tenant lengkap** (retrieval, cache, log, admin, widget) | L | Gate wajib 100% |
| L4-S6-04 | Uji hallucination pada data bisnis (harga, jam buka, promo) | M | |
| L4-S6-05 | Kuota dan monitoring pemakaian per tenant, kontrol biaya | M | AI-NFR-008 |
| L4-S6-06 | Dashboard: resolution rate, handoff rate, unanswered rate, usage | M | `[Core]` |
| L4-S6-07 | Regression suite otomatis tiap perubahan prompt/model/knowledge | M | |
| L4-S6-08 | Checklist rilis, runbook operasional, dokumentasi | S | |

**Acceptance:** uji isolasi tenant 100% lulus; hallucination di bawah ambang; metrik dan alert aktif.

---

## 8. Dependensi Lintas Layer

Ini hanya peta ketergantungan, **bukan urutan prioritas**.

| Task | Bergantung pada |
|---|---|
| Semua layer (konfigurasi, retrieval, guardrail) | Shared AI Core |
| L2 (hampir seluruh sprint) | PRD Undangan Digital |
| L3-S3-03 (panduan AI Configuration) | Skema knowledge L4 (L4-S1-01) agar selaras |
| L4-S1-02 (tenant resolution) | Backend: domain/website → `tenant_id` |
| L4-S5-03 (Knowledge Management) | Admin Dashboard (Backend + Frontend) |
| Widget semua layer | Frontend AI Chat UI |
| Pernyataan harga oleh AI (L2, L3, L4) | Keputusan pricing final |

---

## 9. Keputusan yang Memblokir Sprint

| # | Keputusan | Memblokir |
|---|---|---|
| 1 | Model LLM dan provider | CORE-S1 |
| 2 | Vector DB dan strategi isolasi tenant | CORE-S2, L4-S2 |
| 3 | Target angka (latency, akurasi, hallucination) | Gate rilis semua layer |
| 4 | PRD Undangan Digital | Seluruh L2 |
| 5 | Pricing final | AI boleh menyebut harga atau tidak |
| 6 | Kuota AI per paket | L4-S6-05 |
| 7 | Retensi log dan kebijakan privasi | Logging di semua layer |
| 8 | Kanal handoff (WhatsApp saja atau lebih) | Handoff di semua layer |

---

## 10. Ringkasan

| Layer | Sprint | Fokus Utama |
|---|---|---|
| Core | 3 | Orchestration, RAG + tenant boundary, guardrail, evaluasi |
| L1 | 4 | Knowledge layanan → routing → widget homepage → evaluasi |
| L2 | 3 | Placeholder: knowledge → rekomendasi template/package → evaluasi (menunggu PRD) |
| L3 | 4 | Knowledge katalog → rekomendasi paket/modul → business brief → evaluasi |
| L4 | 6 | Tenant schema → isolasi retrieval → chatbot + fallback → widget → modul → hardening |

---

*AI Sprint Backlog — D-KREASI & WEBIA v1.0 | Draft*
