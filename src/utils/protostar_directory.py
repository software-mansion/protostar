from mimetypes import init
from typing import Union
import os.path
import shutil
from pathlib import Path
from typing import Optional
import tomli
from packaging import version
from packaging.version import LegacyVersion, Version as PackagingVersion


class ProtostarDirectory:
    def __init__(self) -> None:
        self._protostar_binary_dir: Optional[Path] = None
        self._protostar_root_dir: Optional[Path] = None

    @property
    def protostar_binary_dir_path(self) -> Optional[Path]:
        if self._protostar_binary_dir:
            return self._protostar_binary_dir

        protostar_path = shutil.which("protostar")
        if protostar_path:
            self._protostar_binary_dir = Path(os.path.split(protostar_path)[0])

        return self._protostar_binary_dir

    @property
    def directory_root_path(self) -> Path:
        protostar_binary_dir = self.protostar_binary_dir_path
        self._protostar_root_dir = (
            protostar_binary_dir / ".." / ".."
            if protostar_binary_dir
            else Path.home() / ".protostar"
        )
        return self._protostar_root_dir


class VersionManager:
    VersionType = Union[LegacyVersion, PackagingVersion]

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
        with open(path, "r", encoding="UTF-8") as file:
            version_s = tomli.loads(file.read())["tool"]["poetry"]["version"]
            return VersionManager.parse(version_s)

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
