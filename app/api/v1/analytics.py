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
