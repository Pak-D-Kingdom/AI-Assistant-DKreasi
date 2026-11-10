from typing import Optional, Dict, Any
from pydantic import BaseModel


class RequestContext(BaseModel):
    layer: str = "l1"
    tenant_id: Optional[str] = None
    site_id: Optional[str] = None
    origin: Optional[str] = None
    session_id: Optional[str] = None
    site_name: Optional[str] = None
    api_key_hash: Optional[str] = None
    hosting_status: Optional[Dict[str, Any]] = None
    customer_info: Optional[Dict[str, Any]] = None
