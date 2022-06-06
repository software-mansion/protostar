from pathlib import Path
from typing import Any, Dict, Optional

import flatdict
import tomli

from protostar.protostar_toml.protostar_toml_exceptions import \
    NoProtostarProjectFoundException
from protostar.utils.protostar_directory import VersionManager


class ProtostarTOMLReader:
    def __init__(
        self,
        version_manager: VersionManager,
        protostar_toml_path: Optional[Path] = None,
    ):
        self.path = protostar_toml_path or Path() / "protostar.toml"
        self._version_manager = version_manager
        self._cache: Optional[Dict[str, Any]] = None

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

    def _read_if_cache_miss(self) -> Dict[str, Any]:
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
