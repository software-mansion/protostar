import json
from pathlib import Path
from typing import List, Type

from starkware.cairo.lang.compiler.preprocessor.preprocessor_error import (
    PreprocessorError,
)
from starkware.cairo.lang.vm.vm_exceptions import VmException
from starkware.starkware_utils.error_handling import StarkException

from protostar.commands.build.build_exceptions import CairoCompilationException
from protostar.protostar_toml.io.protostar_toml_reader import ProtostarTOMLReader
from protostar.protostar_toml.protostar_contracts_section import (
    ProtostarContractsSection,
)
from protostar.protostar_toml.protostar_project_section import ProtostarProjectSection
from protostar.utils.starknet_compilation import StarknetCompiler


class ProjectCompiler:
    def __init__(
        self,
        protostar_toml_reader: ProtostarTOMLReader,
        ProjectSection: Type[ProtostarProjectSection],
        ContractsSection: Type[ProtostarContractsSection],
    ):
        self._protostar_toml_reader = protostar_toml_reader
        self._ProjectSection = ProjectSection
        self._ContractsSection = ContractsSection

    def compile(
        self,
        output_dir: Path,
        cairo_path: List[Path],
        disable_hint_validation: bool,
        is_account_contract=False,
    ):
        include_paths = [
            str(pth) for pth in [*cairo_path, self._project_section.libs_path]
        ]
        output_dir.mkdir(exist_ok=True)

        for (
            contract_name,
            contract_paths,
        ) in self._contracts_section.contract_name_to_paths.items():
            try:
                contract = StarknetCompiler(
                    include_paths=include_paths,
                    disable_hint_validation=disable_hint_validation,
                ).compile_contract(
                    *contract_paths,
                    is_account_contract=is_account_contract,
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

            with open(
                Path(output_dir, f"{contract_name}_abi.json"),
                mode="w",
                encoding="utf-8",
            ) as output_abi_file:
                json.dump(contract.abi, output_abi_file, indent=4, sort_keys=True)
                output_abi_file.write("\n")
