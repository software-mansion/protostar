from pathlib import Path
from typing import Dict, Optional

import tomli_w

from protostar.configuration_file.configuration_file import CommandConfig

ConfigurationTOMLContent = Dict


class ConfigurationTOMLContentBuilder:
    def __init__(self) -> None:
        self._content = {}

    def set_section(
        self,
        section_name: str,
        data: CommandConfig,
        profile_name: Optional[str] = None,
    ):
        section_name = (
            section_name
            if profile_name is None
            else f"profile.{profile_name}.{section_name}"
        )
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
