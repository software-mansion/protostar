import functools
from abc import ABC, abstractmethod
from typing import Callable, cast, TypeVar

from hypothesis.strategies import SearchStrategy
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType

from protostar.testing.fuzzing.exceptions import SearchStrategyBuildError

InitT = TypeVar("InitT", bound=Callable[..., "StrategyDescriptor"])


def catch_strategy_build_exceptions(init: InitT) -> InitT:
    @functools.wraps(init)
    def wrapped(*args, **kwargs):
        try:
            return init(*args, **kwargs)
        except SearchStrategyBuildError:  # pylint: disable=try-except-raise
            raise
        except Exception as ex:
            raise SearchStrategyBuildError(str(ex)) from ex

    return cast(InitT, wrapped)


MappingFunction = Callable[[int], int]
FilterFunction = Callable[[int], bool]


class StrategyDescriptor(ABC):
    @abstractmethod
    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy:
        ...

    @catch_strategy_build_exceptions
    def filter(self, f: FilterFunction, /) -> "FilteredStrategyDescriptor":
        return FilteredStrategyDescriptor(inner=self, function=f)

    @catch_strategy_build_exceptions
    def map(self, f: MappingFunction, /) -> "MappedStrategyDescriptor":
        return MappedStrategyDescriptor(inner=self, function=f)


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
