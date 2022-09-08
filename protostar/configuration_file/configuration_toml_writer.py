from pathlib import Path
from typing import Any, Dict, Generic, Optional, TypeVar

import tomli_w

from .configuration_file import (
    ConfigurationFileContentBuilder,
    ConfigurationFileContentConfigurator,
)

ConfigurationTOMLContent = Dict


class ConfigurationTOMLContentBuilder(
    ConfigurationFileContentBuilder[ConfigurationTOMLContent]
):
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


ConfigurationFileModelT = TypeVar("ConfigurationFileModelT")


class ConfigurationTOMLWriter(Generic[ConfigurationFileModelT]):
    def __init__(
        self,
        content_configurator: ConfigurationFileContentConfigurator[
            ConfigurationFileModelT
        ],
    ) -> None:
        self._content_configurator = content_configurator

    def save(
        self, configuration_model: ConfigurationFileModelT, filepath: Path
    ) -> None:
        content_builder = ConfigurationTOMLContentBuilder()
        content = self._content_configurator.create_file_content(
            content_builder, configuration_model
        )
        with open(filepath, "wb") as file_handle:
            tomli_w.dump(content, file_handle)
