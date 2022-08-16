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


class NetworkCommandMixin:
    @property
    def network_arguments(self):
        return [
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

    @staticmethod
    def validate_network_command_args(args, logger: Logger):
        if args.network is None and args.gateway_url is None:
            raise ProtostarException(
                f"Argument `{GATEWAY_URL_ARG_NAME}` or `{NETWORK_ARG_NAME}` is required"
            )

        # TODO(arcticae): Remove in the future version, with the legacy names formats support
        if args.network and is_legacy_network_name(args.network):
            logger.warning(
                f"{args.network} is a legacy network name parameter and it won't be supported in future versions"
            )

        if args.gateway_url and not args.chain_id:
            raise ProtostarException(
                f"Argument `{CHAIN_ID_ARG_NAME}` is required when `{GATEWAY_URL_ARG_NAME}` is provided"
            )

    @staticmethod
    def get_network_config(args: Any, logger: Logger) -> NetworkConfig:
        NetworkCommandMixin.validate_network_command_args(args, logger)
        return NetworkConfig.build(
            args.gateway_url, args.network, chain_id=args.chain_id
        )

    @staticmethod
    def get_gateway_client(args: Any, logger: Logger) -> GatewayClient:
        network_config = NetworkCommandMixin.get_network_config(args, logger)
        return GatewayClient(
            net=network_config.gateway_url,
            chain=network_config.chain_id,  # type: ignore
        )
