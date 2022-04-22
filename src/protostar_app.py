# pylint: disable=no-self-use
from logging import INFO, StreamHandler, getLogger
from pathlib import Path
from typing import Any

from src.commands import BuildCommand, InitCommand
from src.core import Application, Command
from src.protostar_exception import ProtostarException
from src.utils import (
    Project,
    ProtostarDirectory,
    StandardLogFormatter,
    VersionManager,
    log_color_provider,
)

SCRIPT_ROOT = Path(__file__).parent / ".."
protostar_directory = ProtostarDirectory(SCRIPT_ROOT)
version_manager = VersionManager(protostar_directory)
current_project = Project(version_manager)


class ProtostarApplication(Application):
    def _setup_logger(self, is_ci_mode: bool):
        log_color_provider.is_ci_mode = is_ci_mode
        logger = getLogger()
        logger.setLevel(INFO)
        handler = StreamHandler()
        handler.setFormatter(StandardLogFormatter(log_color_provider))
        logger.addHandler(handler)

    def _check_git_version(self):
        git_version = version_manager.git_version
        if git_version and git_version < VersionManager.parse("2.28"):
            raise ProtostarException(
                f"Protostar requires version 2.28 or greater of Git (current version: {git_version})"
            )

    async def run(self, args: Any) -> bool:
        self._setup_logger(args.no_color)
        self._check_git_version()

        if args.version:
            version_manager.print_current_version()
            return True

        return await super().run(args)


protostar_app = ProtostarApplication(
    root_args=[
        Command.Argument(
            name="version",
            short_name="v",
            type="bool",
            description="Show Protostar and Cairo-lang version.",
        ),
        Command.Argument(
            name="no-color",
            type="bool",
            description="Disable colors.",
        ),
    ],
    commands=[InitCommand(SCRIPT_ROOT, version_manager), BuildCommand(current_project)],
)
