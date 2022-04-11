from logging import getLogger
from pathlib import Path
from typing import Optional, Union

import tomli
from packaging import version
from packaging.version import LegacyVersion
from packaging.version import Version as PackagingVersion


class ProtostarDirectory:
    def __init__(self, protostar_binary_dir_path: Path) -> None:
        self._protostar_binary_dir_path: Path = protostar_binary_dir_path

    @property
    def protostar_binary_dir_path(self) -> Optional[Path]:
        return self._protostar_binary_dir_path

    @property
    def directory_root_path(self) -> Path:
        return self._protostar_binary_dir_path / ".." / ".."


VersionType = Union[LegacyVersion, PackagingVersion]


class VersionManager:
    @staticmethod
    def parse(version_str: str) -> VersionType:
        return version.parse(version_str)

    def __init__(self, protostar_directory: ProtostarDirectory) -> None:
        self._protostar_directory = protostar_directory

    @property
    def protostar_version(self) -> VersionType:
        path = (
            self._protostar_directory.directory_root_path
            / "dist"
            / "protostar"
            / "info"
            / "pyproject.toml"
        )
        try:
            with open(path, "r", encoding="UTF-8") as file:
                version_s = tomli.loads(file.read())["tool"]["poetry"]["version"]
                return VersionManager.parse(version_s)
        except FileNotFoundError:
            getLogger().warning("Couldn't read Protostar version.")
            return VersionManager.parse("0.0.0")

    @property
    def cairo_version(self) -> VersionType:
        path = (
            self._protostar_directory.directory_root_path
            / "dist"
            / "protostar"
            / "info"
            / "pyproject.toml"
        )
        with open(path, "r", encoding="UTF-8") as file:
            version_s = tomli.loads(file.read())["tool"]["poetry"]["dependencies"][
                "cairo-lang"
            ]
            return VersionManager.parse(version_s)

    def print_current_version(self) -> None:
        print(f"Protostar version: {self.protostar_version}")
        print(f"Cairo-lang version: {self.cairo_version}")
