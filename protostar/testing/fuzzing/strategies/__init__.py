from types import SimpleNamespace
from typing import Any

from protostar.starknet.hint_local import HintLocal
from .felts import FeltsStrategyDescriptor
from .integers import IntegersStrategyDescriptor
from .one_of import OneOfStrategyDescriptor
from .short_strings import ShortStringsStrategyDescriptor
from .uint256 import Uint256StrategyDescriptor

namespace = SimpleNamespace(
    felts=FeltsStrategyDescriptor,
    integers=IntegersStrategyDescriptor,
    one_of=OneOfStrategyDescriptor,
    short_strings=ShortStringsStrategyDescriptor,
    uint256=Uint256StrategyDescriptor,
)


class StrategiesHintLocal(HintLocal):
    @property
    def name(self) -> str:
        return "strategy"

    def build(self) -> Any:
        return namespace
