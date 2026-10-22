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
    "site_webia_tenant_public": {"layer": "l4", "tenant_id": None, "name": "WEBIA Tenant Portal"},
}


async def get_request_context(
    request: Request,
    x_site_key: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
) -> RequestContext:
    site_key = x_site_key or x_api_key
    origin = request.headers.get("origin")

    # Dynamic tenant header override (e.g. from tenant switcher)
    if x_tenant_id:
        return RequestContext(
            layer="l4",
            tenant_id=x_tenant_id,
            site_id=site_key or f"site_{x_tenant_id}",
            origin=origin,
        )

    # If valid registered site key provided
    if site_key and site_key in BUILTIN_SITES:
        site_info = BUILTIN_SITES[site_key]
        resolved_tenant = site_info["tenant_id"]
        if site_info["layer"] == "l4" and not resolved_tenant:
            resolved_tenant = "tenant_automotive_01"
        return RequestContext(
            layer=site_info["layer"],
            tenant_id=resolved_tenant,
            site_id=site_key,
            origin=origin,
        )

    # Dynamic tenant site key resolution (e.g. site_tenant_automotive_01)
    if site_key and site_key.startswith("site_tenant_"):
        extracted_tenant_id = site_key.replace("site_", "")
        return RequestContext(
            layer="l4",
            tenant_id=extracted_tenant_id,
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
