from enum import Enum, auto
from pathlib import Path
import json

from starkware.starknet.services.api.contract_class.contract_class import (
    ContractClass,
    CompiledClass,
)

from protostar.cairo.cairo_bindings import (
    compile_starknet_contract_to_sierra_from_path,
    compile_starknet_contract_to_casm_from_path,
)
from protostar.cairo.cairo_bindings import CairoBindingException
from protostar.compiler.project_compiler_exceptions import (
    CompilationException,
)
from protostar.compiler.project_compiler_types import (
    ContractIdentifier,
)
from protostar.configuration_file.configuration_file import ConfigurationFile


def make_contract_class(sierra_compiled: str):
    sierra_compiled_dict = json.loads(sierra_compiled)
    sierra_compiled_dict.pop("sierra_program_debug_info", None)
    sierra_compiled_dict["abi"] = json.dumps(sierra_compiled_dict["abi"])

    return ContractClass.load(sierra_compiled_dict)


def make_compiled_class(casm_compiled: str):
    return CompiledClass.loads(casm_compiled)


class _OutputType(Enum):
    SIERRA = auto()
    CASM = auto()


class ProjectCompiler:
    def __init__(
        self,
        project_root_path: Path,
        configuration_file: ConfigurationFile,
    ):
        self._project_root_path = project_root_path
        self.configuration_file = configuration_file

    def compile_contract_to_sierra_from_contract_identifier(
        self, contract_identifier: ContractIdentifier
    ) -> str:
        return self._compile_cairo1_contract_from_contract_identifier(
            contract_identifier=contract_identifier, output_type=_OutputType.SIERRA
        )

    def compile_contract_to_sierra_from_contract_name(self, contract_name: str) -> str:
        return self._compile_cairo1_contract_from_contract_name(
            contract_name=contract_name, output_type=_OutputType.SIERRA
        )

    def compile_contract_to_sierra_from_source_path(self, contract_path: Path) -> str:
        return self._compile_cairo1_contract_from_contract_source_path(
            contract_path=contract_path, output_type=_OutputType.SIERRA
        )

    def compile_contract_to_casm_from_contract_identifier(
        self, contract_identifier: ContractIdentifier
    ) -> str:
        return self._compile_cairo1_contract_from_contract_identifier(
            contract_identifier=contract_identifier, output_type=_OutputType.CASM
        )

    def compile_contract_to_casm_from_contract_name(self, contract_name: str) -> str:
        return self._compile_cairo1_contract_from_contract_name(
            contract_name=contract_name, output_type=_OutputType.CASM
        )

    def compile_contract_to_casm_from_source_path(self, contract_path: Path) -> str:
        return self._compile_cairo1_contract_from_contract_source_path(
            contract_path=contract_path, output_type=_OutputType.CASM
        )

    def _compile_cairo1_contract_from_contract_identifier(
        self, contract_identifier: ContractIdentifier, output_type: _OutputType
    ) -> str:
        if isinstance(contract_identifier, str):
            contract_identifier = (
                Path(contract_identifier).resolve()
                if contract_identifier.endswith(".cairo")
                else contract_identifier
            )

        if isinstance(contract_identifier, Path):
            return self._compile_cairo1_contract_from_contract_source_path(
                contract_path=contract_identifier, output_type=output_type
            )
        return self._compile_cairo1_contract_from_contract_name(
            contract_name=contract_identifier, output_type=output_type
        )

    def _compile_cairo1_contract_from_contract_name(
        self, contract_name: str, output_type: _OutputType
    ) -> str:
        contract_paths = self.configuration_file.get_contract_source_paths(
            contract_name
        )

        assert len(contract_paths) == 1, (
            f"Multiple files found for contract {contract_name}, "
            f"only one file per contract is supported in cairo1!"
        )
        assert contract_paths, f"No contract paths found for {contract_name}!"

        return self._compile_cairo1_contract_from_contract_source_path(
            contract_path=contract_paths[0], output_type=output_type
        )

    def _compile_cairo1_contract_from_contract_source_path(
        self, contract_path: Path, output_type: _OutputType
    ) -> str:
        if output_type == _OutputType.SIERRA:
            return self._compile_to_sierra(contract_path)

        if output_type == _OutputType.CASM:
            return self._compile_to_casm(contract_path)

        raise ValueError("Incorrect output_type provided")

    @staticmethod
    def _compile_to_sierra(contract_path: Path) -> str:
        try:
            compiled = compile_starknet_contract_to_sierra_from_path(
                input_path=contract_path
            )
        except CairoBindingException as ex:
            raise CompilationException(contract_name=contract_path.name, err=ex) from ex

        assert compiled is not None
        return compiled

    @staticmethod
    def _compile_to_casm(contract_path: Path) -> str:
        try:
            compiled = compile_starknet_contract_to_casm_from_path(
                input_path=contract_path
            )
        except CairoBindingException as ex:
            raise CompilationException(contract_name=contract_path.name, err=ex) from ex

        assert compiled is not None
        return compiled
