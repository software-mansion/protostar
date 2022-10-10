import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from starkware.starknet.services.api.contract_class import ContractClass


@dataclass
class CompiledContractWriterSaveResult:
    compiled_contract_path: Path
    compiled_contract_path_abi: Path


class CompiledContractWriter:
    def __init__(self, contract: ContractClass, contract_name: str) -> None:
        self._contract = contract
        self._contract_name = contract_name

    def save(self, output_dir: Path) -> CompiledContractWriterSaveResult:
        compiled_contract_path = self.save_compiled_contract(output_dir)
        compiled_contract_path_abi = self.save_compiled_contract_abi(output_dir)

        return CompiledContractWriterSaveResult(
            compiled_contract_path, compiled_contract_path_abi
        )

    def save_compiled_contract(self, output_dir: Path) -> Path:
        self._create_output_dir(output_dir)
        serialized_contract = self._contract.Schema().dump(self._contract)
        file_path = output_dir / f"{self._contract_name}.json"
        self._save_as_json(data=serialized_contract, path=file_path)
        return file_path

    def save_compiled_contract_abi(self, output_dir: Path) -> Path:
        self._create_output_dir(output_dir)
        file_path = output_dir / f"{self._contract_name}_abi.json"
        self._save_as_json(data=self._contract.abi or "", path=file_path)
        return file_path

    @staticmethod
    def _create_output_dir(output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _save_as_json(data: Any, path: Path):
        assert path.suffix == ".json"
        with open(
            path,
            mode="w",
            encoding="utf-8",
        ) as output_file:
            json.dump(data, output_file, indent=4, sort_keys=True)
            output_file.write("\n")
