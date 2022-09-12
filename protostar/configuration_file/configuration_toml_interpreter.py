from typing import Any, Dict, List, Optional

import flatdict
import tomli

from .configuration_file import ConfigurationFileInterpreter


class ConfigurationTOMLInterpreter(ConfigurationFileInterpreter):
    QualifiedSectionName = str

    def __init__(self, file_content: str):
        self._file_content = file_content

    def get_section(
        self,
        section_name: str,
        profile_name: Optional[str] = None,
        section_namespace: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:

        section_name = (
            f"{section_namespace}.{section_name}" if section_namespace else section_name
        )

        protostar_toml_dict = self._get_flat_dict_representation()

        if profile_name:
            section_name = f"profile.{profile_name}.{section_name}"

        if section_name not in protostar_toml_dict:
            return None

        return protostar_toml_dict[section_name]

    def _get_flat_dict_representation(self):
        protostar_toml_dict = tomli.loads(self._file_content)
        return flatdict.FlatDict(protostar_toml_dict, delimiter=".")

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
        attribute_name = (
            self._find_alternative_key(attribute_name, section) or attribute_name
        )
        if attribute_name in section:
            return section[attribute_name]
        return None

    def get_profile_names(self) -> List[str]:
        protostar_toml_dict = self._get_flat_dict_representation()
        section_names = list(protostar_toml_dict.keys())
        profile_section_names = [
            section_name
            for section_name in section_names
            if section_name.startswith("profile.")
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
