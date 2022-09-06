from hypothesis.strategies import SearchStrategy, one_of
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType

from protostar.commands.test.fuzzing.exceptions import SearchStrategyBuildError
from protostar.commands.test.fuzzing.strategy_descriptor import StrategyDescriptor


class OneOfStrategyDescriptor(StrategyDescriptor):
    def __init__(self, *strategies: StrategyDescriptor):
        for arg in args:
            if not isinstance(cast(Any, arg), StrategyDescriptor):
                raise SearchStrategyBuildError(
                    "Strategy 'one_of' takes only other strategies as arguments."
                )
        if len(args) == 0:
            raise SearchStrategyBuildError(
                "Strategy 'one_of' takes at least one argument."
            )
        self.strategies = strategies

    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy[int]:
        return one_of(*(arg.build_strategy(cairo_type) for arg in self.args))
