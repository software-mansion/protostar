from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

from starkware.cairo.lang.compiler.preprocessor.preprocessor_error import (
    PreprocessorError,
)
from starkware.cairo.lang.vm.vm_exceptions import VmException
from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starkware_utils.error_handling import StarkException

from protostar.compiler.compiled_contract_writer import CompiledContractWriter
from protostar.protostar_exception import ProtostarException
from protostar.protostar_toml.protostar_contracts_section import (
    ProtostarContractsSection,
)
from protostar.utils.compiler.pass_managers import StarknetPassManagerFactory
from protostar.utils.starknet_compilation import CompilerConfig, StarknetCompiler

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
        contracts_section_loader: ProtostarContractsSection.Loader,
        default_config: Optional[ProjectCompilerConfig] = None,
    ):
        self._project_root_path = project_root_path
        self._project_cairo_path_builder = project_cairo_path_builder
        self._contracts_section_loader = contracts_section_loader
        self._default_config = default_config or ProjectCompilerConfig(
            relative_cairo_path=[]
        )

    def compile_project(
        self, output_dir: Path, config: Optional[ProjectCompilerConfig] = None
    ) -> None:
        contracts_section = self._contracts_section_loader.load()
        for contract_name in contracts_section.get_contract_names():
            contract = self.compile_contract_from_contract_name(contract_name, config)
            CompiledContractWriter(contract, contract_name).save(
                output_dir=self._get_compilation_output_dir(output_dir)
            )

    def compile_contract_from_contract_identifier(
        self,
        contract_identifier: ContractIdentifier,
        config: Optional[ProjectCompilerConfig] = None,
    ) -> ContractClass:
        if isinstance(contract_identifier, Path):
            return self.compile_contract_from_contract_source_paths(
                [contract_identifier], config
            )
        return self.compile_contract_from_contract_name(contract_identifier, config)

    def compile_contract_from_contract_name(
        self, contract_name: str, config: Optional[ProjectCompilerConfig] = None
    ) -> ContractClass:
        try:
            contract_paths = self._map_contract_name_to_contract_source_paths(
                contract_name
            )
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
            config=CompilerConfig(
                include_paths=self._build_str_cairo_path_list(
                    current_config.relative_cairo_path
                ),
                disable_hint_validation=current_config.hint_validation_disabled,
            ),
            pass_manager_factory=StarknetPassManagerFactory,
        ).compile_contract(
            *contract_paths, add_debug_info=current_config.debugging_info_attached
        )

    def _map_contract_name_to_contract_source_paths(
        self, contract_name: str
    ) -> List[Path]:
        contracts_section = self._contracts_section_loader.load()
        relative_source_paths = contracts_section.get_relative_contract_source_paths(
            contract_name
        )
        source_paths = [
            self._project_root_path / path for path in relative_source_paths
        ]
        map(self._check_source_file_exists, source_paths)
        return source_paths

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

    def _get_compilation_output_dir(self, output_dir: Path) -> Path:
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
