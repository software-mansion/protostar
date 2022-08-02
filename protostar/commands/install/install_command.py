from logging import Logger
from pathlib import Path
from typing import List, Optional

from protostar.cli import Command
from protostar.commands.install.install_package_from_repo import (
    install_package_from_repo,
)
from protostar.commands.install.pull_package_submodules import pull_package_submodules
from protostar.protostar_toml.protostar_project_section import ProtostarProjectSection
from protostar.utils import extract_info_from_repo_id
from protostar.utils.log_color_provider import LogColorProvider

EXTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION = """- `GITHUB_ACCOUNT_NAME/REPO_NAME[@TAG]`
    - `OpenZeppelin/cairo-contracts@0.1.0`
- `URL_TO_THE_REPOSITORY`
    - `https://github.com/OpenZeppelin/cairo-contracts`
- `SSH_URI`
    - `git@github.com:OpenZeppelin/cairo-contracts.git`
"""


class InstallCommand(Command):
    def __init__(
        self,
        project_root_path: Path,
        project_section_loader: ProtostarProjectSection.Loader,
        logger: Logger,
        log_color_provider: LogColorProvider,
    ) -> None:
        super().__init__()
        self._project_root_path = project_root_path
        self._project_section_loader = project_section_loader
        self._logger = logger
        self._log_color_provider = log_color_provider

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
        self.install(
            package_name=args.package,
            alias=args.name,
        )

    def install(
        self,
        package_name: Optional[str],
        alias: Optional[str] = None,
    ) -> None:
        project_section = self._project_section_loader.load()
        libs_path = self._project_root_path / project_section.libs_relative_path

        if package_name:
            package_info = extract_info_from_repo_id(package_name)

            install_package_from_repo(
                alias or package_info.name,
                package_info.url,
                repo_dir=self._project_root_path,
                destination=libs_path,
                tag=package_info.version,
            )
        else:
            pull_package_submodules(
                on_submodule_update_start=lambda package_info: self._logger.info(
                    "Installing %s%s%s %s(%s)%s",
                    self._log_color_provider.get_color("CYAN"),
                    package_info.name,
                    self._log_color_provider.get_color("RESET"),
                    self._log_color_provider.get_color("GRAY"),
                    package_info.url,
                    self._log_color_provider.get_color("RESET"),
                ),
                repo_dir=self._project_root_path,
                libs_dir=libs_path,
            )
