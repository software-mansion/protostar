from contextlib import contextmanager
from typing import Dict, Any, Generator, Mapping

from hypothesis.strategies import SearchStrategy
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType, TypeFelt

from protostar.commands.test.fuzzing.exceptions import (
    FuzzingError,
    SearchStrategyBuildError,
)
from protostar.commands.test.fuzzing.strategies import FeltsStrategyDescriptor
from protostar.commands.test.fuzzing.strategy_descriptor import StrategyDescriptor


class StrategySelector:
    def __init__(self, parameters: Dict[str, CairoType]):
        # NOTE: We store each parameter info property in separate dict in order to optimise
        #   ``given_strategies`` property.
        self._parameters = parameters
        self._descriptors: Dict[str, StrategyDescriptor] = {}
        self._strategies: Dict[str, SearchStrategy[Any]] = {}

        for param, cairo_type in parameters.items():
            with wrap_search_strategy_build_error(param):
                descriptor = infer_strategy_from_cairo_type(cairo_type)
                strategy = descriptor.build_strategy(cairo_type)

            self._descriptors[param] = descriptor
            self._strategies[param] = strategy

    @property
    def given_strategies(self) -> Mapping[str, SearchStrategy[Any]]:
        return self._strategies

    def learn(self, param: str, descriptor: StrategyDescriptor) -> bool:
        """
        :return: ``True`` if selector has changed the strategy for the ``param``
            (_learned new strategy_); otherwise, ``False``.
        """

        self.check_exists(param)

        existing_descriptor = self._descriptors[param]
        if descriptor == existing_descriptor:
            return False

        with wrap_search_strategy_build_error(param):
            cairo_type = self._parameters[param]
            strategy = descriptor.build_strategy(cairo_type=cairo_type)

        self._descriptors[param] = descriptor
        self._strategies[param] = strategy
        return True

    def check_exists(self, param: str):
        if param not in self._parameters:
            raise FuzzingError(f"Unknown fuzzing parameter '{param}'.")


def infer_strategy_from_cairo_type(cairo_type: CairoType) -> StrategyDescriptor:
    if isinstance(cairo_type, TypeFelt):
        return FeltsStrategyDescriptor()

    raise SearchStrategyBuildError(f"Type {cairo_type.format()} cannot be fuzzed.")


@contextmanager
def wrap_search_strategy_build_error(param: str) -> Generator[None, None, None]:
    try:
        yield
    except SearchStrategyBuildError as ex:
        raise FuzzingError(f"Parameter '{param}' cannot be fuzzed: {ex}") from ex
