from typing import Optional

from hypothesis.strategies import SearchStrategy, integers
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType, TypeStruct

from protostar.testing.fuzzing.exceptions import SearchStrategyBuildError
from protostar.testing.fuzzing.strategy_descriptor import StrategyDescriptor


def _get_low(uint256: int):
    mask = (1 << 128) - 1  # 128*"1"
    mask = mask << 128  # 128*"1"+128*"0"
    mask = ~mask  # 128*"0"+128*"1"
    return uint256 & mask


def _get_high(uint256: int):
    return uint256 >> 128


class Uint256StrategyDescriptor(StrategyDescriptor):
    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy[int]:
        if not isinstance(cairo_type, TypeStruct):  # TODO: FIND BETTER CHECK
            raise SearchStrategyBuildError(
                "Strategy 'uint256' can only be applied to Uint256 parameters."
            )

        return integers(min_value=0, max_value=(1 << 256) - 1).map(
            lambda x: (_get_low(x), _get_high(x))
        )
