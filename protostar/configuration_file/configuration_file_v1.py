from pathlib import Path
from typing import List, Optional, Union

from protostar.protostar_toml.io.protostar_toml_reader import ProtostarTOMLReader
from protostar.utils.protostar_directory import VersionManager, VersionType

from .configuration_file import (
    ConfigurationFile,
    ContractNameNotFoundException,
    PrimitiveTypesSupportedByConfigurationFile,
)


class ConfigurationFileV1(ConfigurationFile):
    def __init__(
        self, protostar_toml_reader: ProtostarTOMLReader, project_root_path: Path
    ) -> None:
        super().__init__()
        self._protostar_toml_reader = protostar_toml_reader
        self._project_root_path = project_root_path

    def get_min_protostar_version(self) -> Optional[VersionType]:
        version_str = self._protostar_toml_reader.get_attribute(
            attribute_name="protostar_version", section_name="config"
        )
        if not version_str:
            return None
        return VersionManager.parse(version_str)

    def get_contract_names(self) -> List[str]:
        contract_section = self._protostar_toml_reader.get_section("contracts")
        if not contract_section:
            return []
        return list(contract_section)

    def get_contract_source_paths(self, contract_name: str) -> List[Path]:
        contract_section = self._protostar_toml_reader.get_section("contracts")
        if contract_section is None or contract_name not in contract_section:
            raise ContractNameNotFoundException(
                contract_name,
                expected_declaration_localization='protostar.toml::["protostar.contracts"]',
            )
        return [
            self._project_root_path / Path(path_str)
            for path_str in contract_section[contract_name]
        ]

    def get_lib_path(self) -> Optional[Path]:
        lib_relative_path_str = self._protostar_toml_reader.get_attribute(
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
        return self._protostar_toml_reader.get_attribute(
            section_name=command_name,
            attribute_name=argument_name,
            profile_name=profile_name,
        )
