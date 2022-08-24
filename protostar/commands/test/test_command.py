# pylint: disable=too-many-arguments

from logging import Logger
from pathlib import Path
from typing import List, Optional

from protostar.cli.activity_indicator import ActivityIndicator
from protostar.cli.command import Command
from protostar.commands.test.environments.fuzz_test_execution_environment import (
    FuzzConfig,
)
from protostar.commands.test.test_collector import TestCollector
from protostar.commands.test.test_collector_summary_formatter import (
    format_test_collector_summary,
)
from protostar.commands.test.test_result_formatter import format_test_result
from protostar.commands.test.test_results import TestResult
from protostar.commands.test.test_runner import TestRunner
from protostar.commands.test.test_scheduler import TestScheduler
from protostar.commands.test.testing_live_logger import TestingLiveLogger
from protostar.commands.test.testing_seed import TestingSeed
from protostar.commands.test.testing_summary import TestingSummary
from protostar.compiler import ProjectCairoPathBuilder
from protostar.utils.compiler.pass_managers import (
    StarknetPassManagerFactory,
    TestCollectorPassManagerFactory,
)
from protostar.utils.log_color_provider import LogColorProvider
from protostar.utils.protostar_directory import ProtostarDirectory
from protostar.utils.starknet_compilation import CompilerConfig, StarknetCompiler


class TestCommand(Command):
    def __init__(
        self,
        project_root_path: Path,
        protostar_directory: ProtostarDirectory,
        project_cairo_path_builder: ProjectCairoPathBuilder,
        log_color_provider: LogColorProvider,
        logger: Logger,
    ) -> None:
        super().__init__()
        self._logger = logger
        self._log_color_provider = log_color_provider
        self._project_root_path = project_root_path
        self._protostar_directory = protostar_directory
        self._project_cairo_path_builder = project_cairo_path_builder

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
                description="""
A glob or globs to a directory or a test suite, for example:
- `tests/**/*_main*::*_balance` — find test cases, which names ends with `_balance` in test suites with the `_main` in filenames in the `tests` directory,
- `::test_increase_balance` — find `test_increase_balance` test_cases in any test suite within the project.   
""".strip(),
                type="str",
                is_array=True,
                is_positional=True,
                default=["."],
            ),
            Command.Argument(
                name="ignore",
                short_name="i",
                description=(
                    "A glob or globs to a directory or a test suite, which should be ignored."
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
                    "`declare` cheatcode or deployed by `deploy_contract` cheatcode."
                ),
                type="bool",
            ),
            Command.Argument(
                name="no-progress-bar",
                type="bool",
                description="Disable progress bar.",
            ),
            Command.Argument(
                name="safe-collecting",
                type="bool",
                description="Use Cairo compiler for test collection.",
            ),
            Command.Argument(
                name="exit-first",
                short_name="x",
                type="bool",
                description="Exit immediately on first broken or failed test.",
            ),
            Command.Argument(
                name="seed",
                type="int",
                description="Set a seed to use for all fuzz tests.",
            ),
            # TODO(mkaput): Remove this.
            Command.Argument(
                name="fuzz-max-examples",
                type="int",
                default=100,
                description=(
                    "Once this many satisfying examples have been considered "
                    "without finding any counter-example, falsification will terminate."
                ),
            ),
            Command.Argument(
                name="report-slowest-tests",
                type="int",
                description="Print slowest tests at the end.",
                default=0,
            ),
        ]

    async def run(self, args) -> TestingSummary:
        summary = await self.test(
            targets=args.target,
            ignored_targets=args.ignore,
            cairo_path=args.cairo_path,
            disable_hint_validation=args.disable_hint_validation,
            no_progress_bar=args.no_progress_bar,
            safe_collecting=args.safe_collecting,
            exit_first=args.exit_first,
            seed=args.seed,
            # TODO(mkaput): Remove this.
            fuzz_max_examples=args.fuzz_max_examples,
            slowest_tests_to_report_count=args.report_slowest_tests,
        )
        summary.assert_all_passed()
        return summary

    # pylint: disable=too-many-locals
    async def test(
        self,
        targets: List[str],
        ignored_targets: Optional[List[str]] = None,
        cairo_path: Optional[List[Path]] = None,
        disable_hint_validation: bool = False,
        no_progress_bar: bool = False,
        safe_collecting: bool = False,
        exit_first: bool = False,
        seed: Optional[int] = None,
        # TODO(mkaput): Remove this.
        fuzz_max_examples: int = 100,
        slowest_tests_to_report_count: int = 0,
    ) -> TestingSummary:
        include_paths = [
            str(path)
            for path in [
                self._protostar_directory.protostar_test_only_cairo_packages_path,
                *self._project_cairo_path_builder.build_project_cairo_path_list(
                    cairo_path or []
                ),
            ]
        ]
        factory = (
            StarknetPassManagerFactory
            if safe_collecting
            else TestCollectorPassManagerFactory
        )
        with TestingSeed(seed) as testing_seed:
            with ActivityIndicator(
                self._log_color_provider.colorize("GRAY", "Collecting tests")
            ):
                test_collector_result = TestCollector(
                    StarknetCompiler(
                        config=CompilerConfig(
                            disable_hint_validation=True, include_paths=include_paths
                        ),
                        pass_manager_factory=factory,
                    ),
                    config=TestCollector.Config(safe_collecting=safe_collecting),
                ).collect(
                    targets=targets,
                    ignored_targets=ignored_targets,
                    default_test_suite_glob=str(self._project_root_path),
                )

            self._log_test_collector_result(test_collector_result)

            testing_summary = TestingSummary(
                case_results=test_collector_result.broken_test_suites,  # type: ignore | pyright bug?
                testing_seed=testing_seed,
            )

            if test_collector_result.test_cases_count > 0:
                live_logger = TestingLiveLogger(
                    logger=self._logger,
                    testing_summary=testing_summary,
                    no_progress_bar=no_progress_bar,
                    exit_first=exit_first,
                    slowest_tests_to_report_count=slowest_tests_to_report_count,
                )
                TestScheduler(live_logger, worker=TestRunner.worker).run(
                    include_paths=include_paths,
                    test_collector_result=test_collector_result,
                    # TODO(mkaput): Remove this along with --fuzz-max-examples argument.
                    fuzz_config=FuzzConfig(max_examples=fuzz_max_examples),
                    disable_hint_validation=disable_hint_validation,
                    exit_first=exit_first,
                )

            return testing_summary

    def _log_test_collector_result(
        self, test_collector_result: TestCollector.Result
    ) -> None:
        for broken_test_suite in test_collector_result.broken_test_suites:
            self._log_formatted_test_result(broken_test_suite)
        if test_collector_result.test_cases_count:
            self._log_formatted_test_collector_summary(test_collector_result)
        else:
            self._logger.warning("No test cases found")

    def _log_formatted_test_collector_summary(
        self, test_collector_result: TestCollector.Result
    ) -> None:
        formatted_result = format_test_collector_summary(
            test_case_count=test_collector_result.test_cases_count,
            test_suite_count=len(test_collector_result.test_suites),
            duration_in_sec=test_collector_result.duration,
        )
        self._logger.info(formatted_result)

    @staticmethod
    def _log_formatted_test_result(test_result: TestResult) -> None:
        formatted_test_result = format_test_result(test_result)
        print(formatted_test_result)
