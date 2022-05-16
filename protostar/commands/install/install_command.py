from logging import getLogger
from typing import Any, List, Optional

from protostar.cli import Command
from protostar.commands.install.install_package_from_repo import (
    install_package_from_repo,
)
from protostar.commands.install.pull_package_submodules import pull_package_submodules
from protostar.utils import Project, extract_info_from_repo_id, log_color_provider

EXTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION = """- `GITHUB_ACCOUNT_NAME/REPO_NAME[@TAG]`
    - `OpenZeppelin/cairo-contracts@0.1.0`
- `URL_TO_THE_REPOSITORY`
    - `https://github.com/OpenZeppelin/cairo-contracts`
- `SSH_URI`
    - `git@github.com:OpenZeppelin/cairo-contracts.git`
"""


class InstallCommand(Command):
    def __init__(self, project: Project) -> None:
        super().__init__()
        self._project = project

    @property
    def name(self) -> str:
        return "install"

    @property
    def description(self) -> str:
        return "Install a dependency as a git submodule."

    @property
    def example(self) -> Optional[str]:
        return "$ protostar install https://github.com/OpenZeppelin/cairo-contracts"

    @property
    def arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="package",
                description=EXTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION,
                type="str",
                is_positional=True,
            ),
            Command.Argument(
                name="name",
                description="A custom package name. Use it to resolve name conflicts.",
                type="str",
            ),
        ]

    async def run(self, args):
        handle_install_command(args, self._project)


def handle_install_command(args: Any, project: Project) -> None:
    logger = getLogger()

    if args.package is not None and args.package != "":
        package_info = extract_info_from_repo_id(args.package)

        install_package_from_repo(
            package_info.name if args.name is None else args.name,
            package_info.url,
            repo_dir=project.project_root,
            destination=project.libs_path,
            tag=package_info.version,
        )
    else:
        pull_package_submodules(
            on_submodule_update_start=lambda package_info: logger.info(
                "Installing %s%s%s %s(%s)%s",
                log_color_provider.get_color("CYAN"),
                package_info.name,
                log_color_provider.get_color("RESET"),
                log_color_provider.get_color("GRAY"),
                package_info.url,
                log_color_provider.get_color("RESET"),
            ),
            repo_dir=project.project_root,
            libs_dir=project.libs_path,
        )
