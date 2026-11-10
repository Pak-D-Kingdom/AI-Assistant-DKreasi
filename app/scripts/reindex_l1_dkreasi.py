"""
Utilitas Re-Indexing Knowledge Base L1 D-KREASI ke FAISS Vector Store.
Membaca seluruh file markdown di knowledge_base/l1_dkreasi/, memecahnya menjadi
potongan (chunks) kontekstual, lalu membangun ulang indeks FAISS dan metadata.json.

Penggunaan:
    python -m app.scripts.reindex_l1_dkreasi
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
        raw_title = top_title_match.group(1).strip()
        clean_top_title = raw_title.split("—")[0].split("·")[0].strip()
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

        full_title = f"{clean_top_title} - {sec_title}" if sec_title else clean_top_title
        chunks.append({
            "title": full_title,
            "content": sec,
            "file_path": rel_path.replace("\\", "/"),
        })

    return chunks


def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    kb_dir = os.path.join(base_dir, "knowledge_base", "l1_dkreasi")

    print(f"=== RE-INDEXING L1 D-KREASI KNOWLEDGE BASE ===")
    print(f"Target directory: {kb_dir}")

    md_files = glob.glob(os.path.join(kb_dir, "**", "*.md"), recursive=True)
    print(f"Ditemukan {len(md_files)} file markdown.")

    all_chunks: List[Dict[str, Any]] = []
    for f in md_files:
        c = chunk_markdown_file(f, base_dir)
        all_chunks.extend(c)

    print(f"Total contextual chunks dihasilkan: {len(all_chunks)}")

    rag = RagService()
    rag.save_index(layer="l1_dkreasi", chunks=all_chunks)
    print(f"SUCCESS: FAISS Index l1_dkreasi berhasil diperbarui dengan {len(all_chunks)} chunks.")


if __name__ == "__main__":
    main()
