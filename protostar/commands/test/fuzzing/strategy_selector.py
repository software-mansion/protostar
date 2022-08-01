from contextlib import contextmanager
from typing import Dict, Iterable, Any, Generator

from hypothesis.strategies import SearchStrategy
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType, TypeFelt

from protostar.commands.test.fuzzing.exceptions import FuzzingError
from protostar.commands.test.fuzzing.strategies.felt import (
    UnsignedFeltStrategyDescriptor,
)
from protostar.commands.test.fuzzing.strategy_descriptor import (
    StrategyDescriptor,
    SearchStrategyBuildError,
)


class StrategySelector:
    def __init__(self, parameters: Dict[str, CairoType]):
        self._parameters = parameters
        self._strategy_descriptors: Dict[str, StrategyDescriptor] = {}
        self._search_strategies: Dict[str, SearchStrategy[Any]] = {}

    @property
    def parameter_names(self) -> Iterable[str]:
        return self._parameters.keys()

    def __contains__(self, param: str) -> bool:
        return param in self._parameters

    def get_strategy_descriptor(self, param: str) -> StrategyDescriptor:
        self.check_exists(param)

        if param in self._strategy_descriptors:
            return self._strategy_descriptors[param]

        cairo_type = self._parameters[param]

        with wrap_search_strategy_build_error(param):
            descriptor = infer_strategy_from_cairo_type(cairo_type)

        self._strategy_descriptors[param] = descriptor
        return descriptor

    def get_search_strategy(self, param: str) -> SearchStrategy[Any]:
        self.check_exists(param)

        if param in self._search_strategies:
            return self._search_strategies[param]

        descriptor = self.get_strategy_descriptor(param)
        cairo_type = self._parameters[param]

        with wrap_search_strategy_build_error(param):
            strategy = descriptor.build_strategy(cairo_type)

        self._search_strategies[param] = strategy
        return strategy

    def set_strategy_descriptor(
        self,
        param: str,
        strategy_descriptor: StrategyDescriptor,
    ):
        self.check_exists(param)

        # NOTE: Calling `get_strategy_descriptor` may construct default descriptor if not already
        #   set, which may raise an exception from `infer_strategy_from_cairo_type` if it fails.
        #   To avoid that, we explicitly look at `_strategy_descriptors` beforehand.
        if (
            param not in self._strategy_descriptors
            or strategy_descriptor != self.get_strategy_descriptor(param)
        ):
            self._forget(param)
            self._strategy_descriptors[param] = strategy_descriptor

    def check_exists(self, param: str):
        if param not in self._parameters:
            raise FuzzingError(f"Unknown fuzzing parameter '{param}'.")

    def _forget(self, param: str):
        if param in self._strategy_descriptors:
            del self._strategy_descriptors[param]

        if param in self._search_strategies:
            del self._search_strategies[param]


def infer_strategy_from_cairo_type(cairo_type: CairoType) -> StrategyDescriptor:
    if isinstance(cairo_type, TypeFelt):
        return UnsignedFeltStrategyDescriptor()

    raise SearchStrategyBuildError(f"Type {cairo_type.format()} cannot be fuzzed.")


@contextmanager
def wrap_search_strategy_build_error(param: str) -> Generator[None, None, None]:
    try:
        yield
    except SearchStrategyBuildError as ex:
        raise FuzzingError(f"Parameter '{param}' cannot be fuzzed: {ex}") from ex
