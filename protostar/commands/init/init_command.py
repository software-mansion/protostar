from argparse import Namespace
from glob import glob
from typing import Optional

from protostar.cli import ProtostarArgument, ProtostarCommand
from protostar.commands.init.project_creator.adapted_project_creator import (
    AdaptedProjectCreator,
)
from protostar.commands.init.project_creator.new_project_creator import (
    NewProjectCreator,
)
from protostar.io.input_requester import InputRequester


class InitCommand(ProtostarCommand):
    def __init__(
        self,
        requester: InputRequester,
        new_project_creator: NewProjectCreator,
        adapted_project_creator: AdaptedProjectCreator,
        is_cairo_1: bool = False,
    ) -> None:
        super().__init__()
        self._adapted_project_creator = adapted_project_creator
        self._new_project_creator = new_project_creator
        self._requester = requester
        self._is_cairo_1 = is_cairo_1

    @property
    def name(self) -> str:
        return "init" + ("-cairo1" if self._is_cairo_1 else "")

    @property
    def description(self) -> str:
        return "Create a Protostar project."

    @property
    def example(self) -> Optional[str]:
        return "$ protostar init"

    @property
    def arguments(self):
        return [
            ProtostarArgument(
                name="name",
                description="Name of the directory a new project will be placed in."
                "Ignored when `--existing` is passed.",
                type="str",
                is_positional=True,
            ),
            ProtostarArgument(
                name="existing",
                description="Adapt current directory to a Protostar project.",
                type="bool",
            ),
        ]

    async def run(self, args: Namespace):
        self.init(
            force_adapting_existing_project=args.existing,
            project_name=args.name,
        )

    def init(
        self, force_adapting_existing_project: bool, project_name: Optional[str] = None
    ):
        should_adapt_existing_project = False

        if force_adapting_existing_project:
            should_adapt_existing_project = True
        elif project_name:
            should_adapt_existing_project = False
        else:
            if self._can_be_protostar_project():
                should_adapt_existing_project = self._requester.confirm(
                    "Your current directory may be a Cairo project.\n"
                    "Do you want to adapt current working directory "
                    "as a project instead of creating a new project?."
                )

        if should_adapt_existing_project:
            self._adapted_project_creator.run(self._is_cairo_1)
        else:
            self._new_project_creator.run(self._is_cairo_1, project_name)

    @staticmethod
    def _can_be_protostar_project() -> bool:
        files_depth_3 = glob("*") + glob("*/*") + glob("*/*/*")
        return any(
            map(lambda f: f.endswith(".cairo") or f == ".git", files_depth_3)
        ) and "protostar.toml" not in glob("*")
