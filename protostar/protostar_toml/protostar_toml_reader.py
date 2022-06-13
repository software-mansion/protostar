from pathlib import Path
from typing import Any, Dict, Optional, cast

import flatdict
import tomli

from protostar.protostar_toml.protostar_toml_exceptions import (
    NoProtostarProjectFoundException,
)


class ProtostarTOMLReader:
    FlatSectionName = str

    def __init__(
        self,
        protostar_toml_path: Optional[Path] = None,
    ):
        self.path = protostar_toml_path or Path() / "protostar.toml"
        self._cache: Optional[Dict[ProtostarTOMLReader.FlatSectionName, Any]] = None

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

        alternative_attribute_name = self._find_alternative_key(attribute_name, section)

        if alternative_attribute_name in section:
            return section[alternative_attribute_name]
        return None

    # pylint: disable=no-self-use
    def _find_alternative_key(
        self, base_key: str, raw_dict: Dict[str, Any]
    ) -> Optional[str]:
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
            raise NoProtostarProjectFoundException(
                "No protostar.toml found in the working directory"
            )

        with open(self.path, "rb") as protostar_toml_file:
            protostar_toml_dict = tomli.load(protostar_toml_file)
            protostar_toml_flat_dict = cast(
                Dict[ProtostarTOMLReader.FlatSectionName, Any],
                flatdict.FlatDict(protostar_toml_dict, delimiter="."),
            )

            self._cache = protostar_toml_flat_dict

            return protostar_toml_flat_dict
