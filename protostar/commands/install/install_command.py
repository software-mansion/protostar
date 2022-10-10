from logging import Logger
from pathlib import Path
from typing import Callable, List, Optional

from protostar.argument_parser import Command
from protostar.commands.install.install_package_from_repo import (
    install_package_from_repo,
)
from protostar.commands.install.pull_package_submodules import pull_package_submodules
from protostar.io.log_color_provider import LogColorProvider
from protostar.package_manager import extract_info_from_repo_id
from protostar.protostar_toml.protostar_project_section import ProtostarProjectSection

EXTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION = """- `GITHUB_ACCOUNT_NAME/REPO_NAME[@TAG]`
    - `OpenZeppelin/cairo-contracts@v0.4.0`
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
        self._logger.info("Executing install")
        try:
            self.install(
                package_name=args.package,
                on_unknown_version=lambda: self._logger.warning(
                    (
                        "Fetching from the mainline. The mainline can be in the non-releasable state.\n"
                        "Installing packages without providing specific version/tag is strongly discouraged."
                    )
                ),
                alias=args.name,
            )
        except BaseException as exc:
            self._logger.error("Installation failed")
            raise exc
        self._logger.info("Installed successfully")

    def install(
        self,
        package_name: Optional[str],
        on_unknown_version: Callable,
        alias: Optional[str] = None,
    ) -> None:
        project_section = self._project_section_loader.load()
        libs_path = self._project_root_path / project_section.libs_relative_path

        if package_name:
            package_info = extract_info_from_repo_id(package_name)
            if package_info.version is None:
                on_unknown_version()
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
