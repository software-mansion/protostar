import logging
from argparse import Namespace
from os import listdir
from pathlib import Path
from typing import Optional

from protostar.cli import LibPathResolver, ProtostarCommand
from protostar.cli.common_arguments import (
    PACKAGE_ARG,
    LIB_PATH_ARG,
    INTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION,
)
from protostar.package_manager import retrieve_real_package_name

from .update_package import update_package
from .updating_exceptions import PackageAlreadyUpToDateException


class UpdateCommand(ProtostarCommand):
    def __init__(
        self,
        project_root_path: Path,
        lib_path_resolver: LibPathResolver,
    ) -> None:
        super().__init__()
        self._project_root_path = project_root_path
        self._lib_path_resolver = lib_path_resolver

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
            PACKAGE_ARG.copy_with(
                description=INTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION,
            ),
        ]

    async def run(self, args: Namespace):
        logging.info("Running dependency update")
        try:
            self.update(
                args.package, lib_path=self._lib_path_resolver.resolve(args.lib_path)
            )
        except BaseException as exc:
            logging.error("Update command failed")
            raise exc
        logging.info("Updated successfully")

    def update(self, package: Optional[str], lib_path: Path) -> None:
        if not lib_path.exists():
            logging.warning(
                "Directory %s doesn't exist.\n"
                "Did you install any package before running this command?",
                lib_path,
            )
            return

        if package:
            package = retrieve_real_package_name(
                package, self._project_root_path, packages_dir=lib_path
            )
            try:
                update_package(package, self._project_root_path, packages_dir=lib_path)
            except PackageAlreadyUpToDateException as err:
                logging.info(err.message)
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
