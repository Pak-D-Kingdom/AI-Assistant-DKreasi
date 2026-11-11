from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.analytics_service import AnalyticsService

import json
import os
from pydantic import BaseModel

router = APIRouter(prefix="/analytics", tags=["AI Analytics & Monitoring"])


class EngineConfigPayload(BaseModel):
    llm_model: Optional[str] = None
    llm_temperature: Optional[float] = None
    llm_max_tokens: Optional[int] = None
    ai_cs_whatsapp: Optional[str] = None
    l1_prompt: Optional[str] = None
    l2_prompt: Optional[str] = None
    l3_prompt: Optional[str] = None
    l4_prompt: Optional[str] = None



@router.get("/overview")
async def get_analytics_overview(
    days: int = Query(30, description="Periode analisis dalam jumlah hari"),
    db: AsyncSession = Depends(get_db),
):
    """Mengembalikan data metrik analitik performa AI dalam format JSON."""
    return await AnalyticsService.get_overview_metrics(db=db, days=days)


@router.get("/hourly-traffic")
async def get_hourly_traffic(
    days: int = Query(30, description="Periode analisis dalam jumlah hari"),
    db: AsyncSession = Depends(get_db),
):
    """Mengembalikan data tren lalu lintas AI beserta SVG chart animasi dan sumbu X dinamis."""
    traffic_data = await AnalyticsService.get_traffic_trend_metrics(db=db, days=days)
    chart_svg = AnalyticsService._render_hourly_chart(traffic_data, days=days)
    max_count = traffic_data.get("max_count", 0)
    peak_unit = traffic_data.get("peak_unit", "chat/jam")
    return {
        "status": "success",
        "period_days": days,
        "badge_text": traffic_data.get("badge_text", "Continuous 24 Jam"),
        "subtitle": traffic_data.get("subtitle", "Kurva Throughput Beban Chat"),
        "peak_unit": peak_unit,
        "max_hourly_count": max_count,
        "peak_label": f"Puncak: {max_count} {peak_unit}",
        "chart_svg": chart_svg,
        "hourly_traffic": traffic_data.get("traffic_points", []),
    }


@router.get("/dashboard", response_class=HTMLResponse)
@router.get("", response_class=HTMLResponse)
async def get_analytics_dashboard_ui(
    days: int = Query(30, description="Periode analisis"),
    db: AsyncSession = Depends(get_db),
):
    """Menyajikan halaman UI Dashboard visual untuk manajemen D-Kreasi & Tim AI."""
    data = await AnalyticsService.get_overview_metrics(db=db, days=days)
    html_content = AnalyticsService.render_dashboard_html(data=data, days=days)
    return HTMLResponse(content=html_content)


@router.get("/cache")
async def get_cache_metrics():
    """Mengembalikan metrik performa Semantic Caching (Hit ratio, token saved, latency saved)."""
    from app.services.semantic_cache_service import get_semantic_cache
    return {
        "status": "success",
        "cache_metrics": get_semantic_cache().get_stats(),
    }


@router.post("/cache/clear")
async def clear_semantic_cache(
    layer: Optional[str] = Query(None, description="Layer spesifik yang ingin dibersihkan"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID spesifik yang ingin dibersihkan"),
):
    """Membersihkan semantic cache (global atau spesifik layer/tenant)."""
    from app.services.semantic_cache_service import invalidate_semantic_cache_safely
    invalidate_semantic_cache_safely(layer=layer, tenant_id=tenant_id)
    return {
        "status": "success",
        "message": f"Semantic cache berhasil dibersihkan (layer={layer}, tenant_id={tenant_id}).",
    }


@router.get("/engine-config")
def get_engine_config():
    """Mengambil konfigurasi AI Engine: Prompts per layer & parameter LLM."""
    from app.core.config import get_settings
    from app.layers.l1_dkreasi.prompts import get_l1_system_prompt
    from app.layers.l2_dkarsa.prompts import get_l2_system_prompt
    from app.layers.l3_webia.prompts import get_l3_system_prompt
    from app.layers.l4_business.prompts import get_l4_system_prompt

    settings = get_settings()
    config_file = os.path.join(settings.BASE_DIR, "data", "engine_config.json")
    custom_data = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                custom_data = json.load(f)
        except Exception:
            pass

    return {
        "status": "success",
        "llm_model": custom_data.get("llm_model", settings.LLM_MODEL),
        "llm_temperature": custom_data.get("llm_temperature", settings.LLM_TEMPERATURE),
        "llm_max_tokens": custom_data.get("llm_max_tokens", settings.LLM_MAX_TOKENS),
        "ai_cs_whatsapp": custom_data.get("ai_cs_whatsapp", settings.AI_CS_WHATSAPP),
        "l1_prompt": custom_data.get("l1_prompt", get_l1_system_prompt()),
        "l2_prompt": custom_data.get("l2_prompt", get_l2_system_prompt()),
        "l3_prompt": custom_data.get("l3_prompt", get_l3_system_prompt()),
        "l4_prompt": custom_data.get("l4_prompt", get_l4_system_prompt()),
    }


@router.post("/engine-config")
def save_engine_config(payload: EngineConfigPayload):
    """Menyimpan pembaruan konfigurasi AI Engine & Prompts."""
    from app.core.config import get_settings
    from app.services.semantic_cache_service import get_semantic_cache

    settings = get_settings()
    config_file = os.path.join(settings.BASE_DIR, "data", "engine_config.json")
    os.makedirs(os.path.dirname(config_file), exist_ok=True)

    data = payload.model_dump(exclude_unset=True)
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    from app.services.semantic_cache_service import invalidate_semantic_cache_safely
    invalidate_semantic_cache_safely()

    return {
        "status": "success",
        "message": "Konfigurasi AI Engine dan Prompts berhasil disimpan & semantic cache dibersihkan.",
        "config": data,
    }

