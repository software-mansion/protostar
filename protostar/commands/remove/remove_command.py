from logging import Logger
from pathlib import Path
from typing import List, Optional

from protostar.cli import Command
from protostar.commands.install.install_command import (
    EXTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION,
)
from protostar.commands.remove.remove_package import remove_package
from protostar.protostar_toml.protostar_project_section import ProtostarProjectSection
from protostar.utils import log_color_provider, retrieve_real_package_name

INTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION = (
    EXTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION
    + "- `PACKAGE_DIRECTORY_NAME`\n"
    + "    - `cairo_contracts`, if the package location is `lib/cairo_contracts`"
)


class RemoveCommand(Command):
    def __init__(
        self,
        project_root_path: Path,
        project_section_loader: ProtostarProjectSection.Loader,
        logger: Logger,
    ) -> None:
        super().__init__()
        self._project_root_path = project_root_path
        self._project_section_loader = project_section_loader
        self._logger = logger

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
        self._logger.info("Retrieving package for removal")
        try:
            self.remove(args.package)
        except BaseException as exc:
            self._logger.error("Package removal failed")
            raise exc
        self._logger.info("Removed the package successfully")

    def remove(self, internal_dependency_reference: str):
        project_section = self._project_section_loader.load()

        package_name = retrieve_real_package_name(
            internal_dependency_reference,
            self._project_root_path,
            project_section.libs_relative_path,
        )

        self._logger.info(
            "Removing %s%s%s",
            log_color_provider.get_color("RED"),
            package_name,
            log_color_provider.get_color("RESET"),
        )
        remove_package(package_name, self._project_root_path)
