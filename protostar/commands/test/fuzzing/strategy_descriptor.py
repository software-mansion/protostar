from abc import ABC, abstractmethod
from typing import Callable, Any

from hypothesis.strategies import SearchStrategy
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType

MappingFunction = Callable[[int], int]
FilterFunction = Callable[[int], bool]


class StrategyDescriptor(ABC):
    @abstractmethod
    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy:
        ...

    def filter(self, filter_function: FilterFunction) -> "FilteredStrategyDescriptor":
        return FilteredStrategyDescriptor(inner=self, function=filter_function)

    def map(self, mapping_function: MappingFunction) -> "MappedStrategyDescriptor":
        return MappedStrategyDescriptor(inner=self, function=mapping_function)


class MappedStrategyDescriptor(StrategyDescriptor):
    def __init__(self, function: MappingFunction, inner: StrategyDescriptor):
        self.inner = inner
        self.function = function

    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy:
        return self.inner.build_strategy(cairo_type=cairo_type).map(self.function)


class FilteredStrategyDescriptor(StrategyDescriptor):
    def __init__(self, function: FilterFunction, inner: StrategyDescriptor):
        self.inner = inner
        self.function = function

    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy:
        return self.inner.build_strategy(cairo_type=cairo_type).filter(self.function)
