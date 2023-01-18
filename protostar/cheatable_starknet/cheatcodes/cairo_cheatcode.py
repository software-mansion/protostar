from abc import ABC
from typing import TYPE_CHECKING

from protostar.cairo import HintLocal

if TYPE_CHECKING:
    from protostar.cheatable_starknet.cheaters import CairoCheaters


class CairoCheatcode(HintLocal, ABC):
    def __init__(self, cheaters: "CairoCheaters"):
        self.cheaters = cheaters
