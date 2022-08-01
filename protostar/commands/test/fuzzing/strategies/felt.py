from hypothesis.strategies import SearchStrategy, integers
from starknet_py.cairo.felt import MIN_FELT, MAX_FELT
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType, TypeFelt
from starkware.crypto.signature.signature import FIELD_PRIME

from protostar.commands.test.fuzzing.strategy_descriptor import (
    StrategyDescriptor,
    SearchStrategyBuildError,
)


def signed_felts() -> SearchStrategy[int]:
    return integers(min_value=MIN_FELT, max_value=MAX_FELT)


def unsigned_felts() -> SearchStrategy[int]:
    return integers(min_value=0, max_value=FIELD_PRIME)


class SignedFeltStrategyDescriptor(StrategyDescriptor):
    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy[int]:
        if not isinstance(cairo_type, TypeFelt):
            raise SearchStrategyBuildError(
                "Strategy 'signed' can only be applied to felt parameters."
            )

        return signed_felts()

    def __eq__(self, other: "StrategyDescriptor") -> bool:
        return isinstance(other, self.__class__)


class UnsignedFeltStrategyDescriptor(StrategyDescriptor):
    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy[int]:
        if not isinstance(cairo_type, TypeFelt):
            raise SearchStrategyBuildError(
                "Strategy 'unsigned' can only be applied to felt parameters."
            )

        return unsigned_felts()

    def __eq__(self, other: "StrategyDescriptor") -> bool:
        return isinstance(other, self.__class__)
