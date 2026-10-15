from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.db.models import Site

router = APIRouter(tags=["Sites"])


class SiteCreate(BaseModel):
    api_key: str
    name: str
    layer: str = "l1"
    tenant_id: Optional[str] = None
    origin_allowlist: Optional[str] = None


@router.get("/sites")
async def list_sites(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Site))
    sites = result.scalars().all()
    return [{"api_key": s.api_key, "name": s.name, "layer": s.layer, "tenant_id": s.tenant_id} for s in sites]


@router.post("/sites")
async def create_site(site_in: SiteCreate, db: AsyncSession = Depends(get_db)):
    new_site = Site(
        api_key=site_in.api_key,
        name=site_in.name,
        layer=site_in.layer,
        tenant_id=site_in.tenant_id,
        origin_allowlist=site_in.origin_allowlist,
    )
    db.add(new_site)
    await db.commit()
    return {"message": "Site created", "api_key": new_site.api_key}
