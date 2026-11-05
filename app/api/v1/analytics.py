from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["AI Analytics & Monitoring"])


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
    """Menyajikan halaman UI Dashboard visual untuk manajemen PakDe Group & Tim AI."""
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
    from app.services.semantic_cache_service import get_semantic_cache
    get_semantic_cache().invalidate(layer=layer, tenant_id=tenant_id)
    return {
        "status": "success",
        "message": f"Semantic cache berhasil dibersihkan (layer={layer}, tenant_id={tenant_id}).",
    }
