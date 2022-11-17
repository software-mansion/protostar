import logging
from argparse import Namespace
from pathlib import Path
from typing import Optional

from protostar.cli import (
    LIB_PATH_ARG,
    LibPathResolver,
    ProtostarArgument,
    ProtostarCommand,
)
from protostar.commands.install.install_command import (
    EXTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION,
)
from protostar.commands.remove.remove_package import remove_package
from protostar.io import log_color_provider
from protostar.package_manager import retrieve_real_package_name

INTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION = (
    EXTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION
    + "- `PACKAGE_DIRECTORY_NAME`\n"
    + "    - `cairo_contracts`, if the package location is `lib/cairo_contracts`"
)


class RemoveCommand(ProtostarCommand):
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
        return "remove"

    @property
    def description(self) -> str:
        return "Remove a dependency."

    @property
    def example(self) -> Optional[str]:
        return "$ protostar remove cairo-contracts"

    @property
    def arguments(self):
        return [
            LIB_PATH_ARG,
            ProtostarArgument(
                name="package",
                description=INTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION,
                type="str",
                is_required=True,
                is_positional=True,
            ),
        ]

    async def run(self, args: Namespace):
        logging.info("Retrieving package for removal")
        try:
            self.remove(
                args.package, lib_path=self._lib_path_resolver.resolve(args.lib_path)
            )
        except BaseException as exc:
            logging.error("Package removal failed")
            raise exc
        logging.info("Removed the package successfully")

    def remove(self, internal_dependency_reference: str, lib_path: Path):
        if not lib_path.exists():
            logging.warning(
                "Directory %s doesn't exist.\n"
                "Did you install any package before running this command?",
                lib_path,
            )
            return
        package_name = retrieve_real_package_name(
            internal_dependency_reference,
            self._project_root_path,
            packages_dir=lib_path,
        )
        logging.info(
            "Removing %s%s%s",
            log_color_provider.get_color("RED"),
            package_name,
            log_color_provider.get_color("RESET"),
        )
        remove_package(package_name, self._project_root_path)
