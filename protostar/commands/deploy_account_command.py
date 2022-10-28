from argparse import Namespace
from dataclasses import dataclass
from logging import Logger
from typing import Optional

from protostar.cli import ProtostarArgument, ProtostarCommand
from protostar.cli.network_command_util import NetworkCommandUtil
from protostar.starknet_gateway import GatewayFacadeFactory
from protostar.starknet_gateway.gateway_facade import DeployAccountArgs
from protostar.starknet_gateway.gateway_response import SuccessfulDeployAccountResponse


@dataclass
class DeployAccountCommandArgs:
    @classmethod
    def from_args(cls, args: Namespace):
        cls()


class DeployAccountCommand(ProtostarCommand):
    def __init__(
        self,
        logger: Logger,
        gateway_facade_factory: GatewayFacadeFactory,
    ) -> None:
        self._logger = logger
        self._gateway_facade_factory = gateway_facade_factory

    @property
    def name(self) -> str:
        return "deploy"

    @property
    def description(self) -> str:
        return "Deploy contracts."

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self):
        return [
            *NetworkCommandUtil.network_arguments,
        ]

    async def run(self, args: Namespace):
        typed_args = DeployAccountCommandArgs.from_args(args)
        if self._validate_cli_args(typed_args):
            deploy_account_args = self._map_typed_args_to_deploy_account_args(
                typed_args
            )
            response = await self._send_deploy_account_tx(deploy_account_args)
            self._log_response(response)

    def _validate_cli_args(self, typed_args: DeployAccountCommandArgs) -> bool:
        return True

    def _map_typed_args_to_deploy_account_args(
        self, typed_args: DeployAccountCommandArgs
    ) -> DeployAccountArgs:
        return DeployAccountArgs()

    async def _send_deploy_account_tx(
        self,
        typed_args: DeployAccountCommandArgs,
        deploy_account_args: DeployAccountArgs,
    ):
        gateway_facade = self._gateway_facade_factory.create(
            gateway_client=typed_args.gateway_client, logger=None
        )
        return await gateway_facade.deploy_account()

    async def _log_response(self, response: SuccessfulDeployAccountResponse):
        pass
