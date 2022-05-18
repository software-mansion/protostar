from typing import List

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

        return cls(gateway_url=f"https://{NETWORKS[starkware_network_name]}/gateway")

    def __init__(self, gateway_url: str):
        self.gateway_url = gateway_url
