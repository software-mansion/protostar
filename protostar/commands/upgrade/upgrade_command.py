from logging import Logger
from typing import List, Optional

from protostar.cli.command import Command
from protostar.upgrader import UpgradeManager


class UpgradeCommand(Command):
    def __init__(self, upgrade_manager: UpgradeManager, logger: Logger) -> None:
        super().__init__()
        self._upgrade_manager = upgrade_manager
        self._logger = logger

    @property
    def name(self) -> str:
        return "upgrade"

    @property
    def description(self) -> str:
        return "Upgrade Protostar."

    @property
    def example(self) -> Optional[str]:
        return "$ protostar upgrade"

    @property
    def arguments(self) -> List[Command.Argument]:
        return []

    @property
    def outputs(self) -> Command.PrintedOutputs:
        return Command.PrintedOutputs(
            entry="Running upgrade of protostar",
            exit_success="Upgraded successfully",
            exit_error="Upgrade failed",
        )

    async def run(self, _args):
        self._logger.info(self.outputs.entry)
        try:
            await self._upgrade_manager.upgrade()
        except BaseException as exc:
            self._logger.error(self.outputs.exit_error)
            raise exc
        self._logger.info(self.outputs.exit_success)
