import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from starkware.cairo.lang.compiler.preprocessor.preprocessor_error import (
    PreprocessorError,
)
from starkware.cairo.lang.vm.vm_exceptions import VmException
from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starkware_utils.error_handling import StarkException

from protostar.commands.build.build_exceptions import CairoCompilationException
from protostar.protostar_toml.protostar_contracts_section import (
    ProtostarContractsSection,
)
from protostar.utils.compiler.pass_managers import StarknetPassManagerFactory
from protostar.utils.starknet_compilation import CompilerConfig, StarknetCompiler

from .project_cairo_path_builder import ProjectCairoPathBuilder


class ProjectCompiler:
    @dataclass
    class Config:
        relative_cairo_path: List[Path]
        debugging_info_attached: bool = False
        hint_validation_disabled: bool = False

    def __init__(
        self,
        project_root_path: Path,
        project_cairo_path_builder: ProjectCairoPathBuilder,
        contracts_section_loader: ProtostarContractsSection.Loader,
        config: Optional["ProjectCompiler.Config"] = None,
    ):
        self._project_root_path = project_root_path
        self._project_cairo_path_builder = project_cairo_path_builder
        self._contracts_section_loader = contracts_section_loader
        self._config = config or ProjectCompiler.Config(relative_cairo_path=[])

    def set_config(self, config: "ProjectCompiler.Config") -> None:
        self._config = config

    def compile_project(
        self,
        output_dir: Path,
    ):
        contracts_section = self._contracts_section_loader.load()
        if not output_dir.is_absolute():
            output_dir = self._project_root_path / output_dir
        output_dir.mkdir(exist_ok=True)

        for (
            contract_name,
            user_contract_paths,
        ) in contracts_section.contract_name_to_paths.items():
            contract_paths = [
                self._project_root_path / path for path in user_contract_paths
            ]
            contract = self._compile_contract(
                contract_name,
                contract_paths,
            )

            self._save_compiled_contract(contract, output_dir, contract_name)
            self._save_compiled_contract_abi(contract, output_dir, contract_name)

    def build_str_cairo_path_list(self) -> List[str]:
        return [
            str(path)
            for path in self._project_cairo_path_builder.build_project_cairo_path_list(
                self._config.relative_cairo_path
            )
        ]

    def _compile_contract(
        self,
        contract_name: str,
        contract_paths: List[Path],
    ) -> ContractClass:
        str_cairo_path_list = self.build_str_cairo_path_list()

        try:
            return StarknetCompiler(
                config=CompilerConfig(
                    include_paths=str_cairo_path_list,
                    disable_hint_validation=self._config.hint_validation_disabled,
                ),
                pass_manager_factory=StarknetPassManagerFactory,
            ).compile_contract(
                *contract_paths, add_debug_info=self._config.debugging_info_attached
            )
        except StarknetCompiler.FileNotFoundException as err:
            raise StarknetCompiler.FileNotFoundException(
                message=(
                    err.message
                    + '\nDid you forget to update protostar.toml::["protostar.contracts"]?'
                )
            ) from err
        except (StarkException, VmException, PreprocessorError) as err:
            raise CairoCompilationException(
                f"Protostar couldn't compile '{contract_name}' contract\n{str(err)}"
            ) from err

    @staticmethod
    def _save_compiled_contract(
        contract: ContractClass, output_dir: Path, contract_name: str
    ) -> None:
        with open(
            Path(output_dir, f"{contract_name}.json"), mode="w", encoding="utf-8"
        ) as output_file:
            json.dump(
                contract.Schema().dump(contract),
                output_file,
                indent=4,
                sort_keys=True,
            )
            output_file.write("\n")

    @staticmethod
    def _save_compiled_contract_abi(
        contract: ContractClass, output_dir: Path, contract_name: str
    ) -> None:
        with open(
            Path(output_dir, f"{contract_name}_abi.json"),
            mode="w",
            encoding="utf-8",
        ) as output_abi_file:
            json.dump(contract.abi, output_abi_file, indent=4, sort_keys=True)
            output_abi_file.write("\n")
