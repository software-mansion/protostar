from dataclasses import dataclass
from typing import Optional, Union, cast, Dict

from starknet_py.net.models import chain_from_network, StarknetChainId
from starknet_py.net.networks import (
    TESTNET,
    MAINNET,
    net_address_from_net,
    PredefinedNetwork as SimpleNetwork,
)
from starkware.starknet.cli.starknet_cli import NETWORKS as LEGACY_NETWORKS
from typing_extensions import Literal

from protostar.protostar_exception import ProtostarException

SIMPLE_NETWORKS = [TESTNET, MAINNET]
NETWORKS = [*SIMPLE_NETWORKS, *LEGACY_NETWORKS.keys()]

LegacyNetwork = Literal["alpha-goerli", "alpha-mainnet"]
PredefinedNetwork = Union[SimpleNetwork, LegacyNetwork]


def is_legacy_network_name(network: PredefinedNetwork):
    return network in LEGACY_NETWORKS


def legacy_to_simple_network_name(legacy_name: LegacyNetwork) -> SimpleNetwork:
    mapping: Dict[LegacyNetwork, SimpleNetwork] = {
        "alpha-goerli": "testnet",
        "alpha-mainnet": "mainnet",
    }

    return mapping[legacy_name]


def predefined_to_simple_network(network: PredefinedNetwork) -> SimpleNetwork:
    return (
        legacy_to_simple_network_name(cast(LegacyNetwork, network))
        if is_legacy_network_name(network)
        else cast(SimpleNetwork, network)
    )


@dataclass
class NetworkConfig:
    gateway_url: str
    chain_id: StarknetChainId
    contract_explorer_search_url: Optional[str] = None

    @classmethod
    def build(
        cls,
        gateway_url: Optional[str] = None,
        network: Optional[PredefinedNetwork] = None,
        chain_id: Optional[StarknetChainId] = None,
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
            gateway_url=net_address_from_net(network),
            contract_explorer_search_url=contract_explorer_search_url_mapping.get(
                network
            ),
            chain_id=chain_id,
        )

    def get_contract_explorer_url(self, contract_address: int) -> Optional[str]:
        if not self.contract_explorer_search_url:
            return None

        return f"{self.contract_explorer_search_url}/0x{contract_address:064x}"
