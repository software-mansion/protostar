from typing import Optional

from protostar.starknet_gateway.network_config import PredefinedNetwork

from .block_explorer import BlockExplorer, ClassHash, Address, TransactionHash


class ViewblockBlockExplorer(BlockExplorer):
    def __init__(self, network: PredefinedNetwork) -> None:
        super().__init__()
        self._network: PredefinedNetwork = network
        self._prefix: str = "https://v2.viewblock.io/starknet"

    def get_name(self) -> str:
        return "ViewBlock"

    def create_link_to_transaction(self, tx_hash: TransactionHash) -> Optional[str]:
        return f"{self._prefix}/tx/0x{tx_hash:064x}{self._get_network_query_param()}"

    def create_link_to_contract(self, contract_address: Address) -> Optional[str]:
        return f"{self._prefix}/contract/{contract_address}{self._get_network_query_param()}"

    def create_link_to_class(self, class_hash: ClassHash) -> Optional[str]:
        return (
            f"{self._prefix}/class/0x{class_hash:064x}{self._get_network_query_param()}"
        )

    def _get_network_query_param(self) -> str:
        predefined_network_to_query_value: dict[PredefinedNetwork, Optional[str]] = {
            "mainnet": None,
            "testnet": "goerli",
        }
        param_value = predefined_network_to_query_value[self._network]
        if param_value is None:
            return ""
        return f"?network={param_value}"
