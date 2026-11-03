"""
Utilitas Sinkronisasi Otomatis Template Webia -> AI Assistant Knowledge Base.
Membaca katalog template dari seeder Webia (Laravel) dan memastikan seluruh
template terdaftar di knowledge_base/l3_webia/template/katalog_template.md.

Penggunaan:
    python -m app.scripts.sync_webia_templates [--webia-path PATH] [--dry-run]
"""

import os
import re
import argparse
from typing import List, Dict, Any


def extract_templates_from_seeder(filepath: str) -> List[Dict[str, Any]]:
    if not os.path.exists(filepath):
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    templates = []
    # Match template array blocks in Laravel seeder
    pattern = re.compile(
        r"\[\s*'name'\s*=>\s*'([^']+)',\s*'slug'\s*=>\s*'([^']+)',\s*'category_slug'\s*=>\s*'([^']+)',"
        r".*?'description'\s*=>\s*'([^']+)',",
        re.DOTALL,
    )
    for match in pattern.finditer(content):
        name = match.group(1).replace("—", "-")
        slug = match.group(2)
        category = match.group(3)
        desc = match.group(4)
        templates.append({
            "name": name,
            "slug": slug,
            "category": category,
            "description": desc,
            "source": os.path.basename(filepath),
        })

    return templates


def sync_templates(webia_dir: str, kb_path: str, dry_run: bool = False):
    print("=" * 60)
    print("AI ASSISTANT - WEBIA TEMPLATE CATALOG SYNC")
    print("=" * 60)

    seeder_files = [
        os.path.join(webia_dir, "database", "seeders", "WebiaTemplateAqilaSeeder.php"),
        os.path.join(webia_dir, "database", "seeders", "WebiaTemplateSeeder.php"),
    ]

    all_templates = []
    for sf in seeder_files:
        ts = extract_templates_from_seeder(sf)
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

    # Append missing templates to knowledge base
    append_buffer = "\n\n---\n\n## 🔄 Template Tambahan Hasil Sinkronisasi Webia\n"
    for m in missing:
        append_buffer += (
            f"- **{m['name']}** (`{m['slug']}` • Category: *{m['category']}*):\n"
            f"  - Deskripsi: {m['description']}\n"
            f"  - Demo / Live: `/webia/template/{m['slug']}`\n\n"
        )

    with open(kb_path, "a", encoding="utf-8") as f:
        f.write(append_buffer)

    print(f"[OK] Berhasil menambahkan {len(missing)} template baru ke {kb_path}")


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
