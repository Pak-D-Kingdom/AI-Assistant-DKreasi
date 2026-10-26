from app.layers.l1_dkreasi.config import L1DkreasiLayer
from app.layers.l2_dkarsa.config import L2DkarsaLayer
from app.layers.l3_webia.config import L3WebiaLayer
from app.layers.l4_tenant.config import L4TenantLayer


class ToolRegistry:
    def __init__(self):
        l4_tenant_layer = L4TenantLayer()
        self._layers = {
            "l1": L1DkreasiLayer(),
            "l1_dkreasi": L1DkreasiLayer(),
            "l2": L2DkarsaLayer(),
            "l2_dkarsa": L2DkarsaLayer(),
            "l3": L3WebiaLayer(),
            "l3_webia": L3WebiaLayer(),
            "l4": l4_tenant_layer,
            "l4_tenant": l4_tenant_layer,
            "l4_business": l4_tenant_layer,
        }

    def get_layer(self, layer_name: str):
        return self._layers.get(layer_name, self._layers["l1"])

