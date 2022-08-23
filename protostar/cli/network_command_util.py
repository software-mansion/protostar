from logging import Logger
from typing import Any

from starknet_py.net.gateway_client import GatewayClient

from protostar.cli import Command
from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway import NetworkConfig
from protostar.starknet_gateway.network_config import is_legacy_network_name, NETWORKS

GATEWAY_URL_ARG_NAME = "gateway-url"
NETWORK_ARG_NAME = "network"
CHAIN_ID_ARG_NAME = "chain-id"


class NetworkCommandUtil:
    network_arguments = [
        Command.Argument(
            name=GATEWAY_URL_ARG_NAME,
            description="The URL of a StarkNet gateway. It is required unless `--network` is provided.",
            type="str",
        ),
        Command.Argument(
            name=CHAIN_ID_ARG_NAME,
            description="The chain id. It is required unless `--network` is provided.",
            type="int",
        ),
        Command.Argument(
            name=NETWORK_ARG_NAME,
            short_name="n",
            description=(
                "\n".join(
                    [
                        "The name of the StarkNet network.",
                        "It is required unless `--gateway-url` is provided.",
                        "",
                        "Supported StarkNet networks:",
                    ]
                    + [f"- `{n}`" for n in NETWORKS]
                )
            ),
            type="str",
        ),
    ]

    def __init__(self, args: Any, logger: Logger):
        self._args = args
        self._logger = logger

    def validate_network_command_args(self):
        if self._args.network is None and self._args.gateway_url is None:
            raise ProtostarException(
                f"Argument `{GATEWAY_URL_ARG_NAME}` or `{NETWORK_ARG_NAME}` is required"
            )

        # TODO(arcticae): Remove in the future version, with the legacy names formats support
        if self._args.network and is_legacy_network_name(self._args.network):
            self._logger.warning(
                f"{self._args.network} is a legacy network name parameter and it won't be supported in future versions"
            )

        if self._args.gateway_url and not self._args.chain_id:
            raise ProtostarException(
                f"Argument `{CHAIN_ID_ARG_NAME}` is required when `{GATEWAY_URL_ARG_NAME}` is provided"
            )

    def get_network_config(self) -> NetworkConfig:
        self.validate_network_command_args()
        return NetworkConfig.build(
            self._args.gateway_url, self._args.network, chain_id=self._args.chain_id
        )

    def get_gateway_client(self) -> GatewayClient:
        network_config = self.get_network_config()
        # FIXME(arcticae): Remove ignore of this type when starknet.py implements ChainId as Union[StarknetChainId, int]
        return GatewayClient(
            net=network_config.gateway_url,
            chain=network_config.chain_id,  # type: ignore
        )
