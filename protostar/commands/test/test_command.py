import logging
from argparse import Namespace
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from protostar.io import StructuredMessage
from protostar.cli import ProtostarArgument, ProtostarCommand, MessengerFactory
from protostar.cli.activity_indicator import ActivityIndicator
from protostar.commands.test.test_collector_summary_formatter import (
    format_test_collector_summary,
)
from protostar.commands.test.test_result_formatter import (
    format_test_result,
)
from protostar.testing.test_scheduler import make_path_relative_if_possible
from protostar.commands.test.testing_live_logger import TestingLiveLogger
from protostar.compiler import ProjectCairoPathBuilder
from protostar.io.log_color_provider import LogColorProvider
from protostar.protostar_exception import ProtostarException
from protostar.self.cache_io import CacheIO
from protostar.self.protostar_directory import ProtostarDirectory
from protostar.starknet.compiler.pass_managers import (
    StarknetPassManagerFactory,
    TestCollectorPassManagerFactory,
)
from protostar.starknet.compiler.starknet_compilation import (
    StarknetCompiler,
)
from protostar.starknet.compiler.cairo_compilation import CairoCompiler
from protostar.starknet.compiler.common import CompilerConfig
from protostar.testing import (
    TestCollector,
    TestingSummary,
    TestResult,
    TestRunner,
    TestScheduler,
    determine_testing_seed,
)
from protostar.testing.cairo_test_runner import CairoTestRunner

from .test_command_cache import TestCommandCache


@dataclass
class SuccessfulTestMessage(StructuredMessage):
    summary: TestingSummary
    test_collector_result: TestCollector.Result

    def format_human(self, fmt: LogColorProvider) -> str:
        assert False, "Tests should use live logging for the human-readable output"

    def format_dict(self) -> dict:
        test_cases = 0
        for test_suite in self.test_collector_result.test_suites:
            test_cases += len(test_suite.test_cases)
        failed_tests = len(self.summary.failed)
        passed_tests = len(self.summary.passed)
        execution_times = [
            test.execution_time for test in self.summary.passed + self.summary.failed
        ]

        failed_tests_paths = {str(item.file_path) for item in self.summary.failed}
        passed_test_suites = failed_test_suites = 0
        for test_suite in self.test_collector_result.test_suites:
            if str(test_suite.test_path) in failed_tests_paths:
                failed_test_suites += 1
            else:
                passed_test_suites += 1

        return {
            "collected_tests": {
                "broken_test_suites": len(
                    self.test_collector_result.broken_test_suites
                ),
                "test_suites": len(self.test_collector_result.test_suites),
                "test_cases": test_cases,
                "duration": self.test_collector_result.duration,
            },
            "summary": {
                "test_suites": {
                    "total": failed_test_suites + passed_test_suites,
                    "failed": failed_test_suites,
                    "passed": passed_test_suites,
                },
                "tests": {
                    "total": failed_tests + passed_tests,
                    "failed": failed_tests,
                    "passed": passed_tests,
                },
                "seed": self.summary.testing_seed,
                "execution_time": f"{sum(execution_times):0.2f}",
            },
        }


class TestCommand(ProtostarCommand):
    def __init__(
        self,
        project_root_path: Path,
        protostar_directory: ProtostarDirectory,
        project_cairo_path_builder: ProjectCairoPathBuilder,
        log_color_provider: LogColorProvider,
        cwd: Path,
        active_profile_name: Optional[str],
        messenger_factory: Optional[MessengerFactory],
    ) -> None:
        super().__init__()
        self._log_color_provider = log_color_provider
        self._project_root_path = project_root_path
        self._protostar_directory = protostar_directory
        self._project_cairo_path_builder = project_cairo_path_builder
        self._cwd = cwd
        self._active_profile_name = active_profile_name
        self._messenger_factory = messenger_factory

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
            *MessengerFactory.OUTPUT_ARGUMENTS,
            ProtostarArgument(
                name="target",
                description="""
A glob or globs to a directory or a test suite, for example:
- `tests/**/*_main*::*_balance` — find test cases, which names ends with `_balance` in test suites with the `_main` in filenames in the `tests` directory,
- `::test_increase_balance` — find `test_increase_balance` test_cases in any test suite within the project.   
""".strip(),
                type="str",
                value_parser="list",
                is_positional=True,
                default=["."],
            ),
            ProtostarArgument(
                name="ignore",
                short_name="i",
                description=(
                    "A glob or globs to a directory or a test suite, which should be ignored."
                ),
                value_parser="list",
                type="str",
            ),
            ProtostarArgument(
                name="cairo-path",
                value_parser="list",
                description="Additional directories to look for sources.",
                type="path",
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
                name="profiling",
                description=(
                    "Run profiling for a test contract. Works only for a single test case."
                    "Protostar generates a file that can be opened with https://github.com/google/pprof"
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
                name="max-steps",
                type="int",
                description="Set Cairo execution step limit.",
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
            ProtostarArgument(
                name="estimate-gas",
                type="bool",
                description="Show gas estimation for each test case. Estimations might be inaccurate.",
            ),
        ]

    async def run(self, args: Namespace) -> TestingSummary:
        cache = TestCommandCache(CacheIO(self._project_root_path))
        json_format = args.json if hasattr(args, "json") else False
        summary, test_collector_result = await self.test(
            targets=cache.obtain_targets(args.target, args.last_failed),
            ignored_targets=args.ignore,
            cairo_path=args.cairo_path,
            disable_hint_validation=args.disable_hint_validation,
            profiling=args.profiling,
            no_progress_bar=args.no_progress_bar,
            safe_collecting=args.safe_collecting,
            exit_first=args.exit_first,
            seed=args.seed,
            max_steps=args.max_steps,
            slowest_tests_to_report_count=args.report_slowest_tests,
            gas_estimation_enabled=args.estimate_gas,
            json_format=json_format,
        )
        cache.write_failed_tests_to_cache(summary)
        if json_format:
            if self._messenger_factory is None:
                raise ProtostarException(
                    "Messanger factory has to be provided in order to format the output"
                )
            write = self._messenger_factory.json()
            write(SuccessfulTestMessage(summary, test_collector_result))
        summary.assert_all_passed()
        return summary

    async def test(
        self,
        targets: List[str],
        use_cairo_test_runner: bool = False,
        ignored_targets: Optional[List[str]] = None,
        cairo_path: Optional[List[Path]] = None,
        disable_hint_validation: bool = False,
        profiling: bool = False,
        no_progress_bar: bool = False,
        safe_collecting: bool = False,
        exit_first: bool = False,
        seed: Optional[int] = None,
        max_steps: Optional[int] = None,
        slowest_tests_to_report_count: int = 0,
        gas_estimation_enabled: bool = False,
        json_format: bool = False,
    ) -> tuple[TestingSummary, TestCollector.Result]:
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
            compiler_config = CompilerConfig(
                disable_hint_validation=True, include_paths=include_paths
            )
            if use_cairo_test_runner:
                cairo_compiler = CairoCompiler(compiler_config)
                test_collector = TestCollector(
                    get_suite_function_names=cairo_compiler.get_function_names,
                )
            else:
                starknet_compiler = StarknetCompiler(
                    config=compiler_config,
                    pass_manager_factory=factory,
                )
                test_collector = TestCollector(
                    get_suite_function_names=starknet_compiler.get_function_names
                )

            test_collector_result = test_collector.collect(
                targets=targets,
                ignored_targets=ignored_targets,
                default_test_suite_glob=str(self._project_root_path),
            )

        if profiling and test_collector_result.test_cases_count > 1:
            raise ProtostarException(
                "Only one test case can be profiled at the time. Please specify path to a single test case."
            )

        if not json_format:
            self._log_test_collector_result(test_collector_result)

        testing_summary = TestingSummary(
            test_results=test_collector_result.broken_test_suites,  # type: ignore | pyright bug?
            testing_seed=testing_seed,
        )

        if test_collector_result.test_cases_count > 0:
            live_logger = TestingLiveLogger(
                testing_summary=testing_summary,
                no_progress_bar=no_progress_bar,
                exit_first=exit_first,
                slowest_tests_to_report_count=slowest_tests_to_report_count,
                project_root_path=self._project_root_path,
            )
            worker = (
                CairoTestRunner.worker if use_cairo_test_runner else TestRunner.worker
            )

            TestScheduler(live_logger=live_logger, worker=worker).run(
                include_paths=include_paths,
                test_collector_result=test_collector_result,
                disable_hint_validation=disable_hint_validation,
                profiling=profiling,
                exit_first=exit_first,
                testing_seed=testing_seed,
                max_steps=max_steps,
                project_root_path=self._project_root_path,
                active_profile_name=self._active_profile_name,
                cwd=self._cwd,
                gas_estimation_enabled=gas_estimation_enabled,
                testing_summary=testing_summary,
                json_format=json_format,
            )

        return testing_summary, test_collector_result

    def _log_test_collector_result(
        self, test_collector_result: TestCollector.Result
    ) -> None:
        for broken_test_suite in test_collector_result.broken_test_suites:
            self._log_formatted_test_result(broken_test_suite)
        if test_collector_result.test_cases_count:
            self._log_formatted_test_collector_summary(test_collector_result)
        else:
            logging.warning("No test cases found")

    def _log_formatted_test_collector_summary(
        self, test_collector_result: TestCollector.Result
    ) -> None:
        formatted_result = format_test_collector_summary(
            test_case_count=test_collector_result.test_cases_count,
            test_suite_count=len(test_collector_result.test_suites),
            duration_in_sec=test_collector_result.duration,
        )
        logging.info(formatted_result)

    def _log_formatted_test_result(self, test_result: TestResult) -> None:
        test_result = make_path_relative_if_possible(
            test_result, self._project_root_path
        )
        formatted_test_result = format_test_result(test_result)
        print(formatted_test_result)
