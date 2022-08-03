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
        gateway_facade_builder: GatewayFacade.Builder,
        logger: Logger,
    ):
        self._gateway_facade_builder = gateway_facade_builder
        self._gateway_facade: Optional[GatewayFacade] = None
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
            # Command.Argument(
            #     name="signature",
            #     description=("Signature information for the declaration."),
            #     type="str",
            #     is_array=True,
            # ),
            Command.Argument(
                name="token",
                description="Used for declaring contracts in Alpha MainNet.",
                type="str",
            ),
            Command.Argument(
                name="wait-for-acceptance",
                description="Wait until 'Accepted on L2' status.",
                type="bool",
                default=False,
            ),
            DeployCommand.network_arg,
        ]

    async def run(self, args) -> SuccessfulDeclareResponse:
        assert isinstance(args.contract, Path)
        assert args.network is None or isinstance(args.network, str)
        assert args.token is None or isinstance(args.token, str)
        assert isinstance(args.wait_for_acceptance, bool)
        # assert args.signature is None or isinstance(args.signature, list)

        self._gateway_facade_builder.set_network(args.network)
        self._gateway_facade = self._gateway_facade_builder.build()

        return await self.declare(
            compiled_contract_path=args.contract,
            network=args.network,
            token=args.token,
            wait_for_acceptance=args.wait_for_acceptance
            # signature=args.signature,
        )

    # pylint: disable=too-many-arguments
    async def declare(
        self,
        compiled_contract_path: Path,
        network: Optional[str] = None,
        token: Optional[str] = None,
        wait_for_acceptance: bool = False
        # signature: Optional[List[str]] = None,
    ) -> SuccessfulDeclareResponse:
        if network is None:
            raise ProtostarException(
                f"Argument `{DeployCommand.network_arg.name}` is required"
            )

        network_config = NetworkConfig.build(network=network)

        response = await self._gateway_facade.declare(
            compiled_contract_path=compiled_contract_path,
            token=token,
            wait_for_acceptance=wait_for_acceptance
            # signature=signature,
        )

        explorer_url = network_config.get_contract_explorer_url(response.class_hash)
        explorer_url_msg_lines: List[str] = []
        if explorer_url:
            explorer_url_msg_lines = ["", explorer_url]

        response.log(self._logger, extra_msg=explorer_url_msg_lines)
        return response
