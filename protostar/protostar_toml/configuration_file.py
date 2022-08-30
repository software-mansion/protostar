from pathlib import Path
from typing import List, Optional

from typing_extensions import Protocol

from protostar.protostar_exception import ProtostarException
from protostar.protostar_toml.io.protostar_toml_reader import ProtostarTOMLReader
from protostar.utils.protostar_directory import VersionManager, VersionType


class ConfigurationFile(Protocol):
    def get_min_protostar_version(self) -> VersionType:
        ...

    def get_contract_names(self) -> List[str]:
        ...

    def get_contract_source_paths(self, contract_name: str) -> List[Path]:
        ...


class ContractNameNotFoundException(ProtostarException):
    def __init__(self, contract_name: str):
        super().__init__(
            f"Couldn't find `{contract_name}` in `protostar.toml::[protostar.contracts]`"
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
            raise ContractNameNotFoundException(contract_name)
        return [
            self._project_root_path / Path(path_str)
            for path_str in contract_section[contract_name]
        ]
