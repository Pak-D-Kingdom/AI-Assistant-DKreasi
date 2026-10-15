from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseLayer(ABC):
    @property
    @abstractmethod
    def layer_name(self) -> str:
        pass

    @abstractmethod
    def get_system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        pass

    @abstractmethod
    def route_intent(self, query: str) -> Dict[str, Any]:
        pass
