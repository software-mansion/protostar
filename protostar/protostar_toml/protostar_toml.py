from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Optional

import flatdict
import tomli
import tomli_w

from protostar.protostar_toml.protostar_toml_exceptions import (
    InvalidProtostarTOMLException,
    NoProtostarProjectFoundException,
)
from protostar.protostar_toml.sections import (
    ProtostarConfig,
    ProtostarContracts,
    ProtostarProject,
    ProtostarTOMLSection,
)
from protostar.utils.protostar_directory import VersionManager

ProtostarTOMLDict = Dict[str, Any]


class ProtostarTOML:
    def __init__(
        self,
        version_manager: VersionManager,
        protostar_toml_path: Optional[Path] = None,
    ):
        self.path = protostar_toml_path or Path() / "protostar.toml"
        self._version_manager = version_manager
        self._cache: Optional[Dict[str, Any]] = None

    @property
    def protostar_config(self) -> ProtostarConfig:
        config_section = self.get_section(ProtostarConfig.get_name())
        if config_section is None:
            raise InvalidProtostarTOMLException(ProtostarConfig.get_name())
        return ProtostarConfig.from_dict(config_section)

    @property
    def protostar_project(self) -> ProtostarProject:
        project_section = self.get_section(ProtostarProject.get_name())
        if project_section is None:
            raise InvalidProtostarTOMLException(ProtostarProject.get_name())
        return ProtostarProject.from_dict(project_section)

    @property
    def contracts_config(self) -> ProtostarContracts:
        return ProtostarContracts.from_dict(
            self.get_section(ProtostarContracts.get_name())
        )

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

    def save(
        self,
        protostar_config: ProtostarConfig,
        protostar_project: ProtostarProject,
        protostar_contracts: ProtostarContracts,
    ) -> None:
        result = OrderedDict()

        sections: List[ProtostarTOMLSection] = [
            protostar_config,
            protostar_project,
            protostar_contracts,
        ]

        for section in sections:
            result[section.get_name()] = section.to_dict()

        with open(self.path, "wb") as protostar_toml_file:
            tomli_w.dump(result, protostar_toml_file)

    def _read_if_cache_miss(self) -> ProtostarTOMLDict:
        if self._cache:
            return self._cache

        if not self.path.is_file():
            raise NoProtostarProjectFoundException(
                "No protostar.toml found in the working directory"
            )

        with open(self.path, "rb") as protostar_toml_file:
            protostar_toml_dict = tomli.load(protostar_toml_file)
            flat_protostar_toml_dict = flatdict.FlatDict(
                protostar_toml_dict, delimiter="."
            ).as_dict()
            self._cache = flat_protostar_toml_dict

            return flat_protostar_toml_dict
