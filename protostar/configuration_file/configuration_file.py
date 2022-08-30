from pathlib import Path
from typing import List, Optional

from typing_extensions import Protocol

from protostar.protostar_exception import ProtostarException
from protostar.utils.protostar_directory import VersionType


class ConfigurationFile(Protocol):
    def get_min_protostar_version(self) -> Optional[VersionType]:
        ...

    def get_contract_names(self) -> List[str]:
        ...

    def get_contract_source_paths(self, contract_name: str) -> List[Path]:
        ...

    def get_lib_path(self) -> Optional[Path]:
        ...


class ContractNameNotFoundException(ProtostarException):
    def __init__(self, contract_name: str, expected_declaration_localization: str):
        super().__init__(
            f"Couldn't find `{contract_name}` in `{expected_declaration_localization}`"
        )
