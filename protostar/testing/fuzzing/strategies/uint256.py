from typing import Optional, NamedTuple

from hypothesis.strategies import SearchStrategy, integers
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType, TypeStruct

from protostar.testing.fuzzing.exceptions import SearchStrategyBuildError
from protostar.testing.fuzzing.strategy_descriptor import StrategyDescriptor

MIN_UINT256 = 0
MAX_UINT256 = (1 << 256) - 1


def _get_low(uint256: int):
    return uint256 & ((1 << 128) - 1)


def _get_high(uint256: int):
    return uint256 >> 128


def is_uint256(cairo_type: CairoType):
    return isinstance(cairo_type, TypeStruct) and str(cairo_type.scope).endswith(
        "Uint256"
    )


class Uint256StrategyDescriptor(StrategyDescriptor):
    def __init__(
        self, min_value: Optional[int] = None, max_value: Optional[int] = None
    ):
        min_value = MIN_UINT256 if min_value is None else min_value
        max_value = MAX_UINT256 if max_value is None else max_value
        assert MIN_UINT256 <= min_value <= max_value <= MAX_UINT256

        self.min_value = min_value
        self.max_value = max_value

    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy[tuple[int, int]]:
        if not is_uint256(cairo_type):
            raise SearchStrategyBuildError(
                "Strategy 'uint256' can only be applied to Uint256 parameters."
            )

        Uint256 = NamedTuple("Uint256", (("low", int), ("high", int)))

        return integers(min_value=self.min_value, max_value=self.max_value).map(
            lambda x: Uint256(low=_get_low(x), high=_get_high(x))
        )
