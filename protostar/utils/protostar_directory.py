import re
from pathlib import Path
from typing import Optional, Union, List

import tomli
from git.cmd import Git
from packaging import version
from packaging.version import LegacyVersion
from packaging.version import Version as PackagingVersion

from protostar.protostar_exception import ProtostarException


class ProtostarDirectory:
    def __init__(self, protostar_binary_dir_path: Path) -> None:
        self._protostar_binary_dir_path: Path = protostar_binary_dir_path

    @property
    def protostar_binary_dir_path(self) -> Optional[Path]:
        return self._protostar_binary_dir_path

    @property
    def directory_root_path(self) -> Path:
        return self._protostar_binary_dir_path.parent.parent.resolve()

    @property
    def info_dir_path(self) -> Path:
        return self.directory_root_path / "dist" / "protostar" / "info"

    @property
    def latest_version_cache_path(self) -> Path:
        return self.info_dir_path / "latest_version_cache.toml"

    @property
    def protostar_test_only_cairo_packages_path(self) -> Path:
        assert self.protostar_binary_dir_path is not None
        return self.protostar_binary_dir_path / "cairo"


VersionType = Union[LegacyVersion, PackagingVersion]


class VersionManager:
    @staticmethod
    def parse(version_str: str) -> VersionType:
        return version.parse(version_str)

    def __init__(self, protostar_directory: ProtostarDirectory) -> None:
        self._protostar_directory = protostar_directory
        self._pyproject_toml_dict = None

    @property
    def pyproject_toml(self) -> dict:
        if self._pyproject_toml_dict:
            return self._pyproject_toml_dict

        path = (
            self._protostar_directory.directory_root_path
            / "dist"
            / "protostar"
            / "info"
            / "pyproject.toml"
        )
        try:
            with open(path, "r", encoding="UTF-8") as file:
                self._pyproject_toml_dict = tomli.loads(file.read())
                return self._pyproject_toml_dict
        except FileNotFoundError as err:
            raise ProtostarException("Couldn't read Protostar version") from err

    @property
    def protostar_version(self) -> VersionType:
        version_s = self.pyproject_toml["tool"]["poetry"]["version"]
        return VersionManager.parse(version_s)

    @property
    def cairo_version(self) -> VersionType:
        version_s = self.pyproject_toml["tool"]["poetry"]["dependencies"]["cairo-lang"]
        return VersionManager.parse(version_s)

    @property
    def breaking_versions(self) -> List[VersionType]:
        return [
            VersionManager.parse(v)
            for v in self.pyproject_toml["tool"]["protostar"]["breaking_versions"]
        ]

    def version_range_has_breaking_changes(self, low: VersionType, high: VersionType):
        for breaking_v in self.breaking_versions:
            if low <= breaking_v <= high:
                return True
        return False

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
