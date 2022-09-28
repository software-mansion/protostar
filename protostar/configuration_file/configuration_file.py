from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Generic, Optional, TypeVar, Union

from protostar.protostar_exception import ProtostarException
from protostar.self import DeclaredProtostarVersionProviderProtocol, ProtostarVersion

PrimitiveTypesSupportedByConfigurationFile = Union[str, int, bool]

CommandName = str
CommandArgName = str
CommandArgValue = Union[str, int, bool]
CommandConfig = dict[CommandArgName, Union[CommandArgValue, list[CommandArgValue]]]
CommandNameToConfig = dict[CommandName, CommandConfig]
ProfileName = str
ContractName = str

ConfigurationFileModelT = TypeVar("ConfigurationFileModelT")


class ConfigurationFileContentBuilder(ABC):
    @abstractmethod
    def set_section(
        self,
        section_name: str,
        data: dict[str, Any],
        profile_name: Optional[str] = None,
    ) -> None:
        pass

    @abstractmethod
    def build(self) -> str:
        ...

    def get_file_extension(self) -> str:
        ...


class ConfigurationFileContentConfigurator(Generic[ConfigurationFileModelT]):
    @abstractmethod
    def create_file_content(
        self,
        model: ConfigurationFileModelT,
    ) -> str:
        ...

    def get_file_extension(self) -> str:
        ...


class ConfigurationFile(
    DeclaredProtostarVersionProviderProtocol, Generic[ConfigurationFileModelT]
):
    @abstractmethod
    def get_declared_protostar_version(self) -> Optional[ProtostarVersion]:
        ...

    @abstractmethod
    def get_filepath(self) -> Path:
        ...

    @abstractmethod
    def get_contract_names(self) -> list[str]:
        ...

    @abstractmethod
    def get_contract_source_paths(self, contract_name: str) -> list[Path]:
        ...

    @abstractmethod
    def get_command_argument(
        self, command_name: str, argument_name: str, profile_name: Optional[str] = None
    ) -> Optional[
        Union[
            PrimitiveTypesSupportedByConfigurationFile,
            list[PrimitiveTypesSupportedByConfigurationFile],
        ]
    ]:
        ...

    @abstractmethod
    def read(self) -> ConfigurationFileModelT:
        ...


class ContractNameNotFoundException(ProtostarException):
    def __init__(self, contract_name: str, expected_declaration_location: str):
        super().__init__(
            f"Couldn't find `{contract_name}` in `{expected_declaration_location}`"
        )
