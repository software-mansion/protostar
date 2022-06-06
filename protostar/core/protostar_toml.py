from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import flatdict
import tomli

from protostar.protostar_exception import ProtostarException
from protostar.utils.protostar_directory import VersionManager, VersionType


class NoProtostarProjectFoundException(ProtostarException):
    pass


class VersionNotSupportedException(ProtostarException):
    pass


class InvalidProtostarTOMLException(ProtostarException):
    def __init__(self, section_name: str):
        self.section_name = section_name
        super().__init__(section_name)

    def __str__(self) -> str:
        return "\n".join(
            [
                "Invalid 'protostar.toml' configuration.",
                f"Couldn't load [protostar.{self.section_name}]",
            ]
        )


ProtostarTOMLDict = Dict[str, Any]


class ProtostarTOML:
    @dataclass
    class ProtostarConfig:
        protostar_version: VersionType

        @classmethod
        def from_dict(cls, raw_dict: Dict[str, Any]) -> "ProtostarTOML.ProtostarConfig":
            return cls(
                protostar_version=VersionManager.parse(raw_dict["protostar_version"])
            )

    @dataclass
    class ProjectConfig:
        libs_path: Path

        @classmethod
        def from_dict(cls, raw_dict: Dict[str, Any]) -> "ProtostarTOML.ProjectConfig":
            return cls(libs_path=Path(raw_dict["libs_path"]))

    @dataclass
    class ContractsConfig:
        contract_dict: Dict[str, List[Path]]

        @classmethod
        def from_dict(
            cls, raw_dict: Optional[Dict[str, Any]]
        ) -> "ProtostarTOML.ContractsConfig":
            if not raw_dict:
                return cls(contract_dict={})

            contract_dict: Dict[str, List[Path]] = {}
            for contract_name, str_paths in raw_dict.items():
                contract_dict[contract_name] = [
                    Path(str_path) for str_path in str_paths
                ]
            return cls(contract_dict=contract_dict)

    @dataclass
    class CLIConfig:
        def __init__(self, protostar_toml: "ProtostarTOML"):
            self._protostar_toml = protostar_toml

        def get_attribute(
            self,
            section_name: str,
            attribute_name: str,
            profile_name: Optional[str] = None,
        ) -> Optional[Any]:
            return self._protostar_toml.get_attribute(
                section_name, attribute_name, profile_name
            )

    def __init__(
        self, version_manager: VersionManager, project_root: Optional[Path] = None
    ):
        self.project_root = project_root or Path()
        self.shared_command_configs_section_name = "shared_command_configs"
        self._version_manager = version_manager
        self._cache: Optional[Dict[str, Any]] = None

    @property
    def protostar_config(self) -> ProtostarConfig:
        config_section = self.get_section("config")
        if config_section is None:
            raise InvalidProtostarTOMLException("config")

        return ProtostarTOML.ProtostarConfig.from_dict(config_section)

    @property
    def project_config(self) -> ProjectConfig:
        project_section = self.get_section("project")
        if project_section is None:
            raise InvalidProtostarTOMLException("project")

        return ProtostarTOML.ProjectConfig.from_dict(project_section)

    @property
    def contracts_config(self) -> ContractsConfig:
        contracts_section = self.get_section("contracts")

        return ProtostarTOML.ContractsConfig.from_dict(contracts_section)

    @property
    def path(self) -> Path:
        return self.project_root / "protostar.toml"

    def get_section(
        self, section_name: str, profile_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        assert not section_name.startswith("protostar.")
        section_name = f"protostar.{section_name}"

        protostar_toml_dict = self._read_if_cache_miss()

        if profile_name:
            section_name = f"profile.{profile_name}.{section_name}"

        if section_name not in protostar_toml_dict:
            return None

        return protostar_toml_dict[section_name]

    def get_attribute(
        self,
        section_name: str,
        attribute_name: str,
        profile_name: Optional[str] = None,
    ) -> Optional[Any]:
        section = self.get_section(section_name, profile_name)
        if not section:
            return None

        if attribute_name not in section:
            attribute_name = attribute_name.replace("-", "_")
            if attribute_name not in section:
                return None

        return section[attribute_name]

    def _read_if_cache_miss(self) -> ProtostarTOMLDict:
        if self._cache:
            return self._cache

        if not self.path.is_file():
            raise NoProtostarProjectFoundException(
                "No protostar.toml found in the working directory"
            )

        with open(self.path, "rb") as protostar_toml:
            protostar_toml_dict = tomli.load(protostar_toml)
            flat_protostar_toml_dict = flatdict.FlatDict(
                protostar_toml_dict, delimiter="."
            ).as_dict()
            self._cache = flat_protostar_toml_dict

            return flat_protostar_toml_dict
