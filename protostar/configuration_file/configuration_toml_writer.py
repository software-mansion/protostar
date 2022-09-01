from pathlib import Path
from typing import Any, Dict, Optional

import tomli_w

ConfigurationTOMLContent = Dict


class ConfigurationTOMLContentBuilder:
    def __init__(self) -> None:
        self._content = {}

    def set_section(
        self,
        section_name: str,
        data: Dict[str, Any],
        profile_name: Optional[str] = None,
    ):
        if profile_name:
            if "profile" not in self._content:
                self._content["profile"] = {}
            if profile_name not in self._content["profile"]:
                self._content["profile"][profile_name] = {}
            if section_name not in self._content["profile"][profile_name]:
                self._content["profile"][profile_name][section_name] = data
        else:
            self._content[section_name] = data

    def build(self) -> ConfigurationTOMLContent:
        return self._content


class ConfigurationTOMLWriter:
    def __init__(self, output_file_path: Path) -> None:
        self._output_file_path = output_file_path

    @staticmethod
    def create_content_builder() -> ConfigurationTOMLContentBuilder:
        return ConfigurationTOMLContentBuilder()

    def save(self, content: ConfigurationTOMLContent) -> Path:
        with open(self._output_file_path, "wb") as file_handle:
            tomli_w.dump(content, file_handle)
        return self._output_file_path
