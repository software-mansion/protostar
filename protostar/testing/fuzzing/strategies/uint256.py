from hypothesis.strategies import SearchStrategy, integers
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType, TypeStruct

from protostar.testing.fuzzing.exceptions import SearchStrategyBuildError
from protostar.testing.fuzzing.strategy_descriptor import StrategyDescriptor


def _get_low(uint256: int):
    return uint256 & ((1 << 128) - 1)


def _get_high(uint256: int):
    return uint256 >> 128


class Uint256StrategyDescriptor(StrategyDescriptor):
    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy[tuple[int, int]]:
        if not isinstance(cairo_type, TypeStruct) or not str(cairo_type.scope).endswith(
            "starkware.cairo.common.uint256.Uint256"
        ):
            raise SearchStrategyBuildError(
                "Strategy 'uint256' can only be applied to Uint256 parameters."
            )

        return integers(min_value=0, max_value=(1 << 256) - 1).map(
            lambda x: (_get_low(x), _get_high(x))
        )
