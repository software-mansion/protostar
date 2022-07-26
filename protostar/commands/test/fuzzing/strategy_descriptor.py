from abc import ABC, abstractmethod
from typing import Any

from hypothesis.strategies import SearchStrategy


class StrategyDescriptor(ABC):
    @abstractmethod
    def build_strategy(self) -> SearchStrategy[Any]:
        ...
