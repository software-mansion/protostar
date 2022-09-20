from hypothesis.strategies import SearchStrategy, integers
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType, TypeFelt
from starkware.crypto.signature.signature import FIELD_PRIME

from protostar.testing.fuzzing.exceptions import SearchStrategyBuildError
from protostar.testing.fuzzing.strategy_descriptor import StrategyDescriptor


class FeltsStrategyDescriptor(StrategyDescriptor):
    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy[int]:
        if not isinstance(cairo_type, TypeFelt):
            raise SearchStrategyBuildError(
                "Strategy 'felts' can only be applied to felt parameters."
            )

        # NOTE: Hypothesis seems to pick more distinct numbers when allowed to search the space
        #   of negative numbers. Searching between `-(FIELD_PRIME // 2)` and `FIELD_PRIME // 2`
        #   resulted in about 30% more diversity of input values, in comparison with searching
        #   between 0 and FIELD_PRIME. The intuition behind this is that this trick makes
        #   Hypothesis more keen to explore right-most side of the felt value space as 0 is now
        #   in the centre of fuzzed value space.
        #
        #   In order to make input values look more like felts in fuzzer output, we explicitly
        #   apply the conversion from integers to felts in `map` strategy. This operation is purely
        #   for cosmetic purposes, Cairo VM would do this anyway.
        max_felt = FIELD_PRIME // 2
        min_felt = -max_felt
        return integers(min_value=min_felt, max_value=max_felt).map(to_felt)


def to_felt(value: int) -> int:
    return value % FIELD_PRIME
