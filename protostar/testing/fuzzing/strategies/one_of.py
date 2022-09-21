from typing import Any, cast

from hypothesis.strategies import SearchStrategy, one_of as h_one_of
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType

from protostar.testing.fuzzing.strategy_descriptor import StrategyDescriptor


def one_of(*strategies: StrategyDescriptor) -> StrategyDescriptor:
    return OneOfStrategyDescriptor(*strategies)


class OneOfStrategyDescriptor(StrategyDescriptor):
    def __init__(self, *strategies: StrategyDescriptor):
        for strategy in strategies:
            if not isinstance(cast(Any, strategy), StrategyDescriptor):
                raise TypeError("one_of() takes only other strategies as arguments")
        if len(strategies) == 0:
            raise TypeError("one_of() takes at least 1 positional argument")
        self.strategies = strategies

    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy[int]:
        return h_one_of(*(arg.build_strategy(cairo_type) for arg in self.strategies))
