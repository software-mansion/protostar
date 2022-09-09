from pathlib import Path
from typing import Any, Dict, Generic, Optional, TypeVar

import tomlkit
from tomlkit.items import InlineTable, Table

from .configuration_file import (
    ConfigurationFileContentBuilder,
    ConfigurationFileContentConfigurator,
)

ConfigurationTOMLContent = str


class ConfigurationTOMLContentBuilder(
    ConfigurationFileContentBuilder[ConfigurationTOMLContent]
):
    def __init__(self) -> None:
        self._doc = tomlkit.document()
        self._profile = tomlkit.table()

    def set_section(
        self,
        section_name: str,
        data: Dict[str, Any],
        profile_name: Optional[str] = None,
    ):
        table = self._map_data_to_table(data)

        if not profile_name:
            self._doc.add(key=section_name, item=table)
        else:
            self._doc.add(
                key=tomlkit.key(["profile", profile_name, section_name]),
                item=table,
            )

    def _map_data_to_table(self, data: Dict) -> Table:
        table = tomlkit.table()
        for key, value in data.items():
            if isinstance(value, Dict):
                table.add(key, self._map_data_to_inline_table(value))
            else:
                table.add(key, value)
        return table

    def _map_data_to_inline_table(self, data: Dict) -> InlineTable:
        inline_table = tomlkit.inline_table()
        for key, value in data.items():
            if isinstance(value, Dict):
                inline_table.add(key, self._map_data_to_inline_table(value))
            else:
                inline_table.add(key, value)
        return inline_table

    def build(self) -> ConfigurationTOMLContent:
        return tomlkit.dumps(self._doc)


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
        with open(filepath, "w", encoding="UTF-8") as file_handle:
            file_handle.write(content)
