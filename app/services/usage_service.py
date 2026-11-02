from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Conversation, Message, Usage, Tenant, FallbackEvent, HandoffEvent
from app.core.logging import logger


class UsageService:
    PACKAGE_QUOTAS = {
        "pixel": 500,
        "pulse": 1500,
        "nexus": 2500,
        "infinity": 5000,
    }
    DEFAULT_QUOTA = 500

    @classmethod
    def evaluate_quota(
        cls,
        layer: str,
        tenant_id: Optional[str],
        current_usage: int,
        quota_limit: Optional[int] = None,
        package_tier: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Pure business rule logic for quota evaluation.
        Layer L1, L2, L3 are unlimited.
        L4 is limited based on package tier (Pixel: 500, Pulse: 1500, Nexus: 2500, Infinity: 5000).
        """
        layer_norm = str(layer).lower()
        if layer_norm not in ("l4", "l4_business") or not tenant_id:
            return {
                "allowed": True,
                "remaining": None,
                "quota": None,
                "usage": current_usage,
                "package_tier": package_tier or "unlimited",
            }

        tier = (package_tier or "pixel").lower()
        limit = quota_limit or cls.PACKAGE_QUOTAS.get(tier, cls.DEFAULT_QUOTA)

        if current_usage >= limit:
            return {
                "allowed": False,
                "remaining": 0,
                "quota": limit,
                "usage": current_usage,
                "package_tier": tier,
                "message": (
                    f"Mohon maaf, kuota layanan asisten chat otomatis bulan ini untuk bisnis ini "
                    f"telah mencapai batas maksimal ({limit} pesan). "
                    f"Silakan hubungi kami langsung via WhatsApp untuk bantuan lebih lanjut."
                ),
            }

        return {
            "allowed": True,
            "remaining": max(0, limit - current_usage),
            "quota": limit,
            "usage": current_usage,
            "package_tier": tier,
        }

    @classmethod
    async def check_quota(
        cls,
        db: Optional[AsyncSession],
        tenant_id: Optional[str],
        layer: str,
    ) -> Dict[str, Any]:
        """
        Memeriksa apakah tenant L4 masih memiliki sisa kuota pesan di bulan berjalan.
        Layer L1, L2, L3 tidak dibatasi kuota (unlimited).
        """
        layer_norm = str(layer).lower()
        if layer_norm not in ("l4", "l4_business") or not tenant_id or not db:
            return cls.evaluate_quota(layer=layer, tenant_id=tenant_id, current_usage=0)

        now = datetime.utcnow()
        first_day_of_month = datetime(now.year, now.month, 1)

        try:
            # 1. Hitung total pesan bulan ini untuk tenant
            stmt = select(func.count(Usage.id)).where(
                Usage.tenant_id == tenant_id,
                Usage.created_at >= first_day_of_month,
            )
            res = await db.execute(stmt)
            usage_count = res.scalar() or 0

            # 2. Ambil kuota paket tenant
            quota_limit = cls.DEFAULT_QUOTA
            tier = "pixel"
            tenant_res = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
            tenant_obj = tenant_res.scalar_one_or_none()
            if tenant_obj:
                if getattr(tenant_obj, "package_tier", None):
                    tier = tenant_obj.package_tier.lower()
                    quota_limit = cls.PACKAGE_QUOTAS.get(tier, cls.DEFAULT_QUOTA)
                if getattr(tenant_obj, "monthly_message_quota", None):
                    quota_limit = tenant_obj.monthly_message_quota

            eval_res = cls.evaluate_quota(
                layer=layer,
                tenant_id=tenant_id,
                current_usage=usage_count,
                quota_limit=quota_limit,
                package_tier=tier,
            )
            if not eval_res["allowed"]:
                logger.warning(
                    f"Quota exceeded for tenant={tenant_id}: {usage_count}/{quota_limit} (tier={tier})"
                )
            return eval_res
        except Exception as e:
            logger.error(f"Error checking quota for tenant={tenant_id}: {e}")
            # Fail-open if DB error occurs so legitimate chat is not broken
            return {"allowed": True, "remaining": None, "quota": None, "usage": 0}

    @classmethod
    async def get_tenant_usage_stats(cls, db: AsyncSession, tenant_id: str) -> Dict[str, Any]:
        """Mengambil data statistik pemakaian kuota bulan ini untuk tenant."""
        now = datetime.utcnow()
        first_day_of_month = datetime(now.year, now.month, 1)

        stmt = select(func.count(Usage.id)).where(
            Usage.tenant_id == tenant_id,
            Usage.created_at >= first_day_of_month,
        )
        res = await db.execute(stmt)
        usage_count = res.scalar() or 0

        tier = "pixel"
        quota_limit = cls.DEFAULT_QUOTA
        tenant_res = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant_obj = tenant_res.scalar_one_or_none()
        if tenant_obj:
            if getattr(tenant_obj, "package_tier", None):
                tier = tenant_obj.package_tier.lower()
                quota_limit = cls.PACKAGE_QUOTAS.get(tier, cls.DEFAULT_QUOTA)
            if getattr(tenant_obj, "monthly_message_quota", None):
                quota_limit = tenant_obj.monthly_message_quota

        return {
            "tenant_id": tenant_id,
            "period": f"{now.year}-{now.month:02d}",
            "package_tier": tier,
            "monthly_quota": quota_limit,
            "used_messages": usage_count,
            "remaining_messages": max(0, quota_limit - usage_count),
            "percentage_used": round((usage_count / quota_limit) * 100, 2) if quota_limit > 0 else 0,
            "is_quota_exhausted": usage_count >= quota_limit,
        }

    @staticmethod
    async def log_interaction(
        db: AsyncSession,
        session_id: str,
        layer: str,
        user_message: str,
        assistant_message: str,
        tenant_id: Optional[str] = None,
        site_id: Optional[str] = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        latency_ms: int = 0,
        provider: str = "llm",
        model: str = "default",
        is_fallback: bool = False,
    ):
        try:
            # 1. Create conversation record if not exists
            conv = Conversation(
                session_id=session_id,
                layer=layer,
                tenant_id=tenant_id,
                site_id=site_id,
            )
            db.add(conv)
            await db.flush()

            # 2. Add Messages
            db.add(Message(conversation_id=conv.id, role="user", content=user_message))
            db.add(Message(conversation_id=conv.id, role="assistant", content=assistant_message))

            # 3. Add Usage Record
            usage = Usage(
                session_id=session_id,
                layer=layer,
                tenant_id=tenant_id,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                latency_ms=latency_ms,
                provider=provider,
                model=model,
                is_fallback=is_fallback,
            )
            db.add(usage)
            await db.commit()
        except Exception as e:
            logger.error(f"Failed to log interaction to DB: {e}")
            await db.rollback()
