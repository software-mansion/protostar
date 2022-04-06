from typing import Union, Optional
from pathlib import Path

import os.path
import shutil
import tomli

from packaging import version
from packaging.version import LegacyVersion, Version as PackagingVersion
from src.protostar_exception import ProtostarException


class ProtostarDirectory:
    class ProtostarNotInstalledException(ProtostarException):
        def __init__(self):
            super().__init__(
                "Couldn't find the protostar binary\n"
                "Did you add the protostar binary to the $PATH variable?"
            )

    def __init__(self) -> None:
        self._protostar_binary_dir: Optional[Path] = None
        self._protostar_root_dir: Optional[Path] = None

    @property
    def protostar_binary_dir_path(self) -> Optional[Path]:
        if self._protostar_binary_dir:
            return self._protostar_binary_dir

        protostar_path = shutil.which("protostar")
        if protostar_path is None:
            raise ProtostarDirectory.ProtostarNotInstalledException()

        self._protostar_binary_dir = Path(os.path.split(protostar_path)[0])

        return self._protostar_binary_dir

    @property
    def directory_root_path(self) -> Path:
        protostar_binary_dir = self.protostar_binary_dir_path

        assert protostar_binary_dir is not None

        self._protostar_root_dir = protostar_binary_dir / ".." / ".."
        return self._protostar_root_dir


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
