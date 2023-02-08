from os import listdir
from os.path import isfile, join
from pathlib import Path
from typing import Optional

from protostar.starknet import CompiledContract

from .project_compiler import ContractIdentifier


class CompiledContractsCache:
    @classmethod
    def from_compiled_contracts_dir(cls, compiled_contracts_dir: Path):
        cache = cls()
        compiled_contract_filenames = [
            filename
            for filename in listdir(compiled_contracts_dir)
            if isfile(join(compiled_contracts_dir, filename))
            and filename.endswith(".json")
            and not filename.endswith("_abi.json")
        ]
        for filename in compiled_contract_filenames:
            compiled_contract_file_content = (
                compiled_contracts_dir / filename
            ).read_text()
            compiled_contract = CompiledContract.loads(compiled_contract_file_content)
            contract_identifier = Path(filename).stem
            cache.write(key=contract_identifier, value=compiled_contract)
        return cache

    def __init__(self) -> None:
        self._key_to_value: dict[ContractIdentifier, CompiledContract] = {}

    def write(self, key: ContractIdentifier, value: CompiledContract) -> None:
        self._key_to_value[key] = value

    def read(self, key: ContractIdentifier) -> Optional[CompiledContract]:
        return self._key_to_value.get(key, None)
