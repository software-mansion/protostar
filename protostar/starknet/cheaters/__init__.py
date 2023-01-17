from dataclasses import dataclass

from typing_extensions import Self

from .block_info import BlockInfoCheater


@dataclass(frozen=True)
class Cheaters:
    block_info: BlockInfoCheater

    def copy(self) -> Self:
        return Cheaters(block_info=self.block_info.copy())

    def apply(self, parent: Self) -> None:
        parent.block_info.apply(self.block_info)
