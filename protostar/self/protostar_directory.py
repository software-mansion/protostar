import json
import logging
import re
from pathlib import Path
from typing import Literal, Optional, Union

from packaging import version
from packaging.version import LegacyVersion
from packaging.version import Version as PackagingVersion

from protostar.git import Git, ProtostarGitException

from .protostar_compatibility_with_project_checker import (
    ProtostarVersion,
    parse_protostar_version,
)

RuntimeConstantName = Literal["PROTOSTAR_VERSION", "CAIRO_VERSION"]
RuntimeConstantValue = str
RuntimeConstantsDict = dict[RuntimeConstantName, RuntimeConstantValue]


class ProtostarDirectory:
    RUNTIME_CONSTANTS_FILE_NAME = "constants.json"

    def __init__(self, protostar_binary_dir_path: Path) -> None:
        self._protostar_binary_dir_path: Path = protostar_binary_dir_path
        self._runtime_constants = None

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

    def _read_runtime_constants(self) -> Optional[RuntimeConstantsDict]:
        constants_str = (
            self.info_dir_path / ProtostarDirectory.RUNTIME_CONSTANTS_FILE_NAME
        ).read_text("utf-8")
        return json.loads(constants_str)

    def get_runtime_constant(
        self, name: RuntimeConstantName
    ) -> Optional[RuntimeConstantValue]:
        if self._runtime_constants is None:
            try:
                self._runtime_constants = self._read_runtime_constants()
            except FileNotFoundError as ex:
                logging.getLogger().warning(
                    "Couldn't load constant `%s` from %s", name, ex.filename
                )
                return None

        if self._runtime_constants is None:
            return None
        return self._runtime_constants[name]


VersionType = Union[LegacyVersion, PackagingVersion]


class VersionManager:
    @staticmethod
    def parse(version_str: str) -> VersionType:
        return version.parse(version_str)

    def __init__(
        self, protostar_directory: ProtostarDirectory, logger: logging.Logger
    ) -> None:
        self._protostar_directory = protostar_directory
        self._pyproject_toml_dict = None
        self._logger = logger

    @property
    def protostar_version(self) -> ProtostarVersion:
        version_s = self._protostar_directory.get_runtime_constant("PROTOSTAR_VERSION")
        if version_s is None:
            return parse_protostar_version("0.0.0")
        return parse_protostar_version(version_s)

    @property
    def cairo_version(self) -> Optional[VersionType]:
        version_s = self._protostar_directory.get_runtime_constant("CAIRO_VERSION")
        if version_s is None:
            return VersionManager.parse("0.0.0")
        return VersionManager.parse(version_s)

    @property
    def git_version(self) -> Optional[VersionType]:
        try:
            output = Git.get_version()
            result = re.search(r"\d*\.\d*.\d*", output)
            if result:
                return version.parse(result.group())
        except ProtostarGitException:
            pass
        return None

    def print_current_version(self) -> None:
        print(f"Protostar version: {self.protostar_version or 'unknown'}")
        print(f"Cairo-lang version: {self.cairo_version or 'unknown'}")
