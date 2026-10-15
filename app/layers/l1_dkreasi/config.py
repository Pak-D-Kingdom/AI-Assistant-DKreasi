from app.layers.base import BaseLayer
from app.layers.l1_dkreasi.prompts import get_l1_system_prompt
from app.layers.l1_dkreasi.tools import L1IntentRouter


class L1DkreasiLayer(BaseLayer):
    @property
    def layer_name(self) -> str:
        return "l1_dkreasi"

    def get_system_prompt(self, context=None) -> str:
        return get_l1_system_prompt()

    def route_intent(self, query: str):
        return L1IntentRouter.detect_and_route(query)
