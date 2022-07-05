from dataclasses import dataclass
from typing import Optional

import tomli
import tomli_w

from protostar.utils.protostar_directory import ProtostarDirectory, VersionType


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
