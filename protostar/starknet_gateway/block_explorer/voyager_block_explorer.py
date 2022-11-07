from .block_explorer import (
    URL,
    BlockExplorer,
    ClassHash,
    ContractAddress,
    TransactionHash,
)


class VoyagerBlockExplorer(BlockExplorer):
    def create_link_to_transaction(self, tx_hash: TransactionHash) -> URL:
        ...

    def create_link_to_contract(self, contract_address: ContractAddress) -> URL:
        ...

    def create_link_to_class(self, class_hash: ClassHash) -> URL:
        ...
