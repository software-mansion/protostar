from argparse import Namespace
from typing import Optional

from protostar.cli import ProtostarArgument, ProtostarCommand
from protostar.cairo import CairoVersion
from protostar.commands.legacy_commands.init_cairo0.project_creator.new_project_creator import (
    NewProjectCreator,
)


class InitCommand(ProtostarCommand):
    def __init__(
        self,
        new_project_creator: NewProjectCreator,
    ) -> None:
        super().__init__()
        self._new_project_creator = new_project_creator

    @property
    def name(self) -> str:
        return "init"

    @property
    def description(self) -> str:
        return "Create a Protostar project with Cairo 1 template."

    @property
    def example(self) -> Optional[str]:
        return "$ protostar init"

    @property
    def arguments(self):
        return [
            ProtostarArgument(
                name="name",
                description="The name of the directory a new project will be placed in.",
                type="str",
                is_positional=True,
            ),
            ProtostarArgument(
                name="minimal",
                type="bool",
                default=False,
                description="Create a minimal project structure.",
            ),
        ]

    async def run(self, args: Namespace):
        self.init(project_name=args.name, minimal=args.minimal)

    def init(self, minimal: bool, project_name: Optional[str] = None):
        self._new_project_creator.run(
            cairo_version=CairoVersion.cairo1,
            project_name=project_name,
            minimal=minimal,
        )
