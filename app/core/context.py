from typing import Optional
from pydantic import BaseModel


class RequestContext(BaseModel):
    layer: str = "l1"
    tenant_id: Optional[str] = None
    site_id: Optional[str] = None
    origin: Optional[str] = None
    session_id: Optional[str] = None
