import logging
from pathlib import Path
from typing import Optional, Any

from protostar.cli import ProtostarCommand
from protostar.cli.common_arguments import (
    COMPILED_CONTRACTS_DIR_ARG,
    CONTRACT_NAME,
)
from protostar.configuration_file.configuration_file import ConfigurationFile
import protostar.cairo.bindings.cairo_bindings as cairo1

from protostar.commands.cairo1_commands.fetch_from_scarb import (
    fetch_linked_libraries_from_scarb,
)
from protostar.protostar_exception import ProtostarException


class BuildCommand(ProtostarCommand):
    def __init__(
        self,
        configuration_file: ConfigurationFile,
        project_root_path: Path,
    ):
        super().__init__()
        self._configuration_file = configuration_file
        self._project_root_path = project_root_path

    @property
    def example(self) -> Optional[str]:
        return "$ protostar build"

    @property
    def name(self) -> str:
        return "build"

    @property
    def description(self) -> str:
        return "Compile cairo 1 contracts."

    @property
    def arguments(self):
        return [
            COMPILED_CONTRACTS_DIR_ARG,
            CONTRACT_NAME,
        ]

    async def run(self, args: Any):
        logging.info("Building cairo1 contracts")
        try:
            await self.build(
                output_dir=args.compiled_contracts_dir,
                target_contract_name=args.contract_name,
            )
        except BaseException as ex:
            logging.error("Build failed")
            raise ex

        logging.info("Contracts built successfully")

    async def _build_contract(self, contract_name: str, output_dir: Path):
        contract_paths = self._configuration_file.get_contract_source_paths(
            contract_name
        )
        assert contract_paths, f"No contract paths found for {contract_name}!"
        assert len(contract_paths) == 1, (
            f"Multiple files found for contract {contract_name}, "
            f"only one file per contract is supported in cairo1!"
        )
        sierra_file_path = output_dir / (contract_name + ".sierra.json")
        try:
            cairo1.compile_starknet_contract_to_sierra_from_path(
                input_path=contract_paths[0],
                maybe_cairo_paths=fetch_linked_libraries_from_scarb(
                    package_root_path=self._project_root_path,
                ),
                output_path=sierra_file_path,
            )
            cairo1.compile_starknet_contract_sierra_to_casm_from_path(
                input_path=sierra_file_path,
                output_path=output_dir / (contract_name + ".casm.json"),
            )
        except cairo1.CairoBindingException as ex:
            raise ProtostarException(ex.message) from ex

    async def build(
        self,
        output_dir: Path,
        target_contract_name: str = "",
    ) -> None:
        if not output_dir.is_absolute():
            output_dir = self._project_root_path / output_dir

        if target_contract_name:
            await self._build_contract(
                contract_name=target_contract_name,
                output_dir=output_dir,
            )
            return
        for contract_name in self._configuration_file.get_contract_names():
            await self._build_contract(
                contract_name=contract_name,
                output_dir=output_dir,
            )
