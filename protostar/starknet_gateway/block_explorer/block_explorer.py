from abc import ABC, abstractmethod
from typing import Optional

TransactionHash = int
ContractAddress = int
ClassHash = int


class BlockExplorer(ABC):
    @abstractmethod
    def create_link_to_transaction(self, tx_hash: TransactionHash) -> Optional[str]:
        ...

    @abstractmethod
    def create_link_to_contract(
        self, contract_address: ContractAddress
    ) -> Optional[str]:
        ...

    @abstractmethod
    def create_link_to_class(self, class_hash: ClassHash) -> Optional[str]:
        ...
