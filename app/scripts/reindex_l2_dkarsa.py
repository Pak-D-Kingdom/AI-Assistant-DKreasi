"""
Utilitas Re-Indexing Knowledge Base L2 D'Karsa ke FAISS Vector Store.
Membaca seluruh file markdown di knowledge_base/l2_dkarsa/, memecahnya menjadi
potongan (chunks) kontekstual, lalu membangun ulang indeks FAISS dan metadata.json.

Penggunaan:
    python -m app.scripts.reindex_l2_dkarsa
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

    # Ambil judul utama dari baris "# ..."
    top_title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if top_title_match:
        raw_title = top_title_match.group(1).strip()
        clean_top_title = raw_title.split("—")[0].split("·")[0].strip()
    else:
        clean_top_title = os.path.splitext(os.path.basename(filepath))[0].replace("_", " ").title()

    # Pecah berdasarkan heading "## "
    sections = re.split(r"\n(?=##\s+)", text)
    chunks = []

    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue

        heading_match = re.search(r"^##\s+(.+)$", sec, re.MULTILINE)
        sec_title = heading_match.group(1).strip() if heading_match else ""

        # Jika ada sub-heading "### " dan konten cukup panjang, pecah lagi per sub-heading
        if "### " in sec and len(sec) > 900:
            sub_sections = re.split(r"\n(?=###\s+)", sec)
            for sub in sub_sections:
                sub = sub.strip()
                if not sub:
                    continue
                sub_heading = re.search(r"^###\s+(.+)$", sub, re.MULTILINE)
                if sub_heading:
                    sub_title = sub_heading.group(1).strip()
                    chunk_title = f"{clean_top_title} - {sec_title} - {sub_title}"
                else:
                    chunk_title = f"{clean_top_title} - {sec_title}" if sec_title else clean_top_title

                chunks.append({
                    "title": chunk_title,
                    "content": sub,
                    "file_path": rel_path,
                })
        else:
            chunk_title = f"{clean_top_title} - {sec_title}" if sec_title else clean_top_title
            chunks.append({
                "title": chunk_title,
                "content": sec,
                "file_path": rel_path,
            })

    return chunks


def reindex_l2():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "knowledge_base", "l2_dkarsa"))
    print("=" * 60)
    print(f"RE-INDEXING KNOWLEDGE BASE L2 D'KARSA: {base_dir}")
    print("=" * 60)

    md_files = sorted(glob.glob(os.path.join(base_dir, "**", "*.md"), recursive=True))
    print(f"[*] Ditemukan {len(md_files)} file markdown.")

    all_chunks = []
    for f in md_files:
        chs = chunk_markdown_file(f, base_dir)
        print(f"  - {os.path.relpath(f, base_dir)}: {len(chs)} chunks")
        all_chunks.extend(chs)

    print(f"\n[*] Total chunks yang akan diindeks: {len(all_chunks)}")

    # Inisialisasi RagService dan simpan index
    rag = RagService()
    rag.save_index(layer="l2_dkarsa", chunks=all_chunks)
    print(f"[OK] Berhasil menyimpan FAISS index & metadata untuk layer l2_dkarsa ({len(all_chunks)} chunks)!")


if __name__ == "__main__":
    reindex_l2()
