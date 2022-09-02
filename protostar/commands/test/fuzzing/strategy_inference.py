from starkware.cairo.lang.compiler.ast.cairo_types import CairoType, TypeFelt

from protostar.commands.test.fuzzing.exceptions import FuzzingError
from protostar.commands.test.fuzzing.strategies import FeltsStrategyDescriptor
from protostar.commands.test.fuzzing.strategy_descriptor import StrategyDescriptor


def infer_strategy_from_cairo_type(
    parameter_name: str,
    cairo_type: CairoType,
) -> StrategyDescriptor:
    if isinstance(cairo_type, TypeFelt):
        return FeltsStrategyDescriptor()

    raise FuzzingError(
        f"Parameter '{parameter_name}' cannot be fuzzed automatically, "
        f"because Protostar cannot infer fuzzing strategy for type {cairo_type.format()}."
    )
