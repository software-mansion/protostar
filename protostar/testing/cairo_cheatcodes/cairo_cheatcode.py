from abc import ABC

from protostar.starknet import HintLocal
from protostar.starknet.cheaters import Cheaters
from protostar.starknet.forkable_starknet import ForkableStarknet


class CairoCheatcode(HintLocal, ABC):
    def __init__(self, starknet: ForkableStarknet):
        self.starknet = starknet

    @property
    def cheaters(self) -> Cheaters:
        return self.starknet.cheatable_state.cheatable_state.cheaters
