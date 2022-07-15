from logging import Logger
from pathlib import Path
from typing import List, Optional

from protostar.cli.command import Command
from protostar.commands.deploy.deploy_command import DeployCommand
from protostar.deployer import Deployer
from protostar.deployer.deployer import InvalidNetworkConfigurationException
from protostar.deployer.gateway_response import SuccessfulDeclareResponse
from protostar.protostar_exception import ProtostarException


class DeclareCommand(Command):
    def __init__(self, deployer: Deployer, logger: Logger):
        self._deployer = deployer
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
                description=("The path to the compiled contract."),
                type="path",
                is_positional=True,
                is_required=True,
            ),
            Command.Argument(
                name="signature",
                description=("The signature information for the declaration."),
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
        try:
            network_config = self._deployer.build_network_config(
                network=network, gateway_url=gateway_url
            )
        except InvalidNetworkConfigurationException as err:
            raise ProtostarException(
                f"Argument `{DeployCommand.gateway_url_arg.name}` or `{DeployCommand.network_arg.name}` is required"
            ) from err

        response = await self._deployer.declare(
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
