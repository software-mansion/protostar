from logging import Logger
from pathlib import Path
from typing import List, Optional

from protostar.cli.command import Command
from protostar.commands.deploy.deploy_command import DeployCommand
from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway import (
    GatewayFacade,
    NetworkConfig,
    SuccessfulDeclareResponse,
)


class DeclareCommand(Command):
    def __init__(
        self,
        gateway_facade: GatewayFacade,
        logger: Logger,
    ):
        self._gateway_facade = gateway_facade
        self._logger = logger

    @property
    def name(self) -> str:
        return "declare"

    @property
    def description(self) -> str:
        return "Sends a declare transaction to StarkNet."

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="contract",
                description=("Path to compiled contract."),
                type="path",
                is_positional=True,
                is_required=True,
            ),
            Command.Argument(
                name="signature",
                description=("Signature information for the declaration."),
                type="str",
                is_array=True,
            ),
            Command.Argument(
                name="token",
                description="Used for declaring contracts in Alpha MainNet.",
                type="str",
            ),
            DeployCommand.gateway_url_arg,
            DeployCommand.network_arg,
        ]

    async def run(self, args) -> SuccessfulDeclareResponse:
        assert isinstance(args.contract, Path)
        assert args.network is None or isinstance(args.network, str)
        assert args.gateway_url is None or isinstance(args.gateway_url, str)
        assert args.token is None or isinstance(args.token, str)
        assert args.signature is None or isinstance(args.signature, list)

        return await self.declare(
            compiled_contract_path=args.contract,
            network=args.network,
            gateway_url=args.gateway_url,
            token=args.token,
            signature=args.signature,
        )

    # pylint: disable=too-many-arguments
    async def declare(
        self,
        compiled_contract_path: Path,
        network: Optional[str] = None,
        gateway_url: Optional[str] = None,
        token: Optional[str] = None,
        signature: Optional[List[str]] = None,
    ) -> SuccessfulDeclareResponse:
        if network is None and gateway_url is None:
            raise ProtostarException(
                f"Argument `{DeployCommand.gateway_url_arg.name}` or `{DeployCommand.network_arg.name}` is required"
            )

        network_config = NetworkConfig.build(network=network, gateway_url=gateway_url)

        response = await self._gateway_facade.declare(
            compiled_contract_path=compiled_contract_path,
            gateway_url=network_config.gateway_url,
            token=token,
            signature=signature,
        )

        explorer_url = network_config.get_contract_explorer_url(response.class_hash)
        explorer_url_msg_lines: List[str] = []
        if explorer_url:
            explorer_url_msg_lines = ["", explorer_url]

        response.log(self._logger, extra_msg=explorer_url_msg_lines)
        return response
