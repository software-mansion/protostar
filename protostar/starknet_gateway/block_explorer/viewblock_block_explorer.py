from typing import Optional

from protostar.starknet_gateway.network_config import PredefinedNetwork

from .block_explorer import (
    URL,
    BlockExplorer,
    ClassHash,
    ContractAddress,
    TransactionHash,
)


class ViewblockBlockExplorer(BlockExplorer):
    def __init__(self, network: PredefinedNetwork) -> None:
        super().__init__()
        self._network: PredefinedNetwork = network
        self._prefix: URL = "https://v2.viewblock.io/starknet"

    def create_link_to_transaction(self, tx_hash: TransactionHash) -> URL:
        return f"{self._prefix}/tx/0x{tx_hash:064x}{self._get_network_query_param()}"

    def create_link_to_contract(self, contract_address: ContractAddress) -> URL:
        return f"{self._prefix}/contract/0x{contract_address:064x}{self._get_network_query_param()}"

    def create_link_to_class(self, class_hash: ClassHash) -> URL:
        return (
            f"{self._prefix}/class/0x{class_hash:064x}{self._get_network_query_param()}"
        )

    def _get_network_query_param(self) -> str:
        predefined_network_to_query_value: dict[PredefinedNetwork, Optional[str]] = {
            "mainnet": None,
            "alpha-mainnet": None,
            "testnet": "goerli",
            "alpha-goerli": "goerli",
        }
        param_value = predefined_network_to_query_value[self._network]
        if param_value is None:
            return ""
        return f"?network={param_value}"
