from typing import List, Optional

from protostar.cli.command import Command
from protostar.commands.deploy.deploy_command import DeployCommand
from protostar.deployer import Deployer


class DeclareCommand(Command):
    def __init__(self, deployer: Deployer):
        self._deployer = deployer

    @property
    def name(self) -> str:
        return "declare"

    @property
    def description(self) -> str:
        return "\n".join(
            [
                "Sends a declare transaction to StarkNet.",
            ]
        )

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self) -> List[Command.Argument]:
        return [
            DeployCommand.gateway_url_arg,
            DeployCommand.network_arg,
        ]

    async def run(self, args):
        raise NotImplementedError()
