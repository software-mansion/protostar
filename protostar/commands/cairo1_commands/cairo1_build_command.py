import logging
from pathlib import Path
from typing import List, Optional, Any

from protostar.cli import ProtostarArgument, ProtostarCommand
from protostar.cli.common_arguments import COMPILED_CONTRACTS_DIR_ARG
from protostar.compiler import (
    ProjectCompiler,
)
import protostar.cairo.cairo_bindings as cairo1


class Cairo1BuildCommand(ProtostarCommand):
    def __init__(
        self,
        project_compiler: ProjectCompiler,
    ):
        super().__init__()
        self._project_compiler = project_compiler

    @property
    def example(self) -> Optional[str]:
        return "$ protostar build-cairo1"

    @property
    def name(self) -> str:
        return "build-cairo1"

    @property
    def description(self) -> str:
        return "Compile cairo1 contracts."

    @property
    def arguments(self):
        return [
            ProtostarArgument(
                name="cairo-path",
                description="Additional directories to look for sources.",
                type="path",
                value_parser="list",
            ),
            COMPILED_CONTRACTS_DIR_ARG,
        ]

    async def run(self, args: Any):
        logging.info("Building cairo1 contracts")
        try:
            await self.build(
                output_dir=args.compiled_contracts_dir,
                relative_cairo_path=args.cairo_path,
            )
        except BaseException as ex:
            logging.error("Build failed")
            raise ex

        logging.info("Contracts built successfully")

    async def build(
        self,
        output_dir: Path,
        relative_cairo_path: Optional[List[Path]] = None,
    ) -> None:
        configuration_file = self._project_compiler.configuration_file
        cairo_path = relative_cairo_path or []
        for contract_name in configuration_file.get_contract_names():
            contract_paths = configuration_file.get_contract_source_paths(contract_name)
            assert contract_paths, f"No contract paths found for {contract_name}!"
            assert len(contract_paths) == 1, (
                f"Multiple files found for contract {contract_name}, "
                f"only one file per contract is supported in cairo1!"
            )
            cairo1.compile_starknet_contract_from_path(
                input_path=contract_paths[0],
                cairo_path=cairo_path,
                output_path=self._project_compiler.get_compilation_output_dir(
                    output_dir
                )
                / (contract_name + ".json"),
            )
