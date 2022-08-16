from typing import List, Optional

from starknet_py.net.models import chain_from_network
from starknet_py.net.networks import Network, TESTNET, MAINNET, net_address_from_net

from protostar.protostar_exception import ProtostarException

KNOWN_NETWORKS = [TESTNET, MAINNET]


class NetworkConfig:
    @classmethod
    def build(
        cls,
        gateway_url: Optional[str] = None,
        network: Optional[Network] = None,
        chain_id: Optional[int] = None,
    ) -> "NetworkConfig":
        if network:
            return cls.from_starknet_network_name(network)
        if gateway_url and chain_id:
            return cls(
                gateway_url=gateway_url,
                chain_id=chain_id,
                contract_explorer_search_url=None,
            )

        raise ProtostarException(
            "Either network parameter or pair (chain_id, gateway_url) is required"
        )

    @staticmethod
    def get_starknet_networks() -> List[str]:
        return KNOWN_NETWORKS

    @classmethod
    def from_starknet_network_name(cls, network: str) -> "NetworkConfig":
        if network not in NetworkConfig.get_starknet_networks():
            raise ProtostarException(
                "\n".join(
                    [
                        "Unknown StarkNet network",
                        "The following StarkNet network names are supported:",
                        *(f"- {network_name}" for network_name in KNOWN_NETWORKS),
                    ]
                )
            )

        contract_explorer_search_url_mapping = {
            TESTNET: "https://goerli.voyager.online/contract",
            MAINNET: "https://voyager.online/contract",
        }

        chain_id = chain_from_network(net=network, chain=None)

        return cls(
            gateway_url=f"{net_address_from_net(network)}/gateway",
            contract_explorer_search_url=contract_explorer_search_url_mapping.get(
                network
            ),
            chain_id=chain_id.value,
        )

    def __init__(
        self,
        gateway_url: str,
        chain_id: int,
        contract_explorer_search_url: Optional[str] = None,
    ):
        self.gateway_url = gateway_url
        self.chain_id = chain_id
        self.contract_explorer_search_url = contract_explorer_search_url

    def get_contract_explorer_url(self, contract_address: int) -> Optional[str]:
        if not self.contract_explorer_search_url:
            return None

        return f"{self.contract_explorer_search_url}/0x{contract_address:064x}"
