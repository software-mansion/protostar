from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Generic, List, Optional, TypeVar, Union

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

TConfigurationFileModel = TypeVar("TConfigurationFileModel")


class ConfigurationFile(Generic[TConfigurationFileModel]):
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

    def create_model(
        self,
    ) -> TConfigurationFileModel:
        ...

    def save(self, configuration_file_model: TConfigurationFileModel) -> Path:
        ...


class ContractNameNotFoundException(ProtostarException):
    def __init__(self, contract_name: str, expected_declaration_localization: str):
        super().__init__(
            f"Couldn't find `{contract_name}` in `{expected_declaration_localization}`"
        )
