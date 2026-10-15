from typing import Optional
from fastapi import Header, Request
from app.core.config import get_settings
from app.core.context import RequestContext

settings = get_settings()

# Default sites for initial bootstrap
BUILTIN_SITES = {
    "site_dkreasi_public": {"layer": "l1", "tenant_id": None, "name": "D-KREASI Portal"},
    "site_dkarsa_public": {"layer": "l2", "tenant_id": None, "name": "D-Karsa Undangan"},
    "site_webia_public": {"layer": "l3", "tenant_id": None, "name": "WEBIA Business"},
}


async def get_request_context(
    request: Request,
    x_site_key: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None),
) -> RequestContext:
    site_key = x_site_key or x_api_key
    origin = request.headers.get("origin")

    # If valid registered site key provided
    if site_key and site_key in BUILTIN_SITES:
        site_info = BUILTIN_SITES[site_key]
        return RequestContext(
            layer=site_info["layer"],
            tenant_id=site_info["tenant_id"],
            site_id=site_key,
            origin=origin,
        )

    # Fallback default for direct API call
    return RequestContext(
        layer="l1",
        tenant_id=None,
        site_id="default_public",
        origin=origin,
    )
