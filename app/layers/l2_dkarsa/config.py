from app.layers.base import BaseLayer
from app.layers.l2_dkarsa.prompts import get_l2_system_prompt
from app.layers.l2_dkarsa.tools import L2IntentRouter


class L2DkarsaLayer(BaseLayer):
    @property
    def layer_name(self) -> str:
        return "l2_dkarsa"

    def get_system_prompt(self, context=None) -> str:
        return get_l2_system_prompt()

    def route_intent(self, query: str):
        return L2IntentRouter.detect_and_route(query)
