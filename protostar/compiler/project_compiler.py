import json
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import List, Optional, Union

from starkware.cairo.lang.compiler.preprocessor.preprocessor_error import (
    PreprocessorError,
)
from starkware.cairo.lang.vm.vm_exceptions import VmException
from starkware.starknet.core.os.contract_class.deprecated_class_hash import (
    compute_deprecated_class_hash,
)
from starkware.starknet.services.api.contract_class.contract_class import (
    DeprecatedCompiledClass,
    CompiledClass,
    ContractClass,
)
from starkware.starkware_utils.error_handling import StarkException

from protostar.cairo.cairo_bindings import (
    compile_starknet_contract_to_sierra_from_path,
    compile_starknet_contract_to_casm_from_path,
)
from protostar.compiler.compiled_contract_writer import CompiledContractWriter
from protostar.compiler.project_cairo_path_builder import LinkedLibrariesBuilder
from protostar.configuration_file.configuration_file import ConfigurationFile
from protostar.protostar_exception import ProtostarException
from protostar.starknet import (
    StarknetPassManagerFactory,
    StarknetCompiler,
    StarknetCompilerConfig,
)


ContractName = str
ContractSourcePath = Path
ContractIdentifier = Union[ContractName, ContractSourcePath]


@dataclass
class ProjectCompilerConfig:
    relative_cairo_path: List[Path]
    debugging_info_attached: bool = False
    hint_validation_disabled: bool = False


class OutputType(Enum):
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

    def _compile_contract(
        self,
        contract_name: str,
        output_dir: Path,
        config: Optional[ProjectCompilerConfig] = None,
    ):
        contract = self.compile_contract_from_contract_name(contract_name, config)
        class_hash = compute_deprecated_class_hash(contract_class=contract)
        CompiledContractWriter(contract, contract_name).save(
            output_dir=self.get_compilation_output_dir(output_dir)
        )
        return class_hash

    def compile_project(
        self,
        output_dir: Path,
        config: Optional[ProjectCompilerConfig] = None,
        target_contract_name: Optional[str] = None,
    ) -> dict[str, int]:
        class_hashes = {}
        if target_contract_name:
            return {
                target_contract_name: self._compile_contract(
                    contract_name=target_contract_name,
                    output_dir=output_dir,
                    config=config,
                )
            }
        for contract_name in self.configuration_file.get_contract_names():
            class_hashes[contract_name] = self._compile_contract(
                contract_name=contract_name, output_dir=output_dir, config=config
            )
        return class_hashes

    def compile_contract_from_contract_identifier(
        self,
        contract_identifier: ContractIdentifier,
        config: Optional[ProjectCompilerConfig] = None,
    ) -> DeprecatedCompiledClass:
        if isinstance(contract_identifier, str):
            contract_identifier = (
                Path(contract_identifier).resolve()
                if contract_identifier.endswith(".cairo")
                else contract_identifier
            )

        if isinstance(contract_identifier, Path):
            return self.compile_contract_from_contract_source_paths(
                [contract_identifier], config
            )
        return self.compile_contract_from_contract_name(contract_identifier, config)

    def compile_contract_to_sierra_from_contract_identifier(
        self, contract_identifier: ContractIdentifier
    ) -> ContractClass:
        result = self._compile_cairo1_contract_from_contract_identifier(
            contract_identifier=contract_identifier, output_type=OutputType.SIERRA
        )
        assert isinstance(result, ContractClass)
        return result

    def compile_contract_to_sierra_from_contract_name(
        self, contract_name: str
    ) -> ContractClass:
        result = self._compile_cairo1_contract_from_contract_name(
            contract_name=contract_name, output_type=OutputType.SIERRA
        )
        assert isinstance(result, ContractClass)
        return result

    def compile_contract_to_sierra_from_source_path(
        self, contract_path: Path
    ) -> ContractClass:
        result = self._compile_cairo1_contract_from_contract_source_path(
            contract_path=contract_path, output_type=OutputType.SIERRA
        )
        assert isinstance(result, ContractClass)
        return result

    def compile_contract_to_casm_from_contract_identifier(
        self, contract_identifier: ContractIdentifier
    ) -> CompiledClass:
        result = self._compile_cairo1_contract_from_contract_identifier(
            contract_identifier=contract_identifier, output_type=OutputType.CASM
        )
        assert isinstance(result, CompiledClass)
        return result

    def compile_contract_to_casm_from_contract_name(
        self, contract_name: str
    ) -> CompiledClass:
        result = self._compile_cairo1_contract_from_contract_name(
            contract_name=contract_name, output_type=OutputType.CASM
        )
        assert isinstance(result, CompiledClass)
        return result

    def compile_contract_to_casm_from_source_path(
        self, contract_path: Path
    ) -> CompiledClass:
        result = self._compile_cairo1_contract_from_contract_source_path(
            contract_path=contract_path, output_type=OutputType.CASM
        )
        assert isinstance(result, CompiledClass)
        return result

    def _compile_cairo1_contract_from_contract_identifier(
        self, contract_identifier: ContractIdentifier, output_type: OutputType
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
        self, contract_name: str, output_type: OutputType
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
        self, contract_path: Path, output_type: OutputType
    ) -> Union[ContractClass, CompiledClass]:
        if output_type == OutputType.SIERRA:
            return self._compile_to_sierra(contract_path)

        if output_type == OutputType.CASM:
            return self._compile_to_casm(contract_path)

        raise ValueError("Incorrect output_type provided")

    def _compile_to_sierra(self, contract_path: Path) -> ContractClass:
        compiled = compile_starknet_contract_to_sierra_from_path(
            input_path=contract_path
        )
        assert compiled is not None

        loaded = json.loads(compiled)
        loaded.pop("sierra_program_debug_info", None)
        loaded["abi"] = json.dumps(loaded["abi"])

        return ContractClass.load(loaded)

    def _compile_to_casm(self, contract_path: Path) -> CompiledClass:
        compiled = compile_starknet_contract_to_casm_from_path(input_path=contract_path)
        assert compiled is not None

        compiled_class = json.loads(compiled)
        compiled_class["pythonic_hints"] = compiled_class["hints"]
        compiled_class["hints"] = []

        return CompiledClass.load(compiled_class)

    def compile_contract_from_contract_name(
        self, contract_name: str, config: Optional[ProjectCompilerConfig] = None
    ) -> DeprecatedCompiledClass:
        try:
            contract_paths = self.configuration_file.get_contract_source_paths(
                contract_name
            )
            assert contract_paths, f"No contract paths found for {contract_name}!"
            return self.compile_contract_from_contract_source_paths(
                contract_paths, config
            )
        except (StarkException, VmException, PreprocessorError) as err:
            raise CompilationException(contract_name, err) from err

    def compile_contract_from_contract_source_paths(
        self, contract_paths: List[Path], config: Optional[ProjectCompilerConfig] = None
    ) -> DeprecatedCompiledClass:
        current_config = config or self._default_config

        return StarknetCompiler(
            config=StarknetCompilerConfig(
                include_paths=self._build_str_cairo_path_list(
                    current_config.relative_cairo_path
                ),
                disable_hint_validation=current_config.hint_validation_disabled,
            ),
            pass_manager_factory=StarknetPassManagerFactory,
        ).compile_contract(
            *contract_paths, add_debug_info=current_config.debugging_info_attached
        )

    @staticmethod
    def _check_source_file_exists(source_path: Path) -> None:
        if not source_path.exists():
            raise SourceFileNotFoundException(source_path)

    def _build_str_cairo_path_list(
        self, user_relative_cairo_path: List[Path]
    ) -> List[str]:
        return [
            str(path)
            for path in self._project_cairo_path_builder.build_project_cairo_path_list(
                user_relative_cairo_path
            )
        ]

    def get_compilation_output_dir(self, output_dir: Path) -> Path:
        if not output_dir.is_absolute():
            output_dir = self._project_root_path / output_dir
        return output_dir


class SourceFileNotFoundException(ProtostarException):
    def __init__(self, contract_path: Path):
        super().__init__(
            f"Couldn't find Cairo file `{contract_path.resolve()}`\n"
            'Did you forget to update protostar.toml::["protostar.contracts"]?'
        )


class CompilationException(ProtostarException):
    def __init__(self, contract_name: str, err: Exception):
        super().__init__(
            f"Protostar couldn't compile '{contract_name}' contract\n{str(err)}"
        )
