from types import SimpleNamespace
from typing import Any

from protostar.starknet.hint_local import HintLocal
from .felt import (
    IntegersStrategyDescriptor,
    SignedFeltStrategyDescriptor,
    UnsignedFeltStrategyDescriptor,
)

namespace = SimpleNamespace(
    integers=IntegersStrategyDescriptor,
    signed=SignedFeltStrategyDescriptor,
    unsigned=UnsignedFeltStrategyDescriptor,
)


class StrategiesHintLocal(HintLocal):
    @property
    def name(self) -> str:
        return "st"

    def build(self) -> Any:
        return namespace
