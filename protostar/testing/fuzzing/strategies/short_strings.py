import string

from hypothesis.strategies import SearchStrategy, text
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType, TypeFelt

from protostar.testing.fuzzing.exceptions import SearchStrategyBuildError
from protostar.testing.fuzzing.strategy_descriptor import StrategyDescriptor


class ShortStringsStrategyDescriptor(StrategyDescriptor):

    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy[int]:
        if not isinstance(cairo_type, TypeFelt):
            raise SearchStrategyBuildError(
                "Strategy 'short strings' can only be applied to felt parameters."
            )

        def string_to_bytes_int(val: str) -> int:
            if not val:
                return 0
            # pylint: disable=consider-using-f-string
            return int('0x' + ''.join('{:02x}'.format(ord(c)) for c in val), 16)

        return text(alphabet=list(string.ascii_lowercase), min_size=0, max_size=31).map(string_to_bytes_int)
