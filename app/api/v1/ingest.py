from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_service import RagService

router = APIRouter(tags=["Ingest"])
rag_service = RagService()


class ChunkItem(BaseModel):
    title: str
    content: str
    category: Optional[str] = "general"


class IngestRequest(BaseModel):
    layer: str
    tenant_id: Optional[str] = None
    chunks: List[ChunkItem]


@router.post("/ingest")
async def ingest_knowledge(req: IngestRequest):
    if req.layer == "l4" and not req.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required for layer l4")

    chunks_data = [c.model_dump() for c in req.chunks]
    rag_service.save_index(layer=req.layer, chunks=chunks_data, tenant_id=req.tenant_id)
    return {
        "status": "success",
        "layer": req.layer,
        "tenant_id": req.tenant_id,
        "chunks_indexed": len(req.chunks),
    }
