from dataclasses import dataclass
from typing import Optional

from hypothesis.strategies import SearchStrategy, integers
from starknet_py.cairo.felt import MIN_FELT, MAX_FELT
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType, TypeFelt
from starkware.crypto.signature.signature import FIELD_PRIME

from protostar.commands.test.fuzzing.exceptions import SearchStrategyBuildError
from protostar.commands.test.fuzzing.strategy_descriptor import StrategyDescriptor


def signed_felts() -> SearchStrategy[int]:
    return integers(min_value=MIN_FELT, max_value=MAX_FELT)


def unsigned_felts() -> SearchStrategy[int]:
    return integers(min_value=0, max_value=FIELD_PRIME)


@dataclass
class SignedFeltStrategyDescriptor(StrategyDescriptor):
    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy[int]:
        if not isinstance(cairo_type, TypeFelt):
            raise SearchStrategyBuildError(
                "Strategy 'signed' can only be applied to felt parameters."
            )

        return signed_felts()


@dataclass
class UnsignedFeltStrategyDescriptor(StrategyDescriptor):
    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy[int]:
        if not isinstance(cairo_type, TypeFelt):
            raise SearchStrategyBuildError(
                "Strategy 'unsigned' can only be applied to felt parameters."
            )

        return unsigned_felts()


@dataclass
class IntegersStrategyDescriptor(StrategyDescriptor):
    # NOTE: Keeping these names matching arguments of Hypothesis' ``integers`` strategy,
    #   so that Hypothesis' exceptions (which contain these names) make sense for our users.
    min_value: Optional[int] = None
    max_value: Optional[int] = None

    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy[int]:
        if not isinstance(cairo_type, TypeFelt):
            raise SearchStrategyBuildError(
                "Strategy 'integers' can only be applied to felt parameters."
            )

        return integers(min_value=self.min_value, max_value=self.max_value)
