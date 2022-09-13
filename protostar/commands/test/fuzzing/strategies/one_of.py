from typing import Any, cast

from hypothesis.strategies import SearchStrategy, one_of
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType

from protostar.commands.test.fuzzing.exceptions import SearchStrategyBuildError
from protostar.commands.test.fuzzing.strategy_descriptor import StrategyDescriptor


class OneOfStrategyDescriptor(StrategyDescriptor):
    def __init__(self, *strategies: StrategyDescriptor):
        for strategy in strategies:
            if not isinstance(cast(Any, strategy), StrategyDescriptor):
                raise SearchStrategyBuildError(
                    "Strategy 'one_of' takes only other strategies as arguments."
                )
        if len(strategies) == 0:
            raise SearchStrategyBuildError(
                "Strategy 'one_of' takes at least one argument."
            )
        self.strategies = strategies

    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy[int]:
        return one_of(*(arg.build_strategy(cairo_type) for arg in self.strategies))
