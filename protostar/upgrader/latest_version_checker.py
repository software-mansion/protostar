from datetime import datetime, timedelta
from logging import Logger
from typing import Optional

# pylint: disable=redefined-builtin
from requests.exceptions import ConnectionError

from protostar.upgrader.latest_version_cache_toml import LatestVersionCacheTOML
from protostar.upgrader.latest_version_remote_checker import LatestVersionRemoteChecker
from protostar.utils.log_color_provider import LogColorProvider
from protostar.utils.protostar_directory import ProtostarDirectory, VersionManager


# pylint: disable=too-many-instance-attributes
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
        self._new_latest_version_cache_toml_cache: Optional[
            LatestVersionCacheTOML
        ] = None

    async def run(self):
        current_latest_version_cache_toml = (
            self._latest_version_cache_toml_reader.read()
        )
        new_latest_version_cache_toml = (
            await self._build_up_to_date_latest_version_cache_toml(
                current_latest_version_cache_toml
            )
        )
        if new_latest_version_cache_toml is not None:
            if current_latest_version_cache_toml != new_latest_version_cache_toml:
                self._latest_version_cache_toml_writer.save(
                    new_latest_version_cache_toml
                )

            if self._version_manager.protostar_version is None or (
                new_latest_version_cache_toml.version
                > self._version_manager.protostar_version
            ):
                self._log_new_version_info(new_latest_version_cache_toml)

    def _log_new_version_info(self, latest_version_cache_toml: LatestVersionCacheTOML):
        bold = self._log_color_provider.bold
        colorize = self._log_color_provider.colorize
        self._logger.info(
            "\n".join(
                [
                    (
                        "A new Protostar version is available: "
                        f"{bold(latest_version_cache_toml.version)}."
                    ),
                    colorize(
                        "GRAY",
                        f"Changelog: {latest_version_cache_toml.changelog_url}",
                    ),
                    (
                        "To install the latest Protostar version, run "
                        f"{bold(colorize('CYAN', 'protostar upgrade'))}."
                    ),
                    "",
                ]
            )
        )

    async def _build_up_to_date_latest_version_cache_toml(
        self, current_latest_version_cache_toml: Optional[LatestVersionCacheTOML]
    ) -> Optional[LatestVersionCacheTOML]:

        if (
            current_latest_version_cache_toml is not None
            and current_latest_version_cache_toml.next_check_datetime > datetime.now()
        ):
            return current_latest_version_cache_toml

        new_latest_version_cache_toml = current_latest_version_cache_toml
        try:
            self._logger.info("Checking for updates")
            result = await self._upgrade_remote_checker.check()
            new_latest_version_cache_toml = LatestVersionCacheTOML(
                version=result.latest_version,
                changelog_url=result.changelog_url,
                next_check_datetime=datetime.now() + timedelta(days=3),
            )
        except ConnectionError:
            if current_latest_version_cache_toml:
                new_latest_version_cache_toml = LatestVersionCacheTOML(
                    version=current_latest_version_cache_toml.version,
                    changelog_url=current_latest_version_cache_toml.changelog_url,
                    next_check_datetime=datetime.now() + timedelta(days=1),
                )
        return new_latest_version_cache_toml
