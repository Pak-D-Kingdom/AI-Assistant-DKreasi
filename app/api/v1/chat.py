from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_request_context
from app.core.context import RequestContext
from app.db.database import get_db
from app.pipeline.orchestrator import PipelineOrchestrator

router = APIRouter(tags=["Chat"])
orchestrator = PipelineOrchestrator()


class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: user, assistant, system")
    content: str = Field(..., description="Content text")


class ChatRequest(BaseModel):
    layer: Optional[str] = Field(None, description="Layer: l1, l2, l3, l4 (overrides context if dev)")
    session_id: Optional[str] = Field(None, description="Session ID for multi-turn tracking")
    messages: List[ChatMessage] = Field(..., description="Chat message history")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for L4")


@router.post("/chat")
@router.post("/api/ai/chat")
async def chat_endpoint(
    req: ChatRequest,
    context: RequestContext = Depends(get_request_context),
    db: AsyncSession = Depends(get_db),
):
    # If client explicitly specifies layer, honor it for flexibility
    if req.layer:
        context.layer = req.layer
    if req.session_id:
        context.session_id = req.session_id
    if req.tenant_id:
        context.tenant_id = req.tenant_id

    messages_dict = [{"role": m.role, "content": m.content} for m in req.messages]
    response = await orchestrator.execute(
        messages=messages_dict,
        context=context,
        db=db,
    )
    return response
