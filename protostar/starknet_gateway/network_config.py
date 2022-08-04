from typing import List, Optional

from starkware.starknet.cli.starknet_cli import NETWORKS

from protostar.protostar_exception import ProtostarException


class InvalidNetworkConfigurationException(Exception):
    pass


class UnknownStarkwareNetworkException(ProtostarException):
    def __init__(self):
        message_lines: List[str] = []
        message_lines.append("Unknown StarkNet network")
        message_lines.append("The following StarkNet network names are supported:")
        for network_name in NETWORKS:
            message_lines.append(f"- {network_name}")
        super().__init__("\n".join(message_lines))


class NetworkConfig:
    @staticmethod
    def get_starknet_networks() -> List[str]:
        return list(NETWORKS.keys())

    def __init__(
        self,
        network: str,
    ) -> None:
        if network not in NETWORKS:
            self.gateway_url = network
            self.contract_explorer_search_url = None
            return

        contract_explorer_search_url_mapping = {
            "alpha-goerli": "https://goerli.voyager.online/contract",
            "alpha-mainnet": "https://voyager.online/contract",
        }

        self.gateway_url = (f"https://{NETWORKS[network]}/gateway",)
        self.contract_explorer_search_url = contract_explorer_search_url_mapping.get(
            network
        )

    def get_contract_explorer_url(self, contract_address: int) -> Optional[str]:
        if not self.contract_explorer_search_url:
            return None

        return f"{self.contract_explorer_search_url}/0x{contract_address:064x}"
