from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from protostar.protostar_exception import ProtostarException
from protostar.protostar_toml.io.protostar_toml_reader import ProtostarTOMLReader
from protostar.protostar_toml.protostar_toml_section import ProtostarTOMLSection


@dataclass
class ProtostarContractsSection(ProtostarTOMLSection):
    contract_name_to_paths: Dict[str, List[Path]]

    class Loader(ProtostarTOMLSection.Loader):
        def __init__(self, protostar_toml_reader: ProtostarTOMLReader):
            self._protostar_toml_reader = protostar_toml_reader

        def load(self):
            return ProtostarContractsSection.load(self._protostar_toml_reader)

    @staticmethod
    def get_section_name() -> str:
        return "contracts"

    @classmethod
    def get_default(cls) -> "ProtostarContractsSection":
        return cls(contract_name_to_paths={"main": [Path("src/main.cairo")]})

    @classmethod
    def load(
        cls, protostar_toml_reader: ProtostarTOMLReader
    ) -> "ProtostarContractsSection":
        section_dict = protostar_toml_reader.get_section(cls.get_section_name())
        if section_dict is None:
            return cls.from_dict({})
        return cls.from_dict(section_dict)

    @classmethod
    def from_dict(cls, raw_dict: Dict[str, Any]) -> "ProtostarContractsSection":
        contract_name_to_paths: Dict[str, List[Path]] = {}
        for contract_name, str_paths in raw_dict.items():
            contract_name_to_paths[contract_name] = [
                Path(str_path) for str_path in str_paths
            ]
        return cls(contract_name_to_paths=contract_name_to_paths)

    def to_dict(self) -> "ProtostarTOMLSection.ParsedProtostarTOML":
        result: "ProtostarTOMLSection.ParsedProtostarTOML" = {}

        for contract_name, paths in self.contract_name_to_paths.items():
            result[contract_name] = [str(path) for path in paths]

        return result

    def get_contract_names(self) -> List[str]:
        return list(self.contract_name_to_paths.keys())

    def get_relative_contract_source_paths(self, contract_name: str) -> List[Path]:
        self.assert_contract_is_defined(contract_name)
        source_paths = self.contract_name_to_paths[contract_name]
        return source_paths

    def assert_contract_is_defined(self, contract_name: str):
        if contract_name not in self.contract_name_to_paths:
            raise ContractNameNotFoundException(contract_name)


class ContractNameNotFoundException(ProtostarException):
    def __init__(self, contract_name: str):
        super().__init__(
            f"Couldn't find `{contract_name}` in `protostar.toml::[protostar.contracts]`"
        )
