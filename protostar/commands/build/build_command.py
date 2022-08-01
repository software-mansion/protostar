from logging import Logger
from typing import List, Optional

from protostar.cli import ActivityIndicator
from protostar.cli.command import Command
from protostar.commands.build.project_compiler import ProjectCompiler
from protostar.utils import log_color_provider


class BuildCommand(Command):
    def __init__(self, project_compiler: ProjectCompiler, logger: Logger) -> None:
        super().__init__()
        self._project_compiler = project_compiler
        self._logger = logger

    @property
    def example(self) -> Optional[str]:
        return "$ protostar build"

    @property
    def name(self) -> str:
        return "build"

    @property
    def description(self) -> str:
        return "Compile contracts."

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

    @property
    def outputs(self) -> Command.PrintedOutputs:
        return Command.PrintedOutputs(
            entry="Building projects' contracts",
            exit_success="Built the project successfully",
            exit_error="Build failed",
        )

    async def run(self, args):
        with ActivityIndicator(log_color_provider.colorize("GRAY", self.outputs.entry)):
            try:
                self._project_compiler.compile(
                    output_dir=args.output,
                    relative_cairo_path=args.cairo_path,
                    disable_hint_validation=args.disable_hint_validation,
                )
            except BaseException as exc:
                self._logger.error(self.outputs.exit_error)
                raise exc
        self._logger.info(self.outputs.exit_success)
