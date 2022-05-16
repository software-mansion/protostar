from typing import List, Optional

from src.cli.command import Command


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
        return []

    async def run(self, _args):
        return await self.deploy()

    async def deploy(self):
        pass
