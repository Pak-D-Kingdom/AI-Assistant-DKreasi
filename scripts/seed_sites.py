import asyncio
from app.db.database import AsyncSessionLocal, init_db
from app.db.models import Site
from sqlalchemy import select


async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        initial_sites = [
            Site(api_key="site_dkreasi_public", name="D-KREASI Platform", layer="l1", origin_allowlist="*"),
            Site(api_key="site_dkarsa_public", name="D-Karsa Undangan", layer="l2", origin_allowlist="*"),
            Site(api_key="site_webia_public", name="WEBIA Business", layer="l3", origin_allowlist="*"),
            # Layer L4 (multi-tenant). Dipakai oleh widget di webia_tenant.html
            Site(api_key="site_webia_tenant_public", name="WEBIA Tenant", layer="l4", origin_allowlist="*"),
        ]

        added = 0
        for s in initial_sites:
            existing = await db.execute(select(Site).where(Site.api_key == s.api_key))
            if not existing.scalar_one_or_none():
                db.add(s)
                added += 1

        await db.commit()
        print(f"Default sites seeded successfully ({added} new, {len(initial_sites) - added} already existed).")


if __name__ == "__main__":
    asyncio.run(seed())