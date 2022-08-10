from logging import Logger
from pathlib import Path
from typing import List, Optional

from starknet_py.net.signer import BaseSigner

from protostar.cli.command import Command
from protostar.cli.network_command_mixin import NetworkCommandMixin
from protostar.cli.signable_command_mixin import SignableCommandMixin
from protostar.commands.deploy.deploy_command import DeployCommand
from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway import (
    GatewayFacade,
    NetworkConfig,
    SuccessfulDeclareResponse,
)


class DeclareCommand(Command, SignableCommandMixin, NetworkCommandMixin):
    def __init__(
        self,
        gateway_facade_builder: GatewayFacade.Builder,
        logger: Logger,
    ):
        self._gateway_facade_builder = gateway_facade_builder
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
            *self.signable_arguments,
            *self.network_arguments,
            Command.Argument(
                name="contract",
                description="Path to compiled contract.",
                type="path",
                is_positional=True,
                is_required=True,
            ),
            Command.Argument(
                name="token",
                description="Used for declaring contracts in Alpha MainNet.",
                type="str",
            ),
            DeployCommand.wait_for_acceptance_arg,
        ]

    async def run(self, args) -> SuccessfulDeclareResponse:
        assert isinstance(args.contract, Path)
        assert args.gateway_url is None or isinstance(args.gateway_url, str)
        assert args.network is None or isinstance(args.network, str)
        assert args.token is None or isinstance(args.token, str)
        assert isinstance(args.wait_for_acceptance, bool)
        assert args.signature is None or isinstance(args.signature, list)

        network_config = self.get_network_config(args)

        return await self.declare(
            compiled_contract_path=args.contract,
            signer=self.get_signer(args, network_config),
            network_config=network_config,
            network=args.network or args.gateway_url,
            token=args.token,
            wait_for_acceptance=args.wait_for_acceptance,
        )

    # pylint: disable=too-many-arguments
    async def declare(
        self,
        compiled_contract_path: Path,
        signer: BaseSigner,
        network_config: NetworkConfig,
        network: Optional[str] = None,
        token: Optional[str] = None,
        wait_for_acceptance: bool = False,
    ) -> SuccessfulDeclareResponse:
        if network is None:
            raise ProtostarException(
                f"Argument `{DeployCommand.gateway_url_arg.name}` or `{DeployCommand.network_arg.name}` is required"
            )

        self._gateway_facade_builder.set_network(network)
        gateway_facade = self._gateway_facade_builder.build()

        response = await gateway_facade.declare(
            compiled_contract_path=compiled_contract_path,
            wait_for_acceptance=wait_for_acceptance,
            token=token,
            signer=signer,
        )

        explorer_url = network_config.get_contract_explorer_url(response.class_hash)
        explorer_url_msg_lines: List[str] = []
        if explorer_url:
            explorer_url_msg_lines = ["", explorer_url]

        response.log(self._logger, extra_msg=explorer_url_msg_lines)
        return response
