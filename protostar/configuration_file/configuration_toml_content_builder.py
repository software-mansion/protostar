from typing import Any, Optional

import tomlkit
from tomlkit.items import InlineTable, Table

from .configuration_file import ConfigurationFileContentBuilder


class ConfigurationTOMLContentBuilder(ConfigurationFileContentBuilder):
    def __init__(self) -> None:
        self._doc = tomlkit.document()
        self._profiles_table = tomlkit.table(is_super_table=True)
        self._profile_name_profile_table: dict[str, Table] = {}

    def set_section(
        self,
        section_name: str,
        data: dict[str, Any],
        profile_name: Optional[str] = None,
    ):
        table = self._map_data_to_table(data)

        if not profile_name:
            self._doc.add(key=section_name, item=table)
        else:
            profile_table = self._create_profile_table(profile_name)
            profile_table.add(
                key=section_name,
                value=table,
            )

    def _create_profile_table(self, profile_name: str) -> Table:
        if profile_name in self._profile_name_profile_table:
            return self._profile_name_profile_table[profile_name]
        profile_table = tomlkit.table(is_super_table=True)
        self._profile_name_profile_table[profile_name] = profile_table
        self._profiles_table.add(profile_name, profile_table)
        return profile_table

    def _map_data_to_table(self, data: dict) -> Table:
        table = tomlkit.table()
        for key, value in data.items():
            if isinstance(value, dict):
                table.add(key, self._map_data_to_inline_table(value))
            else:
                table.add(key, value)
        return table

    def _map_data_to_inline_table(self, data: dict) -> InlineTable:
        inline_table = tomlkit.inline_table()
        for key, value in data.items():
            if isinstance(value, dict):
                inline_table.add(key, self._map_data_to_inline_table(value))
            else:
                inline_table.add(key, value)
        return inline_table

    def build(self) -> str:
        self._doc.add("profile", self._profiles_table)
        return tomlkit.dumps(self._doc)
