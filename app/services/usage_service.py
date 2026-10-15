from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Conversation, Message, Usage, FallbackEvent, HandoffEvent
from app.core.logging import logger


class UsageService:
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
