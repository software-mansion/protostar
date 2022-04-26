# pylint: disable=no-self-use
import sys
from logging import INFO, Logger, StreamHandler, getLogger
from pathlib import Path
from typing import Any

from src.cli import CLIApp, Command
from src.commands import (
    BuildCommand,
    InitCommand,
    InstallCommand,
    RemoveCommand,
    TestCommand,
    UpdateCommand,
    UpgradeCommand,
)
from src.protostar_exception import ProtostarException
from src.utils import (
    Project,
    ProtostarDirectory,
    StandardLogFormatter,
    VersionManager,
    log_color_provider,
)


class ProtostarCLI(CLIApp):
    @classmethod
    def create(cls, script_root: Path):
        protostar_directory = ProtostarDirectory(script_root)
        version_manager = VersionManager(protostar_directory)
        project = Project(version_manager)
        return cls(script_root, protostar_directory, project, version_manager)

    def __init__(
        self,
        script_root: Path,
        protostar_directory: ProtostarDirectory,
        project: Project,
        version_manager: VersionManager,
    ) -> None:
        self.project = project
        super().__init__(
            commands=[
                InitCommand(script_root, version_manager),
                BuildCommand(project),
                InstallCommand(project),
                RemoveCommand(project),
                UpdateCommand(project),
                UpgradeCommand(protostar_directory, version_manager),
                TestCommand(project, protostar_directory),
            ],
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
        )
        self.version_manager = version_manager

    def _setup_logger(self, is_ci_mode: bool) -> Logger:
        log_color_provider.is_ci_mode = is_ci_mode
        logger = getLogger()
        logger.setLevel(INFO)
        handler = StreamHandler()
        handler.setFormatter(StandardLogFormatter(log_color_provider))
        logger.addHandler(handler)
        return logger

    def _check_git_version(self):
        git_version = self.version_manager.git_version
        if git_version and git_version < VersionManager.parse("2.28"):
            raise ProtostarException(
                f"Protostar requires version 2.28 or greater of Git (current version: {git_version})"
            )

    async def run(self, args: Any) -> bool:
        logger = self._setup_logger(args.no_color)

        try:
            self._check_git_version()

            if args.version:
                self.version_manager.print_current_version()
                return True

            return await super().run(args)
        except ProtostarException as err:
            logger.error(err.message)
        except KeyboardInterrupt:
            sys.exit()
        return False
