# AI Assistant (D-Kreasi, Webia, & D-Karsa)

Backend AI Assistant & RAG Engine terpusat yang melayani kebutuhan AI pada seluruh platform ekosistem:
- **L1 (D-Kreasi)**: Front-Desk / Concierge portal utama D-Kreasi untuk konsultasi umum dan mengarahkan pengunjung ke unit layanan yang tepat.
- **L2 (D-Karsa)**: Konsultan Undangan Digital untuk konsultasi tema, estimasi paket & kuota tamu, panduan pemesanan/builder, dan informasi pembayaran.
- **L3 (Webia)**: Sales AI Website Bisnis untuk konsultasi paket, rekomendasi template sesuai bidang usaha, modul add-on, dan panduan checkout.
- **L4 (Tenant)**: AI Customer Support resmi yang menjawab pertanyaan seputar profil bisnis, produk/layanan, jam operasional, dan reservasi pada website masing-masing klien.

---

## 🛠️ Tech Stack
- **Framework**: FastAPI (Async Python 3.12+)
- **LLM Gateway**: 9router (Local Gateway) / OpenAI Compatible (`base_url` disesuaikan di `.env`)
- **Embeddings**: `intfloat/multilingual-e5-small`
- **Vector Store**: FAISS (Namespace terisolasi ketat per layer & per tenant dengan *default-deny*)
- **Database**: SQLite (SQLAlchemy / aiosqlite) untuk logging percakapan, metrik analitik & audit
- **Testing & Evals**: Pytest test suite, Golden Q&A Evals (L1 & L3)

---

## 🚀 Panduan Memulai Cepat (Quick Start)

### 1. Setup Virtual Environment
```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize & Build Vector Indexes
```bash
# Seed initial API keys dan site credentials
python -m scripts.seed_sites

# Rebuild FAISS index per layer:
python -m scripts.rebuild_index --layer l1_dkreasi
python -m scripts.rebuild_index --layer l2_dkarsa
python -m scripts.rebuild_index --layer l3_webia

# Rebuild seluruh FAISS index tenant L4:
python -m scripts.rebuild_index --all-tenants
```

### 4. Menjalankan Server AI
```bash
python main.py
```
*Backend AI berjalan pada port **8001** (port 8000 dicadangkan untuk web Laravel Webia & D-Karsa).*
- **Interactive Swagger API Docs**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **Health Check Endpoint**: [http://localhost:8001/api/v1/health](http://localhost:8001/api/v1/health)
- **Widget Testing UI Sandbox**: [http://localhost:8001/widget/index.html](http://localhost:8001/widget/index.html)

---

## 🧪 Pengujian & Evaluasi

```bash
# Menjalankan seluruh unit test suite
$env:PYTHONPATH="."; pytest -k "not streaming"

# Menjalankan evaluasi dataset Golden Q&A (L1 & L3)
$env:PYTHONPATH="."; python evals/run_eval.py
```

---

## 🔌 Universal Embed Widget (Integrasi Blade / HTML)

Tambahkan tag script berikut pada layout master website masing-masing:

### 1. Layer 1 — D-KREASI Holding
```html
<script 
    src="http://localhost:8001/widget/widget.js" 
    data-site-key="site_dkreasi_public" 
    data-layer="l1" 
    defer>
</script>
```

### 2. Layer 2 — D-KARSA Undangan Digital
```html
<script 
    src="http://localhost:8001/widget/widget.js" 
    data-site-key="site_dkarsa_public" 
    data-layer="l2" 
    defer>
</script>
```

### 3. Layer 3 — WEBIA Platform Katalog
```html
<script 
    src="http://localhost:8001/widget/widget.js" 
    data-site-key="site_webia_public" 
    data-layer="l3" 
    defer>
</script>
```

### 4. Layer 4 — Website Klien / Template Bisnis
```blade
<script 
    src="http://localhost:8001/widget/widget.js" 
    data-site-key="site_webia_tenant_public" 
    data-layer="l4" 
    data-tenant-id="{{ $tenantId ?? 'tenant_laundry_01' }}" 
    defer>
</script>
```

---

## 📡 API Ingest Data Tenant L4 (Integrasi Form Webia)

Ketika klien selesai mengisi formulir data bisnis di Dashboard Akun Webia (`/dashboard`), backend Webia dapat langsung mengirimkan HTTP POST untuk menyusun dan mengindeks AI chatbot toko secara otomatis:

- **Endpoint**: `POST /api/v1/tenants/{tenant_id}/knowledge`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "profil": "# Nama Toko Klien\n- **Kategori**: Laundry\n- **Jam Buka**: 08.00 - 20.00\n- **Alamat**: Jl. Mawar No. 12\n- **WhatsApp**: 081234567890",
  "layanan": "### Daftar Layanan\n- Cuci Komplit Kiloan: Rp 7.000/kg\n- Cuci Sepatu: Rp 25.000/pasang",
  "kebijakan": "- Garansi cuci ulang 24 jam jika masih kotor",
  "faq": "Q: Apakah melayani antar jemput?\nA: Ya, gratis dalam radius 3 km"
}
```
*Sistem AI akan otomatis menyimpan file markdown dan langsung mengompilasi index FAISS dalam 2 detik.*
