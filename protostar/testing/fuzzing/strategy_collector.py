from typing import Dict

from hypothesis.strategies import SearchStrategy
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType

from .exceptions import FuzzingError, SearchStrategyBuildError
from .strategy_descriptor import StrategyDescriptor


def collect_search_strategies(
    declared_strategies: Dict[str, StrategyDescriptor],
    parameters: Dict[str, CairoType],
) -> Dict[str, SearchStrategy]:
    _check_no_extra_strategies(declared_strategies, parameters)
    return {
        param: _build_search_strategy(strategy, param, parameters[param])
        for param, strategy in declared_strategies.items()
    }


def _check_no_extra_strategies(
    declared_strategies: Dict[str, StrategyDescriptor],
    parameters: Dict[str, CairoType],
):
    extra_strategies = [
        param for param in declared_strategies if param not in parameters
    ]

    if len(extra_strategies) > 1:
        raise FuzzingError(
            f"Unknown fuzzing parameters: {', '.join(extra_strategies)}."
        )

    if len(extra_strategies) == 1:
        raise FuzzingError(f"Unknown fuzzing parameter {extra_strategies[0]}.")


def _build_search_strategy(
    descriptor: StrategyDescriptor,
    parameter_name: str,
    cairo_type: CairoType,
) -> SearchStrategy:
    try:
        return descriptor.build_strategy(cairo_type=cairo_type)
    except SearchStrategyBuildError as ex:
        raise FuzzingError(
            f"Parameter '{parameter_name}' cannot be fuzzed: {ex}"
        ) from ex
