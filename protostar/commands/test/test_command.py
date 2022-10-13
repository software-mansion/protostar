from argparse import Namespace
from logging import Logger
from pathlib import Path
from typing import List, Optional

from protostar.cli import ProtostarArgument, ProtostarCommand
from protostar.cli.activity_indicator import ActivityIndicator
from protostar.commands.test.test_collector_summary_formatter import (
    format_test_collector_summary,
)
from protostar.commands.test.test_result_formatter import (
    format_test_result,
    make_path_relative_if_possible,
)
from protostar.commands.test.testing_live_logger import TestingLiveLogger
from protostar.compiler import ProjectCairoPathBuilder
from protostar.io.log_color_provider import LogColorProvider
from protostar.self.cache_io import CacheIO
from protostar.self.protostar_directory import ProtostarDirectory
from protostar.starknet.compiler.pass_managers import (
    StarknetPassManagerFactory,
    TestCollectorPassManagerFactory,
)
from protostar.starknet.compiler.starknet_compilation import (
    CompilerConfig,
    StarknetCompiler,
)
from protostar.testing import (
    TestCollector,
    TestingSummary,
    TestResult,
    TestRunner,
    TestScheduler,
    determine_testing_seed,
)

from .test_command_cache import TestCommandCache


class TestCommand(ProtostarCommand):
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
    def arguments(self):
        return [
            ProtostarArgument(
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
            ProtostarArgument(
                name="ignore",
                short_name="i",
                description=(
                    "A glob or globs to a directory or a test suite, which should be ignored."
                ),
                is_array=True,
                type="str",
            ),
            ProtostarArgument(
                name="cairo-path",
                is_array=True,
                description="Additional directories to look for sources.",
                type="directory",
            ),
            ProtostarArgument(
                name="disable-hint-validation",
                description=(
                    "Disable hint validation in contracts declared by the "
                    "`declare` cheatcode or deployed by `deploy_contract` cheatcode."
                ),
                type="bool",
            ),
            ProtostarArgument(
                name="no-progress-bar",
                type="bool",
                description="Disable progress bar.",
            ),
            ProtostarArgument(
                name="safe-collecting",
                type="bool",
                description="Use Cairo compiler for test collection.",
            ),
            ProtostarArgument(
                name="exit-first",
                short_name="x",
                type="bool",
                description="Exit immediately on first broken or failed test.",
            ),
            ProtostarArgument(
                name="seed",
                type="int",
                description="Set a seed to use for all fuzz tests.",
            ),
            ProtostarArgument(
                name="report-slowest-tests",
                type="int",
                description="Print slowest tests at the end.",
                default=0,
            ),
            ProtostarArgument(
                name="last-failed",
                short_name="lf",
                type="bool",
                description="Only re-run failed and broken test cases.",
            ),
        ]

    async def run(self, args: Namespace) -> TestingSummary:
        cache = TestCommandCache(CacheIO(self._project_root_path), self._logger)
        summary = await self.test(
            targets=cache.obtain_targets(args.target, args.last_failed),
            ignored_targets=args.ignore,
            cairo_path=args.cairo_path,
            disable_hint_validation=args.disable_hint_validation,
            no_progress_bar=args.no_progress_bar,
            safe_collecting=args.safe_collecting,
            exit_first=args.exit_first,
            seed=args.seed,
            slowest_tests_to_report_count=args.report_slowest_tests,
        )
        cache.write_failed_tests_to_cache(summary)
        summary.assert_all_passed()
        return summary

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

        testing_seed = determine_testing_seed(seed)

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
            test_results=test_collector_result.broken_test_suites,  # type: ignore | pyright bug?
            testing_seed=testing_seed,
        )

        if test_collector_result.test_cases_count > 0:
            live_logger = TestingLiveLogger(
                logger=self._logger,
                testing_summary=testing_summary,
                no_progress_bar=no_progress_bar,
                exit_first=exit_first,
                slowest_tests_to_report_count=slowest_tests_to_report_count,
                project_root_path=self._project_root_path,
            )
            TestScheduler(live_logger, worker=TestRunner.worker).run(
                include_paths=include_paths,
                test_collector_result=test_collector_result,
                disable_hint_validation=disable_hint_validation,
                exit_first=exit_first,
                testing_seed=testing_seed,
                project_root_path_str=str(self._project_root_path),
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

    def _log_formatted_test_result(self, test_result: TestResult) -> None:
        test_result = make_path_relative_if_possible(
            test_result, self._project_root_path
        )
        formatted_test_result = format_test_result(test_result)
        print(formatted_test_result)
