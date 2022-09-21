import functools
from types import SimpleNamespace
from typing import Any, Callable, TypeVar, cast

from protostar.starknet.hint_local import HintLocal
from protostar.testing.fuzzing.exceptions import SearchStrategyBuildError
from protostar.testing.fuzzing.strategies.felts import felts
from protostar.testing.fuzzing.strategies.integers import integers
from protostar.testing.fuzzing.strategies.one_of import one_of
from protostar.testing.fuzzing.strategy_descriptor import StrategyDescriptor

InitT = TypeVar("InitT", bound=Callable[..., StrategyDescriptor])


def _build_strategies_namespace(
    *funcs: Callable[..., StrategyDescriptor]
) -> SimpleNamespace:
    return SimpleNamespace(
        **{func.__name__: _wrap_strategy_init(func) for func in funcs}
    )


def _wrap_strategy_init(init: InitT) -> InitT:
    @functools.wraps(init)
    def wrapped(*args, **kwargs):
        try:
            return init(*args, **kwargs)
        except Exception as ex:
            raise SearchStrategyBuildError(str(ex)) from ex

    return cast(InitT, wrapped)


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
