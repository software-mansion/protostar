from types import SimpleNamespace
from typing import Any, Callable

from protostar.starknet.hint_local import HintLocal
from protostar.testing.fuzzing.strategies.felts import felts
from protostar.testing.fuzzing.strategies.integers import integers
from protostar.testing.fuzzing.strategies.one_of import one_of
from protostar.testing.fuzzing.strategy_descriptor import (
    StrategyDescriptor,
    catch_strategy_build_exceptions,
)


def _build_strategies_namespace(
    *funcs: Callable[..., StrategyDescriptor]
) -> SimpleNamespace:
    return SimpleNamespace(
        **{func.__name__: catch_strategy_build_exceptions(func) for func in funcs}
    )


strategies = _build_strategies_namespace(
    felts,
    integers,
    one_of,
)


class StrategiesHintLocal(HintLocal):
    @property
    def name(self) -> str:
        return "strategy"

    def build(self) -> Any:
        return strategies
