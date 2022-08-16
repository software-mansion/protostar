from dataclasses import dataclass

from hypothesis.strategies import SearchStrategy, integers
from starknet_py.cairo.felt import MIN_FELT, MAX_FELT
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType, TypeFelt

from protostar.commands.test.fuzzing.exceptions import SearchStrategyBuildError
from protostar.commands.test.fuzzing.strategy_descriptor import StrategyDescriptor


@dataclass
class FeltsStrategyDescriptor(StrategyDescriptor):
    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy[int]:
        if not isinstance(cairo_type, TypeFelt):
            raise SearchStrategyBuildError(
                "Strategy 'felts' can only be applied to felt parameters."
            )

        return integers(min_value=MIN_FELT, max_value=MAX_FELT)
