import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any

from starkware.starknet.core.os.contract_class.compiled_class_hash import (
    compute_compiled_class_hash,
)
from starkware.starknet.core.os.contract_class.class_hash import (
    compute_class_hash,
)

from protostar.cli import ProtostarCommand, MessengerFactory
from protostar.cli.common_arguments import (
    COMPILED_CONTRACTS_DIR_ARG,
    LINKED_LIBRARIES,
    CONTRACT_NAME,
)
from protostar.compiler.project_compiler import (
    make_compiled_class,
    make_contract_class,
    ProjectCompiler,
)
from protostar.configuration_file.configuration_file import ConfigurationFile
from protostar.io import StructuredMessage, LogColorProvider, Messenger

from protostar.commands.cairo1_commands.fetch_from_scarb import (
    maybe_fetch_linked_libraries_from_scarb,
)
from protostar.protostar_exception import ProtostarException


def compute_class_hash_from_path(sierra_contract_file_path: Path, output_path: Path):
    with open(sierra_contract_file_path, mode="r", encoding="utf-8") as file:
        contract_class = make_contract_class(file.read())
        class_hash = compute_class_hash(contract_class)

        with open(output_path, mode="w", encoding="utf-8") as output_file:
            output_file.write(f"{hex(int(class_hash))}")

        return class_hash


def compute_compiled_class_hash_from_path(
    casm_contract_file_path: Path, output_path: Path
):
    with open(casm_contract_file_path, mode="r", encoding="utf-8") as file:
        compiled_class = make_compiled_class(file.read())
        compiled_class_hash = compute_compiled_class_hash(compiled_class)

        with open(output_path, mode="w", encoding="utf-8") as output_file:
            output_file.write(f"{hex(int(compiled_class_hash))}")

        return compiled_class_hash


def compute_class_hash_from_sierra_code(sierra_compiled: str, output_path: Path):
    contract_class = make_contract_class(sierra_compiled)
    class_hash = compute_class_hash(contract_class)

    with open(output_path, mode="w", encoding="utf-8") as output_file:
        output_file.write(f"{hex(int(class_hash))}")

    return class_hash


def compute_compiled_class_hash_from_casm_code(casm_compiled: str, output_path: Path):
    compiled_class = make_compiled_class(casm_compiled)
    compiled_class_hash = compute_compiled_class_hash(compiled_class)

    with open(output_path, mode="w", encoding="utf-8") as output_file:
        output_file.write(f"{hex(int(compiled_class_hash))}")

    return compiled_class_hash


@dataclass
class SuccessfulBuildCairo1Message(StructuredMessage):
    contract_name: str
    class_hash: int
    compiled_class_hash: int

    def format_human(self, fmt: LogColorProvider) -> str:
        lines: list[str] = [
            "Building cairo1 contracts",
            f'Class hash for contract "{self.contract_name}": {hex(int(self.class_hash))}',
            f'Compiled class hash for contract "{self.contract_name}": {hex(int(self.compiled_class_hash))}',
            "Contracts built successfully",
        ]

        return "\n".join(lines)

    def format_dict(self) -> dict:
        return {
            self.contract_name: {
                "class_hash": hex(int(self.class_hash)),
                "compiled_class_hash": hex(int(self.compiled_class_hash)),
            }
        }


class BuildCairo1Command(ProtostarCommand):
    def __init__(
        self,
        configuration_file: ConfigurationFile,
        project_root_path: Path,
        messenger_factory: MessengerFactory,
        project_compiler: ProjectCompiler,
    ):
        super().__init__()
        self._configuration_file = configuration_file
        self._project_root_path = project_root_path
        self._messenger_factory = messenger_factory
        self._project_compiler = project_compiler

    @property
    def example(self) -> Optional[str]:
        return "$ protostar build-cairo1"

    @property
    def name(self) -> str:
        return "build-cairo1"

    @property
    def description(self) -> str:
        return "Compile cairo1 contracts. Writes `class_hash` and `compiled_class_hash` to the files and to stdout."

    @property
    def arguments(self):
        return [
            *MessengerFactory.OUTPUT_ARGUMENTS,
            LINKED_LIBRARIES,
            COMPILED_CONTRACTS_DIR_ARG,
            CONTRACT_NAME,
        ]

    async def run(self, args: Any):
        try:
            messenger = self._messenger_factory.from_args(args)
            await self.build(
                output_dir=args.compiled_contracts_dir,
                relative_cairo_path=args.linked_libraries,
                target_contract_name=args.contract_name,
                messenger=messenger,
            )
        except BaseException as ex:
            logging.error("Build failed")
            raise ex

    async def _build_contract(
        self, contract_name: str, output_dir: Path, linked_libraries: list[Path], messenger: Messenger,
    ):
        contract_paths = self._configuration_file.get_contract_source_paths(
            contract_name
        )
        assert contract_paths, f"No contract paths found for {contract_name}!"
        assert len(contract_paths) == 1, (
            f"Multiple files found for contract {contract_name}, "
            f"only one file per contract is supported in cairo1!"
        )

        cairo_path = linked_libraries + maybe_fetch_linked_libraries_from_scarb(
            package_root_path=contract_paths[0],
            linked_libraries=linked_libraries,
        )

        sierra_compiled, casm_compiled = self._project_compiler.compile_contract(
            contract_name, cairo_path, output_dir
        )

        class_hash = compute_class_hash_from_sierra_code(
            sierra_compiled, output_dir / (contract_name + ".class.hash")
        )
        compiled_class_hash = compute_compiled_class_hash_from_casm_code(
            casm_compiled,
            output_dir / (contract_name + ".compiled.class.hash"),
        )

        messenger(
            SuccessfulBuildCairo1Message(contract_name, class_hash, compiled_class_hash)
        )

    async def build(
        self,
        output_dir: Path,
        messenger: Messenger,
        relative_cairo_path: Optional[list[Path]] = None,
        target_contract_name: str = "",
    ) -> None:
        linked_libraries = relative_cairo_path or []

        if not output_dir.is_absolute():
            output_dir = self._project_root_path / output_dir

        if target_contract_name:
            await self._build_contract(
                contract_name=target_contract_name,
                output_dir=output_dir,
                linked_libraries=linked_libraries,
                messenger=messenger,
            )
            return
        for contract_name in self._configuration_file.get_contract_names():
            await self._build_contract(
                contract_name=contract_name,
                output_dir=output_dir,
                linked_libraries=linked_libraries,
                messenger=messenger,
            )
