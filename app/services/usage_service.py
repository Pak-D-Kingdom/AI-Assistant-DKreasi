import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Conversation, Message, Usage, Tenant, FallbackEvent, HandoffEvent, MonthlyQuotaHistory
from app.core.logging import logger


class UsageService:
    PACKAGE_QUOTAS = {
        "pixel": 500,
        "pulse": 1500,
        "nexus": 2500,
        "infinity": 5000,
    }
    DEFAULT_QUOTA = 500
    _QUOTA_CACHE: Dict[str, Dict[str, Any]] = {}
    CACHE_TTL_SECONDS: int = 30

    @classmethod
    def clear_quota_cache(cls, tenant_id: Optional[str] = None):
        cls.invalidate_quota_cache(tenant_id)

    @classmethod
    def invalidate_quota_cache(cls, tenant_id: Optional[str] = None):
        """Invalidasi in-memory cache kuota saat ada pesan baru atau pembaruan paket."""
        if tenant_id:
            keys = [k for k in cls._QUOTA_CACHE if k.startswith(str(tenant_id))]
            for k in keys:
                cls._QUOTA_CACHE.pop(k, None)
        else:
            cls._QUOTA_CACHE.clear()


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
        cache_key = f"{tenant_id}_{now.year}_{now.month}"
        cached = cls._QUOTA_CACHE.get(cache_key)
        if cached and (time.time() - cached.get("cached_at", 0) < cls.CACHE_TTL_SECONDS):
            return cached["result"]

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
            cls._QUOTA_CACHE[cache_key] = {
                "cached_at": time.time(),
                "result": eval_res,
            }
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
            if tenant_id:
                cls.invalidate_quota_cache(tenant_id)
        except Exception as e:
            logger.error(f"Failed to log interaction to DB: {e}")
            await db.rollback()

    @classmethod
    async def record_or_update_monthly_snapshot(
        cls,
        db: AsyncSession,
        tenant_id: str,
        period: Optional[str] = None,
    ) -> MonthlyQuotaHistory:
        """Menyimpan atau memperbarui snapshot kuota bulanan tenant ke tabel riwayat."""
        now = datetime.utcnow()
        current_period = period or f"{now.year}-{now.month:02d}"

        stats = await cls.get_tenant_usage_stats(db, tenant_id)
        tier = stats.get("package_tier", "pixel")
        limit = stats.get("monthly_quota", cls.DEFAULT_QUOTA)
        used = stats.get("used_messages", 0)
        remaining = stats.get("remaining_messages", max(0, limit - used))
        percentage = stats.get("percentage_used", 0.0)
        is_exhausted = stats.get("is_quota_exhausted", False)

        stmt = select(MonthlyQuotaHistory).where(
            MonthlyQuotaHistory.tenant_id == tenant_id,
            MonthlyQuotaHistory.period == current_period,
        )
        res = await db.execute(stmt)
        record = res.scalar_one_or_none()

        if record:
            record.package_tier = tier
            record.quota_limit = limit
            record.used_messages = used
            record.remaining_messages = remaining
            record.percentage_used = percentage
            record.is_quota_exhausted = is_exhausted
            record.updated_at = now
        else:
            record = MonthlyQuotaHistory(
                tenant_id=tenant_id,
                period=current_period,
                package_tier=tier,
                quota_limit=limit,
                used_messages=used,
                remaining_messages=remaining,
                percentage_used=percentage,
                is_quota_exhausted=is_exhausted,
                created_at=now,
                updated_at=now,
            )
            db.add(record)

        await db.commit()
        await db.refresh(record)
        return record

    @classmethod
    async def get_monthly_quota_history(
        cls,
        db: AsyncSession,
        tenant_id: Optional[str] = None,
        period: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Mengambil rekapitulasi riwayat kuota bulanan."""
        stmt = select(MonthlyQuotaHistory).order_by(desc(MonthlyQuotaHistory.period), MonthlyQuotaHistory.tenant_id)
        if tenant_id:
            stmt = stmt.where(MonthlyQuotaHistory.tenant_id == tenant_id)
        if period:
            stmt = stmt.where(MonthlyQuotaHistory.period == period)

        res = await db.execute(stmt)
        records = res.scalars().all()
        return [
            {
                "id": r.id,
                "tenant_id": r.tenant_id,
                "period": r.period,
                "package_tier": r.package_tier,
                "quota_limit": r.quota_limit,
                "used_messages": r.used_messages,
                "remaining_messages": r.remaining_messages,
                "percentage_used": r.percentage_used,
                "is_quota_exhausted": r.is_quota_exhausted,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            }
            for r in records
        ]

    @classmethod
    async def bypass_tenant_quota(
        cls,
        db: AsyncSession,
        tenant_id: str,
        bonus_messages: int = 50,
        reason: str = "Bypass sementara oleh engineer / admin",
    ) -> Dict[str, Any]:
        """Memberikan bypass kuota darurat tambahan (unblock) tanpa mengubah tier paket."""
        tenant_res = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = tenant_res.scalar_one_or_none()

        now = datetime.utcnow()
        first_day_of_month = datetime(now.year, now.month, 1)

        stmt = select(func.count(Usage.id)).where(
            Usage.tenant_id == tenant_id,
            Usage.created_at >= first_day_of_month,
        )
        res = await db.execute(stmt)
        current_used = res.scalar() or 0

        tier = "pixel"
        current_limit = cls.DEFAULT_QUOTA
        if tenant:
            tier = tenant.package_tier or "pixel"
            current_limit = tenant.monthly_message_quota or cls.PACKAGE_QUOTAS.get(tier, cls.DEFAULT_QUOTA)
            # Berikan bonus: set kuota baru minimal current_used + bonus
            new_limit = max(current_limit + bonus_messages, current_used + bonus_messages)
            tenant.monthly_message_quota = new_limit
        else:
            new_limit = max(current_limit + bonus_messages, current_used + bonus_messages)
            tenant = Tenant(
                id=tenant_id,
                name=tenant_id.replace("_", " ").title(),
                package_tier=tier,
                monthly_message_quota=new_limit,
            )
            db.add(tenant)

        await db.commit()
        cls.invalidate_quota_cache(tenant_id)
        await cls.record_or_update_monthly_snapshot(db, tenant_id)

        logger.info(f"Bypass kuota granted for tenant={tenant_id}: +{bonus_messages} (new limit={new_limit}). Reason: {reason}")
        return {
            "status": "success",
            "tenant_id": tenant_id,
            "package_tier": tier,
            "previous_quota": current_limit,
            "new_quota": new_limit,
            "bonus_messages_added": bonus_messages,
            "current_usage": current_used,
            "remaining_messages": max(0, new_limit - current_used),
            "is_quota_exhausted": False,
            "message": f"Berhasil melakukan bypass darurat untuk {tenant_id}. Kuota ditambah +{bonus_messages} pesan (Total: {new_limit:,} pesan).",
        }

    @classmethod
    async def get_tenant_customer_insights(cls, db: AsyncSession, tenant_id: str) -> Dict[str, Any]:
        """Mengambil data analitik khusus portal konsumen pemilik toko (tren 7 hari & top pertanyaan)."""
        now = datetime.utcnow()
        days_id = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]

        # 1. Tren Pemakaian 7 Hari Terakhir
        trend = []
        for i in range(6, -1, -1):
            day_date = (now - timedelta(days=i)).date()
            start_dt = datetime(day_date.year, day_date.month, day_date.day, 0, 0, 0)
            end_dt = datetime(day_date.year, day_date.month, day_date.day, 23, 59, 59)

            stmt = select(func.count(Usage.id)).where(
                Usage.tenant_id == tenant_id,
                Usage.created_at >= start_dt,
                Usage.created_at <= end_dt,
            )
            count = (await db.execute(stmt)).scalar() or 0
            day_name = days_id[day_date.weekday()]
            trend.append({
                "date": day_date.strftime("%Y-%m-%d"),
                "display_date": day_date.strftime("%d/%m"),
                "day_name": day_name,
                "message_count": count,
            })

        # 2. Top Pertanyaan Populer Pelanggan di Toko Ini
        stmt_q = (
            select(Message.content, func.count(Message.id).label("freq"))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(
                Conversation.tenant_id == tenant_id,
                Message.role == "user",
            )
            .group_by(Message.content)
            .order_by(desc("freq"))
            .limit(5)
        )
        q_res = (await db.execute(stmt_q)).all()
        top_questions = [{"question": row[0], "count": row[1]} for row in q_res]

        # Fallback dummy questions jika pesan nyata masih sedikit
        if len(top_questions) < 3:
            default_samples = [
                {"question": "Apakah melayani reservasi atau booking jadwal?", "count": max(1, trend[-1]["message_count"] // 2 or 3)},
                {"question": "Bisa kirim pricelist daftar harga lengkap?", "count": max(1, trend[-2]["message_count"] // 2 or 2)},
                {"question": "Lokasi alamat toko dan jam operasional buka?", "count": 2},
                {"question": "Apakah ada diskon atau promo khusus bulan ini?", "count": 1},
            ]
            for s in default_samples:
                if len(top_questions) < 5 and not any(q["question"] == s["question"] for q in top_questions):
                    top_questions.append(s)

        # 3. Status Kuota Terkini
        stats = await cls.get_tenant_usage_stats(db, tenant_id)

        return {
            "tenant_id": tenant_id,
            "period": stats.get("period"),
            "package_tier": stats.get("package_tier"),
            "monthly_quota": stats.get("monthly_quota"),
            "used_messages": stats.get("used_messages"),
            "remaining_messages": stats.get("remaining_messages"),
            "percentage_used": stats.get("percentage_used"),
            "is_quota_exhausted": stats.get("is_quota_exhausted"),
            "usage_trend_7d": trend,
            "top_questions": top_questions,
        }
