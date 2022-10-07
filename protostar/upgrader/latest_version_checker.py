from datetime import datetime, timedelta
from logging import Logger
from typing import Optional

# pylint: disable=redefined-builtin
from requests.exceptions import ConnectionError

from protostar.upgrader.latest_version_cache_toml import LatestVersionCacheTOML
from protostar.upgrader.latest_version_remote_checker import LatestVersionRemoteChecker
from protostar.utils.log_color_provider import LogColorProvider
from protostar.protostar_directory import ProtostarDirectory, VersionManager


# pylint: disable=too-many-instance-attributes
class LatestVersionChecker:
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
        self._latest_version_remote_checker = latest_version_remote_checker
        self._new_latest_version_cache_toml_cache: Optional[
            LatestVersionCacheTOML
        ] = None

    async def run(self):
        latest_version_cache_toml = (
            self.load_local_latest_version_cache_toml()
        ) or await self.check_latest_version()

        if latest_version_cache_toml:
            self._latest_version_cache_toml_writer.save(latest_version_cache_toml)

            if self._version_manager.protostar_version is None or (
                latest_version_cache_toml.version
                > self._version_manager.protostar_version
            ):
                self.log_new_version_info(latest_version_cache_toml)

    def log_new_version_info(self, latest_version_cache_toml: LatestVersionCacheTOML):
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

    def load_local_latest_version_cache_toml(
        self,
    ) -> Optional[LatestVersionCacheTOML]:
        current_latest_version_cache_toml = (
            self._latest_version_cache_toml_reader.read()
        )
        if (
            current_latest_version_cache_toml is not None
            and current_latest_version_cache_toml.next_check_datetime > datetime.now()
        ):
            return current_latest_version_cache_toml
        return None

    async def check_latest_version(self) -> Optional[LatestVersionCacheTOML]:
        try:
            result = await self._latest_version_remote_checker.check()
            return LatestVersionCacheTOML(
                version=result.latest_version,
                changelog_url=result.changelog_url,
                next_check_datetime=datetime.now() + timedelta(days=3),
            )
        except ConnectionError:
            current_latest_version_cache_toml = (
                self._latest_version_cache_toml_reader.read()
            )
            if current_latest_version_cache_toml:
                return LatestVersionCacheTOML(
                    version=current_latest_version_cache_toml.version,
                    changelog_url=current_latest_version_cache_toml.changelog_url,
                    next_check_datetime=datetime.now() + timedelta(days=1),
                )
