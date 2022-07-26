from hypothesis.strategies import SearchStrategy, integers
from starknet_py.cairo.felt import MIN_FELT, MAX_FELT
from starkware.crypto.signature.signature import FIELD_PRIME

from protostar.commands.test.fuzzing.strategy_descriptor import StrategyDescriptor


def signed_felts() -> SearchStrategy[int]:
    return integers(min_value=MIN_FELT, max_value=MAX_FELT)


def unsigned_felts() -> SearchStrategy[int]:
    return integers(min_value=0, max_value=FIELD_PRIME)


class SignedFeltStrategyDescriptor(StrategyDescriptor):
    def build_strategy(self) -> SearchStrategy[int]:
        return signed_felts()


class UnsignedFeltStrategyDescriptor(StrategyDescriptor):
    def build_strategy(self) -> SearchStrategy[int]:
        return unsigned_felts()
