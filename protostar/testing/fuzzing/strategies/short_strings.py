import string

from hypothesis.strategies import SearchStrategy, text
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType, TypeFelt
from starkware.python.utils import from_bytes

from protostar.testing.fuzzing.exceptions import SearchStrategyBuildError
from protostar.testing.fuzzing.strategy_descriptor import StrategyDescriptor


class ShortStringsStrategyDescriptor(StrategyDescriptor):
    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy[int]:
        if not isinstance(cairo_type, TypeFelt):
            raise SearchStrategyBuildError(
                "Strategy 'short strings' can only be applied to felt parameters."
            )

        return text(alphabet=list(string.printable), min_size=0, max_size=31).map(
            lambda val: from_bytes(val.encode("utf-8"))
        )
