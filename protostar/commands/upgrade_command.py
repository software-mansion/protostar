from logging import Logger
from typing import Optional

from protostar.cli import ProtostarCommand
from protostar.upgrader import UpgradeManager


class UpgradeCommand(ProtostarCommand):
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
    def arguments(self):
        return []

    async def run(self, args):
        self._logger.info("Running upgrade of protostar")
        try:
            await self._upgrade_manager.upgrade()
        except BaseException as exc:
            self._logger.error("Upgrade failed")
            raise exc
        self._logger.info("Upgraded successfully")
