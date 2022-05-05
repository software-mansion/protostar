from logging import getLogger
from typing import Any, List, Optional

from src.cli import Command
from src.commands.install.install_command import (
    EXTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION,
)
from src.commands.remove.remove_package import remove_package
from src.utils import Project, log_color_provider, retrieve_real_package_name

INTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION = (
    EXTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION
    + "- `PACKAGE_DIRECTORY_NAME`\n"
    + "    - `cairo_contracts`, if the package location is `lib/cairo_contracts`"
)


class RemoveCommand(Command):
    def __init__(self, project: Project) -> None:
        super().__init__()
        self._project = project

    @property
    def name(self) -> str:
        return "remove"

    @property
    def description(self) -> str:
        return "Remove a dependency."

    @property
    def example(self) -> Optional[str]:
        return "$ protostar remove cairo-contracts"

    @property
    def arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="package",
                description=INTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION,
                type="str",
                is_required=True,
                is_positional=True,
            ),
        ]

    async def run(self, args):
        handle_remove_command(args, self._project)


# TODO: https://github.com/software-mansion/protostar/issues/241
def handle_remove_command(args: Any, project: Project):
    logger = getLogger()
    assert args.command == "remove"

    package_name = retrieve_real_package_name(
        args.package,
        project.project_root,
        project.project_root / project.config.libs_path,
    )

    logger.info(
        "Removing %s%s%s",
        log_color_provider.get_color("RED"),
        package_name,
        log_color_provider.get_color("RESET"),
    )
    remove_package(package_name, project.project_root)
