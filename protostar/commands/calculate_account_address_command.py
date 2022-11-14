from argparse import Namespace
from logging import Logger
from typing import Optional

from protostar.cli import ProtostarCommand


class DeployCommand(ProtostarCommand):
    def __init__(
        self,
        logger: Logger,
    ) -> None:
        self._logger = logger

    @property
    def name(self) -> str:
        return "calculate-account-address"

    @property
    def description(self) -> str:
        return (
            "In order to create an account, you need to prefund the account. "
            "To prefund the account you need to know its address. "
            "This command calculates the account address."
        )

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self):
        return []

    async def run(self, args: Namespace):
        pass
