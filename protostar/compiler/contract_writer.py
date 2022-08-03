import json
from pathlib import Path

from starkware.starknet.services.api.contract_class import ContractClass


class ContractWriter:
    def __init__(self, contract: ContractClass, contract_name: str) -> None:
        self._contract = contract
        self._contract_name = contract_name

    def save(self, output_dir: Path) -> None:
        self.save_compiled_contract(output_dir)
        self.save_compiled_contract_abi(output_dir)

    def save_compiled_contract(self, output_dir: Path) -> None:
        self._create_output_dir(output_dir)
        with open(
            Path(output_dir, f"{self._contract_name}.json"), mode="w", encoding="utf-8"
        ) as output_file:
            json.dump(
                self._contract.Schema().dump(self._contract),
                output_file,
                indent=4,
                sort_keys=True,
            )
            output_file.write("\n")

    def save_compiled_contract_abi(self, output_dir: Path) -> None:
        if not self._contract.abi:
            return

        self._create_output_dir(output_dir)
        with open(
            Path(output_dir, f"{self._contract_name}_abi.json"),
            mode="w",
            encoding="utf-8",
        ) as output_abi_file:
            json.dump(self._contract.abi, output_abi_file, indent=4, sort_keys=True)
            output_abi_file.write("\n")

    @staticmethod
    def _create_output_dir(output_dir: Path):
        if not output_dir.exists():
            output_dir.mkdir(parents=True)
