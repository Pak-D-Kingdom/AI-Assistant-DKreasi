import os
import re
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.rag_service import RagService
from scripts.rebuild_index import rebuild_tenant_index

router = APIRouter(prefix="/tenants", tags=["Tenants Knowledge"])

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
KB_TENANTS_DIR = os.path.join(ROOT_DIR, "knowledge_base", "l4_tenant")


class TenantKnowledgePayload(BaseModel):
    profil: Optional[str] = ""
    layanan: Optional[str] = ""
    kebijakan: Optional[str] = ""
    faq: Optional[str] = ""


def _extract_biz_info(profil_text: str, tenant_id: str) -> Dict[str, str]:
    name = tenant_id.replace("_", " ").title()
    category = "General"
    
    first_heading = re.search(r"^#\s+(.*?)(?:\s*-\s*Profil Bisnis)?$", profil_text, re.MULTILINE)
    if first_heading:
        name = first_heading.group(1).strip()

    cat_match = re.search(r"-\s+\*\*Kategori\*\*:\s*(.*)", profil_text)
    if cat_match:
        raw_cat = cat_match.group(1).strip()
        clean_cat = re.sub(r"\s*\(.*?\)", "", raw_cat).strip()
        category = clean_cat if clean_cat else raw_cat

    return {"name": name, "category": category}


@router.get("")
async def list_tenants():
    """List all available tenants in knowledge_base/l4_tenant."""
    if not os.path.exists(KB_TENANTS_DIR):
        return []

    tenants = []
    for entry in sorted(os.listdir(KB_TENANTS_DIR)):
        entry_path = os.path.join(KB_TENANTS_DIR, entry)
        if os.path.isdir(entry_path):
            profil_path = os.path.join(entry_path, "profil.md")
            profil_text = ""
            if os.path.exists(profil_path):
                with open(profil_path, "r", encoding="utf-8") as f:
                    profil_text = f.read()
            info = _extract_biz_info(profil_text, entry)
            tenants.append({
                "tenant_id": entry,
                "name": info["name"],
                "category": info["category"],
            })
    return tenants


@router.get("/next-id")
async def get_next_id(category: str):
    """Generate the next auto-incrementing tenant_id for a given category (e.g. tenant_beauty_02)."""
    pattern = re.compile(rf"^tenant_{re.escape(category)}_(\d+)$")
    existing_nums = []
    if os.path.exists(KB_TENANTS_DIR):
        for entry in os.listdir(KB_TENANTS_DIR):
            m = pattern.match(entry)
            if m:
                existing_nums.append(int(m.group(1)))
    next_num = max(existing_nums, default=0) + 1
    next_id = f"tenant_{category}_{next_num:02d}"
    return {"category": category, "next_id": next_id, "next_num": next_num}


@router.get("/{tenant_id}/knowledge")
async def get_tenant_knowledge(tenant_id: str):
    """Retrieve 4 knowledge markdown files for the given tenant."""
    tenant_dir = os.path.join(KB_TENANTS_DIR, tenant_id)
    if not os.path.exists(tenant_dir):
        raise HTTPException(status_code=404, detail=f"Tenant '{tenant_id}' not found.")

    def read_file(name: str) -> str:
        p = os.path.join(tenant_dir, name)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return f.read().strip()
        return ""

    return {
        "tenant_id": tenant_id,
        "profil": read_file("profil.md"),
        "layanan": read_file("layanan.md"),
        "kebijakan": read_file("kebijakan.md"),
        "faq": read_file("faq.md"),
    }


@router.post("/{tenant_id}/knowledge")
async def save_tenant_knowledge(tenant_id: str, payload: TenantKnowledgePayload):
    """Save knowledge markdown files for a tenant and automatically rebuild FAISS index."""
    tenant_dir = os.path.join(KB_TENANTS_DIR, tenant_id)
    os.makedirs(tenant_dir, exist_ok=True)

    files_to_write = {
        "profil.md": payload.profil or "",
        "layanan.md": payload.layanan or "",
        "kebijakan.md": payload.kebijakan or "",
        "faq.md": payload.faq or "",
    }

    for fname, content in files_to_write.items():
        if content:
            fpath = os.path.join(tenant_dir, fname)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content.strip() + "\n")

    # Re-index immediately in FAISS
    rag = RagService()
    rebuild_tenant_index(tenant_id, rag_service=rag)

    return {
        "status": "success",
        "tenant_id": tenant_id,
        "message": f"Knowledge base untuk '{tenant_id}' berhasil disimpan dan di-index ke FAISS.",
    }
