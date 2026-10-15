from typing import Dict, Any
from app.layers.l1_dkreasi.config import L1DkreasiLayer


class ToolRegistry:
    def __init__(self):
        self._layers = {
            "l1": L1DkreasiLayer(),
            "l1_dkreasi": L1DkreasiLayer(),
        }

    def get_layer(self, layer_name: str):
        return self._layers.get(layer_name, self._layers["l1"])
