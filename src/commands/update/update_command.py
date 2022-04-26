from logging import getLogger
from os import listdir
from typing import List, Optional

from src.cli import Command
from src.commands.remove.remove_command import INTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION
from src.commands.update.update_package import update_package
from src.commands.update.updating_exceptions import PackageAlreadyUpToDateException
from src.utils import Project, retrieve_real_package_name


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
    assert args.command == "update"

    root_repo_dir = project.project_root
    packages_dir = project.project_root / project.config.libs_path
    logger = getLogger()

    if args.package:
        package_name = retrieve_real_package_name(
            args.package, root_repo_dir, packages_dir
        )
        try:
            update_package(package_name, root_repo_dir, packages_dir)
        except PackageAlreadyUpToDateException as err:
            logger.info(err.message)
    else:
        for package_name in listdir(packages_dir):
            try:
                update_package(package_name, root_repo_dir, packages_dir)
            except PackageAlreadyUpToDateException:
                continue
