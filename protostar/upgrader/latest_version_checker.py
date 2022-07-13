from datetime import datetime, timedelta
from logging import Logger
from typing import Optional

from protostar.upgrader.latest_version_cache_toml import LatestVersionCacheTOML
from protostar.upgrader.latest_version_remote_checker import LatestVersionRemoteChecker
from protostar.utils.log_color_provider import LogColorProvider
from protostar.utils.protostar_directory import ProtostarDirectory, VersionManager


class LatestVersionChecker:

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        protostar_directory: ProtostarDirectory,
        version_manager: VersionManager,
        logger: Logger,
        log_color_provider: LogColorProvider,
        latest_version_cache_toml_reader: LatestVersionCacheTOML.Reader,
        latest_version_cache_toml_writer: LatestVersionCacheTOML.Writer,
        latest_version_remote_checker: LatestVersionRemoteChecker,
    ) -> None:
        self._protostar_directory = protostar_directory
        self._version_manager = version_manager
        self._logger = logger
        self._log_color_provider = log_color_provider
        self._latest_version_cache_toml_reader = latest_version_cache_toml_reader
        self._latest_version_cache_toml_writer = latest_version_cache_toml_writer
        self._upgrade_remote_checker = latest_version_remote_checker

    async def check_for_upgrades_if_necessary(self):
        latest_version_cache_toml = self._latest_version_cache_toml_reader.read()
        new_latest_version_cache_toml = await self._update_upgrade_toml_if_necessary(
            latest_version_cache_toml
        )
        if new_latest_version_cache_toml:
            self._log_info_if_update_available(new_latest_version_cache_toml)

    def _log_info_if_update_available(self, upgrade_toml: LatestVersionCacheTOML):
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
        self, upgrade_toml: Optional[LatestVersionCacheTOML]
    ) -> Optional[LatestVersionCacheTOML]:
        new_upgrade_toml = upgrade_toml

        if upgrade_toml is None or upgrade_toml.next_check_datetime < datetime.now():
            self._logger.info("Checking for updates...")
            result = await self._upgrade_remote_checker.check()

            if result is not None:
                new_upgrade_toml = LatestVersionCacheTOML(
                    version=result.latest_version,
                    changelog_url=result.changelog_url,
                    next_check_datetime=datetime.now() + timedelta(days=3),
                )

        if new_upgrade_toml is not None:
            self._latest_version_cache_toml_writer.save(new_upgrade_toml)
        return new_upgrade_toml
