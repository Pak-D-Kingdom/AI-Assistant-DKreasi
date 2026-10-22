from app.layers.base import BaseLayer
from app.layers.l3_webia.prompts import get_l3_system_prompt
from app.layers.l3_webia.tools import L3IntentRouter


class L3WebiaLayer(BaseLayer):
    @property
    def layer_name(self) -> str:
        return "l3_webia"

    def get_system_prompt(self, context=None) -> str:
        return get_l3_system_prompt()

    def route_intent(self, query: str):
        return L3IntentRouter.detect_and_route(query)
