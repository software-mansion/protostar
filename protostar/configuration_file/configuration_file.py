from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Generic, Optional, Protocol, TypeVar, Union

from protostar.cli import ArgumentValueProviderProtocol
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
        ...

    @abstractmethod
    def build(self) -> str:
        ...

    @abstractmethod
    def get_content_format(self) -> str:
        ...


class ConfigurationFileContentFactory(Generic[ConfigurationFileModelT]):
    @abstractmethod
    def create_file_content(
        self,
        model: ConfigurationFileModelT,
    ) -> str:
        ...

    def get_file_extension(self) -> str:
        ...


class ConfigurationFile(
    DeclaredProtostarVersionProviderProtocol,
    ArgumentValueProviderProtocol,
    Generic[ConfigurationFileModelT],
):
    @abstractmethod
    def get_declared_protostar_version(self) -> Optional[ProtostarVersion]:
        ...

    @abstractmethod
    def get_argument_value(
        self, command_name: str, argument_name: str, profile_name: Optional[str] = None
    ) -> Optional[Any]:
        ...

    @abstractmethod
    def get_shared_argument_value(
        self, argument_name: str, profile_name: Optional[str] = None
    ) -> Optional[Any]:
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
    def read(self) -> ConfigurationFileModelT:
        ...


class ContractNameNotFoundException(ProtostarException):
    def __init__(self, contract_name: str, expected_declaration_location: str):
        super().__init__(
            f"Couldn't find `{contract_name}` in `{expected_declaration_location}`"
        )


class ConfigurationFileMigratorProtocol(Protocol):
    def run(self) -> None:
        pass
