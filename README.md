# PakDe AI Engine (D-KREASI & Ekosistem PakDe Group)

Centralized Multi-Tier AI Assistant Backend & RAG Engine powering:
- **L1**: D-KREASI Platform Portal (Front-Desk / Concierge)
- **L2**: D-Karsa Undangan Digital (Event & Invitation Assistant)
- **L3**: WEBIA Website Bisnis (Sales AI & Package Recommendation)
- **L4**: Customer Business Chatbot (Multi-tenant B2B Chatbots for clients)

---

## 🛠️ Tech Stack
- **Framework**: FastAPI (Async Python 3.12+)
- **LLM Gateway**: 9router (Local) / OpenAI / Google Gemini
- **Embeddings**: `intfloat/multilingual-e5-small`
- **Vector Store**: FAISS (isolated per namespace with strict default-deny)
- **Database**: SQLite (SQLAlchemy / aiosqlite) for usage, conversations & audit logs
- **Testing & Evals**: Pytest, Golden Q&A Evals

---

## 🚀 Quick Start

### 1. Setup Virtual Environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize & Index Knowledge
```bash
# Seed initial API keys and sites
python -m scripts.seed_sites

# Build RAG vector index from Markdown knowledge base
python -m scripts.rebuild_index --layer l1_dkreasi
```

### 4. Run Server
```bash
uvicorn app.main:app --reload --port 8000
```
- Interactive Swagger API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/v1/health`

---

## 🧪 Testing & Evaluation
```bash
# Run unit & integration tests
pytest

# Run L1 Golden Q&A evaluation
python -m evals.run_eval
```

---

## 🔌 Universal Embed Widget
Tambahkan baris berikut di template HTML/Blade platform manapun (`d-kreasi`, `webia`, `d-karsa`):
```html
<script 
    src="http://localhost:8000/widget/widget.js" 
    data-site-key="site_dkreasi_public" 
    data-api-url="http://localhost:8000" 
    defer>
</script>
```
