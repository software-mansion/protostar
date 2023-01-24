from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

from starkware.cairo.lang.compiler.preprocessor.preprocessor_error import (
    PreprocessorError,
)
from starkware.cairo.lang.vm.vm_exceptions import VmException
from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starkware_utils.error_handling import StarkException
from starkware.starknet.core.os.class_hash import compute_class_hash

from protostar.compiler.compiled_contract_writer import CompiledContractWriter
from protostar.configuration_file.configuration_file import ConfigurationFile
from protostar.protostar_exception import ProtostarException
from protostar.starknet import (
    StarknetPassManagerFactory,
    StarknetCompiler,
    StarknetCompilerConfig,
)

from .project_cairo_path_builder import ProjectCairoPathBuilder

ContractName = str
ContractSourcePath = Path
ContractIdentifier = Union[ContractName, ContractSourcePath]


@dataclass
class ProjectCompilerConfig:
    relative_cairo_path: List[Path]
    debugging_info_attached: bool = False
    hint_validation_disabled: bool = False


class ProjectCompiler:
    def __init__(
        self,
        project_root_path: Path,
        project_cairo_path_builder: ProjectCairoPathBuilder,
        configuration_file: ConfigurationFile,
        default_config: Optional[ProjectCompilerConfig] = None,
    ):
        self._project_root_path = project_root_path
        self._project_cairo_path_builder = project_cairo_path_builder
        self._configuration_file = configuration_file
        self._default_config = default_config or ProjectCompilerConfig(
            relative_cairo_path=[]
        )

    def compile_project(
        self, output_dir: Path, config: Optional[ProjectCompilerConfig] = None
    ) -> dict[str, int]:
        class_hashes = {}
        for contract_name in self._configuration_file.get_contract_names():
            contract = self.compile_contract_from_contract_name(contract_name, config)
            class_hash = compute_class_hash(contract_class=contract)
            class_hashes[contract_name] = class_hash
            CompiledContractWriter(contract, contract_name).save(
                output_dir=self.get_compilation_output_dir(output_dir)
            )
        return class_hashes

    def compile_contract_from_contract_identifier(
        self,
        contract_identifier: ContractIdentifier,
        config: Optional[ProjectCompilerConfig] = None,
    ) -> ContractClass:
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
    ) -> ContractClass:
        try:
            contract_paths = self._configuration_file.get_contract_source_paths(
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
    ) -> ContractClass:
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
