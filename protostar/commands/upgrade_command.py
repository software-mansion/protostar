import logging
from argparse import Namespace
from typing import Optional

from protostar.cli import ProtostarCommand
from protostar.upgrader import UpgradeManager


class UpgradeCommand(ProtostarCommand):
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
    def arguments(self):
        return []

    async def run(self, args: Namespace):
        logging.info("Running upgrade of protostar")
        try:
            await self._upgrade_manager.upgrade()
        except BaseException as exc:
            logging.error("Upgrade failed")
            raise exc
        logging.info("Upgraded successfully")
