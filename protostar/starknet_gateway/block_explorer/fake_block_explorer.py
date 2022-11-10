from typing import Optional

from .block_explorer import (
    URL,
    BlockExplorer,
    ClassHash,
    ContractAddress,
    TransactionHash,
)


class FakeBlockExplorer(BlockExplorer):
    def create_link_to_transaction(self, tx_hash: TransactionHash) -> Optional[URL]:
        return None

    def create_link_to_contract(
        self, contract_address: ContractAddress
    ) -> Optional[URL]:
        return None

    def create_link_to_class(self, class_hash: ClassHash) -> Optional[URL]:
        return None
