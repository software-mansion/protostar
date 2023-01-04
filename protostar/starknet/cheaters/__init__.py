from dataclasses import dataclass

from typing_extensions import Self

from .block_info import BlockInfoCheater
from .contracts import ContractsCheater


@dataclass(frozen=True)
class Cheaters:
    block_info: BlockInfoCheater
    contracts: ContractsCheater

    def copy(self) -> Self:
        return Cheaters(
            block_info=self.block_info.copy(), contracts=self.contracts.copy()
        )

    def apply(self, parent: Self) -> None:
        parent.block_info.apply(self.block_info)
        parent.contracts.apply(self.contracts)
