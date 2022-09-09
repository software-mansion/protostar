from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import flatdict
import tomli

from protostar.protostar_exception import ProtostarException


class ConfigurationTOMLReader:
    QualifiedSectionName = str

    def __init__(self, path: Path, ignore_attribute_casing: bool = False):
        self.path = path
        self._ignore_attribute_casing = ignore_attribute_casing
        self._cache: Optional[
            Dict[ConfigurationTOMLReader.QualifiedSectionName, Any]
        ] = None

    def get_filename(self) -> str:
        return self.path.name

    def get_section(
        self,
        section_name: str,
        profile_name: Optional[str] = None,
        section_namespace: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:

        section_name = (
            f"{section_namespace}.{section_name}" if section_namespace else section_name
        )

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
        section_namespace: Optional[str] = None,
    ) -> Optional[Any]:
        section = self.get_section(
            section_name, profile_name, section_namespace=section_namespace
        )
        if not section:
            return None
        if self._ignore_attribute_casing:
            attribute_name = (
                self._find_alternative_key(attribute_name, section) or attribute_name
            )
        if attribute_name in section:
            return section[attribute_name]
        return None

    def get_profile_names(self) -> List[str]:
        protostar_toml_dict = self._read_if_cache_miss()
        section_names = list(protostar_toml_dict.keys())
        profile_section_names = [
            section_name
            for section_name in section_names
            if section_name.startswith("profile")
        ]
        profile_names = [
            profile_section_name.split(".")[1]
            for profile_section_name in profile_section_names
        ]
        return profile_names

    @staticmethod
    def _find_alternative_key(base_key: str, raw_dict: Dict[str, Any]) -> Optional[str]:
        if base_key in raw_dict:
            return base_key

        underscored_variant = base_key.replace("-", "_")
        if underscored_variant in raw_dict:
            return underscored_variant

        dashed_variant = base_key.replace("_", "-")
        if dashed_variant in raw_dict:
            return dashed_variant

        return None

    def _read_if_cache_miss(self) -> Dict[str, Any]:
        if self._cache is not None:
            return self._cache

        if not self.path.is_file():
            raise NoProtostarProjectFoundException("`protostar.toml` not found")

        with open(self.path, "rb") as protostar_toml_file:
            protostar_toml_dict = tomli.load(protostar_toml_file)
            protostar_toml_flat_dict = cast(
                Dict[ConfigurationTOMLReader.QualifiedSectionName, Any],
                flatdict.FlatDict(protostar_toml_dict, delimiter="."),
            )

            self._cache = protostar_toml_flat_dict

            return protostar_toml_flat_dict


class NoProtostarProjectFoundException(ProtostarException):
    pass
