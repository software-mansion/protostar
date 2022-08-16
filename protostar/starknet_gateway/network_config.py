from typing import Optional, Union, cast
from typing_extensions import Literal

from starknet_py.net.models import chain_from_network
from starknet_py.net.networks import (
    TESTNET,
    MAINNET,
    net_address_from_net,
    PredefinedNetwork as SimpleNetwork,
)
from starkware.starknet.cli.starknet_cli import NETWORKS as LEGACY_NETWORKS
from protostar.protostar_exception import ProtostarException


SIMPLE_NETWORKS = [TESTNET, MAINNET]
NETWORKS = [*SIMPLE_NETWORKS, *LEGACY_NETWORKS.keys()]

LegacyNetwork = Literal["alpha-goerli", "alpha-mainnet"]
PredefinedNetwork = Union[SimpleNetwork, LegacyNetwork]


def is_legacy_network_name(network: PredefinedNetwork):
    return network in LEGACY_NETWORKS


def legacy_to_simple_network_name(legacy_name: LegacyNetwork) -> SimpleNetwork:
    return {"alpha-goerli": "testnet", "alpha-mainnet": "mainnet"}[legacy_name]


def predefined_to_simple_network(network: PredefinedNetwork) -> SimpleNetwork:
    return (
        legacy_to_simple_network_name(cast(LegacyNetwork, network))
        if is_legacy_network_name(network)
        else network
    )


class NetworkConfig:
    @classmethod
    def build(
        cls,
        gateway_url: Optional[str] = None,
        network: Optional[PredefinedNetwork] = None,
        chain_id: Optional[int] = None,
    ) -> "NetworkConfig":
        if network:
            network = predefined_to_simple_network(network)
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

    @classmethod
    def from_starknet_network_name(cls, network: PredefinedNetwork) -> "NetworkConfig":
        if network not in NETWORKS:
            raise ProtostarException(
                "\n".join(
                    [
                        "Unknown StarkNet network",
                        "The following StarkNet network names are supported:",
                        *(f"- {network_name}" for network_name in NETWORKS),
                    ]
                )
            )

        network = predefined_to_simple_network(network)

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
