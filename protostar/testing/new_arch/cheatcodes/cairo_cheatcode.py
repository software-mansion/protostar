from abc import ABC
from typing import TYPE_CHECKING

from protostar.starknet import HintLocal


if TYPE_CHECKING:
    from protostar.starknet.new_arch.cheaters import CairoCheaters


class CairoCheatcode(HintLocal, ABC):
    def __init__(self, cheaters: "CairoCheaters"):
        self.cheaters = cheaters
