from logging import Logger

from protostar.utils.protostar_directory import ProtostarDirectory, VersionManager
from protostar.utils.update_toml import UpdateTOML


class UpgradeLocalChecker:
    def __init__(
        self,
        protostar_directory: ProtostarDirectory,
        version_manager: VersionManager,
        logger: Logger,
    ) -> None:
        self._protostar_directory = protostar_directory
        self._version_manager = version_manager
        self._logger = logger

    def log_info_if_update_available(self):
        update_toml = UpdateTOML.Reader(self._protostar_directory).read()
        if not update_toml:
            return

        if update_toml.version > (
            self._version_manager.protostar_version or VersionManager.parse("0.0.0")
        ):
            self._logger.info(f"NEW VERSION AVAILABLE: {update_toml.version}")
