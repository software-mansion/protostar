import asyncio
from threading import Thread
from typing import Optional

# pylint: disable=redefined-builtin
from requests.exceptions import ConnectionError

from protostar.upgrader.upgrade_remote_checker import UpgradeRemoteChecker
from protostar.upgrader.upgrade_toml import UpgradeTOML


class UpgradeInfoWriterThread:
    """
    Check if the new version "in the background" and create a `upgrade.toml`.
    """

    def __init__(
        self,
        upgrade_remote_checker: UpgradeRemoteChecker,
        upgrade_toml_writer: UpgradeTOML.Writer,
    ):
        self._upgrade_remote_checker = upgrade_remote_checker
        self._upgrade_toml_writer = upgrade_toml_writer
        self._thread = Thread(
            target=self.overwrite_upgrade_toml_if_necessary, daemon=True
        )
        self._result: Optional[UpgradeRemoteChecker.Result] = None

    def overwrite_upgrade_toml_if_necessary(self):
        try:
            self._result = asyncio.run(self._upgrade_remote_checker.check())
        except ConnectionError:
            pass

    def __enter__(self):
        self._thread.start()

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._thread.join()

        if self._result is not None and self._result.is_newer_version_available:
            self._upgrade_toml_writer.save(
                UpgradeTOML(
                    version=self._result.latest_version,
                    changelog_url=self._result.changelog_url,
                )
            )
