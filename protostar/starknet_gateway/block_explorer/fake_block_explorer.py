from typing import Optional

from .block_explorer import BlockExplorer, ClassHash, ContractAddress, TransactionHash


class FakeBlockExplorer(BlockExplorer):
    def get_name(self) -> str:
        return ""

    def create_link_to_transaction(self, tx_hash: TransactionHash) -> Optional[str]:
        return None

    def create_link_to_contract(
        self, contract_address: ContractAddress
    ) -> Optional[str]:
        return None

    def create_link_to_class(self, class_hash: ClassHash) -> Optional[str]:
        return None
