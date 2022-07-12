from datetime import datetime, timedelta
from logging import Logger
from typing import Optional

from protostar.upgrader.upgrade_remote_checker import UpgradeRemoteChecker
from protostar.upgrader.upgrade_toml import UpgradeTOML
from protostar.utils.log_color_provider import LogColorProvider
from protostar.utils.protostar_directory import ProtostarDirectory, VersionManager


class UpgradeChecker:

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        protostar_directory: ProtostarDirectory,
        version_manager: VersionManager,
        logger: Logger,
        log_color_provider: LogColorProvider,
        upgrade_toml_reader: UpgradeTOML.Reader,
        upgrade_toml_writer: UpgradeTOML.Writer,
        upgrade_remote_checker: UpgradeRemoteChecker,
    ) -> None:
        self._protostar_directory = protostar_directory
        self._version_manager = version_manager
        self._logger = logger
        self._log_color_provider = log_color_provider
        self._upgrade_toml_reader = upgrade_toml_reader
        self._upgrade_toml_writer = upgrade_toml_writer
        self._upgrade_remote_checker = upgrade_remote_checker

    async def check_for_upgrades_if_necessary(self):
        upgrade_toml = self._upgrade_toml_reader.read()
        new_upgrade_toml = await self._update_upgrade_toml_if_necessary(upgrade_toml)
        if new_upgrade_toml:
            self._log_info_if_update_available(new_upgrade_toml)

    def _log_info_if_update_available(self, upgrade_toml: UpgradeTOML):
        if upgrade_toml.version > (
            self._version_manager.protostar_version or VersionManager.parse("0.0.0")
        ):
            bold = self._log_color_provider.bold
            colorize = self._log_color_provider.colorize
            self._logger.info(
                "\n".join(
                    [
                        (
                            "A new Protostar version is available: "
                            f"{bold(upgrade_toml.version)}."
                        ),
                        "",
                        colorize("GRAY", f"Changelog: {upgrade_toml.changelog_url}"),
                        (
                            "To install the latest Protostar version, run "
                            f"{bold(colorize('CYAN', 'protostar upgrade'))}."
                        ),
                        "",
                    ]
                )
            )

    async def _update_upgrade_toml_if_necessary(
        self, upgrade_toml: Optional[UpgradeTOML]
    ) -> Optional[UpgradeTOML]:
        new_upgrade_toml = upgrade_toml

        if upgrade_toml is None or upgrade_toml.next_check_datetime < datetime.now():
            self._logger.info("Checking for updates...")
            result = await self._upgrade_remote_checker.check()

            if result is not None:
                new_upgrade_toml = UpgradeTOML(
                    version=result.latest_version,
                    changelog_url=result.changelog_url,
                    next_check_datetime=datetime.now() + timedelta(days=3),
                )

        if new_upgrade_toml is not None:
            self._upgrade_toml_writer.save(new_upgrade_toml)
        return new_upgrade_toml
