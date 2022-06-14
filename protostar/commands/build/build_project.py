import json
from pathlib import Path
from typing import List, Optional

from starkware.cairo.lang.compiler.preprocessor.preprocessor_error import (
    PreprocessorError,
)
from starkware.cairo.lang.vm.vm_exceptions import VmException
from starkware.starkware_utils.error_handling import StarkException

from protostar.cli.command import Command
from protostar.commands.build.build_exceptions import CairoCompilationException
from protostar.utils.config.project import Project
from protostar.utils.starknet_compilation import StarknetCompiler


class BuildCommand(Command):
    def __init__(self, project: Project) -> None:
        super().__init__()
        self._project = project

    @property
    def name(self) -> str:
        return "build"

    @property
    def description(self) -> str:
        return "Compile contracts."

    @property
    def example(self) -> Optional[str]:
        return "$ protostar build"

    @property
    def arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="cairo-path",
                description="Additional directories to look for sources.",
                type="directory",
                is_array=True,
            ),
            Command.Argument(
                name="disable-hint-validation",
                description="Disable validation of hints when building the contracts.",
                type="bool",
            ),
            Command.Argument(
                name="output",
                short_name="o",
                description="An output directory used to put the compiled contracts in.",
                type="path",
                default="build",
            ),
        ]

    async def run(self, args):
        self.build(
            output_dir=args.output,
            cairo_path=args.cairo_path,
            disable_hint_validation=args.disable_hint_validation,
        )

    def build(
        self,
        output_dir: Path,
        cairo_path: List[Path],
        disable_hint_validation: bool,
    ):
        project_paths = [
            *self._project.get_include_paths(),
            *[str(pth) for pth in cairo_path],
        ]
        output_dir.mkdir(exist_ok=True)

        for (
            contract_name,
            contract_components,
        ) in self._project.config.contracts.items():
            try:
                contract = StarknetCompiler(
                    include_paths=project_paths,
                    disable_hint_validation=disable_hint_validation,
                ).compile_contract(
                    *[Path(component) for component in contract_components],
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
