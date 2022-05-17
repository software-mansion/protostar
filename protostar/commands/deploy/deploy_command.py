from typing import List, Optional

from protostar.cli.command import Command


class DeployCommand(Command):
    @property
    def name(self) -> str:
        return "deploy"

    @property
    def description(self) -> str:
        return "Deploys contracts."

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="contract",
                description='A name of the contract defined in protostar.toml::["protostar.contracts"]',
                type="str",
            ),
            Command.Argument(
                name="inputs",
                description="The inputs to the constructor",
                type="str",
                is_array=True,
            ),
            Command.Argument(
                name="network",
                description="A name of the network defined in protostar.toml",
                type="str",
            ),
            Command.Argument(
                name="token",
                description="Used for deploying contracts in Alpha MainNet.",
                type="str",
            ),
        ]

    async def run(self, _args):
        return await self.deploy()

    async def deploy(self):
        raise NotImplementedError()
