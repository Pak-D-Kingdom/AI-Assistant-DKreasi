import os
import argparse
from app.services.rag_service import RagService


def rebuild_layer_index(layer: str = "l1_dkreasi"):
    rag_service = RagService()
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
                chunks.append({
                    "title": title,
                    "content": content,
                    "file_path": os.path.relpath(file_path, kb_base),
                })

    if chunks:
        rag_service.save_index(layer=layer, chunks=chunks)
        print(f"Indexed {len(chunks)} documents for layer {layer}.")
    else:
        print(f"No documents found for layer {layer}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--layer", default="l1_dkreasi", help="Layer name to index")
    args = parser.parse_args()
    rebuild_layer_index(args.layer)
