from pathlib import Path
from typing import Any, Dict, Optional, cast

import flatdict
import tomli

from protostar.protostar_toml.protostar_toml_exceptions import (
    NoProtostarProjectFoundException,
)


class ProtostarTOMLReader:
    FlattenSectionName = str
    """e.g. `profile.ci.protostar.shared_command_configs`"""

    def __init__(
        self,
        protostar_toml_path: Path,
    ):
        self.path = protostar_toml_path
        self._cache: Optional[Dict[ProtostarTOMLReader.FlattenSectionName, Any]] = None

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

        if alternative_attribute_name and alternative_attribute_name in section:
            return section[alternative_attribute_name]
        return None

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
            raise NoProtostarProjectFoundException(
                "No protostar.toml found in the working directory\n" f"{str(self.path)}"
            )

        with open(self.path, "rb") as protostar_toml_file:
            protostar_toml_dict = tomli.load(protostar_toml_file)
            protostar_toml_flat_dict = cast(
                Dict[ProtostarTOMLReader.FlattenSectionName, Any],
                flatdict.FlatDict(protostar_toml_dict, delimiter="."),
            )

            self._cache = protostar_toml_flat_dict

            return protostar_toml_flat_dict


def search_upwards_protostar_toml_path(start_path: Path) -> Optional[Path]:
    directory_path = start_path
    root_path = Path(directory_path.root)
    while directory_path != root_path:
        for file_path in directory_path.iterdir():
            if "protostar.toml" == file_path.name:
                return directory_path / "protostar.toml"

        directory_path = directory_path.parent
    return None
