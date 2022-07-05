from dataclasses import dataclass
from threading import Thread
from typing import Optional

import tomli
import tomli_w

from protostar.utils.protostar_directory import (ProtostarDirectory,
                                                 VersionManager, VersionType)
from protostar.utils.upgrade_poller import UpgradePoller


@dataclass
class UpdateTOML:
    version: VersionType

    class Writer:
        def __init__(self, protostar_directory: ProtostarDirectory) -> None:
            self._protostar_directory = protostar_directory

        def save(self, update_toml: "UpdateTOML"):
            update_toml_path = (
                self._protostar_directory.directory_root_path
                / "dist"
                / "protostar"
                / "info"
                / "update.toml"
            )

            result = {"info": {"version": str(update_toml.version)}}
            with open(update_toml_path, "wb") as update_toml_file:
                tomli_w.dump(result, update_toml_file)

    class Reader:
        def __init__(self, protostar_directory: ProtostarDirectory) -> None:
            self._protostar_directory = protostar_directory

        def read(self) -> Optional["UpdateTOML"]:
            update_toml_path = (
                self._protostar_directory.directory_root_path
                / "dist"
                / "protostar"
                / "info"
                / "update.toml"
            )
            if not update_toml_path.exists():
                return None

            with open(update_toml_path, "rb") as update_toml_file:
                update_toml_dict = tomli.load(update_toml_file)

                return UpdateTOML(version=update_toml_dict["info"]["version"])


class UpgradePollerThread:
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
            UpdateTOML.Writer(self._protostar_directory).save(
                UpdateTOML(version=result.latest_version)
            )

    def __enter__(self):
        self._thread.start()

    def __exit__(self, exc_type, exc_value, exc_tb):
        pass
