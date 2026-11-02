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
