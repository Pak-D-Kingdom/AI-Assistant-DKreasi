import os
import re
import sys
import argparse
from typing import Any, Dict, List, Optional

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rag_service import RagService

TENANT_ID_RE = re.compile(r"^tenant_[a-z0-9_]{1,60}$")

# Urutan dokumen agar Profil (nama, alamat, jam, WhatsApp) selalu muncul paling awal di prompt
DOC_PRIORITY = {"profil": 0, "layanan": 1, "kebijakan": 2, "faq": 3}


def _is_heading(line: str) -> bool:
    return line.strip().startswith("#")


def chunk_markdown_by_headings(content: str, default_title: str) -> List[Dict[str, Any]]:
    """
    Chunk Markdown by H2 headings (## ) for high-precision semantic retrieval.

    Perbaikan:
    - Chunk yang hanya berisi judul (mis. "# Nama Bisnis - FAQ") TIDAK dibuat lagi.
    - Judul H1 (yang memuat nama bisnis) disisipkan ke setiap chunk, sehingga tiap chunk
      tahu bisnis mana yang dimaksud.
    """
    lines = content.splitlines()
    h1 = next((ln.strip() for ln in lines if ln.startswith("# ")), "")
    chunks: List[Dict[str, Any]] = []
    current_title = default_title
    current_lines: List[str] = []

    def flush() -> None:
        text = "\n".join(current_lines).strip()
        has_body = any(ln.strip() and not _is_heading(ln) for ln in text.splitlines())
        if not has_body:
            return  # lewati chunk yang hanya judul
        if h1 and not text.startswith(h1):
            text = f"{h1}\n{text}"
        chunks.append({"title": current_title, "content": text})

    for line in lines:
        if line.startswith("## "):
            flush()
            current_lines = []
            current_title = f"{default_title} - {line[3:].strip()}"
        current_lines.append(line)
    flush()

    return chunks if chunks else [{"title": default_title, "content": content}]


def collect_chunks(base_dir: str) -> List[Dict[str, Any]]:
    """Baca semua file .md di base_dir (urutan deterministik, Profil lebih dulu)."""
    chunks: List[Dict[str, Any]] = []
    for root, dirs, files in os.walk(base_dir):
        dirs.sort()
        md_files = sorted(
            (f for f in files if f.endswith(".md")),
            key=lambda f: (DOC_PRIORITY.get(f[:-3].lower(), 99), f),
        )
        for f in md_files:
            file_path = os.path.join(root, f)
            with open(file_path, "r", encoding="utf-8") as fp:
                content = fp.read().strip()
            if not content:
                continue
            doc_title = f[:-3].replace("_", " ").title()
            for c in chunk_markdown_by_headings(content, doc_title):
                c["file_path"] = os.path.relpath(file_path, base_dir)
                chunks.append(c)
    return chunks


def rebuild_layer_index(layer: str = "l1_dkreasi", rag_service: Optional[RagService] = None):
    if layer in ["l4", "l4_tenant"]:
        rebuild_all_tenants(rag_service=rag_service)
        return

    rag = rag_service or RagService()
    kb_base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base", layer)

    if not os.path.exists(kb_base):
        print(f"Directory {kb_base} does not exist.")
        return

    chunks = collect_chunks(kb_base)
    if chunks:
        rag.save_index(layer=layer, chunks=chunks)
        print(f"Indexed {len(chunks)} chunks for layer {layer}.")
    else:
        print(f"No documents found for layer {layer}.")


def rebuild_tenant_index(tenant_id: str, rag_service: Optional[RagService] = None):
    if not TENANT_ID_RE.match(tenant_id or ""):
        print(f"Invalid tenant id: {tenant_id!r}")
        return

    rag = rag_service or RagService()
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Use knowledge_base/l4_tenant as the primary source
    tenant_dir = os.path.join(root_dir, "knowledge_base", "l4_tenant", tenant_id)

    if not os.path.exists(tenant_dir):
        print(f"Tenant directory for {tenant_id} does not exist in knowledge_base/l4_tenant.")
        return

    chunks = collect_chunks(tenant_dir)
    if chunks:
        rag.save_index(layer="l4", chunks=chunks, tenant_id=tenant_id)
        print(f"Indexed {len(chunks)} chunks for tenant {tenant_id}.")
    else:
        print(f"No documents found for tenant {tenant_id}.")


def rebuild_all_tenants(rag_service: Optional[RagService] = None):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_tenants_dir = os.path.join(root_dir, "knowledge_base", "l4_tenant")
    if not os.path.exists(base_tenants_dir):
        print("Tenant knowledge directory does not exist in knowledge_base/l4_tenant.")
        return

    rag = rag_service or RagService()
    tenants = sorted(
        d for d in os.listdir(base_tenants_dir)
        if os.path.isdir(os.path.join(base_tenants_dir, d))
    )
    print(f"Found {len(tenants)} tenants to index in {base_tenants_dir}...")
    for t in tenants:
        rebuild_tenant_index(t, rag_service=rag)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rebuild FAISS Vector Index for Layers and Tenants")
    parser.add_argument("--layer", help="Layer name (e.g. l1_dkreasi, l2_dkarsa, l3_webia, l4_tenant)")
    parser.add_argument("--tenant", help="Tenant ID (e.g. tenant_automotive_01)")
    parser.add_argument("--all-tenants", action="store_true", help="Index all tenants in knowledge_base/l4_tenant/")
    args = parser.parse_args()

    if args.all_tenants:
        rebuild_all_tenants()
    elif args.tenant:
        rebuild_tenant_index(args.tenant)
    elif args.layer:
        rebuild_layer_index(args.layer)
    else:
        print("Please specify --layer, --tenant, or --all-tenants")