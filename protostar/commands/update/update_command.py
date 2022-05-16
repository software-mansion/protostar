from logging import getLogger
from os import listdir
from typing import List, Optional

from protostar.cli import Command
from protostar.commands.remove.remove_command import (
    INTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION,
)
from protostar.commands.update.update_package import update_package
from protostar.commands.update.updating_exceptions import (
    PackageAlreadyUpToDateException,
)
from protostar.utils import Project, retrieve_real_package_name


class UpdateCommand(Command):
    def __init__(self, project: Project) -> None:
        super().__init__()
        self._project = project

    @property
    def name(self) -> str:
        return "update"

    @property
    def description(self) -> str:
        return " ".join(
            [
                "Update a dependency or dependencies.",
                "If the default branch of a dependency's repository uses tags,",
                "Protostar will pull a commit marked with the newest tag.",
                "Otherwise, Protostar will pull a recent commit from the default branch.",
            ]
        )

    @property
    def example(self) -> Optional[str]:
        return "$ protostar update cairo-contracts"

    @property
    def arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                description=INTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION,
                name="package",
                type="str",
                is_positional=True,
            ),
        ]

    async def run(self, args):
        handle_update_command(args, self._project)


def handle_update_command(args, project: Project) -> None:

    logger = getLogger()

    if args.package:
        package_name = retrieve_real_package_name(
            args.package, project.project_root, project.libs_path
        )
        try:
            update_package(package_name, project.project_root, project.libs_path)
        except PackageAlreadyUpToDateException as err:
            logger.info(err.message)
    else:
        for package_name in listdir(project.libs_path):
            try:
                update_package(package_name, project.project_root, project.libs_path)
            except PackageAlreadyUpToDateException:
                continue
