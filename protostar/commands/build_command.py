from pathlib import Path
from typing import List, Optional, Any

from protostar.cli import ProtostarArgument, ProtostarCommand, MessengerFactory
from protostar.cli.common_arguments import COMPILED_CONTRACTS_DIR_ARG
from protostar.compiler import ProjectCompiler, ProjectCompilerConfig
from protostar.io import LogColorProvider, Message


class BuildActivityMessageTemplate(Message):
    def format_human(self, fmt: LogColorProvider) -> str:
        return "Building projects' contracts"


class BuildCommand(ProtostarCommand):
    def __init__(
        self,
        project_compiler: ProjectCompiler,
        messenger_factory: MessengerFactory,
    ):
        super().__init__()
        self._project_compiler = project_compiler
        self._messenger_factory = messenger_factory

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
    def arguments(self):
        return [
            ProtostarArgument(
                name="cairo-path",
                description="Additional directories to look for sources.",
                type="directory",
                is_array=True,
            ),
            ProtostarArgument(
                name="disable-hint-validation",
                description="Disable validation of hints when building the contracts.",
                type="bool",
            ),
            COMPILED_CONTRACTS_DIR_ARG,
        ]

    async def run(self, args: Any):
        write = self._messenger_factory.human()

        with write.activity(BuildActivityMessageTemplate()):
            await self.build(
                output_dir=args.compiled_contracts_dir,
                disable_hint_validation=args.disable_hint_validation,
                relative_cairo_path=args.cairo_path,
            )

    async def build(
        self,
        output_dir: Path,
        disable_hint_validation: bool = False,
        relative_cairo_path: Optional[List[Path]] = None,
    ):
        self._project_compiler.compile_project(
            output_dir=output_dir,
            config=ProjectCompilerConfig(
                hint_validation_disabled=disable_hint_validation,
                relative_cairo_path=relative_cairo_path or [],
            ),
        )
