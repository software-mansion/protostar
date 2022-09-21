from typing import Optional

from hypothesis.strategies import SearchStrategy, integers as h_integers
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType, TypeFelt

from protostar.testing.fuzzing.exceptions import SearchStrategyBuildError
from protostar.testing.fuzzing.strategy_descriptor import StrategyDescriptor


def integers(
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
) -> StrategyDescriptor:
    return IntegersStrategyDescriptor(min_value, max_value)


class IntegersStrategyDescriptor(StrategyDescriptor):
    # NOTE: Keeping these names matching arguments of Hypothesis' ``integers`` strategy,
    #   so that Hypothesis' exceptions (which contain these names) make sense for our users.
    def __init__(self, min_value: Optional[int], max_value: Optional[int]):
        self.min_value = min_value
        self.max_value = max_value

    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy[int]:
        if not isinstance(cairo_type, TypeFelt):
            raise SearchStrategyBuildError(
                "Strategy 'integers' can only be applied to felt parameters."
            )

        return h_integers(min_value=self.min_value, max_value=self.max_value)
