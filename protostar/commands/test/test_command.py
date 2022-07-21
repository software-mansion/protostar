from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from protostar.cli.activity_indicator import ActivityIndicator
from protostar.cli.command import Command
from protostar.commands.test.test_collector import TestCollector
from protostar.commands.test.test_runner import TestRunner
from protostar.commands.test.test_scheduler import TestScheduler
from protostar.commands.test.testing_live_logger import TestingLiveLogger
from protostar.commands.test.testing_summary import TestingSummary
from protostar.utils.compiler.pass_managers import (
    StarknetPassManagerFactory,
    TestCollectorPassManagerFactory,
)
from protostar.utils.log_color_provider import log_color_provider
from protostar.utils.protostar_directory import ProtostarDirectory
from protostar.utils.starknet_compilation import CompilerConfig, StarknetCompiler

if TYPE_CHECKING:
    from protostar.commands.build.project_compiler import ProjectCompiler


class TestCommand(Command):
    def __init__(
        self,
        project_root_path: Path,
        protostar_directory: ProtostarDirectory,
        project_compiler: "ProjectCompiler",
    ) -> None:
        super().__init__()
        self._project_root_path = project_root_path
        self._protostar_directory = protostar_directory
        self._project_compiler = project_compiler

    @property
    def name(self) -> str:
        return "test"

    @property
    def description(self) -> str:
        return "Execute tests."

    @property
    def example(self) -> Optional[str]:
        return "$ protostar test"

    @property
    def arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="target",
                description=(
                    "A glob or globs to a directory or a test suite, for example:\n"
                    "- `tests/**/*_main*::*_balance` — "
                    "find test cases, which names ends with `_balance` in test suites with the `_main` "
                    "in filenames in the `tests` directory\n"
                    "- `::test_increase_balance` — "
                    "find `test_increase_balance` test_cases in any test suite within the project \n"
                ),
                type="str",
                is_array=True,
                is_positional=True,
                default=["tests"],
            ),
            Command.Argument(
                name="ignore",
                short_name="i",
                description=(
                    "A glob or globs to a directory or a test suite, which should be ignored.\n"
                ),
                is_array=True,
                type="str",
            ),
            Command.Argument(
                name="cairo-path",
                is_array=True,
                description="Additional directories to look for sources.",
                type="directory",
            ),
            Command.Argument(
                name="disable-hint-validation",
                description=(
                    "Disable hint validation in contracts declared by the "
                    "`declare` cheatcode or deployed by `deploy_contract` cheatcode.\n"
                ),
                type="bool",
            ),
            Command.Argument(
                name="no-progress-bar",
                type="bool",
                description="Disable progress bar.",
            ),
            Command.Argument(
                name="fast-collecting",
                type="bool",
                description=(
                    "Enables fast but unsafe test collecting algorithm. "
                    "It searches for identifiers in the test file that start with `test_`."
                ),
            ),
            Command.Argument(
                name="safe-collecting",
                type="bool",
                description=("Uses cairo compiler for test collection"),
            ),
            Command.Argument(
                name="exit-first",
                short_name="x",
                type="bool",
                description="Exit immediately on first broken or failed test",
            ),
            Command.Argument(
                name="stdout-on-success",
                type="bool",
                description="Also print captured standard output for passed test cases.",
            ),
        ]

    async def run(self, args) -> TestingSummary:
        summary = await self.test(
            targets=args.target,
            ignored_targets=args.ignore,
            cairo_path=args.cairo_path,
            disable_hint_validation=args.disable_hint_validation,
            no_progress_bar=args.no_progress_bar,
            fast_collecting=args.fast_collecting,
            safe_collecting=args.safe_collecting,
            exit_first=args.exit_first,
            stdout_on_success=args.stdout_on_success,
        )
        summary.assert_all_passed()
        return summary

    # pylint: disable=too-many-arguments
    async def test(
        self,
        targets: List[str],
        ignored_targets: Optional[List[str]] = None,
        cairo_path: Optional[List[Path]] = None,
        disable_hint_validation: bool = False,
        no_progress_bar: bool = False,
        fast_collecting: bool = False,
        safe_collecting: bool = False,
        exit_first: bool = False,
        stdout_on_success: bool = False,
    ) -> TestingSummary:
        logger = getLogger()
        include_paths = [
            str(path)
            for path in [
                self._protostar_directory.protostar_test_only_cairo_packages_path,
                *self._project_compiler.build_cairo_path(cairo_path or []),
            ]
        ]
        factory = (
            StarknetPassManagerFactory
            if safe_collecting
            else TestCollectorPassManagerFactory
        )

        assert (
            not fast_collecting
        ), "`--fast-collecting` is deprecated, use default strategy"
        with ActivityIndicator(log_color_provider.colorize("GRAY", "Collecting tests")):
            test_collector_result = TestCollector(
                StarknetCompiler(
                    config=CompilerConfig(
                        disable_hint_validation=True, include_paths=include_paths
                    ),
                    pass_manager_factory=factory,
                ),
                config=TestCollector.Config(fast_collecting=fast_collecting),
            ).collect(
                targets=targets,
                ignored_targets=ignored_targets,
                default_test_suite_glob=str(self._project_root_path),
            )
        test_collector_result.log(logger)

        testing_summary = TestingSummary(
            case_results=test_collector_result.broken_test_suites  # type: ignore | pyright bug?
        )

        if test_collector_result.test_cases_count > 0:
            live_logger = TestingLiveLogger(
                logger,
                testing_summary,
                no_progress_bar=no_progress_bar,
                exit_first=exit_first,
                stdout_on_success=stdout_on_success,
            )
            TestScheduler(live_logger, worker=TestRunner.worker).run(
                include_paths=include_paths,
                test_collector_result=test_collector_result,
                disable_hint_validation=disable_hint_validation,
                exit_first=exit_first,
            )

        return testing_summary
