from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from typing_extensions import Self

from protostar.self import ProtostarVersion, parse_protostar_version

from .configuration_file import (
    CommandConfig,
    CommandNameToConfig,
    ConfigurationFileContentBuilder,
    ConfigurationFileContentConfigurator,
    ConfigurationFileFacade,
    ContractName,
    ContractNameNotFoundException,
    PrimitiveTypesSupportedByConfigurationFile,
    ProfileName,
)
from .configuration_file_interpreter import ConfigurationFileInterpreter
from .configuration_file_v1 import ConfigurationFileV1


@dataclass
class ConfigurationFileV2:
    protostar_version: Optional[str]
    contract_name_to_path_strs: dict[ContractName, list[str]]
    project_config: CommandConfig
    command_name_to_config: CommandNameToConfig
    profile_name_to_project_config: dict[ProfileName, CommandConfig]
    profile_name_to_commands_config: dict[ProfileName, CommandNameToConfig]

    @classmethod
    # pylint: disable=invalid-name
    def from_v1(cls, v1: ConfigurationFileV1, protostar_version: str) -> Self:
        project_config = v1.shared_command_config
        if v1.libs_path_str:
            project_config = {
                **{"lib-path": v1.libs_path_str},
                **v1.shared_command_config,
            }
        return cls(
            protostar_version=protostar_version,
            contract_name_to_path_strs=v1.contract_name_to_path_strs,
            command_name_to_config=v1.command_name_to_config,
            profile_name_to_commands_config=v1.profile_name_to_commands_config,
            project_config=project_config,
            profile_name_to_project_config=v1.profile_name_to_shared_command_config,
        )


class ConfigurationFileFacadeV2(
    ConfigurationFileFacade[ConfigurationFileV2],
    ConfigurationFileContentConfigurator[ConfigurationFileV2],
):
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

    def get_declared_protostar_version(self) -> Optional[ProtostarVersion]:
        version_str = self._configuration_file_reader.get_attribute(
            attribute_name="min-protostar-version", section_name="project"
        )
        if not version_str:
            return None
        return parse_protostar_version(version_str)

    def get_contract_names(self) -> list[str]:
        contract_section = self._configuration_file_reader.get_section("contracts")
        if not contract_section:
            return []
        return list(contract_section)

    def get_contract_source_paths(self, contract_name: str) -> list[Path]:
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

    def get_command_argument(
        self, command_name: str, argument_name: str, profile_name: Optional[str] = None
    ) -> Optional[
        Union[
            PrimitiveTypesSupportedByConfigurationFile,
            list[PrimitiveTypesSupportedByConfigurationFile],
        ]
    ]:
        return self._configuration_file_reader.get_attribute(
            section_name=command_name,
            attribute_name=argument_name,
            profile_name=profile_name,
        )

    def read(
        self,
    ) -> ConfigurationFileV2:
        raise NotImplementedError("Operation not supported.")

    def create_file_content(
        self,
        content_builder: ConfigurationFileContentBuilder,
        model: ConfigurationFileV2,
    ) -> str:
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
        return content

    @staticmethod
    def _prepare_project_section_data(model: ConfigurationFileV2) -> dict:
        project_config_section = {}
        project_config_section["min-protostar-version"] = str(model.protostar_version)
        project_config_section: dict = {
            **project_config_section,
            **model.project_config,
        }

        return project_config_section
