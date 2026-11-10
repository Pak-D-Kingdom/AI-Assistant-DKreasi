"""
Utilitas Sinkronisasi Otomatis Template D'Karsa -> AI Assistant Knowledge Base (Layer 2).
Membaca katalog resmi dari D-Karsa (docs/template-pricing-catalog.json & template-registry.json)
dan menghasilkan berkas knowledge_base/l2_dkarsa/template/katalog_template.md lengkap.

Penggunaan:
    python -m app.scripts.sync_dkarsa_templates [--dkarsa-path PATH] [--ref GIT_REF]
"""

import os
import sys
import json
import subprocess
import argparse
from typing import List, Dict, Any
from collections import defaultdict


def load_dkarsa_data(dkarsa_path: str, git_ref: str = "jefri-dev"):
    # 1. Coba baca via git show dari ref branch
    pricing_data = None
    registry_data = None

    try:
        cmd_pricing = ["git", "show", f"{git_ref}:docs/template-pricing-catalog.json"]
        out_pricing = subprocess.check_output(cmd_pricing, cwd=dkarsa_path, stderr=subprocess.DEVNULL)
        pricing_data = json.loads(out_pricing.decode("utf-8"))
    except Exception:
        # Fallback ke file fisik lokal jika ada
        local_p = os.path.join(dkarsa_path, "docs", "template-pricing-catalog.json")
        if os.path.exists(local_p):
            with open(local_p, "r", encoding="utf-8") as f:
                pricing_data = json.load(f)

    try:
        cmd_reg = ["git", "show", f"{git_ref}:docs/template-registry.json"]
        out_reg = subprocess.check_output(cmd_reg, cwd=dkarsa_path, stderr=subprocess.DEVNULL)
        registry_data = json.loads(out_reg.decode("utf-8"))
    except Exception:
        local_r = os.path.join(dkarsa_path, "docs", "template-registry.json")
        if os.path.exists(local_r):
            with open(local_r, "r", encoding="utf-8") as f:
                registry_data = json.load(f)

    return pricing_data, registry_data


def generate_katalog_markdown(pricing_items: List[Dict[str, Any]], registry_dict: Dict[str, Any]) -> str:
    # Buat lookup dari registry berdasarkan key
    reg_lookup = {}
    if registry_dict and "templates" in registry_dict:
        for t in registry_dict["templates"]:
            k = t.get("key")
            if k:
                reg_lookup[k] = t

    # Kelompokkan berdasarkan L1 Bab (Kategori Acara) dan L2 Subbab
    grouped = defaultdict(lambda: defaultdict(list))
    for item in pricing_items:
        l1 = item.get("l1_name", "Undangan Lainnya").strip()
        l2 = item.get("l2_subbab", "Umum").strip()
        grouped[l1][l2].append(item)

    lines = [
        "# Katalog Desain & Koleksi Template Undangan Digital D'Karsa",
        "",
        f"D'Karsa menyediakan koleksi **{len(pricing_items)} tema desain resmi siap pakai (turnkey templates)** + opsi Custom Request yang terbagi ke dalam 6 Kategori Acara Utama dan 4 Tingkatan Paket Harga (Basic Rp50.000, Premium Rp110.000, Eksklusif Rp180.000, dan Kustom Rp280.000).",
        "",
        "Setiap template dilengkapi tautan demo resmi `/demo/{key}` yang dapat langsung dibuka dan dicoba oleh calon pemesan.",
        "",
        "---",
        "",
    ]

    # Urutan kategori bab acara
    category_order = [
        "Undangan Pernikahan",
        "Undangan Ulang Tahun",
        "Undangan Wisuda dan Kelulusan",
        "Undangan Aqiqah dan Kelahiran",
        "Undangan Keagamaan",
        "Undangan Acara Formal",
    ]

    cat_idx = 1
    for cat_name in category_order:
        if cat_name not in grouped:
            continue

        subgroups = grouped[cat_name]
        lines.append(f"## {cat_idx}. Kategori {cat_name}")
        lines.append("")

        for sub_name, items in subgroups.items():
            lines.append(f"### Sub-Kategori: {sub_name} ({len(items)} Desain)")
            lines.append("")

            for it in items:
                code = it.get("code", "")
                key = it.get("template_key", it.get("key", ""))
                style = it.get("l3_style", "")
                color = it.get("l4_color_name", "")
                demo_url = it.get("demo_url", f"/demo/{key}")
                rec_tier = (it.get("recommended_tier") or "premium").capitalize()

                # Cari nama dari registry jika ada
                reg_info = reg_lookup.get(key, {})
                display_name = reg_info.get("name")
                if not display_name:
                    display_name = key.replace("-", " ").title()

                motifs = reg_info.get("motifs", [])
                motifs_str = f", motif: {', '.join(motifs[:4])}" if motifs else ""

                # Format harga tier
                price_str = "Rp180.000" if rec_tier.lower() == "eksklusif" else ("Rp110.000" if rec_tier.lower() == "premium" else "Rp50.000")

                lines.append(
                    f"- **{display_name}** (`{key}` · *{rec_tier} - {price_str}*):\n"
                    f"  - Kode: `{code}` | Gaya: **{style}** | Palet Warna: **{color}**{motifs_str}.\n"
                    f"  - Cocok untuk acara: {sub_name}.\n"
                    f"  - Live Demo: `{demo_url}`"
                )

            lines.append("")

        cat_idx += 1

    # Tambahkan opsi Custom Request
    lines.extend([
        "---",
        "",
        "## 7. Opsi Kustom Request & Layanan Desain Bebas Impianmu",
        "- **Custom Request Desain Bebas Impianmu** (`custom-request` · *Kustom - Rp280.000*):",
        "  - Desain eksklusif dibuat dari nol sesuai sketsa/referensi Pinterest customer, konsultasi 1-on-1 langsung dengan desainer D'Karsa.",
        "  - Gratis Custom Domain sendiri (contoh: bima-laras.com), revisi fleksibel, animasi partikel sinematik, QR Code check-in tamu meja VIP.",
        "  - Hubungi WhatsApp CS D'Karsa untuk konsultasi desain kustom.",
        "",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Sinkronisasi Template D-Karsa ke AI Assistant Knowledge Base")
    parser.add_argument("--dkarsa-path", default=r"d:\Intern\Kreasi\D-Karsa", help="Path direktori repositori D-Karsa")
    parser.add_argument("--ref", default="jefri-dev", help="Git ref / branch sumber (default: jefri-dev)")
    args = parser.parse_args()

    print(f"[*] Membaca data template D'Karsa dari {args.dkarsa_path} (ref: {args.ref})...")
    pricing_data, registry_data = load_dkarsa_data(args.dkarsa_path, args.ref)

    if not pricing_data:
        print("[!] Gagal membaca template-pricing-catalog.json!")
        sys.exit(1)

    print(f"[*] Ditemukan {len(pricing_data)} template di pricing catalog.")

    # Target output markdown
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    target_md = os.path.join(base_dir, "knowledge_base", "l2_dkarsa", "template", "katalog_template.md")
    os.makedirs(os.path.dirname(target_md), exist_ok=True)

    md_content = generate_katalog_markdown(pricing_data, registry_data)

    with open(target_md, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"[OK] Berhasil memperbarui {target_md} dengan {len(pricing_data)} template!")


if __name__ == "__main__":
    main()
