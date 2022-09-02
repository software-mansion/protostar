from abc import ABC, abstractmethod

from hypothesis.strategies import SearchStrategy
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType


class StrategyDescriptor(ABC):
    @abstractmethod
    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy:
        ...
