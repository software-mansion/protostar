from abc import ABC, abstractmethod
from typing import Any

from hypothesis.strategies import SearchStrategy
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType

from protostar.commands.test.fuzzing.exceptions import FuzzingError


class SearchStrategyBuildError(FuzzingError):
    pass


class StrategyDescriptor(ABC):
    """
    Invariant: Strategy descriptors must be equatable (provide ``__eq__`` implementation).
    """

    @abstractmethod
    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy[Any]:
        ...
