from typing import Any, Dict, List, Optional

import tomlkit
from tomlkit.toml_document import TOMLDocument

from .configuration_file_interpreter import ConfigurationFileInterpreter


class ConfigurationTOMLInterpreter(ConfigurationFileInterpreter):
    def __init__(self, file_content: str) -> None:
        super().__init__()
        self._content = file_content

    def get_section(
        self,
        section_name: str,
        profile_name: Optional[str] = None,
        section_namespace: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        doc = self._get_doc()
        section_parent = self._get_section_parent(
            dct=doc.value,
            profile_name=profile_name,
            section_namespace=section_namespace,
        )
        if not section_parent:
            return None
        if section_name not in section_parent:
            return None
        return section_parent[section_name]

    def _get_doc(self) -> TOMLDocument:
        return tomlkit.loads(self._content)

    @staticmethod
    def _get_section_parent(
        dct: Dict,
        profile_name: Optional[str] = None,
        section_namespace: Optional[str] = None,
    ) -> Optional[Dict]:
        section_parent = dct
        if profile_name is not None:
            if "profile" not in dct:
                return None
            if profile_name in dct["profile"]:
                section_parent = dct["profile"][profile_name]
        if section_namespace in section_parent:
            section_parent = section_parent[section_namespace]
        return section_parent

    def get_attribute(
        self,
        section_name: str,
        attribute_name: str,
        profile_name: Optional[str] = None,
        section_namespace: Optional[str] = None,
    ) -> Optional[Any]:
        section = self.get_section(
            section_name=section_name,
            profile_name=profile_name,
            section_namespace=section_namespace,
        )
        if section is None:
            return None
        if attribute_name not in section:
            return None
        return section[attribute_name]

    def get_profile_names(self) -> List[str]:
        doc = self._get_doc()
        dct = doc.value
        if "profile" not in dct:
            return []
        profile_dct = dct["profile"]
        if not isinstance(profile_dct, Dict):
            return []
        return list(profile_dct)
