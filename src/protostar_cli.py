# pylint: disable=no-self-use
import sys
from logging import INFO, Logger, StreamHandler, getLogger
from pathlib import Path
from typing import Any, List, Optional

from src.commands import (
    BuildCommand,
    InitCommand,
    InstallCommand,
    RemoveCommand,
    TestCommand,
    UpdateCommand,
    UpgradeCommand,
)
from src.core import CLI, Command
from src.protostar_exception import ProtostarException
from src.utils import (
    Project,
    ProtostarDirectory,
    StandardLogFormatter,
    VersionManager,
    log_color_provider,
)

SCRIPT_ROOT = Path(__file__).parent / ".."
PROTOSTAR_DIRECTORY = ProtostarDirectory(SCRIPT_ROOT)
VERSION_MANAGER = VersionManager(PROTOSTAR_DIRECTORY)
PROJECT = Project(VERSION_MANAGER)

ROOT_ARGS = [
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
]

COMMANDS = [
    InitCommand(SCRIPT_ROOT, VERSION_MANAGER),
    BuildCommand(PROJECT),
    InstallCommand(PROJECT),
    RemoveCommand(PROJECT),
    UpdateCommand(PROJECT),
    UpgradeCommand(PROTOSTAR_DIRECTORY, VERSION_MANAGER),
    TestCommand(PROJECT, PROTOSTAR_DIRECTORY),
]


class ProtostarCLI(CLI):
    def __init__(
        self,
        version_manager: VersionManager,
        commands: Optional[List[Command]] = None,
        root_args: Optional[List[Command.Argument]] = None,
    ) -> None:
        super().__init__(commands, root_args)
        self._version_manager = version_manager

    def _setup_logger(self, is_ci_mode: bool) -> Logger:
        log_color_provider.is_ci_mode = is_ci_mode
        logger = getLogger()
        logger.setLevel(INFO)
        handler = StreamHandler()
        handler.setFormatter(StandardLogFormatter(log_color_provider))
        logger.addHandler(handler)
        return logger

    def _check_git_version(self):
        git_version = self._version_manager.git_version
        if git_version and git_version < VersionManager.parse("2.28"):
            raise ProtostarException(
                f"Protostar requires version 2.28 or greater of Git (current version: {git_version})"
            )

    async def run(self, args: Any) -> bool:
        logger = self._setup_logger(args.no_color)

        try:
            self._check_git_version()

            if args.version:
                self._version_manager.print_current_version()
                return True

            return await super().run(args)
        except ProtostarException as err:
            logger.error(err.message)
        except KeyboardInterrupt:
            sys.exit()
        return False


PROTOSTAR_CLI = ProtostarCLI(VERSION_MANAGER, COMMANDS, ROOT_ARGS)
