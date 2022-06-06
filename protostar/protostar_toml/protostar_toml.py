from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import flatdict
import tomli

from protostar.protostar_toml.protostar_toml_exceptions import (
    InvalidProtostarTOMLException,
    NoProtostarProjectFoundException,
)
from protostar.protostar_toml.sections import (
    ProtostarConfig,
    ProtostarContracts,
    ProtostarProject,
)
from protostar.utils.protostar_directory import VersionManager

ProtostarTOMLDict = Dict[str, Any]


class ProtostarTOML:
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
        self._version_manager = version_manager
        self._cache: Optional[Dict[str, Any]] = None

    @property
    def protostar_config(self) -> ProtostarConfig:
        config_section = self.get_section("config")
        if config_section is None:
            raise InvalidProtostarTOMLException("config")
        return ProtostarConfig.from_dict(config_section)

    @property
    def protostar_project(self) -> ProtostarProject:
        project_section = self.get_section("project")
        if project_section is None:
            raise InvalidProtostarTOMLException("project")
        return ProtostarProject.from_dict(project_section)

    @property
    def contracts_config(self) -> ProtostarContracts:
        contracts_section = self.get_section("contracts")
        return ProtostarContracts.from_dict(contracts_section)

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
