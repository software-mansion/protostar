from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from typing_extensions import Self

from protostar.self import ProtostarVersion, parse_protostar_version

from .configuration_file import (
    CommandConfig,
    CommandNameToConfig,
    ConfigurationFile,
    ConfigurationFileContentBuilder,
    ConfigurationFileContentFactory,
    ContractName,
    ContractNameNotFoundException,
    ProfileName,
)
from .configuration_file_interpreter import ConfigurationFileInterpreter
from .configuration_file_v1 import ConfigurationFileV1Model


@dataclass
class ConfigurationFileV2Model:
    protostar_version: Optional[str]
    contract_name_to_path_strs: dict[ContractName, list[str]]
    project_config: CommandConfig
    command_name_to_config: CommandNameToConfig
    profile_name_to_project_config: dict[ProfileName, CommandConfig]
    profile_name_to_commands_config: dict[ProfileName, CommandNameToConfig]

    @classmethod
    # pylint: disable=invalid-name
    def from_v1(cls, v1: ConfigurationFileV1Model, protostar_version: str) -> Self:
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


class ConfigurationFileV2(
    ConfigurationFile[ConfigurationFileV2Model],
):
    def __init__(
        self,
        project_root_path: Path,
        configuration_file_interpreter: ConfigurationFileInterpreter,
        file_path: Path,
    ) -> None:
        super().__init__()
        self._project_root_path = project_root_path
        self._configuration_file_reader = configuration_file_interpreter
        self._file_path = file_path

    def get_declared_protostar_version(self) -> Optional[ProtostarVersion]:
        version_str = self._configuration_file_reader.get_attribute(
            attribute_name="protostar-version", section_name="project"
        )
        if not version_str:
            return None
        return parse_protostar_version(version_str)

    def get_filepath(self) -> Path:
        return self._file_path

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
                expected_declaration_location=f"{self._file_path.name}::[contracts]",
            )
        return [
            self._project_root_path / Path(path_str)
            for path_str in contract_section[contract_name]
        ]

    def get_argument_value(
        self, command_name: str, argument_name: str, profile_name: Optional[str] = None
    ) -> Optional[Any]:
        return self._configuration_file_reader.get_attribute(
            section_name=command_name,
            attribute_name=argument_name,
            profile_name=profile_name,
        )

    def get_shared_argument_value(
        self, argument_name: str, profile_name: Optional[str] = None
    ) -> Optional[Any]:
        return self._configuration_file_reader.get_attribute(
            attribute_name=argument_name,
            profile_name=profile_name,
            section_name="project",
        )

    def read(
        self,
    ) -> ConfigurationFileV2Model:
        raise NotImplementedError("Operation not supported.")


class ConfigurationFileV2ContentFactory(
    ConfigurationFileContentFactory[ConfigurationFileV2Model]
):
    def __init__(
        self,
        content_builder: ConfigurationFileContentBuilder,
    ) -> None:
        super().__init__()
        self._content_builder = content_builder

    def create_file_content(
        self,
        model: ConfigurationFileV2Model,
    ) -> str:
        self._content_builder.set_section(
            section_name="project", data=self._prepare_project_section_data(model)
        )
        self._content_builder.set_section(
            section_name="contracts", data=model.contract_name_to_path_strs
        )
        for command_name, command_config in model.command_name_to_config.items():
            self._content_builder.set_section(
                section_name=command_name, data=command_config
            )
        for (
            profile_name,
            project_config,
        ) in model.profile_name_to_project_config.items():
            self._content_builder.set_section(
                profile_name=profile_name, section_name="project", data=project_config
            )
        for (
            profile_name,
            command_name_to_config,
        ) in model.profile_name_to_commands_config.items():
            for command_name, command_config in command_name_to_config.items():
                self._content_builder.set_section(
                    profile_name=profile_name,
                    section_name=command_name,
                    data=command_config,
                )
        content = self._content_builder.build()
        return content

    @staticmethod
    def _prepare_project_section_data(model: ConfigurationFileV2Model) -> dict:
        project_config_section = {}
        project_config_section["protostar-version"] = str(model.protostar_version)
        project_config_section: dict = {
            **project_config_section,
            **model.project_config,
        }

        return project_config_section

    def get_file_extension(self) -> str:
        return self._content_builder.get_content_format()
