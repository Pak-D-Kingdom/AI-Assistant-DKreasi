"""
Utilitas Re-Indexing Knowledge Base L4 Tenant ke FAISS Vector Store.
Membaca seluruh file markdown di knowledge_base/l4_tenant/{tenant_id}/,
memecahnya menjadi chunks kontekstual, lalu membangun indeks FAISS untuk masing-masing tenant.

Penggunaan:
    python -m app.scripts.reindex_l4_tenants
"""

import os
import glob
import re
from typing import List, Dict, Any
from app.services.rag_service import RagService


def chunk_markdown_file(filepath: str, base_dir: str) -> List[Dict[str, Any]]:
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read().replace("\r\n", "\n")

    rel_path = os.path.relpath(filepath, base_dir)

    top_title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if top_title_match:
        clean_top_title = top_title_match.group(1).strip()
    else:
        clean_top_title = os.path.splitext(os.path.basename(filepath))[0].replace("_", " ").title()

    sections = re.split(r"\n(?=##\s+)", text)
    chunks = []

    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue

        heading_match = re.search(r"^##\s+(.+)$", sec, re.MULTILINE)
        sec_title = heading_match.group(1).strip() if heading_match else ""
        chunk_title = f"{clean_top_title} - {sec_title}" if sec_title else clean_top_title

        chunks.append({
            "title": chunk_title,
            "content": sec,
            "file_path": rel_path,
        })

    return chunks


def reindex_all_l4():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "knowledge_base", "l4_tenant"))
    print("=" * 60)
    print(f"RE-INDEXING KNOWLEDGE BASE L4 TENANTS: {base_dir}")
    print("=" * 60)

    tenant_dirs = sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d.startswith("tenant_")])
    print(f"[*] Ditemukan {len(tenant_dirs)} tenant.")

    rag = RagService()

    for t_id in tenant_dirs:
        t_path = os.path.join(base_dir, t_id)
        md_files = sorted(glob.glob(os.path.join(t_path, "*.md")))
        t_chunks = []
        for f in md_files:
            chs = chunk_markdown_file(f, t_path)
            t_chunks.extend(chs)

        rag.save_index(layer="l4", chunks=t_chunks, tenant_id=t_id)
        print(f"  [OK] Tenant {t_id}: {len(t_chunks)} chunks terindeks.")

    print("\n[OK] SEMUA TENANT L4 BERHASIL DIINDEKS KE FAISS!")


if __name__ == "__main__":
    reindex_all_l4()
