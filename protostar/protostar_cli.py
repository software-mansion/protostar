# pylint: disable=no-self-use
import sys
import time
from logging import INFO, Logger, StreamHandler
from typing import Any, List

from protostar.cli import CLIApp, Command
from protostar.configuration_profile_cli import ConfigurationProfileCLI
from protostar.protostar_exception import ProtostarException, ProtostarExceptionSilent

from protostar.protostar_toml.protostar_toml_version_checker import (
    ProtostarTOMLVersionChecker,
)
from protostar.upgrader import LatestVersionChecker
from protostar.utils import StandardLogFormatter, VersionManager
from protostar.utils.log_color_provider import LogColorProvider


class ProtostarCLI(CLIApp):
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        logger: Logger,
        log_color_provider: LogColorProvider,
        latest_version_checker: LatestVersionChecker,
        toml_version_checker: ProtostarTOMLVersionChecker,
        version_manager: VersionManager,
        commands: List[Command],
        start_time=0.0,
    ) -> None:
        self._logger = logger
        self._latest_version_checker = latest_version_checker
        self._start_time = start_time
        self._log_color_provider = log_color_provider
        self._version_manager = version_manager
        self._toml_version_checker = toml_version_checker

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
        if args.command in ["init", "upgrade"]:
            self._toml_version_checker.run(args)

        await super().run(args)

    def _print_protostar_exception(self, err: ProtostarException):
        if err.details:
            print(err.details)
        self._logger.error(err.message)

    def _print_execution_time(self):
        self._logger.info(
            "Execution time: %.2f s", time.perf_counter() - self._start_time
        )
