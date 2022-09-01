from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union

from typing_extensions import Self

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
from .configuration_file_v1 import ConfigurationFileV1Model
from .configuration_toml_reader import ConfigurationTOMLReader
from .configuration_toml_writer import ConfigurationTOMLWriter


@dataclass
class ConfigurationFileV2Model:
    min_protostar_version: Optional[str]
    contract_name_to_path_strs: Dict[ContractName, List[str]]
    project_config: CommandConfig
    command_name_to_config: CommandNameToConfig
    profile_name_to_project_config: Dict[ProfileName, CommandConfig]
    profile_name_to_commands_config: Dict[ProfileName, CommandNameToConfig]

    @classmethod
    # pylint: disable=invalid-name
    def from_v1(cls, v1: ConfigurationFileV1Model, min_protostar_version: str) -> Self:
        project_config = v1.shared_command_config
        if v1.libs_path_str:
            project_config["libs-path"] = v1.libs_path_str
        return cls(
            min_protostar_version=min_protostar_version,
            contract_name_to_path_strs=v1.contract_name_to_path_strs,
            command_name_to_config=v1.command_name_to_config,
            profile_name_to_commands_config=v1.profile_name_to_commands_config,
            project_config=project_config,
            profile_name_to_project_config=v1.profile_name_to_shared_command_config,
        )


class ConfigurationFileV2(ConfigurationFile[ConfigurationFileV2Model]):
    def __init__(
        self,
        project_root_path: Path,
        configuration_toml_reader: ConfigurationTOMLReader,
        configuration_toml_writer: ConfigurationTOMLWriter,
    ) -> None:
        super().__init__()
        self._project_root_path = project_root_path
        self._configuration_toml_reader = configuration_toml_reader
        self._configuration_toml_writer = configuration_toml_writer

    def get_min_protostar_version(self) -> Optional[VersionType]:
        version_str = self._configuration_toml_reader.get_attribute(
            attribute_name="min-protostar-version", section_name="project"
        )
        if not version_str:
            return None
        return VersionManager.parse(version_str)

    def get_contract_names(self) -> List[str]:
        contract_section = self._configuration_toml_reader.get_section("contracts")
        if not contract_section:
            return []
        return list(contract_section)

    def get_contract_source_paths(self, contract_name: str) -> List[Path]:
        contract_section = self._configuration_toml_reader.get_section("contracts")
        if contract_section is None or contract_name not in contract_section:
            raise ContractNameNotFoundException(
                contract_name,
                expected_declaration_location=f"{self._configuration_toml_reader.get_filename()}::[contracts]",
            )
        return [
            self._project_root_path / Path(path_str)
            for path_str in contract_section[contract_name]
        ]

    def get_lib_path(self) -> Optional[Path]:
        lib_relative_path_str = self._configuration_toml_reader.get_attribute(
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
        return self._configuration_toml_reader.get_attribute(
            section_name=command_name,
            attribute_name=argument_name,
            profile_name=profile_name,
        )

    def create_model(
        self,
    ) -> ConfigurationFileV2Model:
        assert False, "Operation not supported"

    def save(self, model: ConfigurationFileV2Model) -> Path:
        content_builder = self._configuration_toml_writer.create_content_builder()
        content_builder.set_section(
            section_name="project", data=self._prepare_project_section_data(model)
        )
        content_builder.set_section(
            section_name="contracts", data=model.contract_name_to_path_strs
        )
        for command_name, command_config in model.command_name_to_config.items():
            content_builder.set_section(section_name=command_name, data=command_config)
        for (
            profile_name,
            project_config,
        ) in model.profile_name_to_project_config.items():
            content_builder.set_section(
                profile_name=profile_name, section_name="project", data=project_config
            )
        for (
            profile_name,
            command_name_to_config,
        ) in model.profile_name_to_commands_config.items():
            for command_name, command_config in command_name_to_config.items():
                content_builder.set_section(
                    profile_name=profile_name,
                    section_name=command_name,
                    data=command_config,
                )
        content = content_builder.build()
        return self._configuration_toml_writer.save(content)

    @staticmethod
    def _prepare_project_section_data(model: ConfigurationFileV2Model) -> Dict:
        project_config_section = {}
        project_config_section["min-protostar-version"] = str(
            model.min_protostar_version
        )
        project_config_section: Dict = {
            **project_config_section,
            **model.project_config,
        }

        return project_config_section
