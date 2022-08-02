from typing import List, Optional

from protostar.cli.command import Command
from protostar.compiler import ProjectCompiler


class BuildCommand(Command):
    def __init__(self, project_compiler: ProjectCompiler) -> None:
        super().__init__()
        self._project_compiler = project_compiler

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
        self._project_compiler.set_config(
            ProjectCompiler.Config(
                hint_validation_disabled=args.disable_hint_validation,
                relative_cairo_path=args.cairo_path,
            )
        )
        self._project_compiler.compile_project(
            output_dir=args.output,
        )
