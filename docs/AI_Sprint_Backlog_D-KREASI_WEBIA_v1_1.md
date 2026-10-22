# AI SPRINT BACKLOG — D-KREASI, WEBIA & D-KARSA

**Versi:** 1.1 (Draft)
**Pemilik:** AI Engineering, PakDe Group
**Repo:** `kreasi-ai-core`
**Acuan:** PRD D-KREASI v1.0, PRD WEBIA v1.0, PRD AI v1.1

---

## 0. Riwayat Perubahan

| Versi | Perubahan |
|---|---|
| 1.0 | Draft awal |
| 1.1 | Menyesuaikan dengan keputusan arsitektur: satu repo `kreasi-ai-core`, lapisan Site Identity (site key + origin allowlist), server key untuk ingest, stack teknis ditetapkan (FastAPI, SQLite + SQLAlchemy, OpenAI SDK, FAISS per namespace, e5-small), widget tunggal, kontrak API, `tenant_templates/`. Task Core ditambah (setup repo, site identity, kontrak API). Tenant resolution dipindah dari Backend ke AI service. Bagian keputusan yang memblokir diperbarui |

---

## 1. Cara Membaca Dokumen Ini

- Setiap layer (**L1, L2, L3, L4**) punya **sprint sendiri** dan dapat dikerjakan **independen**. Dokumen ini **tidak menentukan layer mana yang dikerjakan lebih dulu**; urutan antar layer diputuskan tim.
- Di dalam satu layer, sprint berurutan karena tiap sprint membangun hasil sebelumnya.
- **Shared AI Core** (Bagian 3) adalah fondasi bersama. Task yang bergantung padanya ditandai `[Core]`.
- **Asumsi panjang sprint:** 2 minggu (silakan ubah). Estimasi memakai ukuran **S / M / L**.
- Format ID: `L1-S1-01` = Layer 1, Sprint 1, task 01. Core: `CORE-S1-01`.
- Nama layer: L1 = D-KREASI, L2 = D-KARSA (Undangan Digital), L3 = WEBIA (Sales AI), L4 = Business Chatbot.

### Legenda

| Tanda | Arti |
|---|---|
| `[Core]` | Bergantung pada task Shared AI Core |
| `[BE]` `[FE]` `[PRD]` | Butuh dukungan Backend web / Frontend web / Product |
| `[BLOCKED]` | Menunggu keputusan atau dokumen eksternal |
| S / M / L | Ukuran kasar (kecil / sedang / besar) |

### Definition of Done (semua task)

- Kode ter-review dan ter-merge.
- Perilaku sesuai requirement di PRD AI v1.1.
- Lolos evaluation set yang relevan (tidak ada regresi).
- Tidak melanggar guardrail (tidak mengarang fakta, tidak bocor lintas tenant).
- Tidak ada secret di kode (semua lewat `.env`).
- Log dan error tertangani.
- Dokumentasi singkat (konfigurasi, prompt version, cara uji) diperbarui.

---

## 2. Ringkasan Sprint per Layer

| Layer | Nama | Jumlah Sprint | Sifat |
|---|---|---|---|
| Core | Shared AI Core | 4 | Fondasi bersama |
| L1 | AI Assistant D-KREASI | 4 | Routing dan rekomendasi layanan |
| L2 | AI Assistant D-KARSA | 3 | **Placeholder**, menunggu PRD Undangan |
| L3 | AI Assistant WEBIA (Sales AI) | 4 | Rekomendasi paket, template, modul, brief |
| L4 | AI Business Chatbot | 6 | Multi-tenant, paling kompleks |

---

## 3. SHARED AI CORE

Fondasi yang dipakai semua layer. Dikerjakan sebagian atau seluruhnya sesuai kebutuhan layer yang dimulai tim.

### Sprint CORE-1 — Setup Repo, LLM Gateway & Orchestrator

**Goal:** Repo siap dan pipeline dasar berjalan: pesan masuk → konfigurasi layer → LLM → respons.

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| CORE-S1-01 | Inisialisasi repo `kreasi-ai-core` sesuai struktur final (`app/`, `knowledge_base/`, `tenant_templates/`, `widget/`, `evals/`, `tests/`, `scripts/`, `docs/`) | S | Salin PRD dan backlog ke `docs/` |
| CORE-S1-02 | Setup Python 3.10+, FastAPI, Uvicorn, Pydantic v2, `requirements.txt`, `.env.example`, `.gitignore` (`data/`, `.env`) | S | Stack sudah ditetapkan |
| CORE-S1-03 | Dockerfile dan docker-compose | S | |
| CORE-S1-04 | LLM Gateway: OpenAI SDK dengan `base_url` dan model dari `.env`, mendukung streaming | M | Provider diganti lewat `.env` |
| CORE-S1-05 | Orchestrator: terima pesan, pilih konfigurasi layer/tenant, panggil LLM | L | |
| CORE-S1-06 | Prompt/Persona Manager dengan versioning (`layers/*/prompts.py`) | M | |
| CORE-S1-07 | Interface `LayerConfig` (`layers/base.py`) dan kerangka empat layer | M | Perbedaan layer hanya di sini |
| CORE-S1-08 | Database: SQLite + SQLAlchemy, model dasar (conversations, messages) | M | |
| CORE-S1-09 | Endpoint `POST /v1/chat` (streaming) dan `GET /health` | M | |
| CORE-S1-10 | Logging dasar (layer, tenant, waktu, latency, error) | S | |

**Exit criteria:** pesan uji menghasilkan respons lewat gateway dengan persona berbeda per layer; repo bisa dijalankan lewat Docker.

### Sprint CORE-2 — Site Identity, Keamanan & Kontrak API

**Goal:** Setiap request teridentifikasi server-side; website klien bisa memakai AI dengan aman.

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| CORE-S2-01 | Model `sites`: nama, layer, `tenant_id` (L4), API key (disimpan sebagai hash), origin allowlist, status, modul aktif | M | |
| CORE-S2-02 | Validasi site key + origin allowlist (`core/security.py`) | M | |
| CORE-S2-03 | `core/context.py`: tentukan layer dan `tenant_id` **server-side** dari site key; abaikan nilai dari body/parameter request | M | Kritis |
| CORE-S2-04 | Rate limit dan kuota dasar per key | M | Site key bersifat publik, jadi ini wajib |
| CORE-S2-05 | Rotasi dan penonaktifan key tanpa mengganggu site lain | S | |
| CORE-S2-06 | **Server key** terpisah dari site key untuk endpoint internal (ingest, kelola site) | M | Site key tidak boleh mengakses endpoint internal |
| CORE-S2-07 | `scripts/seed_sites.py`: buat site awal untuk dkreasi, webia, dkarsa | S | |
| CORE-S2-08 | CORS sesuai allowlist | S | |
| CORE-S2-09 | Tulis `docs/API_CONTRACT.md` v1 (`/v1/chat`, ingest, sites, widget config, error code) | M | Dibaca semua tim web |
| CORE-S2-10 | Tes: key invalid, origin salah, manipulasi `layer`/`tenant_id` pada request | M | `tests/` |

**Exit criteria:** request tanpa key valid atau dari origin salah ditolak; layer dan tenant tidak dapat dipalsukan dari klien.

### Sprint CORE-3 — Retrieval/RAG & Namespace

**Goal:** Retrieval aman dengan batas namespace.

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| CORE-S3-01 | Embedding service: e5-small dengan prefix `query:` / `passage:` | S | |
| CORE-S3-02 | Skema knowledge chunk (namespace, tipe, status, versi, sumber) | M | |
| CORE-S3-03 | Pipeline ingest `.md`: validasi → chunking → embedding → index FAISS | L | |
| CORE-S3-04 | `rag_service`: **satu index FAISS per namespace** (`l1_dkreasi`, `l2_dkarsa`, `l3_webia`, `tenants/{tenant_id}`) | L | |
| CORE-S3-05 | Aturan **default deny**: retrieval tanpa namespace ditolak | S | Kritis |
| CORE-S3-06 | Ambang relevansi untuk deteksi "tidak ada jawaban" | M | Dasar fallback |
| CORE-S3-07 | `scripts/rebuild_index.py --layer {x}` dan `--tenant {id}` | M | |
| CORE-S3-08 | Lazy load index per tenant dan cache terbatas | M | Cegah memori membengkak |
| CORE-S3-09 | Namespace cache (respons/embedding) per layer/tenant | S | |

**Exit criteria:** retrieval hanya mengembalikan data dari namespace yang diminta; query tanpa namespace ditolak.

### Sprint CORE-4 — Guardrail, Fallback, Handoff, Widget & Evaluasi

**Goal:** AI terkendali, terukur, dan dapat dipasang di website.

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| CORE-S4-01 | Guardrail input: prompt injection, permintaan membuka system prompt | M | |
| CORE-S4-02 | Guardrail output: validasi jawaban terhadap konteks retrieval (anti-halusinasi) | L | |
| CORE-S4-03 | Alur fallback standar + pencatatan `fallback_events` | M | |
| CORE-S4-04 | Tool Registry + izin tool per layer | M | |
| CORE-S4-05 | Handoff WhatsApp (kontak dari CTA knowledge, tidak dikarang) | M | |
| CORE-S4-06 | Widget tunggal (`widget.js`, `widget.css`) disajikan AI service; membaca layer dari site key | L | Vanilla JS, terisolasi dari halaman host |
| CORE-S4-07 | Endpoint widget config (branding per site/tenant) | S | |
| CORE-S4-08 | Evaluation harness (`evals/run_eval.py`): golden, unanswerable, adversarial | L | |
| CORE-S4-09 | Dashboard internal: usage, token, latency, error, fallback rate | M | |
| CORE-S4-10 | Alert: lonjakan error, lonjakan biaya, anomali lintas tenant, penolakan key | S | |

**Exit criteria:** guardrail aktif, fallback berfungsi, widget dapat ditempel di website uji, evaluation harness berjalan otomatis.

---

## 4. L1 — AI ASSISTANT D-KREASI

**Tujuan:** asisten umum di homepage D-KREASI untuk menjelaskan layanan, menanyakan kebutuhan, merekomendasikan, dan mengarahkan ke website jasa.
**Sumber:** PRD D-KREASI §7 · Requirement: AI-L1-001 s.d. 006 · Namespace: `l1_dkreasi`

### Sprint L1-1 — Knowledge & Persona

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L1-S1-01 | Susun `knowledge_base/l1_dkreasi/layanan/`: Undangan Digital, Website Bisnis, Coming Soon (satu topik satu file) | M | `[PRD]` konten dari tim product |
| L1-S1-02 | Susun `knowledge_base/l1_dkreasi/faq/`: FAQ umum D-KREASI dan PakDe Group | M | |
| L1-S1-03 | Persona/tone L1 (sopan, ringkas, bahasa Indonesia) | S | `[Core]` |
| L1-S1-04 | Build index L1 (`rebuild_index.py --layer l1_dkreasi`) | S | `[Core]` |
| L1-S1-05 | Aturan: layanan Coming Soon tidak dijanjikan ketersediaannya | S | AI-L1-006 |

**Acceptance:** L1 menjawab pertanyaan layanan dan FAQ sesuai knowledge; Coming Soon dijelaskan apa adanya.

### Sprint L1-2 — Intent Detection & Routing

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L1-S2-01 | Definisikan intent: butuh undangan, butuh website bisnis, belum jelas, di luar scope | M | |
| L1-S2-02 | Pertanyaan klarifikasi untuk kebutuhan ambigu (maks 1 pertanyaan per giliran) | M | |
| L1-S2-03 | Tool routing: arahkan ke D-KARSA / WEBIA (URL dari konfigurasi site, bukan dikarang AI) | M | `[Core]` Tool Registry |
| L1-S2-04 | Contoh uji: "website untuk bengkel" → Website Bisnis | S | Dari PRD |
| L1-S2-05 | Kebutuhan yang tidak cocok kedua layanan: jujur dan tawarkan human support | S | |

**Acceptance:** routing tepat pada routing set; kebutuhan ambigu memicu klarifikasi, bukan tebakan.

### Sprint L1-3 — Widget, Integrasi Homepage & Handoff

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L1-S3-01 | Daftarkan site D-KREASI, branding widget (warna brand D-KREASI) | S | `[Core]` |
| L1-S3-02 | Integrasi tag `<script>` + AI Assistant button di homepage | S | `[FE]` web D-KREASI |
| L1-S3-03 | Welcome message dan suggested prompts | S | |
| L1-S3-04 | Handoff ke human/WhatsApp bila AI tidak bisa membantu | M | `[Core]` |
| L1-S3-05 | Penanganan error/timeout LLM dengan pesan jelas | S | |
| L1-S3-06 | Uji responsif mobile, tablet, desktop | S | `[FE]` |

**Acceptance:** alur pengunjung → chat → diarahkan ke website jasa berjalan di semua device.

### Sprint L1-4 — Evaluasi, Tuning & Rilis

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L1-S4-01 | Bangun `evals/l1_routing_set.json` dan golden Q&A L1 | M | `[Core]` harness |
| L1-S4-02 | Uji unanswerable dan adversarial (prompt injection, minta data internal) | M | |
| L1-S4-03 | Tuning prompt dan threshold | M | |
| L1-S4-04 | Pasang metrik: conversations, routing accuracy, handoff rate | S | |
| L1-S4-05 | Checklist rilis dan dokumentasi | S | |

**Acceptance:** lolos gate rilis (ambang diputuskan, lihat Open Question #3).

---

## 5. L2 — AI ASSISTANT D-KARSA / UNDANGAN DIGITAL (PLACEHOLDER)

> **Status:** Detail menunggu **PRD Undangan Digital**. Sprint dibuat dari lima requirement tingkat tinggi PRD D-KREASI §8. Task `[BLOCKED]` tidak boleh dimulai sebelum PRD Undangan tersedia.

**Tujuan:** membantu memilih kategori, merekomendasikan template, menjelaskan package dan fitur, FAQ, dan proses pemesanan.
**Requirement:** AI-L2-001 s.d. 005 · Namespace: `l2_dkarsa`

### Sprint L2-1 — Knowledge & Persona

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L2-S1-01 | `knowledge_base/l2_dkarsa/category/`: Pernikahan, Khitan, Ulang Tahun, Anniversary, Aqiqah, Graduation, Event, Lainnya | M | `[PRD]` |
| L2-S1-02 | Knowledge template per kategori | M | `[BLOCKED]` daftar template belum ada |
| L2-S1-03 | Knowledge package (Basic, Standard, Premium, Custom) dan fitur | M | `[BLOCKED]` detail fitur dan harga belum final |
| L2-S1-04 | FAQ dan proses pemesanan undangan | M | `[BLOCKED]` PRD Undangan |
| L2-S1-05 | Persona/tone L2 | S | `[Core]` |
| L2-S1-06 | Build index L2 | S | `[Core]` |

**Acceptance:** L2 menjawab kategori, template, package, dan proses order sesuai knowledge.

### Sprint L2-2 — Rekomendasi & Alur Order

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L2-S2-01 | Rekomendasi kategori dari kebutuhan acara pengguna | M | |
| L2-S2-02 | Rekomendasi template berdasarkan kategori dan preferensi | M | `[BLOCKED]` data template |
| L2-S2-03 | Penjelasan perbandingan package dan arahan ke alur order (Category → Template → Package → Data → Review → Order) | M | `[BLOCKED]` struktur package final |
| L2-S2-04 | Tool arahkan pengguna ke langkah order yang relevan | M | `[Core]` |
| L2-S2-05 | Larangan menyebut harga/fitur yang belum final | S | Guardrail |

**Acceptance:** rekomendasi masuk akal pada recommendation set; AI tidak menyebut harga/fitur yang belum final.

### Sprint L2-3 — Integrasi, Evaluasi & Rilis

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L2-S3-01 | Daftarkan site D-KARSA dan integrasi tag `<script>` | S | `[FE]` web D-KARSA |
| L2-S3-02 | Handoff ke human/WhatsApp | S | `[Core]` |
| L2-S3-03 | Golden Q&A, unanswerable, adversarial set L2 | M | |
| L2-S3-04 | Tuning prompt dan threshold | M | |
| L2-S3-05 | Metrik, checklist rilis, dokumentasi | S | |
| L2-S3-06 | **Review ulang cakupan L2** setelah PRD Undangan final (apakah ada AI untuk tamu undangan) | S | `[BLOCKED]` Open Question #8 |

**Acceptance:** lolos gate rilis; cakupan L2 diselaraskan dengan PRD Undangan.

---

## 6. L3 — AI ASSISTANT WEBIA (SALES AI)

**Tujuan:** membantu prospect memahami paket, template, kategori, modul, proses order; merekomendasikan paket; membantu menyusun business brief.
**Sumber:** PRD WEBIA §11.1 · Requirement: AI-L3-001 s.d. 010 · Namespace: `l3_webia`

### Sprint L3-1 — Knowledge Katalog & Persona

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L3-S1-01 | `knowledge_base/l3_webia/category/`: 10 kategori awal + subkategori + kebutuhan tipikal | M | PRD WEBIA §6.2 |
| L3-S1-02 | `.../template/`: F01–F05, B01–B05, A01–A05, C01–C05, dst. | M | |
| L3-S1-03 | `.../package/`: Static, Starter, Business, Professional, Custom + level SEO | M | |
| L3-S1-04 | `.../module/`: daftar modul dan kebutuhan autentikasi | M | PRD WEBIA §9 |
| L3-S1-05 | `.../faq/`: FAQ, proses order, workflow project | M | `[PRD]` |
| L3-S1-06 | Aturan harga: tidak menyebut angka sampai pricing final | S | Open Question #5 |
| L3-S1-07 | Persona/tone Sales AI dan build index L3 | M | `[Core]` |

**Acceptance:** L3 menjawab pertanyaan katalog dengan benar; tidak menyebut harga yang belum final.

### Sprint L3-2 — Rekomendasi Paket, Template & Modul

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L3-S2-01 | Alur kualifikasi prospect: jenis bisnis, kebutuhan (admin? booking? online store?), skala | M | Maks 1 pertanyaan per giliran |
| L3-S2-02 | Logika rekomendasi paket memakai Recommendation Matrix PRD WEBIA §7.6 (baseline, bukan pembatas) | L | AI-L3-002 |
| L3-S2-03 | Rekomendasi template berdasarkan kategori | M | |
| L3-S2-04 | Rekomendasi modul sesuai kategori | M | AI-L3-004 |
| L3-S2-05 | Jalur ke paket Custom bila kebutuhan tidak cocok kategori | S | AI-L3-010 |
| L3-S2-06 | Penjelasan jujur soal SEO (tanpa jaminan ranking) | S | AI-L3-009 |
| L3-S2-07 | Penjelasan upsell berdasarkan kebutuhan, bukan memaksa | S | |

**Acceptance:** rekomendasi lolos recommendation set; AI tidak menjanjikan ranking.

### Sprint L3-3 — Business Brief, Order & Handoff

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L3-S3-01 | Alur percakapan penyusunan business brief (nama bisnis, kategori, deskripsi, jam operasional, kontak, sosial media) | L | PRD WEBIA §13.2 |
| L3-S3-02 | Keluaran brief terstruktur (JSON) yang dapat diteruskan ke form checkout | M | `[BE][FE]` web WEBIA |
| L3-S3-03 | Panduan pengisian AI Configuration yang **selaras dengan `tenant_templates/`** agar knowledge L4 berkualitas | M | Menghubungkan L3 → L4 |
| L3-S3-04 | Tool arahkan ke demo/order/human support | M | `[Core]` |
| L3-S3-05 | Daftarkan site WEBIA dan integrasi tag `<script>` | S | `[FE]` web WEBIA |
| L3-S3-06 | Handoff ke human/WhatsApp | S | `[Core]` |

**Acceptance:** prospect dapat dibantu dari pertanyaan awal hingga brief terstruktur dan diarahkan ke order.

### Sprint L3-4 — Evaluasi, Guardrail & Rilis

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L3-S4-01 | Golden Q&A katalog, unanswerable (SLA/harga/kebijakan yang tak ada), adversarial set | M | |
| L3-S4-02 | Uji khusus: AI tidak mengarang harga, fitur, SLA, atau kebijakan | M | AI-L3-008 |
| L3-S4-03 | `evals/l3_recommendation_set.json`: profil prospect → paket/template/modul | M | |
| L3-S4-04 | Tuning prompt dan threshold | M | |
| L3-S4-05 | Metrik: conversations, rekomendasi diterima, AI-assisted conversion, handoff rate | S | |
| L3-S4-06 | Checklist rilis dan dokumentasi | S | |

**Acceptance:** lolos gate rilis; tidak ada kasus mengarang harga/fitur/SLA pada uji.

---

## 7. L4 — AI BUSINESS CHATBOT

**Tujuan:** chatbot di setiap website customer yang menjawab berdasarkan data bisnis tenant.
**Sumber:** PRD WEBIA §10, §11.2–11.5 · Requirement: AI-L4-001 s.d. 009, AI-ISO-001 s.d. 008 · Namespace: `tenants/{tenant_id}`

> L4 paling kompleks dan wajib ada di **semua paket**. **Uji isolasi tenant adalah gate wajib.**

### Sprint L4-1 — Tenant Model, Template Isian & Knowledge Schema

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L4-S1-01 | Skema knowledge tenant: Business, Product, Service, FAQ, Promotion, Policy, CTA | M | PRD WEBIA §11.3 |
| L4-S1-02 | Model `tenants` dan relasi ke `sites`; **tenant ditentukan server dari site key** (memakai CORE-S2) | M | Tidak lagi tugas Backend web |
| L4-S1-03 | Skema status knowledge (draft/approved), versi, masa berlaku (mis. promo kedaluwarsa) | M | |
| L4-S1-04 | `tenant_templates/_base/` (company, faq, promotion, policy, cta) | M | |
| L4-S1-05 | Template per kategori awal: `fnb/` (menu), `beauty/` (layanan + durasi), `automotive/` (layanan) | M | Pola `.md` per topik ala Nasikotak |
| L4-S1-06 | Validator ingest: data tenant dicek terhadap template kategori | M | |
| L4-S1-07 | Kontrak data tenant dengan Backend WEBIA (format payload ingest) | S | `[BE]` masuk `API_CONTRACT.md` |

**Acceptance:** data tenant tersimpan terstruktur, tervalidasi terhadap template kategori, entri punya status dan versi.

### Sprint L4-2 — Ingest, Retrieval & Isolasi Tenant

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L4-S2-01 | Endpoint `POST /v1/tenants/{tenant_id}/knowledge` (server key), simpan ke `data/tenant_knowledge/{tenant_id}/` | L | AI-ISO-009 |
| L4-S2-02 | Build index per tenant (`data/faiss_index/tenants/{tenant_id}/`) | L | `[Core]` |
| L4-S2-03 | Retrieval dengan namespace tenant wajib + default deny | L | `[Core]` Kritis |
| L4-S2-04 | Hanya knowledge berstatus approved yang terindeks/dijawab | S | PRD WEBIA §29 |
| L4-S2-05 | Re-index otomatis saat harga/jam buka/promo/kebijakan berubah | M | |
| L4-S2-06 | Namespace cache per tenant | S | `[Core]` |
| L4-S2-07 | **Uji isolasi tenant awal**: Tenant A tak bisa mengambil data Tenant B | L | Gate |

**Acceptance:** uji isolasi lulus 100%; perubahan knowledge tercermin setelah re-index.

### Sprint L4-3 — Chatbot Core: Jawaban, Fallback & Handoff

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L4-S3-01 | Prompt L4: jawab hanya dari konteks retrieval tenant | L | AI-L4-001 |
| L4-S3-02 | Jawaban produk/layanan/harga/jam buka/lokasi/promo/kebijakan/FAQ | M | |
| L4-S3-03 | Rekomendasi produk/layanan dari knowledge | M | AI-L4-002 |
| L4-S3-04 | Fallback saat info tidak ada: jujur + klarifikasi/handoff, tanpa mengarang | L | AI-L4-006 |
| L4-S3-05 | Handoff WhatsApp memakai CTA knowledge tenant | M | AI-HO-004 |
| L4-S3-06 | Pencatatan fallback event per tenant | M | |
| L4-S3-07 | Jawab promo hanya bila masih berlaku | S | |

**Acceptance:** chatbot menjawab akurat dari data tenant; fallback dan handoff berfungsi pada unanswerable set.

### Sprint L4-4 — Widget, Branding & Pendaftaran Tenant

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L4-S4-01 | Endpoint pendaftaran tenant + pembuatan site key (server key), dipanggil Backend WEBIA | M | Open Question #12 |
| L4-S4-02 | Branding per tenant: nama, tone, bahasa, warna (widget config) | M | AI-L4-007 |
| L4-S4-03 | Integrasi widget ke template website di seluruh paket (Static → Custom) | M | `[FE][BE]` web WEBIA; cukup satu tag `<script>` |
| L4-S4-04 | Konfigurasi per paket/tenant: fitur dan modul aktif disimpan di site config | M | |
| L4-S4-05 | Aturan: AI tidak menawarkan fitur modul yang tidak aktif | S | |
| L4-S4-06 | Responsif mobile/tablet/desktop; error state jelas + opsi WhatsApp | M | `[FE]` |
| L4-S4-07 | Uji widget tidak merusak halaman host saat AI gagal | S | AI-NFR-010 |

**Acceptance:** widget tampil dan berfungsi di semua paket, dengan branding dan pesan error yang sesuai.

### Sprint L4-5 — Modul: Lead, Booking & Knowledge Management

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L4-S5-01 | Lead capture oleh AI (nama, kontak, kebutuhan) bila modul tersedia | M | `[BE]` AI-L4-003 |
| L4-S5-02 | Dukungan Booking bila Booking module aktif | L | `[BE]` AI-L4-005 |
| L4-S5-03 | AI Knowledge Management untuk customer admin: Backend WEBIA meneruskan perubahan ke endpoint ingest, AI service menyediakan preview jawaban | L | `[BE][FE]` FR-020, Professional ke atas |
| L4-S5-04 | Permission pengelolaan knowledge sesuai role (dipegang Backend WEBIA, AI service memverifikasi server key) | M | `[BE]` |
| L4-S5-05 | Alur update knowledge oleh tim internal untuk paket tanpa admin | M | Open Question #11 |
| L4-S5-06 | Event analytics AI bila modul Analytics aktif | S | |

**Acceptance:** lead/booking hanya berfungsi bila modul aktif; admin dapat mengelola knowledge sesuai permission.

### Sprint L4-6 — Hardening, Evaluasi & Rilis

| ID | Task | Ukuran | Catatan |
|---|---|---|---|
| L4-S6-01 | Golden Q&A, unanswerable, adversarial set L4 per kategori | L | |
| L4-S6-02 | Uji adversarial: prompt injection, minta data tenant lain, minta system prompt | L | AI-ISO |
| L4-S6-03 | **Uji isolasi tenant lengkap** (retrieval, cache, log, admin, widget, site key) | L | Gate wajib 100% |
| L4-S6-04 | Uji hallucination pada data bisnis (harga, jam buka, promo) | M | |
| L4-S6-05 | Kuota dan monitoring pemakaian per tenant, kontrol biaya | M | AI-NFR-008 |
| L4-S6-06 | Dashboard: resolution rate, handoff rate, unanswered rate, usage | M | `[Core]` |
| L4-S6-07 | Regression suite otomatis tiap perubahan prompt/model/knowledge | M | |
| L4-S6-08 | Uji beban: banyak tenant, memori FAISS per tenant, evaluasi perlu tidaknya migrasi ke Qdrant/pgvector | M | Open Question #2 |
| L4-S6-09 | Checklist rilis, runbook operasional, dokumentasi | S | |

**Acceptance:** uji isolasi tenant 100% lulus; hallucination di bawah ambang; metrik dan alert aktif.

---

## 8. Dependensi Lintas Layer

Hanya peta ketergantungan, **bukan urutan prioritas**.

| Task | Bergantung pada |
|---|---|
| Semua layer (konfigurasi, retrieval, guardrail, widget) | Shared AI Core (CORE-1 s.d. CORE-4) |
| Semua layer (identitas site) | CORE-2 (Site Identity) |
| L2 (hampir seluruh sprint) | PRD Undangan Digital |
| L3-S3-03 (panduan AI Configuration) | `tenant_templates/` (L4-S1-04, L4-S1-05) agar selaras |
| L4-S4-01 (pendaftaran tenant) | Backend WEBIA memanggil endpoint dengan server key |
| L4-S5-03 (Knowledge Management) | Admin Dashboard WEBIA (Backend + Frontend) |
| Pemasangan widget di tiap website | Tim web masing-masing (satu tag `<script>`) |
| Pernyataan harga oleh AI (L2, L3, L4) | Keputusan pricing final |

> Tenant resolution tidak lagi bergantung pada Backend web; diselesaikan di AI service lewat site key (CORE-S2-03).

---

## 9. Keputusan

### 9.1 Sudah Diputuskan

| Keputusan | Hasil |
|---|---|
| Provider LLM | OpenAI SDK dengan `base_url` custom, provider diganti lewat `.env` |
| Vector DB awal | FAISS, satu index per namespace, semua layer |
| Struktur service | Satu service dan satu repo AI bersama |
| Penentuan layer dan tenant | Server-side dari site key dan origin allowlist |
| Widget | Satu widget disajikan AI service |

### 9.2 Masih Memblokir atau Memengaruhi Sprint

| # | Keputusan | Memengaruhi |
|---|---|---|
| 1 | Model LLM spesifik dan kebijakan cadangan provider | CORE-S1-04 (konfigurasi), tuning semua layer |
| 2 | Vector DB L4 jangka panjang (tetap FAISS atau pindah) | L4-S6-08 |
| 3 | Target angka (latency, akurasi, hallucination) | Gate rilis semua layer |
| 4 | PRD Undangan Digital | Seluruh L2 |
| 5 | Pricing final | Boleh tidaknya AI menyebut harga |
| 6 | Kuota AI per paket | CORE-S2-04, L4-S6-05 |
| 7 | Retensi log dan kebijakan privasi | Logging di semua layer |
| 8 | Kanal handoff (WhatsApp saja atau lebih) | Handoff di semua layer |
| 9 | Kapan Backend WEBIA mendaftarkan tenant dan siapa yang membuat site key | L4-S4-01 |
| 10 | Hosting AI service dan domain publik untuk widget dan API | CORE-S1-03, CORE-S4-06 |

---

## 10. Ringkasan

| Layer | Sprint | Fokus Utama |
|---|---|---|
| Core | 4 | Setup repo + orchestrator, site identity + kontrak API, RAG per namespace, guardrail + widget + evaluasi |
| L1 | 4 | Knowledge layanan → routing → widget homepage → evaluasi |
| L2 | 3 | Placeholder: knowledge → rekomendasi template/package → evaluasi (menunggu PRD) |
| L3 | 4 | Knowledge katalog → rekomendasi paket/modul → business brief → evaluasi |
| L4 | 6 | Tenant schema + template isian → ingest dan isolasi → chatbot + fallback → widget + pendaftaran tenant → modul → hardening |

---

*AI Sprint Backlog — D-KREASI, WEBIA & D-KARSA v1.1 | Draft*
