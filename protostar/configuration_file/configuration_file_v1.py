from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

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


@dataclass(frozen=True)
class ConfigurationFileV1Model:
    protostar_version: Optional[str]
    contract_name_to_path_str: dict[ContractName, str]
    lib_path_str: Optional[str]
    command_name_to_config: CommandNameToConfig
    shared_command_config: CommandConfig
    profile_name_to_commands_config: dict[ProfileName, CommandNameToConfig]
    profile_name_to_shared_command_config: dict[ProfileName, CommandConfig]


class ConfigurationFileV1(ConfigurationFile[ConfigurationFileV1Model]):
    def __init__(
        self,
        configuration_file_interpreter: ConfigurationFileInterpreter,
        project_root_path: Path,
        filename: str,
    ) -> None:
        super().__init__()
        self._configuration_file_interpreter = configuration_file_interpreter
        self._project_root_path = project_root_path
        self._filename = filename
        self._command_names = [
            "build",
            "init",
            "test",
            "deploy",
            "declare",
            "migrate",
        ]

    def get_min_protostar_version(self) -> Optional[VersionType]:
        version_str = self._configuration_file_interpreter.get_attribute(
            attribute_name="protostar_version",
            section_name="config",
            section_namespace="protostar",
        )
        if not version_str:
            return None
        return VersionManager.parse(version_str)

    def get_contract_names(self) -> list[str]:
        contract_section = self._configuration_file_interpreter.get_section(
            "contracts", section_namespace="protostar"
        )
        if not contract_section:
            return []
        return list(contract_section)

    def get_contract_source_paths(self, contract_name: str) -> list[Path]:
        contract_section = self._configuration_file_interpreter.get_section(
            "contracts", section_namespace="protostar"
        )
        if contract_section is None or contract_name not in contract_section:
            contracts_config_location = f'{self._filename}::["protostar.contracts"]'
            raise ContractNameNotFoundException(
                contract_name,
                expected_declaration_location=contracts_config_location,
            )
        return [
            self._project_root_path / Path(path_str)
            for path_str in contract_section[contract_name]
        ]

    def get_lib_path(self) -> Optional[Path]:
        lib_relative_path_str = self._configuration_file_interpreter.get_attribute(
            section_name="project",
            attribute_name="libs_path",
            section_namespace="protostar",
        )
        if not lib_relative_path_str:
            return None
        return self._project_root_path / lib_relative_path_str

    def get_command_argument(
        self, command_name: str, argument_name: str, profile_name: Optional[str] = None
    ) -> Optional[
        Union[
            PrimitiveTypesSupportedByConfigurationFile,
            list[PrimitiveTypesSupportedByConfigurationFile],
        ]
    ]:
        return self._configuration_file_interpreter.get_attribute(
            section_name=command_name,
            attribute_name=argument_name,
            profile_name=profile_name,
            section_namespace="protostar",
        )

    def read(
        self,
    ) -> ConfigurationFileV1Model:
        return ConfigurationFileV1Model(
            protostar_version=self._get_min_protostar_version_str(),
            lib_path_str=self._get_libs_path_str(),
            contract_name_to_path_str=self._get_contract_name_to_path_str(),
            command_name_to_config=self._get_command_name_to_config(),
            profile_name_to_commands_config=self._get_profile_name_to_commands_config(),
            shared_command_config=self._get_shared_command_config(),
            profile_name_to_shared_command_config=self._get_profile_name_to_shared_command_config(),
        )

    def _get_min_protostar_version_str(self) -> Optional[str]:
        version = self.get_min_protostar_version()
        if not version:
            return None
        return str(version)

    def _get_libs_path_str(self) -> Optional[str]:
        result: Optional[str] = None
        lib_path = self.get_lib_path()
        if lib_path:
            result = str(lib_path.relative_to(self._project_root_path))
        return result

    def _get_contract_name_to_path_str(self) -> dict[ContractName, str]:
        result = {}
        for contract_name in self.get_contract_names():
            result[contract_name] = self.get_contract_source_paths(contract_name)
        return result

    def _get_profile_name_to_commands_config(
        self,
    ) -> dict[ProfileName, CommandNameToConfig]:
        result: dict[ProfileName, CommandNameToConfig] = {}
        profile_names = self._configuration_file_interpreter.get_profile_names()
        for profile_name in profile_names:
            command_name_to_config = self._get_command_name_to_config(profile_name)
            if command_name_to_config:
                result[profile_name] = command_name_to_config
        return result

    def _get_command_name_to_config(
        self, profile_name: Optional[str] = None
    ) -> CommandNameToConfig:
        result: CommandNameToConfig = {}
        for command_name in self._command_names:
            command_config = self._configuration_file_interpreter.get_section(
                section_name=command_name,
                profile_name=profile_name,
                section_namespace="protostar",
            )
            if command_config:
                result[command_name] = command_config
        return result

    def _get_profile_name_to_shared_command_config(
        self,
    ) -> dict[ProfileName, CommandConfig]:
        result: dict[ProfileName, CommandConfig] = {}
        profile_names = self._configuration_file_interpreter.get_profile_names()
        for profile_name in profile_names:
            shared_command_config = self._get_shared_command_config(profile_name)
            if shared_command_config:
                result[profile_name] = shared_command_config
        return result

    def _get_shared_command_config(
        self, profile_name: Optional[str] = None
    ) -> CommandConfig:
        return (
            self._configuration_file_interpreter.get_section(
                "shared_command_configs",
                profile_name=profile_name,
                section_namespace="protostar",
            )
            or {}
        )
