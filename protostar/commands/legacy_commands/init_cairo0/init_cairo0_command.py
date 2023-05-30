from argparse import Namespace
from glob import glob
from logging import getLogger
from typing import Optional

from protostar.cli import ProtostarArgument, ProtostarCommand
from protostar.commands.legacy_commands.init_cairo0.project_creator import (
    NewProjectCreator,
    AdaptedProjectCreator,
)
from protostar.io.input_requester import InputRequester
from protostar.cairo import CairoVersion

logger = getLogger()


class InitCairo0Command(ProtostarCommand):
    def __init__(
        self,
        requester: InputRequester,
        new_project_creator: NewProjectCreator,
        adapted_project_creator: AdaptedProjectCreator,
    ) -> None:
        super().__init__()
        self._adapted_project_creator = adapted_project_creator
        self._new_project_creator = new_project_creator
        self._requester = requester

    @property
    def name(self) -> str:
        return "init-cairo0"

    @property
    def description(self) -> str:
        return "Create a Protostar project with Cairo 0 template."

    @property
    def example(self) -> Optional[str]:
        return "$ protostar init-cairo0"

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
        logger.warning(
            "Legacy cairo 0 projects are deprecated, and support for them will be removed in future versions."
            "Consider using init command instead.",
        )
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
            self._adapted_project_creator.run()
        else:
            self._new_project_creator.run(CairoVersion.cairo0, project_name)

    @staticmethod
    def _can_be_protostar_project() -> bool:
        files_depth_3 = glob("*") + glob("*/*") + glob("*/*/*")
        return any(
            map(lambda f: f.endswith(".cairo") or f == ".git", files_depth_3)
        ) and "protostar.toml" not in glob("*")
