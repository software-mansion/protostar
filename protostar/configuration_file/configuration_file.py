from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Generic, Optional, Protocol, TypeVar, Union
import tomli
import tomli_w

from protostar.protostar_exception import ProtostarException
from protostar.self import DeclaredProtostarVersionProviderProtocol, ProtostarVersion

from .argument_value_resolver import ArgumentValueResolver

PrimitiveTypesSupportedByConfigurationFile = Union[str, int, bool]

CommandName = str
CommandArgName = str
CommandArgValue = Union[str, int, bool]
CommandConfig = dict[CommandArgName, Union[CommandArgValue, list[CommandArgValue]]]
CommandNameToConfig = dict[CommandName, CommandConfig]
ProfileName = str
ContractName = str

ConfigurationFileModelT = TypeVar("ConfigurationFileModelT")


class CommandNamesProviderProtocol(Protocol):
    def get_command_names(self) -> list[str]:
        ...


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
    ArgumentValueResolver,
    DeclaredProtostarVersionProviderProtocol,
    Generic[ConfigurationFileModelT],
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
    def read(self) -> ConfigurationFileModelT:
        ...

    def set_command_names_provider(
        self, command_names_provider: CommandNamesProviderProtocol
    ):
        pass

    @classmethod
    def create_appending_cairo_path_suggestion(
        cls, logger, project_root_path, libs_path, package_name
    ):
        protostar_toml = "protostar.toml"
        shared_command_configs_key = "protostar.shared_command_configs"

        data = tomli.loads(
            (project_root_path / protostar_toml).read_text(encoding="utf-8")
        )
        shared_command_configs = data.get(shared_command_configs_key)
        if not shared_command_configs:
            shared_command_configs = {}
        shared_command_configs["cairo_path"] = (
            ["..."] if shared_command_configs.get("cairo_path") else []
        )
        shared_command_configs["cairo_path"].append(f"{libs_path}/{package_name}/src")

        logger.info(
            "You may want to add your new library's path to the 'cairo_path' section of your "
            f"`{protostar_toml}` file"
        )
        logger.info(
            f"\n[{shared_command_configs_key}]\n{tomli_w.dumps(shared_command_configs)}"
        )


class ContractNameNotFoundException(ProtostarException):
    def __init__(self, contract_name: str, expected_declaration_location: str):
        super().__init__(
            f"Couldn't find `{contract_name}` in `{expected_declaration_location}`"
        )


class ConfigurationFileMigratorProtocol(Protocol):
    def run(self) -> None:
        pass
