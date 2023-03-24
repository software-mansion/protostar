from pathlib import Path
from typing import List, Optional

from starkware.cairo.lang.compiler.preprocessor.preprocessor_error import (
    PreprocessorError,
)
from starkware.cairo.lang.vm.vm_exceptions import VmException
from starkware.starknet.core.os.contract_class.deprecated_class_hash import (
    compute_deprecated_class_hash,
)
from starkware.starknet.services.api.contract_class.contract_class import (
    DeprecatedCompiledClass,
)
from starkware.starkware_utils.error_handling import StarkException

from protostar.compiler import (
    ProjectCompilerConfig,
    SourceFileNotFoundException,
    CompilationException,
)
from protostar.compiler.compiled_contract_writer import CompiledContractWriter
from protostar.compiler.project_cairo_path_builder import LinkedLibrariesBuilder
from protostar.compiler.project_compiler_types import ContractIdentifier
from protostar.configuration_file.configuration_file import ConfigurationFile
from protostar.starknet import (
    StarknetPassManagerFactory,
    StarknetCompiler,
    StarknetCompilerConfig,
)


class Cairo0ProjectCompiler:
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
