from starkware.starknet.cli.starknet_cli import NETWORKS

from protostar.protostar_exception import ProtostarException
from protostar.utils.config.project import Project


class InvalidNetworkConfigException(ProtostarException):
    pass


class NetworkConfig:
    @classmethod
    def from_config_file(cls, network_name: str, project: Project) -> "NetworkConfig":
        gateway_url = project.load_argument(f"network.{network_name}", "gateway_url")
        if gateway_url:
            return cls(gateway_url=gateway_url)

        starkware_network_name = project.load_argument(
            f"network.{network_name}", "network"
        )
        if starkware_network_name:
            return cls.from_starkware_network(starkware_network_name)

        raise InvalidNetworkConfigException(
            (
                f"Protostar couldn't find `gateway_url` for `{network_name}` network\n"
                f'Did you define `network` or `gateway_url`in protostar.toml::["protostar.network.{network_name}"]?'
            )
        )

    @classmethod
    def from_starkware_network(cls, starkware_network_name: str) -> "NetworkConfig":
        return cls(gateway_url=f"https://{NETWORKS[starkware_network_name]}/gateway")

    def __init__(self, gateway_url: str):
        self.gateway_url = gateway_url
