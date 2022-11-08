from protostar.starknet_gateway.network_config import PredefinedNetwork

from .block_explorer import (
    URL,
    BlockExplorer,
    ClassHash,
    ContractAddress,
    TransactionHash,
)


class VoyagerBlockExplorer(BlockExplorer):
    def __init__(self, network: PredefinedNetwork) -> None:
        super().__init__()
        network_to_domain: dict[PredefinedNetwork, URL] = {
            "mainnet": "https://voyager.online",
            "testnet": "https://goerli.voyager.online",
            "alpha-mainnet": "https://voyager.online",
            "alpha-goerli": "https://goerli.voyager.online",
        }
        self._domain = network_to_domain[network]

    def create_link_to_transaction(self, tx_hash: TransactionHash) -> URL:
        return f"{self._domain}/tx/0x{tx_hash:064x}"

    def create_link_to_contract(self, contract_address: ContractAddress) -> URL:
        return f"{self._domain}/contract/0x{contract_address:064x}"

    def create_link_to_class(self, class_hash: ClassHash) -> URL:
        return f"{self._domain}/class/0x{class_hash:064x}"
