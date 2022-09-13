import os
import sys
import time
from logging import INFO, Logger, StreamHandler
from pathlib import Path
from typing import Any, List, Optional

from protostar.cli import CLIApp, Command
from protostar.compiler import ProjectCairoPathBuilder
from protostar.configuration_profile_cli import ConfigurationProfileCLI
from protostar.protostar_exception import ProtostarException, ProtostarExceptionSilent
from protostar.protostar_toml.protostar_toml_version_checker import (
    ProtostarTOMLVersionChecker,
)
from protostar.upgrader import LatestVersionChecker
from protostar.utils import StandardLogFormatter, VersionManager
from protostar.utils.log_color_provider import LogColorProvider


def _consume_pythonpath():
    pythonpath_env_var = os.environ.get("PYTHONPATH") or ""
    split_paths = pythonpath_env_var.split(":")
    if split_paths != [""]:
        sys.path.extend(split_paths)


class ProtostarCLI(CLIApp):
    def __init__(
        self,
        logger: Logger,
        log_color_provider: LogColorProvider,
        project_cairo_path_builder: ProjectCairoPathBuilder,
        latest_version_checker: LatestVersionChecker,
        protostar_toml_version_checker: ProtostarTOMLVersionChecker,
        version_manager: VersionManager,
        commands: List[Command],
        start_time: float = 0,
    ) -> None:
        self._logger = logger
        self._latest_version_checker = latest_version_checker
        self._log_color_provider = log_color_provider
        self._version_manager = version_manager
        self._protostar_toml_version_checker = protostar_toml_version_checker
        self._start_time = start_time
        self._project_cairo_path_builder = project_cairo_path_builder

        super().__init__(
            commands=commands,
            root_args=[
                ConfigurationProfileCLI.PROFILE_ARG,
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

    async def run(self, args: Any) -> None:
        has_failed = False
        try:
            self._setup_logger(args.no_color)
            self._check_git_version()
            await self._run_command_from_args(args)
            await self._latest_version_checker.run()
        except (ProtostarExceptionSilent, KeyboardInterrupt):
            has_failed = True
        except ProtostarException as err:
            has_failed = True
            self._print_protostar_exception(err)
        self._print_execution_time()
        if has_failed:
            sys.exit(1)

    def _setup_logger(self, is_ci_mode: bool) -> None:
        self._log_color_provider.is_ci_mode = is_ci_mode
        handler = StreamHandler()
        standard_log_formatter = StandardLogFormatter(self._log_color_provider)
        handler.setFormatter(standard_log_formatter)
        self._logger.setLevel(INFO)
        self._logger.addHandler(handler)

    def _check_git_version(self):
        git_version = self._version_manager.git_version
        if git_version and git_version < VersionManager.parse("2.28"):
            raise ProtostarException(
                f"Protostar requires version 2.28 or greater of Git (current version: {git_version})"
            )

    async def _run_command_from_args(self, args: Any) -> None:
        if args.version:
            self._version_manager.print_current_version()
            return

        # FIXME(arcticae): Those should be run when command is running in project context
        if args.command not in ["init", "upgrade"]:
            self._protostar_toml_version_checker.run()
            cairo_path_arg = vars(args).get("cairo_path")
            self._extend_pythonpath_with_cairo_path(cairo_path_arg)
            _consume_pythonpath()

        await super().run(args)

    def _print_protostar_exception(self, err: ProtostarException):
        if err.details:
            print(err.details)
        self._logger.error(err.message)

    def _print_execution_time(self):
        self._logger.info(
            "Execution time: %.2f s", time.perf_counter() - self._start_time
        )

    def _extend_pythonpath_with_cairo_path(
        self, cairo_path_arg: Optional[List[Path]] = None
    ):
        cairo_path_list = (
            str(path)
            for path in self._project_cairo_path_builder.build_project_cairo_path_list(
                cairo_path_arg or []
            )
        )
        sys.path.extend(cairo_path_list)
