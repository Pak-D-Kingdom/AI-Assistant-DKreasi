"""
Business Brief Generator Service for WEBIA (Sprint L3-3).
Menyusun ringkasan kebutuhan website bisnis calon klien menjadi format terstruktur (JSON & Markdown),
serta menyediakan link pesan WhatsApp siap kirim ke tim sales dan payload dasar untuk knowledge tenant L4.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import urllib.parse
from pydantic import BaseModel, Field
import uuid


class BusinessBriefSchema(BaseModel):
    business_name: str = Field(..., description="Nama usaha / brand")
    category: str = Field(..., description="Kategori bisnis (F&B, Beauty, Automotive, dll)")
    description: str = Field(..., description="Deskripsi singkat jenis usaha dan keunggulan")
    target_audience: Optional[str] = Field(None, description="Target pelanggan / pasar")
    package_recommendation: Optional[str] = Field("Pulse (Rp899.000)", description="Paket WEBIA yang direkomendasikan")
    features_needed: List[str] = Field(default_factory=list, description="Daftar modul / fitur yang dibutuhkan")
    location: Optional[str] = Field(None, description="Kota / alamat operasional usaha")
    operating_hours: Optional[str] = Field(None, description="Hari dan jam operasional")
    contact_whatsapp: Optional[str] = Field(None, description="Nomor WhatsApp pemilik / admin")
    social_media: Optional[str] = Field(None, description="Akun Instagram, TikTok, atau medsos lain")


class BusinessBriefService:
    DEFAULT_SALES_PHONE = "6281234567890"

    @classmethod
    def create_brief(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Menerima data wawancara brief, memvalidasi dengan schema,
        dan menghasilkan keluaran terstruktur, tampilan Markdown, serta link WhatsApp.
        """
        brief = BusinessBriefSchema(**data)
        brief_id = f"BRIEF-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Format Teks untuk WhatsApp Sales
        wa_text = cls.format_whatsapp_text(brief, brief_id)
        encoded_wa_text = urllib.parse.quote(wa_text)
        wa_url = f"https://wa.me/{cls.DEFAULT_SALES_PHONE}?text={encoded_wa_text}"

        # Format Markdown Display untuk Chatbot UI
        md_display = cls.format_markdown_display(brief, brief_id, created_at)

        # L4 Tenant Starter Seed (Siap di-ingest saat client onboard ke L4)
        l4_seed = {
            "tenant_name": brief.business_name,
            "category": brief.category.lower(),
            "profile": {
                "description": brief.description,
                "target_audience": brief.target_audience,
                "location": brief.location,
                "operating_hours": brief.operating_hours,
            },
            "contact": {
                "whatsapp": brief.contact_whatsapp,
                "social_media": brief.social_media,
            },
            "features_requested": brief.features_needed,
            "selected_package": brief.package_recommendation,
        }

        return {
            "status": "success",
            "brief_id": brief_id,
            "created_at": created_at,
            "data": brief.model_dump(),
            "markdown_display": md_display,
            "whatsapp_url": wa_url,
            "l4_tenant_seed": l4_seed,
        }

    @classmethod
    def format_markdown_display(cls, b: BusinessBriefSchema, brief_id: str, created_at: str) -> str:
        features_str = "\n".join([f"  - {f}" for f in b.features_needed]) if b.features_needed else "  - Standar paket website"
        
        return f"""### 📄 Ringkasan Business Brief Website ({b.business_name})
**ID Dokumen:** `{brief_id}` · *{created_at}*

---

- **Nama Bisnis / Brand**: **{b.business_name}**
- **Kategori Industri**: {b.category}
- **Rekomendasi Paket**: **{b.package_recommendation}**
- **Deskripsi Usaha**: {b.description}
- **Target Pelanggan**: {b.target_audience or '-'}
- **Kota / Lokasi**: {b.location or '-'}
- **Jam Operasional**: {b.operating_hours or '-'}
- **Kontak & Medsos**: WhatsApp: {b.contact_whatsapp or '-'} | Medsos: {b.social_media or '-'}

**Fitur & Modul yang Dibutuhkan:**
{features_str}

---
*Brief ini siap dikirimkan langsung ke Tim Sales WEBIA untuk penawaran resmi dan estimasi pengerjaan.*"""

    @classmethod
    def format_whatsapp_text(cls, b: BusinessBriefSchema, brief_id: str) -> str:
        features_str = ", ".join(b.features_needed) if b.features_needed else "Sesuai rekomendasi paket"
        return (
            f"Halo Tim Sales *WEBIA*, saya ingin mengajukan penawaran pembuatan website berdasarkan Business Brief AI:\n\n"
            f"📄 *ID Brief*: {brief_id}\n"
            f"🏢 *Nama Bisnis*: {b.business_name}\n"
            f"🏷️ *Kategori*: {b.category}\n"
            f"💻 *Pilihan Paket*: {b.package_recommendation}\n"
            f"📝 *Deskripsi*: {b.description}\n"
            f"🎯 *Target Pasar*: {b.target_audience or '-'}\n"
            f"📍 *Lokasi*: {b.location or '-'}\n"
            f"⏰ *Operasional*: {b.operating_hours or '-'}\n"
            f"⚙️ *Kebutuhan Fitur*: {features_str}\n"
            f"📱 *Kontak Pemilik*: {b.contact_whatsapp or '-'}\n\n"
            f"Mohon informasi langkah selanjutnya dan jadwal konsultasinya. Terima kasih!"
        )
