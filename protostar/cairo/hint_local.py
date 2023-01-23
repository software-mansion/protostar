from abc import ABC, abstractmethod
from typing import Any, Dict


class HintLocal(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def build(self) -> Any:
        ...


HintLocalsDict = Dict[str, Any]
