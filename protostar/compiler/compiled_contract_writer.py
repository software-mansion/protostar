import json
from pathlib import Path
from typing import Any

from starkware.starknet.services.api.contract_class import ContractClass


class CompiledContractWriter:
    def __init__(self, contract: ContractClass, contract_name: str) -> None:
        self._contract = contract
        self._contract_name = contract_name

    def save(self, output_dir: Path) -> None:
        self.save_compiled_contract(output_dir)
        self.save_compiled_contract_abi(output_dir)

    def save_compiled_contract(self, output_dir: Path) -> None:
        self._create_output_dir(output_dir)
        serialized_contract = self._contract.Schema().dump(self._contract)
        self._save_as_json(data=serialized_contract, path=output_dir)

    def save_compiled_contract_abi(self, output_dir: Path) -> None:
        if not self._contract.abi:
            return
        self._create_output_dir(output_dir)
        self._save_as_json(data=self._contract.abi, path=output_dir)

    @staticmethod
    def _create_output_dir(output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _save_as_json(data: Any, path: Path):
        with open(
            path,
            mode="w",
            encoding="utf-8",
        ) as output_abi_file:
            json.dump(data, output_abi_file, indent=4, sort_keys=True)
            output_abi_file.write("\n")
