from logging import Logger

from protostar.upgrader.upgrade_toml import UpgradeTOML
from protostar.utils.log_color_provider import LogColorProvider
from protostar.utils.protostar_directory import ProtostarDirectory, VersionManager


class UpgradeLocalChecker:
    """
    Check if there's information about the upgrade on the user's disk.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        protostar_directory: ProtostarDirectory,
        version_manager: VersionManager,
        logger: Logger,
        log_color_provider: LogColorProvider,
        upgrade_toml_reader: UpgradeTOML.Reader,
    ) -> None:
        self._protostar_directory = protostar_directory
        self._version_manager = version_manager
        self._logger = logger
        self._log_color_provider = log_color_provider
        self._upgrade_toml_reader = upgrade_toml_reader

    def log_info_if_update_available(self):
        try:
            update_toml = self._upgrade_toml_reader.read()
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
                f"Couldn't read {self._protostar_directory.upgrade_toml_path}"
            )
