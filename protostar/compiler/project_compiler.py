import json
from enum import Enum, auto
from pathlib import Path
from typing import Optional, Union


from starkware.starknet.services.api.contract_class.contract_class import (
    CompiledClass,
    ContractClass,
)

from protostar.cairo.cairo_bindings import (
    compile_starknet_contract_to_sierra_from_path,
    compile_starknet_contract_to_casm_from_path,
)
from protostar.cairo.cairo_exceptions import CairoBindingException
from protostar.compiler.project_compiler_exceptions import (
    CompilationException,
)
from protostar.compiler.project_cairo_path_builder import LinkedLibrariesBuilder
from protostar.compiler.project_compiler_types import (
    ContractIdentifier,
    ProjectCompilerConfig,
)
from protostar.configuration_file.configuration_file import ConfigurationFile


class _OutputType(Enum):
    SIERRA = auto()
    CASM = auto()


class ProjectCompiler:
    def __init__(
        self,
        project_root_path: Path,
        project_cairo_path_builder: LinkedLibrariesBuilder,
        configuration_file: ConfigurationFile,
        default_config: Optional[ProjectCompilerConfig] = None,
    ):
        self._project_root_path = project_root_path
        self._project_cairo_path_builder = project_cairo_path_builder
        self.configuration_file = configuration_file
        self._default_config = default_config or ProjectCompilerConfig(
            relative_cairo_path=[]
        )

    def compile_contract_to_sierra_from_contract_identifier(
        self, contract_identifier: ContractIdentifier
    ) -> ContractClass:
        result = self._compile_cairo1_contract_from_contract_identifier(
            contract_identifier=contract_identifier, output_type=_OutputType.SIERRA
        )
        assert isinstance(result, ContractClass)
        return result

    def compile_contract_to_sierra_from_contract_name(
        self, contract_name: str
    ) -> ContractClass:
        result = self._compile_cairo1_contract_from_contract_name(
            contract_name=contract_name, output_type=_OutputType.SIERRA
        )
        assert isinstance(result, ContractClass)
        return result

    def compile_contract_to_sierra_from_source_path(
        self, contract_path: Path
    ) -> ContractClass:
        result = self._compile_cairo1_contract_from_contract_source_path(
            contract_path=contract_path, output_type=_OutputType.SIERRA
        )
        assert isinstance(result, ContractClass)
        return result

    def compile_contract_to_casm_from_contract_identifier(
        self, contract_identifier: ContractIdentifier
    ) -> CompiledClass:
        result = self._compile_cairo1_contract_from_contract_identifier(
            contract_identifier=contract_identifier, output_type=_OutputType.CASM
        )
        assert isinstance(result, CompiledClass)
        return result

    def compile_contract_to_casm_from_contract_name(
        self, contract_name: str
    ) -> CompiledClass:
        result = self._compile_cairo1_contract_from_contract_name(
            contract_name=contract_name, output_type=_OutputType.CASM
        )
        assert isinstance(result, CompiledClass)
        return result

    def compile_contract_to_casm_from_source_path(
        self, contract_path: Path
    ) -> CompiledClass:
        result = self._compile_cairo1_contract_from_contract_source_path(
            contract_path=contract_path, output_type=_OutputType.CASM
        )
        assert isinstance(result, CompiledClass)
        return result

    def _compile_cairo1_contract_from_contract_identifier(
        self, contract_identifier: ContractIdentifier, output_type: _OutputType
    ) -> Union[ContractClass, CompiledClass]:
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
    ) -> Union[ContractClass, CompiledClass]:
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
    ) -> Union[ContractClass, CompiledClass]:
        if output_type == _OutputType.SIERRA:
            return self._compile_to_sierra(contract_path)

        if output_type == _OutputType.CASM:
            return self._compile_to_casm(contract_path)

        raise ValueError("Incorrect output_type provided")

    @staticmethod
    def _compile_to_sierra(contract_path: Path) -> ContractClass:
        try:
            compiled = compile_starknet_contract_to_sierra_from_path(
                input_path=contract_path
            )
        except CairoBindingException as ex:
            raise CompilationException(contract_name=contract_path.name, err=ex) from ex
        assert compiled is not None

        loaded = json.loads(compiled)
        loaded.pop("sierra_program_debug_info", None)
        loaded["abi"] = json.dumps(loaded["abi"])

        return ContractClass.load(loaded)

    @staticmethod
    def _compile_to_casm(contract_path: Path) -> CompiledClass:
        try:
            compiled = compile_starknet_contract_to_casm_from_path(
                input_path=contract_path
            )
        except CairoBindingException as ex:
            raise CompilationException(contract_name=contract_path.name, err=ex) from ex

        assert compiled is not None

        compiled_class = json.loads(compiled)
        compiled_class["pythonic_hints"] = compiled_class["hints"]
        compiled_class["hints"] = []

        return CompiledClass.load(compiled_class)
