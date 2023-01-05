from abc import ABC

from protostar.starknet import HintLocal
from protostar.starknet.cheatable_cached_state import CheatableCachedState
from protostar.starknet.cheatable_state import CheatableStarknetState
from protostar.starknet.cheaters import Cheaters
from protostar.starknet.forkable_starknet import ForkableStarknet


class CairoCheatcode(HintLocal, ABC):
    def __init__(self, starknet: ForkableStarknet):
        self.starknet = starknet

    @property
    def cheatable_starknet_state(self) -> CheatableStarknetState:
        return self.starknet.cheatable_state

    @property
    def cheatable_state(self) -> CheatableCachedState:
        return self.cheatable_starknet_state.cheatable_state

    @property
    def cheaters(self) -> Cheaters:
        return self.cheatable_state.cheaters
