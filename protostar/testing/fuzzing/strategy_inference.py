from starkware.cairo.lang.compiler.ast.cairo_types import (
    CairoType,
    TypeFelt,
    TypeStruct,
)

from .exceptions import FuzzingError
from .strategies import FeltsStrategyDescriptor, Uint256StrategyDescriptor
from .strategy_descriptor import StrategyDescriptor
from .strategies.uint256 import is_uint256


def infer_strategy_from_cairo_type(
    parameter_name: str,
    cairo_type: CairoType,
) -> StrategyDescriptor:
    if isinstance(cairo_type, TypeFelt):
        return FeltsStrategyDescriptor()
    if is_uint256(cairo_type):
        return Uint256StrategyDescriptor()
    if isinstance(cairo_type, TypeStruct):
        print(cairo_type.scope.path)

    raise FuzzingError(
        f"Parameter '{parameter_name}' cannot be fuzzed automatically, "
        f"because Protostar cannot infer fuzzing strategy for type {cairo_type.format()}."
    )
