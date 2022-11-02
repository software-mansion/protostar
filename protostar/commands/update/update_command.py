from argparse import Namespace
from logging import Logger
from os import listdir
from pathlib import Path
from typing import Optional

from protostar.cli import (
    LIB_PATH_ARG,
    LibPathResolver,
    ProtostarArgument,
    ProtostarCommand,
)
from protostar.commands.remove.remove_command import (
    INTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION,
)
from protostar.commands.update.update_package import update_package
from protostar.commands.update.updating_exceptions import (
    PackageAlreadyUpToDateException,
)
from protostar.package_manager import retrieve_real_package_name


class UpdateCommand(ProtostarCommand):
    def __init__(
        self,
        project_root_path: Path,
        lib_path_resolver: LibPathResolver,
        logger: Logger,
    ) -> None:
        super().__init__()
        self._project_root_path = project_root_path
        self._lib_path_resolver = lib_path_resolver
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
    def arguments(self):
        return [
            LIB_PATH_ARG,
            ProtostarArgument(
                description=INTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION,
                name="package",
                type="str",
                is_positional=True,
            ),
        ]

    async def run(self, args: Namespace):
        self._logger.info("Running dependency update")
        try:
            self.update(
                args.package, lib_path=self._lib_path_resolver.resolve(args.lib_path)
            )
        except BaseException as exc:
            self._logger.error("Update command failed")
            raise exc
        self._logger.info("Updated successfully")

    def update(self, package: Optional[str], lib_path: Path) -> None:
        if not lib_path.exists():
            self._logger.warning(
                f"Directory {lib_path} doesn't exist.\n"
                "Did you install any package before running this command?"
            )
            return

        if package:
            package = retrieve_real_package_name(
                package, self._project_root_path, packages_dir=lib_path
            )
            try:
                update_package(package, self._project_root_path, packages_dir=lib_path)
            except PackageAlreadyUpToDateException as err:
                self._logger.info(err.message)
        else:
            for package_name in listdir(lib_path or self._project_root_path / "lib"):
                try:
                    update_package(
                        package_name,
                        self._project_root_path,
                        packages_dir=lib_path,
                    )
                except PackageAlreadyUpToDateException:
                    continue
