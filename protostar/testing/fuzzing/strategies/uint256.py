from hypothesis.strategies import SearchStrategy, integers
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType, TypeStruct

from protostar.testing.fuzzing.exceptions import SearchStrategyBuildError
from protostar.testing.fuzzing.strategy_descriptor import StrategyDescriptor

from starknet_py.cairo.felt import is_uint256


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
    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy[tuple[int, int]]:
        if not is_uint256(cairo_type):
            raise SearchStrategyBuildError(
                "Strategy 'uint256' can only be applied to Uint256 parameters."
            )

        return integers(min_value=MIN_UINT256, max_value=MAX_UINT256).map(
            lambda x: (_get_low(x), _get_high(x))
        )
