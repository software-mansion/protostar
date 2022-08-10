from typing import List, Optional, Union

from starknet_py.net.models import chain_from_network, StarknetChainId
from starknet_py.net.networks import Network, TESTNET, MAINNET, net_address_from_net

from protostar.protostar_exception import ProtostarException

KNOWN_NETWORKS = [TESTNET, MAINNET]


class InvalidNetworkConfigurationException(Exception):
    pass


ChainId = Union[StarknetChainId, int]


class UnknownStarkwareNetworkException(ProtostarException):
    def __init__(self):
        message_lines: List[str] = []
        message_lines.append("Unknown StarkNet network")
        message_lines.append("The following StarkNet network names are supported:")
        for network_name in KNOWN_NETWORKS:
            message_lines.append(f"- {network_name}")
        super().__init__("\n".join(message_lines))


class NetworkConfig:
    @classmethod
    def build(
        cls,
        gateway_url: Optional[str] = None,
        network: Optional[Network] = None,
        chain_id: Optional[int] = None,
    ) -> "NetworkConfig":
        network_config: Optional[NetworkConfig] = None

        if network:
            network_config = cls.from_starknet_network_name(network)
        if gateway_url:
            network_config = cls(
                gateway_url=gateway_url,
                chain_id=chain_id,
                contract_explorer_search_url=None
            )

        if network_config is None:
            raise InvalidNetworkConfigurationException()

        return network_config

    @staticmethod
    def get_starknet_networks() -> List[str]:
        return KNOWN_NETWORKS

    @classmethod
    def from_starknet_network_name(cls, network: str) -> None:
        if network not in NetworkConfig.get_starknet_networks():            raise UnknownStarkwareNetworkException()
            raise UnknownStarkwareNetworkException()

        contract_explorer_search_url_mapping = {
            TESTNET: "https://goerli.voyager.online/contract",
            MAINNET: "https://voyager.online/contract",
        }

        chain_id = chain_from_network(net=network, chain=None)

        return cls(
            gateway_url=f"{net_address_from_net(starkware_network_name)}/gateway",
            contract_explorer_search_url=contract_explorer_search_url_mapping.get(
                starkware_network_name
            ),
            chain_id=chain_id.value,
        )

    def __init__(
        self,
        gateway_url: str,
        chain_id: ChainId,
        contract_explorer_search_url: Optional[str] = None,
    ):
        self.gateway_url = gateway_url
        self.chain_id = chain_id
        self.contract_explorer_search_url = contract_explorer_search_url

    def get_contract_explorer_url(self, contract_address: int) -> Optional[str]:
        if not self.contract_explorer_search_url:
            return None

        return f"{self.contract_explorer_search_url}/0x{contract_address:064x}"
