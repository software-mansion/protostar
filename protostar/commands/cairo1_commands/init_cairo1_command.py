from argparse import Namespace
from typing import Optional

from protostar.cli import ProtostarArgument, ProtostarCommand
from protostar.commands.init.project_creator.new_project_creator import (
    NewProjectCreator,
)
from protostar.cairo import CairoVersion


class InitCairo1Command(ProtostarCommand):
    def __init__(
        self,
        new_project_creator: NewProjectCreator,
    ) -> None:
        super().__init__()
        self._new_project_creator = new_project_creator

    @property
    def name(self) -> str:
        return "init-cairo1"

    @property
    def description(self) -> str:
        return "Create a Protostar project with cairo1 template."

    @property
    def example(self) -> Optional[str]:
        return "$ protostar init-cairo1"

    @property
    def arguments(self):
        return [
            ProtostarArgument(
                name="name",
                description="Name of the directory a new project will be placed in.",
                type="str",
                is_positional=True,
            ),
        ]

    async def run(self, args: Namespace):
        self.init(project_name=args.name)

    def init(self, project_name: Optional[str] = None):
        self._new_project_creator.run(
            cairo_version=CairoVersion.cairo1, project_name=project_name
        )
