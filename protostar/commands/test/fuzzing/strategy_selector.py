from typing import Dict, Iterable, Any, DefaultDict

from hypothesis.strategies import SearchStrategy
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType, TypeFelt

from protostar.commands.test.fuzzing.exceptions import FuzzingError
from protostar.commands.test.fuzzing.strategies.felt import (
    UnsignedFeltStrategyDescriptor,
)
from protostar.commands.test.fuzzing.strategy_descriptor import StrategyDescriptor


class StrategySelector:
    def __init__(self, parameters: Dict[str, CairoType]):
        self._parameters = parameters

        self.strategy_descriptors = LazyStrategyDescriptorsDict(self._parameters)
        self.search_strategies = LazySearchStrategiesDict(self.strategy_descriptors)

    @property
    def parameter_names(self) -> Iterable[str]:
        return self._parameters.keys()


class LazyStrategyDescriptorsDict(DefaultDict[str, StrategyDescriptor]):
    def __init__(self, parameters: Dict[str, CairoType]):
        super().__init__()
        self._parameters = parameters

    def __missing__(self, parameter: str) -> StrategyDescriptor:
        if parameter not in self._parameters:
            raise FuzzingError(f"Unknown fuzzing parameter '{parameter}'.")
        return infer_strategy_from_cairo_type(self._parameters[parameter])


class LazySearchStrategiesDict(DefaultDict[str, SearchStrategy[Any]]):
    """
    Readonly.
    """

    def __init__(self, strategy_descriptors: LazyStrategyDescriptorsDict):
        super().__init__()
        self._strategy_descriptors = strategy_descriptors

    def __missing__(self, parameter: str) -> SearchStrategy[Any]:
        descriptor = self._strategy_descriptors[parameter]
        return descriptor.build_strategy()


def infer_strategy_from_cairo_type(cairo_type: CairoType) -> StrategyDescriptor:
    if isinstance(cairo_type, TypeFelt):
        return UnsignedFeltStrategyDescriptor()

    raise FuzzingError(f"Type {cairo_type.format()} cannot be fuzzed.")
