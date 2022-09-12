from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union

from protostar.utils.protostar_directory import VersionManager, VersionType

from .configuration_file import (
    CommandConfig,
    CommandNameToConfig,
    ConfigurationFile,
    ContractName,
    ContractNameNotFoundException,
    PrimitiveTypesSupportedByConfigurationFile,
    ProfileName,
)
from .configuration_file_interpreter import ConfigurationFileInterpreter


@dataclass
class ConfigurationFileV2Model:
    min_protostar_version: Optional[str]
    contract_name_to_path_str: Dict[ContractName, str]
    project_config: CommandConfig
    command_name_to_config: CommandNameToConfig
    profile_name_to_project_config: Dict[ProfileName, CommandConfig]
    profile_name_to_commands_config: Dict[ProfileName, CommandNameToConfig]


class ConfigurationFileV2(ConfigurationFile[ConfigurationFileV2Model]):
    def __init__(
        self,
        project_root_path: Path,
        configuration_file_reader: ConfigurationFileInterpreter,
        filename: str,
    ) -> None:
        super().__init__()
        self._project_root_path = project_root_path
        self._configuration_file_reader = configuration_file_reader
        self._filename = filename

    def get_min_protostar_version(self) -> Optional[VersionType]:
        version_str = self._configuration_file_reader.get_attribute(
            attribute_name="min-protostar-version", section_name="project"
        )
        if not version_str:
            return None
        return VersionManager.parse(version_str)

    def get_contract_names(self) -> List[str]:
        contract_section = self._configuration_file_reader.get_section("contracts")
        if not contract_section:
            return []
        return list(contract_section)

    def get_contract_source_paths(self, contract_name: str) -> List[Path]:
        contract_section = self._configuration_file_reader.get_section("contracts")
        if contract_section is None or contract_name not in contract_section:
            raise ContractNameNotFoundException(
                contract_name,
                expected_declaration_location=f"{self._filename}::[contracts]",
            )
        return [
            self._project_root_path / Path(path_str)
            for path_str in contract_section[contract_name]
        ]

    def get_lib_path(self) -> Optional[Path]:
        lib_relative_path_str = self._configuration_file_reader.get_attribute(
            section_name="project", attribute_name="libs_path"
        )
        if not lib_relative_path_str:
            return None
        return self._project_root_path / lib_relative_path_str

    def get_command_argument(
        self, command_name: str, argument_name: str, profile_name: Optional[str] = None
    ) -> Optional[
        Union[
            PrimitiveTypesSupportedByConfigurationFile,
            List[PrimitiveTypesSupportedByConfigurationFile],
        ]
    ]:
        return self._configuration_file_reader.get_attribute(
            section_name=command_name,
            attribute_name=argument_name,
            profile_name=profile_name,
        )

    def read(
        self,
    ) -> ConfigurationFileV2Model:
        raise NotImplementedError("Operation not supported.")
