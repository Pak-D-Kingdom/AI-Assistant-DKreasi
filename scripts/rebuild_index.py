import os
import sys
import argparse
from typing import Optional

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rag_service import RagService


def chunk_markdown_by_headings(content: str, default_title: str):
    """Chunk Markdown by H2 headings (## ) for high-precision semantic retrieval."""
    lines = content.splitlines()
    chunks = []
    current_title = default_title
    current_lines = []

    for line in lines:
        if line.startswith("## "):
            if current_lines:
                chunk_text = "\n".join(current_lines).strip()
                if chunk_text:
                    chunks.append({"title": current_title, "content": chunk_text})
                current_lines = []
            current_title = f"{default_title} - {line.replace('## ', '').strip()}"
        current_lines.append(line)

    if current_lines:
        chunk_text = "\n".join(current_lines).strip()
        if chunk_text:
            chunks.append({"title": current_title, "content": chunk_text})

    return chunks if chunks else [{"title": default_title, "content": content}]


def rebuild_layer_index(layer: str = "l1_dkreasi", rag_service: Optional[RagService] = None):
    if layer in ["l4", "l4_tenant"]:
        rebuild_all_tenants(rag_service=rag_service)
        return

    rag = rag_service or RagService()
    kb_base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base", layer)

    if not os.path.exists(kb_base):
        print(f"Directory {kb_base} does not exist.")
        return

    chunks = []
    for root, _, files in os.walk(kb_base):
        for f in files:
            if f.endswith(".md"):
                file_path = os.path.join(root, f)
                with open(file_path, "r", encoding="utf-8") as fp:
                    content = fp.read().strip()
                title = f.replace(".md", "").replace("_", " ").title()
                file_chunks = chunk_markdown_by_headings(content, title)
                for c in file_chunks:
                    c["file_path"] = os.path.relpath(file_path, kb_base)
                    chunks.append(c)

    if chunks:
        rag.save_index(layer=layer, chunks=chunks)
        print(f"Indexed {len(chunks)} chunks for layer {layer}.")
    else:
        print(f"No documents found for layer {layer}.")


def rebuild_tenant_index(tenant_id: str, rag_service: Optional[RagService] = None):
    rag = rag_service or RagService()
    root_dir = os.path.dirname(os.path.dirname(__file__))

    # Use knowledge_base/l4_tenant as the primary source
    tenant_dir = os.path.join(root_dir, "knowledge_base", "l4_tenant", tenant_id)

    if not os.path.exists(tenant_dir):
        print(f"Tenant directory for {tenant_id} does not exist in knowledge_base/l4_tenant.")
        return

    chunks = []
    for root, _, files in os.walk(tenant_dir):
        for f in files:
            if f.endswith(".md"):
                file_path = os.path.join(root, f)
                with open(file_path, "r", encoding="utf-8") as fp:
                    content = fp.read().strip()
                doc_title = f.replace(".md", "").replace("_", " ").title()
                file_chunks = chunk_markdown_by_headings(content, doc_title)
                for c in file_chunks:
                    c["file_path"] = os.path.relpath(file_path, tenant_dir)
                    chunks.append(c)

    if chunks:
        rag.save_index(layer="l4", chunks=chunks, tenant_id=tenant_id)
        print(f"Indexed {len(chunks)} chunks for tenant {tenant_id}.")
    else:
        print(f"No documents found for tenant {tenant_id}.")


def rebuild_all_tenants(rag_service: Optional[RagService] = None):
    root_dir = os.path.dirname(os.path.dirname(__file__))
    base_tenants_dir = os.path.join(root_dir, "knowledge_base", "l4_tenant")
    if not os.path.exists(base_tenants_dir):
        print(f"Tenant knowledge directory does not exist in knowledge_base/l4_tenant.")
        return

    rag = rag_service or RagService()
    tenants = [d for d in os.listdir(base_tenants_dir) if os.path.isdir(os.path.join(base_tenants_dir, d))]
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
