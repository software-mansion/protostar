from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union

from typing_extensions import Protocol

from protostar.protostar_exception import ProtostarException
from protostar.utils.protostar_directory import VersionType

PrimitiveTypesSupportedByConfigurationFile = Union[str, int, bool]

CommandName = str
CommandArgName = str
CommandArgValue = Union[str, int, bool]
CommandConfig = Dict[CommandArgName, Union[CommandArgValue, List[CommandArgValue]]]
CommandNameToConfig = Dict[CommandName, CommandConfig]
ProfileName = str
ContractName = str


@dataclass(frozen=True)
class ConfigurationFileData:
    min_protostar_version: Optional[str]
    contract_name_to_path_str: Dict[ContractName, str]
    lib_path_str: Optional[str]
    command_name_to_config: CommandNameToConfig
    shared_command_config: CommandConfig
    profile_name_to_commands_config: Dict[ProfileName, CommandNameToConfig]
    profile_name_to_shared_command_config: Dict[ProfileName, CommandConfig]


class ConfigurationFile(Protocol):
    def get_min_protostar_version(self) -> Optional[VersionType]:
        ...

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

    def create_configuration_file_data(
        self,
    ) -> ConfigurationFileData:
        ...


class ContractNameNotFoundException(ProtostarException):
    def __init__(self, contract_name: str, expected_declaration_localization: str):
        super().__init__(
            f"Couldn't find `{contract_name}` in `{expected_declaration_localization}`"
        )
