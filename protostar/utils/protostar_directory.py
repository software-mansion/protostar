import json
import logging
import re
from pathlib import Path
from typing import Optional, Literal, Union

from git import Git
from packaging import version

from packaging.version import LegacyVersion, Version as PackagingVersion

RuntimeConstant = Literal["PROTOSTAR_VERSION", "CAIRO_VERSION"]


class ProtostarDirectory:
    RUNTIME_CONSTANTS_FILE_NAME = "runtime_constant_values.json"

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

    def _load_runtime_constants(self):
        if self._runtime_constants is None:
            with open(
                file=self.info_dir_path
                / ProtostarDirectory.RUNTIME_CONSTANTS_FILE_NAME,
                mode="r",
                encoding="utf-8",
            ) as constants_file:
                self._runtime_constants = json.load(constants_file)

                # Provides safety, for ignoring the type
                assert self._runtime_constants is not None, "Could not load runtime constants"

    def get_runtime_constant(self, name: RuntimeConstant) -> str:
        if self._runtime_constants is None:
            self._load_runtime_constants()
        return self._runtime_constants[name]  # pyright: ignore


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
    def protostar_version(self) -> Optional[VersionType]:
        version_s = self._protostar_directory.get_runtime_constant("PROTOSTAR_VERSION")
        return VersionManager.parse(version_s)

    @property
    def cairo_version(self) -> Optional[VersionType]:
        version_s = self._protostar_directory.get_runtime_constant("CAIRO_VERSION")
        return VersionManager.parse(version_s)

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
