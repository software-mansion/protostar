from typing import List, Optional

from protostar.cli.command import Command
from protostar.commands.upgrade.upgrade_manager import UpgradeManager


class UpgradeCommand(Command):
    def __init__(self, upgrade_manager: UpgradeManager) -> None:
        super().__init__()
        self._upgrade_manager = upgrade_manager

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

    async def run(self, _args):
        self._upgrade_manager.upgrade()
