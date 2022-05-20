from typing import List, Optional

from starkware.starknet.cli.starknet_cli import NETWORKS

from protostar.protostar_exception import ProtostarException


class UnknownStarkwareNetworkException(ProtostarException):
    def __init__(self):
        message_lines: List[str] = []
        message_lines.append("Unknown starkware network")
        message_lines.append("The following starkware network names are supported:")
        for network_name in NETWORKS:
            message_lines.append(f"- {network_name}")
        super().__init__("\n".join(message_lines))


class NetworkConfig:
    @classmethod
    def from_starknet_network_name(
        cls,
        starkware_network_name: str,
    ) -> "NetworkConfig":
        if starkware_network_name not in NETWORKS:
            raise UnknownStarkwareNetworkException()

        contract_explorer_search_url_mapping = {
            "alpha-goerli": "https://goerli.voyager.online/contract",
            "alpha-mainnet": "https://voyager.online/contract",
        }

        return cls(
            gateway_url=f"https://{NETWORKS[starkware_network_name]}/gateway",
            contract_explorer_search_url=contract_explorer_search_url_mapping.get(
                starkware_network_name
            ),
        )

    def __init__(
        self, gateway_url: str, contract_explorer_search_url: Optional[str] = None
    ):
        self.gateway_url = gateway_url
        self.contract_explorer_search_url = contract_explorer_search_url

    def get_contract_explorer_url(self, contract_address: int) -> Optional[str]:
        if not self.contract_explorer_search_url:
            return None

        return f"{self.contract_explorer_search_url}/0x{contract_address:064x}"
