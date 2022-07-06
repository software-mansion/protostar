from logging import Logger

from protostar.utils.log_color_provider import LogColorProvider
from protostar.utils.protostar_directory import ProtostarDirectory, VersionManager
from protostar.utils.update_toml import UpdateTOML


class UpgradeLocalChecker:
    def __init__(
        self,
        protostar_directory: ProtostarDirectory,
        version_manager: VersionManager,
        logger: Logger,
        log_color_provider: LogColorProvider,
    ) -> None:
        self._protostar_directory = protostar_directory
        self._version_manager = version_manager
        self._logger = logger
        self._log_color_provider = log_color_provider

    def log_info_if_update_available(self):
        try:
            update_toml = UpdateTOML.Reader(self._protostar_directory).read()
            if not update_toml:
                return

            if update_toml.version > (
                self._version_manager.protostar_version or VersionManager.parse("0.0.0")
            ):
                bold = self._log_color_provider.bold
                colorize = self._log_color_provider.colorize
                self._logger.info(
                    "\n".join(
                        [
                            (
                                "A new Protostar version is available: "
                                f"{bold(update_toml.version)}."
                            ),
                            "",
                            colorize("GRAY", f"Changelog: {update_toml.changelog_url}"),
                            (
                                "To install the latest Protostar version, run "
                                f"{bold(colorize('CYAN', 'protostar upgrade'))}."
                            ),
                            "",
                        ]
                    )
                )
        except BaseException:  # pylint: disable=broad-except
            self._logger.warn(
                f"Couldn't read {self._protostar_directory.update_toml_path}"
            )
