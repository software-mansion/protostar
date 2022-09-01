from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

from protostar.utils.protostar_directory import VersionManager, VersionType

from .configuration_file import (
    ConfigurationFile,
    PrimitiveTypesSupportedByConfigurationFile,
)
from .configuration_toml_reader import ConfigurationTOMLReader


@dataclass
class ConfigurationFileV2Model:
    pass


class ConfigurationFileV2(ConfigurationFile[ConfigurationFileV2Model]):
    def __init__(self, configuration_toml_reader: ConfigurationTOMLReader) -> None:
        super().__init__()
        self._configuration_toml_reader = configuration_toml_reader

    def get_min_protostar_version(self) -> Optional[VersionType]:
        version_str = self._configuration_toml_reader.get_attribute(
            section_name="project", attribute_name="min-protostar-version"
        )
        if not version_str:
            return None
        return VersionManager.parse(version_str)

    def get_contract_names(self) -> List[str]:
        ...

    def get_contract_source_paths(self, contract_name: str) -> List[Path]:
        ...

    def get_lib_path(self) -> Optional[Path]:
        ...

    def get_command_argument(
        self, command_name: str, argument_name: str, profile_name: Optional[str] = None
    ) -> Optional[
        Union[
            PrimitiveTypesSupportedByConfigurationFile,
            List[PrimitiveTypesSupportedByConfigurationFile],
        ]
    ]:
        ...

    def create_model(
        self,
    ) -> ConfigurationFileV2Model:
        ...

    def save(self, configuration_file_model: ConfigurationFileV2Model) -> Path:
        ...
