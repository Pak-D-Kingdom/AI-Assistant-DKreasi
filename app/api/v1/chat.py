import copy
import dataclasses
import json
import logging
import re
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_request_context
from app.core.context import RequestContext
from app.db import models
from app.db.database import get_db
from app.pipeline.orchestrator import PipelineOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])
orchestrator = PipelineOrchestrator()

# ---------------------------------------------------------------------------
# Konfigurasi validasi
# ---------------------------------------------------------------------------
VALID_LAYERS = {"l1", "l2", "l3", "l4"}
ALLOWED_ROLES = {"user", "assistant"}   # role "system" dari client DITOLAK (anti prompt-injection)
MAX_MESSAGES = 20                       # riwayat maksimum yang diteruskan ke orchestrator
MAX_CONTENT_CHARS = 4000                # panjang maksimum per pesan

TENANT_ID_RE = re.compile(r"^tenant_[a-z0-9_]{1,60}$")
SESSION_ID_RE = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")

# Aktifkan setelah memastikan model Tenant di app/db/models.py punya kolom `tenant_id`
# dan semua tenant memang tersimpan di database (bukan hanya folder knowledge_base).
VALIDATE_TENANT_EXISTS = False


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: user, assistant (system diabaikan)")
    content: str = Field(..., description="Content text")


class ChatRequest(BaseModel):
    layer: Optional[str] = Field(None, description="Layer: l1, l2, l3, l4")
    session_id: Optional[str] = Field(None, description="Session ID for multi-turn tracking")
    messages: List[ChatMessage] = Field(..., description="Chat message history")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for L4")
    stream: Optional[bool] = Field(False, description="Enable SSE streaming mode")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _clone_context(ctx):
    """Salin context agar perubahan di request ini tidak bocor ke request lain
    (jika get_request_context mengembalikan objek yang di-cache / dibagi)."""
    if hasattr(ctx, "model_copy"):          # pydantic v2
        return ctx.model_copy()
    if hasattr(ctx, "copy") and hasattr(ctx, "__fields__"):  # pydantic v1
        return ctx.copy()
    if dataclasses.is_dataclass(ctx):
        return dataclasses.replace(ctx)
    return copy.copy(ctx)


def _layer_value(ctx) -> str:
    layer = getattr(ctx, "layer", "") or ""
    return str(getattr(layer, "value", layer)).lower()


async def _ensure_tenant_exists(db: AsyncSession, tenant_id: str) -> None:
    Tenant = getattr(models, "Tenant", None)
    column = getattr(Tenant, "tenant_id", None) if Tenant is not None else None
    if column is None:
        logger.warning("Model Tenant/kolom tenant_id tidak ditemukan; validasi keberadaan tenant dilewati.")
        return
    result = await db.execute(select(column).where(column == tenant_id).limit(1))
    if result.first() is None:
        raise HTTPException(status_code=404, detail=f"Tenant '{tenant_id}' tidak ditemukan.")


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def _safe_stream(generator):
    """Bungkus stream agar error di tengah jalan tidak memutus koneksi tanpa pesan."""
    try:
        async for chunk in generator:
            yield chunk
    except Exception:
        logger.exception("Error saat streaming respons chat")
        yield _sse({"type": "token", "content": "Mohon maaf, asisten sedang mengalami kendala teknis."})
        yield _sse({"type": "done"})


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------
@router.post("/chat")
@router.post("/api/ai/chat")
async def chat_endpoint(
    req: ChatRequest,
    raw_request: Request,
    context: RequestContext = Depends(get_request_context),
    db: AsyncSession = Depends(get_db),
):
    context = _clone_context(context)

    # 1. Layer
    if req.layer:
        layer = req.layer.strip().lower()
        if layer not in VALID_LAYERS:
            raise HTTPException(status_code=400, detail="Layer tidak valid.")
        context.layer = layer

    # 2. Tenant: header X-Tenant-Id dan body tidak boleh saling bertentangan
    header_tenant = (raw_request.headers.get("x-tenant-id") or "").strip() or None
    body_tenant = (req.tenant_id or "").strip() or None
    if header_tenant and body_tenant and header_tenant != body_tenant:
        raise HTTPException(status_code=400, detail="tenant_id pada header dan body tidak sama.")

    requested_tenant = body_tenant or header_tenant
    if requested_tenant:
        if not TENANT_ID_RE.match(requested_tenant):
            raise HTTPException(status_code=400, detail="Format tenant_id tidak valid.")
        context.tenant_id = requested_tenant

    is_tenant_layer = _layer_value(context) == "l4"
    tenant_id = getattr(context, "tenant_id", None)

    if is_tenant_layer:
        if not tenant_id:
            raise HTTPException(status_code=400, detail="tenant_id wajib diisi untuk layer L4.")
        if VALIDATE_TENANT_EXISTS:
            await _ensure_tenant_exists(db, tenant_id)

    # 3. Session: diberi awalan tenant agar sesi/riwayat tidak tercampur antar tenant
    raw_session = (req.session_id or "").strip()
    if raw_session:
        if not SESSION_ID_RE.match(raw_session):
            raise HTTPException(status_code=400, detail="Format session_id tidak valid.")
        context.session_id = f"{tenant_id}__{raw_session}" if is_tenant_layer else raw_session

    # 4. Pesan: hanya user/assistant, dipotong dan dibatasi jumlahnya
    messages_dict = []
    for m in req.messages:
        role = (m.role or "").strip().lower()
        content = (m.content or "").strip()
        if role not in ALLOWED_ROLES or not content:
            continue
        messages_dict.append({"role": role, "content": content[:MAX_CONTENT_CHARS]})
    messages_dict = messages_dict[-MAX_MESSAGES:]

    if not messages_dict or messages_dict[-1]["role"] != "user":
        raise HTTPException(status_code=400, detail="Pesan terakhir harus berasal dari user.")

    logger.info(
        "chat layer=%s tenant=%s session=%s msgs=%d",
        _layer_value(context), tenant_id, getattr(context, "session_id", None), len(messages_dict),
    )

    is_stream = req.stream or "text/event-stream" in raw_request.headers.get("accept", "")

    if is_stream:
        return StreamingResponse(
            _safe_stream(
                orchestrator.execute_stream(
                    messages=messages_dict,
                    context=context,
                    db=db,
                )
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    return await orchestrator.execute(
        messages=messages_dict,
        context=context,
        db=db,
    )