import copy

from abc import ABC
from typing import TYPE_CHECKING
from typing_extensions import Self

from protostar.starknet.cheater import Cheater

if TYPE_CHECKING:
    from protostar.starknet.cheatable_cached_state import CheatableCachedState


class StatefulCheater(Cheater, ABC):
    def __init__(self, cheatable_state: "CheatableCachedState"):
        self.cheatable_state = cheatable_state

    def copy(self) -> Self:
        return copy.copy(self)

    def apply(self, parent: Self) -> None:
        pass
