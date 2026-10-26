from app.layers.base import BaseLayer
from app.layers.l4_tenant.prompts import get_l4_system_prompt
from app.layers.l4_tenant.tools import L4IntentRouter


class L4TenantLayer(BaseLayer):
    @property
    def layer_name(self) -> str:
        return "l4_tenant"

    def get_system_prompt(self, context=None) -> str:
        business_name = "Bisnis Klien WEBIA"
        category = "Umum"
        if context and getattr(context, "tenant_id", None):
            # Format readable name from tenant_id, e.g. tenant_automotive_01 -> Automotive 01
            parts = context.tenant_id.replace("tenant_", "").split("_")
            category = parts[0].capitalize()
            business_name = f"Mitra {category} ({context.tenant_id})"
        return get_l4_system_prompt(business_name=business_name, category=category)

    def route_intent(self, query: str):
        return L4IntentRouter.detect_and_route(query)


# Backward compatibility alias
L4BusinessLayer = L4TenantLayer

