from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

from protostar.protostar_toml.io.protostar_toml_reader import ProtostarTOMLReader
from protostar.utils.protostar_directory import VersionType

from .configuration_file import (
    ConfigurationFile,
    PrimitiveTypesSupportedByConfigurationFile,
)


@dataclass
class ConfigurationFileV2Model:
    pass


class ConfigurationFileV2(ConfigurationFile[ConfigurationFileV2Model]):
    def __init__(self, protostar_toml_reader: ProtostarTOMLReader) -> None:
        super().__init__()
        self._protostar_toml_reader = protostar_toml_reader

    def get_min_protostar_version(self) -> Optional[VersionType]:
        self._protostar_toml_reader.get_attribute(
            section_name="project", attribute_name="min-protostar-version"
        )

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
