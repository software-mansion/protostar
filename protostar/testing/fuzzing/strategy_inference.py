from starkware.cairo.lang.compiler.ast.cairo_types import CairoType, TypeFelt

from protostar.testing.fuzzing.exceptions import FuzzingError
from protostar.testing.fuzzing.strategies import strategies
from protostar.testing.fuzzing.strategy_descriptor import StrategyDescriptor


def infer_strategy_from_cairo_type(
    parameter_name: str,
    cairo_type: CairoType,
) -> StrategyDescriptor:
    if isinstance(cairo_type, TypeFelt):
        return strategies.felts()

    raise FuzzingError(
        f"Parameter '{parameter_name}' cannot be fuzzed automatically, "
        f"because Protostar cannot infer fuzzing strategy for type {cairo_type.format()}."
    )
