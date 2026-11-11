import os
import re
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.services.rag_service import RagService
from scripts.rebuild_index import rebuild_tenant_index
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db

from app.db.models import Tenant, Usage
from sqlalchemy import select, delete
from datetime import datetime

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

    # Invalidate semantic cache for this tenant
    from app.services.semantic_cache_service import get_semantic_cache
    get_semantic_cache().invalidate(tenant_id=tenant_id)

    return {
        "status": "success",
        "tenant_id": tenant_id,
        "message": f"Knowledge base untuk '{tenant_id}' berhasil disimpan dan di-index ke FAISS.",
    }

class TenantTierPayload(BaseModel):
    package_tier: str
    custom_quota: Optional[int] = None


@router.get("/{tenant_id}/quota")
async def get_tenant_quota(tenant_id: str, db: AsyncSession = Depends(get_db)):
    """Mengambil status pemakaian kuota chat bulanan tenant."""
    from app.services.usage_service import UsageService
    stats = await UsageService.get_tenant_usage_stats(db=db, tenant_id=tenant_id)
    return stats


@router.post("/{tenant_id}/tier")
async def update_tenant_tier(tenant_id: str, payload: TenantTierPayload, db: AsyncSession = Depends(get_db)):
    """Memperbarui paket layanan tenant (pixel, pulse, nexus, infinity) atau kuota pesan."""
    from app.db.models import Tenant
    from app.services.usage_service import UsageService
    from sqlalchemy import select

    tier = payload.package_tier.lower()
    if tier not in UsageService.PACKAGE_QUOTAS and not payload.custom_quota:
        raise HTTPException(status_code=400, detail="Package tier tidak valid. Pilihan: pixel, pulse, nexus, infinity.")

    quota = payload.custom_quota or UsageService.PACKAGE_QUOTAS.get(tier, 500)

    res = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = res.scalar_one_or_none()
    if not tenant:
        tenant = Tenant(
            id=tenant_id,
            name=tenant_id.replace("_", " ").title(),
            package_tier=tier,
            monthly_message_quota=quota,
        )
        db.add(tenant)
    else:
        tenant.package_tier = tier
        tenant.monthly_message_quota = quota

    await db.commit()
    UsageService.invalidate_quota_cache(tenant_id)
    return {
        "status": "success",
        "tenant_id": tenant_id,
        "package_tier": tier,
        "monthly_quota": quota,
        "message": f"Paket tenant '{tenant_id}' berhasil diperbarui ke {tier} (kuota {quota} pesan/bulan).",
    }


@router.get("/{tenant_id}/history")
async def get_tenant_history(tenant_id: str, period: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """Mengambil riwayat snapshot kuota bulanan untuk tenant tertentu."""
    from app.services.usage_service import UsageService
    history = await UsageService.get_monthly_quota_history(db=db, tenant_id=tenant_id, period=period)
    return {"tenant_id": tenant_id, "history": history}


@router.get("/history/overview")
async def get_all_tenants_history(period: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """Mengambil rekapitulasi riwayat snapshot bulanan seluruh tenant."""
    from app.services.usage_service import UsageService
    history = await UsageService.get_monthly_quota_history(db=db, period=period)
    return {"period": period, "total_records": len(history), "history": history}


@router.get("/{tenant_id}/insights")
async def get_tenant_insights(tenant_id: str, db: AsyncSession = Depends(get_db)):
    """Mengambil wawasan analitik konsumen untuk portal pemilik toko (tren 7 hari & top pertanyaan)."""
    from app.services.usage_service import UsageService
    insights = await UsageService.get_tenant_customer_insights(db=db, tenant_id=tenant_id)
    return insights


@router.get("/{tenant_id}/unanswered")
async def get_tenant_unanswered(tenant_id: str, db: AsyncSession = Depends(get_db)):
    """Mengambil daftar pertanyaan pengunjung yang belum terjawab / low-confidence."""
    from app.services.usage_service import UsageService
    unanswered = await UsageService.get_tenant_unanswered_queries(db=db, tenant_id=tenant_id)
    return {"tenant_id": tenant_id, "unanswered_queries": unanswered}


class TenantAiFullUpdatePayload(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    package_tier: Optional[str] = None
    monthly_quota: Optional[int] = None
    reset_usage: Optional[bool] = False
    whatsapp: Optional[str] = None
    address: Optional[str] = None
    operating_hours: Optional[str] = None
    greeting: Optional[str] = None
    description: Optional[str] = None
    profil_md: Optional[str] = None
    layanan_md: Optional[str] = None
    kebijakan_md: Optional[str] = None
    faq_md: Optional[str] = None


@router.post("/{tenant_id}/update-ai")
@router.put("/{tenant_id}/update-ai")
async def update_tenant_full_ai(tenant_id: str, payload: TenantAiFullUpdatePayload, db: AsyncSession = Depends(get_db)):
    """Memperbarui seluruh konfigurasi AI klien (Profil, Sapaan, Kuota, Tier, dan Dokumen Markdown L4) serta me-rebuild index FAISS."""
    from app.services.usage_service import UsageService
    from app.services.analytics_service import AnalyticsService
    from app.services.semantic_cache_service import get_semantic_cache

    # 1. Update / Insert DB Tenant
    res = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = res.scalar_one_or_none()

    tier = (payload.package_tier or (tenant.package_tier if tenant else "pixel")).lower()
    quota = payload.monthly_quota if payload.monthly_quota is not None else (tenant.monthly_message_quota if tenant else UsageService.PACKAGE_QUOTAS.get(tier, 500))

    if not tenant:
        tenant = Tenant(
            id=tenant_id,
            name=(payload.name or tenant_id.replace("_", " ").title()).strip(),
            category=(payload.category or "general").strip(),
            package_tier=tier,
            monthly_message_quota=quota,
        )
        db.add(tenant)
    else:
        if payload.name:
            tenant.name = payload.name.strip()
        if payload.category:
            tenant.category = payload.category.strip()
        if payload.package_tier:
            tenant.package_tier = tier
        if payload.monthly_quota is not None:
            tenant.monthly_message_quota = int(payload.monthly_quota)

    # 2. Reset pemakaian bulan berjalan jika diminta
    if payload.reset_usage:
        now = datetime.utcnow()
        first_day = datetime(now.year, now.month, 1)
        await db.execute(delete(Usage).where(Usage.tenant_id == tenant_id, Usage.created_at >= first_day))

    await db.commit()
    await db.refresh(tenant)
    UsageService.invalidate_quota_cache(tenant_id)

    # 3. Simpan / Perbarui berkas Knowledge Base di knowledge_base/l4_tenant/{tenant_id}
    tenant_dir = os.path.join(KB_TENANTS_DIR, tenant_id)
    os.makedirs(tenant_dir, exist_ok=True)

    profil_path = os.path.join(tenant_dir, "profil.md")
    if payload.profil_md is not None and payload.profil_md.strip():
        with open(profil_path, "w", encoding="utf-8") as f:
            f.write(payload.profil_md.strip() + "\n")
    elif any([payload.whatsapp, payload.address, payload.operating_hours, payload.greeting, payload.description, payload.name, payload.category]):
        existing_text = ""
        if os.path.exists(profil_path):
            with open(profil_path, "r", encoding="utf-8") as f:
                existing_text = f.read()

        b_name = payload.name or tenant.name or tenant_id.replace("_", " ").title()
        b_cat = payload.category or tenant.category or "General"
        b_wa = payload.whatsapp if payload.whatsapp is not None else "-"
        b_addr = payload.address if payload.address is not None else "-"
        b_hours = payload.operating_hours if payload.operating_hours is not None else "-"
        b_desc = payload.description if payload.description is not None else "-"
        b_greet = payload.greeting if payload.greeting is not None else "-"

        if existing_text:
            new_text = existing_text
            if payload.name:
                new_text = re.sub(r"(#\s+)(.*?)(?:\s*-\s*Profil Bisnis)?(\n|$)", rf"\1{b_name} - Profil Bisnis\3", new_text, count=1)
                new_text = re.sub(r"(-\s+\*\*Nama Bisnis\*\*:\s*)(.*)", rf"\1{b_name}", new_text)
            if payload.category:
                new_text = re.sub(r"(-\s+\*\*Kategori\*\*:\s*)(.*)", rf"\1{b_cat}", new_text)
            if payload.whatsapp is not None:
                new_text = re.sub(r"(-\s+\*\*(?:WhatsApp(?:[^\*]+)?|Kontak|Hotline)\*\*:\s*)(.*)", rf"\1{b_wa}", new_text)
            if payload.address is not None:
                new_text = re.sub(r"(-\s+\*\*Alamat\*\*:\s*)(.*)", rf"\1{b_addr}", new_text)
            if payload.operating_hours is not None:
                new_text = re.sub(r"(-\s+\*\*Jam Operasional\*\*:\s*)(.*)", rf"\1{b_hours}", new_text)
            if payload.description is not None:
                new_text = re.sub(r"(-\s+\*\*Deskripsi\*\*:\s*)(.*)", rf"\1{b_desc}", new_text)
            if payload.greeting is not None:
                if "- **Sapaan**:" in new_text:
                    new_text = re.sub(r"(-\s+\*\*Sapaan\*\*:\s*)(.*)", rf"\1{b_greet}", new_text)
                else:
                    new_text += f"\n- **Sapaan**: {b_greet}\n"
        else:
            new_text = f"""# {b_name} - Profil Bisnis

## Profil & Informasi Bisnis
- **Nama Bisnis**: {b_name}
- **Kategori**: {b_cat}
- **Alamat**: {b_addr}
- **Jam Operasional**: {b_hours}
- **Deskripsi**: {b_desc}

## Kontak & Call to Action (CTA)
- **WhatsApp**: {b_wa}
- **Sapaan**: {b_greet}
"""
        with open(profil_path, "w", encoding="utf-8") as f:
            f.write(new_text.strip() + "\n")

    if payload.layanan_md is not None and payload.layanan_md.strip():
        with open(os.path.join(tenant_dir, "layanan.md"), "w", encoding="utf-8") as f:
            f.write(payload.layanan_md.strip() + "\n")

    if payload.kebijakan_md is not None and payload.kebijakan_md.strip():
        with open(os.path.join(tenant_dir, "kebijakan.md"), "w", encoding="utf-8") as f:
            f.write(payload.kebijakan_md.strip() + "\n")

    if payload.faq_md is not None and payload.faq_md.strip():
        with open(os.path.join(tenant_dir, "faq.md"), "w", encoding="utf-8") as f:
            f.write(payload.faq_md.strip() + "\n")

    # 4. Rebuild FAISS index
    try:
        rag = RagService()
        rebuild_tenant_index(tenant_id, rag_service=rag)
    except Exception as e:
        pass

    # 5. Invalidate semantic cache
    from app.services.semantic_cache_service import invalidate_semantic_cache_safely
    invalidate_semantic_cache_safely(tenant_id=tenant_id)

    # 6. Retrieve fresh stats & details
    stats = await UsageService.get_tenant_usage_stats(db=db, tenant_id=tenant_id)
    detail_info = AnalyticsService._get_tenant_detail_info(tenant_id)

    return {
        "status": "success",
        "tenant_id": tenant_id,
        "name": tenant.name,
        "category": tenant.category,
        "package_tier": tenant.package_tier,
        "monthly_quota": tenant.monthly_message_quota,
        "stats": stats,
        "detail": detail_info,
        "message": f"Konfigurasi AI dan Knowledge Base untuk '{tenant.name}' berhasil disimpan dan di-index ke FAISS.",
    }

