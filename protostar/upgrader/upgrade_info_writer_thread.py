from threading import Thread

from protostar.upgrader.upgrade_poller import UpgradePoller
from protostar.upgrader.upgrade_toml import UpgradeTOML
from protostar.utils.protostar_directory import ProtostarDirectory, VersionManager


class UpgradeInfoWriterThread:
    def __init__(
        self, protostar_directory: ProtostarDirectory, version_manager: VersionManager
    ):
        self._protostar_directory = protostar_directory
        self._version_manager = version_manager

        self._thread = Thread(target=self._overwrite_update_available_file, daemon=True)

    def _overwrite_update_available_file(self):
        upgrade_checker = UpgradePoller(
            self._protostar_directory, self._version_manager
        )
        result = upgrade_checker.poll()
        if result.is_newer_version_available:
            UpgradeTOML.Writer(self._protostar_directory).save(
                UpgradeTOML(
                    version=result.latest_version, changelog_url=result.changelog_url
                )
            )

    def __enter__(self):
        self._thread.start()

    def __exit__(self, exc_type, exc_value, exc_tb):
        pass
