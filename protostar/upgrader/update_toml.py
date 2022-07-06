from dataclasses import dataclass
from typing import Optional

import tomli
import tomli_w

from protostar.utils.protostar_directory import (ProtostarDirectory,
                                                 VersionManager, VersionType)


@dataclass
class UpdateTOML:
    version: VersionType
    changelog_url: str

    class Writer:
        def __init__(self, protostar_directory: ProtostarDirectory) -> None:
            self._protostar_directory = protostar_directory

        def save(self, update_toml: "UpdateTOML"):
            with open(
                self._protostar_directory.update_toml_path, "wb"
            ) as update_toml_file:
                result = {
                    "info": {
                        "version": str(update_toml.version),
                        "changelog_url": update_toml.changelog_url,
                    }
                }
                tomli_w.dump(result, update_toml_file)

    class Reader:
        def __init__(self, protostar_directory: ProtostarDirectory) -> None:
            self._protostar_directory = protostar_directory

        def read(self) -> Optional["UpdateTOML"]:
            if not self._protostar_directory.update_toml_path.exists():
                return None

            with open(
                self._protostar_directory.update_toml_path, "rb"
            ) as update_toml_file:
                update_toml_dict = tomli.load(update_toml_file)

                return UpdateTOML(
                    version=VersionManager.parse(update_toml_dict["info"]["version"]),
                    changelog_url=update_toml_dict["info"]["changelog_url"],
                )
