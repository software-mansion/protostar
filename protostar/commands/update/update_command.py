from logging import Logger
from os import listdir
from pathlib import Path
from typing import List, Optional

from protostar.cli import Command
from protostar.commands.remove.remove_command import (
    INTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION,
)
from protostar.commands.update.update_package import update_package
from protostar.commands.update.updating_exceptions import (
    PackageAlreadyUpToDateException,
)
from protostar.protostar_toml.protostar_project_section import ProtostarProjectSection
from protostar.utils import retrieve_real_package_name


class UpdateCommand(Command):
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
        self._logger.info("Running dependency update")
        try:
            self.update(args.package)
        except BaseException as exc:
            self._logger.error("Update command failed")
            raise exc
        self._logger.info("Updated successfully")

    def update(self, package: Optional[str]) -> None:
        project_section = self._project_section_loader.load()

        if package:
            package = retrieve_real_package_name(
                package, self._project_root_path, project_section.libs_relative_path
            )
            try:
                update_package(
                    package, self._project_root_path, project_section.libs_relative_path
                )
            except PackageAlreadyUpToDateException as err:
                self._logger.info(err.message)
        else:
            for package_name in listdir(project_section.libs_relative_path):
                try:
                    update_package(
                        package_name,
                        self._project_root_path,
                        project_section.libs_relative_path,
                    )
                except PackageAlreadyUpToDateException:
                    continue
