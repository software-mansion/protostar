import re
from logging import getLogger
from pathlib import Path
from typing import List, Optional, Union

import tomli
from git.cmd import Git
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

    def add_protostar_cairo_dir(self, cairo_paths: List[Path]) -> List[Path]:
        if self.protostar_binary_dir_path:
            protostar_cairo_dir = self.protostar_binary_dir_path / "cairo"
            if protostar_cairo_dir not in cairo_paths:
                cairo_paths.append(protostar_cairo_dir)
        return cairo_paths


VersionType = Union[LegacyVersion, PackagingVersion]


class VersionManager:
    @staticmethod
    def parse(version_str: str) -> VersionType:
        return version.parse(version_str)

    def __init__(self, protostar_directory: ProtostarDirectory) -> None:
        self._protostar_directory = protostar_directory

    @property
    def protostar_version(self) -> Optional[VersionType]:
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
            getLogger().warning("Couldn't read Protostar version")
            return None

    @property
    def cairo_version(self) -> Optional[VersionType]:
        path = (
            self._protostar_directory.directory_root_path
            / "dist"
            / "protostar"
            / "info"
            / "pyproject.toml"
        )
        try:
            with open(path, "r", encoding="UTF-8") as file:
                version_s = tomli.loads(file.read())["tool"]["poetry"]["dependencies"][
                    "cairo-lang"
                ]
                return VersionManager.parse(version_s)
        except FileNotFoundError:
            getLogger().warning("Couldn't read cairo-lang version")
            return None

    @property
    def git_version(self) -> Optional[VersionType]:
        output = Git().execute(["git", "--version"])
        # pylint: disable=unidiomatic-typecheck
        if type(output) is str:
            result = re.search(r"\d*\.\d*.\d*", output)
            if result:
                return version.parse(result.group())
        return None

    def print_current_version(self) -> None:
        print(f"Protostar version: {self.protostar_version or 'unknown'}")
        print(f"Cairo-lang version: {self.cairo_version or 'unknown'}")
