from starkware.cairo.lang.compiler.ast.cairo_types import (
    CairoType,
    TypeFelt,
    TypeStruct,
)

from .exceptions import FuzzingError
from .strategies import FeltsStrategyDescriptor, Uint256StrategyDescriptor
from .strategy_descriptor import StrategyDescriptor


def infer_strategy_from_cairo_type(
    parameter_name: str,
    cairo_type: CairoType,
) -> StrategyDescriptor:
    if isinstance(cairo_type, TypeFelt):
        return FeltsStrategyDescriptor()
    if isinstance(cairo_type, TypeStruct) and str(cairo_type.scope).endswith(
        "starkware.cairo.common.uint256.Uint256"
    ):
        return Uint256StrategyDescriptor()

    raise FuzzingError(
        f"Parameter '{parameter_name}' cannot be fuzzed automatically, "
        f"because Protostar cannot infer fuzzing strategy for type {cairo_type.format()}."
    )
