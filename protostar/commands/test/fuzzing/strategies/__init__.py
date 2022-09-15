from types import SimpleNamespace
from typing import Any

from protostar.starknet.hint_local import HintLocal
from .felts import FeltsStrategyDescriptor
from .integers import IntegersStrategyDescriptor
from .one_of import OneOfStrategyDescriptor

namespace = SimpleNamespace(
    felts=FeltsStrategyDescriptor,
    integers=IntegersStrategyDescriptor,
    one_of=OneOfStrategyDescriptor,
)


class StrategiesHintLocal(HintLocal):
    @property
    def name(self) -> str:
        return "strategy"

    def build(self) -> Any:
        return namespace
