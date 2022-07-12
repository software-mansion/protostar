from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import tomli
import tomli_w

from protostar.utils.protostar_directory import (
    ProtostarDirectory,
    VersionManager,
    VersionType,
)


@dataclass(frozen=True)
class UpgradeTOML:
    """
    Pythonic representation of the upgrade.toml.
    """

    version: VersionType
    changelog_url: str
    next_check_datetime: datetime

    class Writer:
        def __init__(self, protostar_directory: ProtostarDirectory) -> None:
            self._protostar_directory = protostar_directory

        def save(self, update_toml: "UpgradeTOML") -> None:
            if not self._protostar_directory.info_dir_path.exists():
                return None

            with open(
                self._protostar_directory.upgrade_toml_path, "wb"
            ) as update_toml_file:
                result = {
                    "info": {
                        "version": str(update_toml.version),
                        "changelog_url": update_toml.changelog_url,
                        "next_check_datetime": update_toml.next_check_datetime.isoformat(),
                    }
                }
                tomli_w.dump(result, update_toml_file)
            return None

    class Reader:
        def __init__(self, protostar_directory: ProtostarDirectory) -> None:
            self._protostar_directory = protostar_directory

        def read(self) -> Optional["UpgradeTOML"]:
            if not self._protostar_directory.upgrade_toml_path.exists():
                return None

            with open(
                self._protostar_directory.upgrade_toml_path, "rb"
            ) as update_toml_file:
                update_toml_dict = tomli.load(update_toml_file)

                return UpgradeTOML(
                    version=VersionManager.parse(update_toml_dict["info"]["version"]),
                    changelog_url=update_toml_dict["info"]["changelog_url"],
                    next_check_datetime=datetime.fromisoformat(
                        update_toml_dict["info"]["next_check_datetime"]
                    ),
                )
