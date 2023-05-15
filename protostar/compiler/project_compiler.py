from enum import Enum, auto
from pathlib import Path
from typing import Optional, Tuple

from protostar.cairo.cairo_bindings import (
    compile_starknet_contract_to_sierra_from_path,
    compile_starknet_contract_to_casm_from_path,
    compile_starknet_contract_sierra_to_casm_from_sierra_code,
)
from protostar.cairo.cairo_bindings import CairoBindingException
from protostar.compiler.project_compiler_exceptions import (
    CompilationException,
)
from protostar.compiler.project_compiler_types import (
    ContractIdentifier,
)
from protostar.configuration_file.configuration_file import ConfigurationFile


class _OutputType(Enum):
    SIERRA = auto()
    CASM = auto()
    SIERRA_CASM = auto()


class ProjectCompiler:
    def __init__(
        self,
        project_root_path: Path,
        configuration_file: ConfigurationFile,
    ):
        self._project_root_path = project_root_path
        self.configuration_file = configuration_file

        self._sierra_file_extension = ".sierra.json"
        self._casm_file_extension = ".casm.json"

    def compile_contract(
        self,
        contract_identifier: ContractIdentifier,
        cairo_path: Optional[list[Path]] = None,
        output_path: Optional[Path] = None,
    ) -> Tuple[str, str]:
        sierra_compiled = self.compile_contract_to_sierra_from_contract_identifier(
            contract_identifier, cairo_path, output_path
        )
        casm_compiled = self.compile_contract_to_casm_from_contract_identifier(
            contract_identifier, cairo_path, output_path
        )
        return sierra_compiled, casm_compiled

    def compile_contract_to_sierra_from_contract_identifier(
        self,
        contract_identifier: ContractIdentifier,
        cairo_path: Optional[list[Path]] = None,
        output_path: Optional[Path] = None,
    ) -> str:
        return self._compile_cairo1_contract_from_contract_identifier(
            contract_identifier=contract_identifier,
            output_type=_OutputType.SIERRA,
            cairo_path=cairo_path,
            output_path=output_path,
        )

    def compile_contract_to_casm_from_contract_identifier(
        self,
        contract_identifier: ContractIdentifier,
        cairo_path: Optional[list[Path]] = None,
        output_path: Optional[Path] = None,
    ) -> str:
        return self._compile_cairo1_contract_from_contract_identifier(
            contract_identifier=contract_identifier,
            output_type=_OutputType.CASM,
            cairo_path=cairo_path,
            output_path=output_path,
        )

    def compile_contract_to_sierra_to_casm_from_contract_identifier(
        self,
        contract_identifier: ContractIdentifier,
        cairo_path: Optional[list[Path]] = None,
        output_path: Optional[Path] = None,
    ) -> str:
        return self._compile_cairo1_contract_from_contract_identifier(
            contract_identifier=contract_identifier,
            output_type=_OutputType.SIERRA_CASM,
            cairo_path=cairo_path,
            output_path=output_path,
        )

    def _compile_cairo1_contract_from_contract_identifier(
        self,
        contract_identifier: ContractIdentifier,
        output_type: _OutputType,
        cairo_path: Optional[list[Path]] = None,
        output_path: Optional[Path] = None,
    ) -> str:
        if isinstance(contract_identifier, str):
            contract_identifier = (
                Path(contract_identifier).resolve()
                if contract_identifier.endswith(".cairo")
                else contract_identifier
            )

        if isinstance(contract_identifier, Path):
            return self._compile_cairo1_contract_from_contract_source_path(
                contract_path=contract_identifier,
                output_type=output_type,
                cairo_path=cairo_path,
                output_path=output_path,
            )
        return self._compile_cairo1_contract_from_contract_name(
            contract_name=contract_identifier,
            output_type=output_type,
            cairo_path=cairo_path,
            output_path=output_path,
        )

    def _compile_cairo1_contract_from_contract_name(
        self,
        contract_name: str,
        output_type: _OutputType,
        cairo_path: Optional[list[Path]] = None,
        output_path: Optional[Path] = None,
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
            contract_path=contract_paths[0],
            output_type=output_type,
            cairo_path=cairo_path,
            output_path=output_path,
        )

    def _compile_cairo1_contract_from_contract_source_path(
        self,
        contract_path: Path,
        output_type: _OutputType,
        cairo_path: Optional[list[Path]] = None,
        output_path: Optional[Path] = None,
    ) -> str:
        sierra_output_path = None
        casm_output_path = None
        if output_path:
            sierra_output_path = output_path.with_suffix(self._sierra_file_extension)
            casm_output_path = output_path.with_suffix(self._casm_file_extension)

        if output_type == _OutputType.SIERRA:
            return self._compile_to_sierra_from_path(
                contract_path, cairo_path=cairo_path, output_path=sierra_output_path
            )

        if output_type == _OutputType.CASM:
            return self._compile_to_casm_from_path(
                contract_path, cairo_path=cairo_path, output_path=casm_output_path
            )

        if output_type == _OutputType.SIERRA_CASM:
            sierra_compiled = self._compile_to_sierra_from_path(
                contract_path, cairo_path=cairo_path, output_path=sierra_output_path
            )
            return self._compile_to_casm_from_sierra_code(
                sierra_compiled,
                contract_name=contract_path.name,
                output_path=casm_output_path,
            )

        raise ValueError("Incorrect output_type provided")

    @staticmethod
    def _compile_to_sierra_from_path(
        contract_path: Path,
        cairo_path: Optional[list[Path]] = None,
        output_path: Optional[Path] = None,
    ) -> str:
        try:
            compiled = compile_starknet_contract_to_sierra_from_path(
                input_path=contract_path, cairo_path=cairo_path, output_path=output_path
            )
        except CairoBindingException as ex:
            raise CompilationException(contract_name=contract_path.name, err=ex) from ex

        assert compiled is not None
        return compiled

    @staticmethod
    def _compile_to_casm_from_sierra_code(
        sierra_code: str,
        contract_name: str,
        output_path: Optional[Path] = None,
    ):
        try:
            compiled = compile_starknet_contract_sierra_to_casm_from_sierra_code(
                sierra_compiled=sierra_code, output_path=output_path
            )
        except CairoBindingException as ex:
            raise CompilationException(contract_name=contract_name, err=ex) from ex

        assert compiled is not None
        return compiled

    @staticmethod
    def _compile_to_casm_from_path(
        contract_path: Path,
        cairo_path: Optional[list[Path]] = None,
        output_path: Optional[Path] = None,
    ) -> str:
        try:
            compiled = compile_starknet_contract_to_casm_from_path(
                input_path=contract_path, cairo_path=cairo_path, output_path=output_path
            )
        except CairoBindingException as ex:
            raise CompilationException(contract_name=contract_path.name, err=ex) from ex

        assert compiled is not None
        return compiled
