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
        ]

        for s in initial_sites:
            existing = await db.execute(select(Site).where(Site.api_key == s.api_key))
            if not existing.scalar_one_or_none():
                db.add(s)

        await db.commit()
        print("Default sites seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
