import logging
import os
import sys
import time
from logging import INFO, StreamHandler
from pathlib import Path
from typing import Any, List, Optional

from protostar.argument_parser import CLIApp
from protostar.cli import ProtostarArgument, ProtostarCommand
from protostar.commands import MigrateConfigurationFileCommand
from protostar.compiler import ProjectCairoPathBuilder
from protostar.configuration_file import (
    CommandNamesProviderProtocol,
    ConfigurationFile,
    ConfigurationFileV1,
)
from protostar.configuration_profile_cli import ConfigurationProfileCLI
from protostar.io import LogColorProvider, StandardLogFormatter
from protostar.protostar_exception import ProtostarException, ProtostarExceptionSilent
from protostar.self import (
    CompatibilityResult,
    ProtostarCompatibilityWithProjectCheckerProtocol,
    VersionManager,
)
from protostar.upgrader import LatestVersionChecker


def _apply_pythonpath():
    pythonpath_env_var = os.environ.get("PYTHONPATH") or ""
    split_paths = pythonpath_env_var.split(os.pathsep)
    if split_paths != [""]:
        sys.path.extend(split_paths)


class ProtostarCLI(CLIApp, CommandNamesProviderProtocol):
    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        log_color_provider: LogColorProvider,
        project_cairo_path_builder: ProjectCairoPathBuilder,
        latest_version_checker: LatestVersionChecker,
        version_manager: VersionManager,
        commands: List[ProtostarCommand],
        configuration_file: ConfigurationFile,
        compatibility_checker: ProtostarCompatibilityWithProjectCheckerProtocol,
        start_time: float = 0,
    ) -> None:
        self._latest_version_checker = latest_version_checker
        self._log_color_provider = log_color_provider
        self._version_manager = version_manager
        self._start_time = start_time
        self._configuration_file = configuration_file
        self._project_cairo_path_builder = project_cairo_path_builder
        self._compatibility_checker = compatibility_checker
        super().__init__(
            commands=commands,
            root_args=[
                ConfigurationProfileCLI.PROFILE_ARG,
                ProtostarArgument(
                    name="version",
                    short_name="v",
                    type="bool",
                    description="Show Protostar and Cairo-lang version.",
                ),
                ProtostarArgument(
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
            if args.command is not None and args.command != "init":
                self._warn_if_compatibility_issues_detected()
            await self._run_command_from_args(args)
            if args.command is not None and args.command != "upgrade":
                await self._latest_version_checker.run()
                self._show_configuration_file_depreciation_warning_if_necessary(
                    args.command
                )

        except (ProtostarExceptionSilent, KeyboardInterrupt):
            has_failed = True
        except ProtostarException as err:
            has_failed = True
            self._print_protostar_exception(err)
        self._print_execution_time()
        if has_failed:
            sys.exit(1)

    def get_command_names(self) -> list[str]:
        return list(self._command_mapping.keys())

    def _setup_logger(self, is_ci_mode: bool) -> None:
        self._log_color_provider.is_ci_mode = is_ci_mode
        handler = StreamHandler()
        standard_log_formatter = StandardLogFormatter(self._log_color_provider)
        handler.setFormatter(standard_log_formatter)
        logging.basicConfig(level=INFO, handlers=[handler])

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
            cairo_path_arg = vars(args).get("cairo_path")
            self._extend_pythonpath_with_cairo_path(cairo_path_arg)
            _apply_pythonpath()

        await super().run(args)

    def _print_protostar_exception(self, err: ProtostarException):
        if err.details:
            print(err.details)
        logging.error(err.message)

    def _print_execution_time(self):
        logging.info("Execution time: %.2f s", time.perf_counter() - self._start_time)

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

    def _show_configuration_file_depreciation_warning_if_necessary(
        self, current_command_name: str
    ):
        if (
            isinstance(self._configuration_file, ConfigurationFileV1)
            and current_command_name != MigrateConfigurationFileCommand.NAME
        ):
            instruction = f"protostar {MigrateConfigurationFileCommand.NAME}"
            instruction = self._log_color_provider.bold(instruction)
            instruction = self._log_color_provider.colorize("CYAN", instruction)
            logging.warning(
                "Current configuration file won't be supported in future releases.\n"
                "To update your configuration file, run: %s",
                instruction,
            )

    def _warn_if_compatibility_issues_detected(self):
        output = self._compatibility_checker.check_compatibility()
        compatibility_result = output.compatibility_result

        if compatibility_result == CompatibilityResult.OUTDATED_DECLARED_VERSION:
            logging.warning(
                "This project expects older Protostar (v%s)\n"
                "Please update the declared Protostar version in the project's configuration file,\n"
                "if the project is compatible with Protostar v%s",
                output.declared_protostar_version_str,
                output.protostar_version_str,
            )
        elif compatibility_result == CompatibilityResult.OUTDATED_PROTOSTAR:
            logging.warning(
                "This project expects newer Protostar (v%s)\n"
                "Your Protostar version is v%s\n"
                "Please upgrade Protostar",
                output.declared_protostar_version_str,
                output.protostar_version_str,
            )
