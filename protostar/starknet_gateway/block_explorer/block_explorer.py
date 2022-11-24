from abc import ABC, abstractmethod
from typing import Optional

from protostar.starknet import Address

TransactionHash = int
ClassHash = int


class BlockExplorer(ABC):
    @abstractmethod
    def get_name(self) -> str:
        ...

    @abstractmethod
    def create_link_to_transaction(self, tx_hash: TransactionHash) -> Optional[str]:
        ...

    @abstractmethod
    def create_link_to_contract(self, contract_address: Address) -> Optional[str]:
        ...

    @abstractmethod
    def create_link_to_class(self, class_hash: ClassHash) -> Optional[str]:
        ...
