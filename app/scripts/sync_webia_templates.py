"""
Utilitas Sinkronisasi Otomatis Template Webia -> AI Assistant Knowledge Base.
Membaca katalog template dari seluruh seeder Webia (Laravel) dan memastikan seluruh
template terdaftar di knowledge_base/l3_webia/template/katalog_template.md.

Penggunaan:
    python -m app.scripts.sync_webia_templates [--webia-path PATH] [--dry-run]
"""

import os
import glob
import re
import argparse
from typing import List, Dict, Any


def extract_templates_from_file(filepath: str) -> List[Dict[str, Any]]:
    if not os.path.exists(filepath):
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    templates = []

    # 1. Format: WebiaTemplate::updateOrCreate( [ 'slug' => '...' ], [ ... ] );
    update_patterns = re.compile(
        r"WebiaTemplate::updateOrCreate\s*\(\s*\[\s*'slug'\s*=>\s*'([^']+)'\s*\]\s*,\s*\[(.*?)\]\s*\);",
        re.DOTALL,
    )
    for m in update_patterns.finditer(content):
        slug = m.group(1).strip()
        body = m.group(2)
        name_m = re.search(r"'name'\s*=>\s*'([^']+)'", body)
        cat_m = re.search(r"'category_slug'\s*=>\s*'([^']+)'", body)
        desc_m = re.search(r"'description'\s*=>\s*'([^']+)'", body)
        url_m = re.search(r"'template_url'\s*=>\s*'([^']+)'", body)

        name = name_m.group(1).strip().replace("—", "-") if name_m else slug
        cat = cat_m.group(1).strip() if cat_m else "general"
        desc = desc_m.group(1).strip() if desc_m else ""
        url = url_m.group(1).strip() if url_m else f"/webia/template/{slug}"

        templates.append({
            "name": name,
            "slug": slug,
            "category": cat,
            "description": desc,
            "template_url": url,
            "source": os.path.basename(filepath),
        })

    # 2. Format: $templates = [ [ ... ], [ ... ] ];
    match_templates_var = re.search(r"\$templates\s*=\s*\[", content)
    if match_templates_var:
        start_idx = match_templates_var.end()
        i = start_idx
        n = len(content)
        depth = 1
        item_start = None
        while i < n and depth > 0:
            c = content[i]
            if c in ("'", '"'):
                quote = c
                i += 1
                while i < n:
                    if content[i] == '\\':
                        i += 2
                        continue
                    if content[i] == quote:
                        break
                    i += 1
            elif c == '[':
                if depth == 1:
                    item_start = i
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 1 and item_start is not None:
                    item_block = content[item_start:i+1]
                    item_start = None
                    slug_m = re.search(r"'slug'\s*=>\s*'([^']+)'", item_block)
                    if slug_m:
                        slug = slug_m.group(1).strip()
                        name_m = re.search(r"'name'\s*=>\s*'([^']+)'", item_block)
                        cat_m = re.search(r"'category_slug'\s*=>\s*'([^']+)'", item_block)
                        desc_m = re.search(r"'description'\s*=>\s*'([^']+)'", item_block)
                        url_m = re.search(r"'template_url'\s*=>\s*'([^']+)'", item_block)

                        name = name_m.group(1).strip().replace("—", "-") if name_m else slug
                        cat = cat_m.group(1).strip() if cat_m else "general"
                        desc = desc_m.group(1).strip() if desc_m else ""
                        url = url_m.group(1).strip() if url_m else f"/webia/template/{slug}"

                        templates.append({
                            "name": name,
                            "slug": slug,
                            "category": cat,
                            "description": desc,
                            "template_url": url,
                            "source": os.path.basename(filepath),
                        })
            i += 1

    return templates


def sync_templates(webia_dir: str, kb_path: str, dry_run: bool = False):
    print("=" * 60)
    print("AI ASSISTANT - WEBIA TEMPLATE CATALOG SYNC")
    print("=" * 60)

    seeder_dir = os.path.join(webia_dir, "database", "seeders")
    seeder_files = sorted(glob.glob(os.path.join(seeder_dir, "*Template*.php")))

    if not seeder_files:
        print(f"[!] Tidak ada file template seeder ditemukan di {seeder_dir}")
        return

    all_templates = []
    for sf in seeder_files:
        ts = extract_templates_from_file(sf)
        print(f"[*] Menemukan {len(ts)} template dari {os.path.basename(sf)}")
        all_templates.extend(ts)

    # Dedup by slug
    seen = set()
    unique_templates = []
    for t in all_templates:
        if t["slug"] not in seen:
            seen.add(t["slug"])
            unique_templates.append(t)

    print(f"[*] Total {len(unique_templates)} template unik di Webia Laravel.")

    if not os.path.exists(kb_path):
        print(f"[!] File katalog knowledge base tidak ditemukan: {kb_path}")
        return

    with open(kb_path, "r", encoding="utf-8") as f:
        kb_content = f.read()

    missing = []
    for t in unique_templates:
        if t["slug"] not in kb_content:
            missing.append(t)

    print(f"[*] Template yang belum terdaftar di Knowledge Base: {len(missing)}")

    if not missing:
        print("[OK] SEMUA TEMPLATE WEBIA SUDAH 100% TERSINKRONISASI DI AI KNOWLEDGE BASE!")
        return

    for m in missing:
        print(f"    - [{m['category']}] {m['name']} (`{m['slug']}`)")

    if dry_run:
        print("\n[i] Mode dry-run aktif. Tidak ada berkas yang dimodifikasi.")
        return

    # Kelompokkan missing templates berdasarkan kategori agar rapi
    category_grouped: Dict[str, List[Dict[str, Any]]] = {}
    for m in missing:
        cat = m["category"]
        category_grouped.setdefault(cat, []).append(m)

    append_buffer = "\n\n---\n\n## 🔄 Katalog Template Tambahan Hasil Sinkronisasi Webia\n"
    append_buffer += "Daftar template berikut disinkronkan langsung dari seluruh seeder resmi Webia Laravel:\n\n"

    for cat, items in category_grouped.items():
        append_buffer += f"### Kategori: {cat.upper()}\n"
        for item in items:
            append_buffer += (
                f"- **{item['name']}** (`{item['slug']}` • Category: *{item['category']}*):\n"
                f"  - Deskripsi: {item['description']}\n"
                f"  - Demo / Live: `{item['template_url']}`\n\n"
            )

    with open(kb_path, "a", encoding="utf-8") as f:
        f.write(append_buffer)

    print(f"\n[OK] Berhasil menambahkan {len(missing)} template baru ke {kb_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sinkronisasi Template Webia ke Knowledge Base AI")
    parser.add_argument(
        "--webia-path",
        default="D:/Intern/Kreasi/Webia",
        help="Direktori root proyek Webia Laravel",
    )
    parser.add_argument(
        "--kb-path",
        default="knowledge_base/l3_webia/template/katalog_template.md",
        help="Path file markdown katalog template AI",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Jalankan pengecekan saja tanpa mengubah file",
    )
    args = parser.parse_args()

    sync_templates(args.webia_path, args.kb_path, args.dry_run)
