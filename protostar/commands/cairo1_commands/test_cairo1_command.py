from argparse import Namespace
from pathlib import Path
from typing import List, Optional

from protostar.cli import ProtostarArgument, ProtostarCommand, MessengerFactory
from protostar.commands.test.messages.testing_summary_message import (
    TestingSummaryResultMessage,
)
from protostar.commands.test.testing_live_logger import TestingLiveLogger
from protostar.compiler import LinkedLibrariesBuilder
from protostar.io.log_color_provider import LogColorProvider
from protostar.self.cache_io import CacheIO
from protostar.self.protostar_directory import ProtostarDirectory
from protostar.cairo import CairoCompilerConfig
from protostar.testing import (
    TestingSummary,
    TestScheduler,
    determine_testing_seed,
)
from protostar.io.output import Messenger


from protostar.commands.test import TestCommandCache
from .fetch_from_scarb import maybe_fetch_linked_libraries
from protostar.commands.test.test_command_cache import TestCommandCache
from protostar.commands.test.messages import TestCollectorResultMessage
from protostar.cairo_testing.cairo1_test_collector import Cairo1TestCollector
from protostar.cairo_testing.cairo1_test_runner import Cairo1TestRunner


class TestCairo1Command(ProtostarCommand):
    def __init__(
        self,
        project_root_path: Path,
        protostar_directory: ProtostarDirectory,
        log_color_provider: LogColorProvider,
        cwd: Path,
        active_profile_name: Optional[str],
        messenger_factory: MessengerFactory,
    ) -> None:
        super().__init__()
        self._log_color_provider = log_color_provider
        self._project_root_path = project_root_path
        self._protostar_directory = protostar_directory
        self._project_cairo_path_builder = LinkedLibrariesBuilder()
        self._cwd = cwd
        self._active_profile_name = active_profile_name
        self._messenger_factory = messenger_factory

    @property
    def name(self) -> str:
        return "test-cairo1"

    @property
    def description(self) -> str:
        return "Executes cairo1 tests."

    @property
    def example(self) -> Optional[str]:
        return "$ protostar test-cairo1"

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
                name="linked-libraries",
                value_parser="list",
                description="Libraries to include in compilation",
                type="path",
            ),
            ProtostarArgument(
                name="no-progress-bar",
                type="bool",
                description="Disable progress bar.",
            ),
            ProtostarArgument(
                name="exit-first",
                short_name="x",
                type="bool",
                description="Exit immediately on first broken or failed test.",
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
        if not vars(args).get("json"):
            args.json = None
        messenger = self._messenger_factory.from_args(args)
        cache = TestCommandCache(CacheIO(self._project_root_path))

        libraries = maybe_fetch_linked_libraries(self._project_root_path) or []

        summary = await self.test(
            targets=cache.obtain_targets(args.target, args.last_failed),
            ignored_targets=args.ignore,
            cairo_path=args.linked_libraries + libraries,
            no_progress_bar=args.no_progress_bar,
            exit_first=args.exit_first,
            slowest_tests_to_report_count=args.report_slowest_tests,
            messenger=messenger,
        )
        cache.write_failed_tests_to_cache(summary)

        summary.assert_all_passed()
        return summary

    async def test(
        self,
        targets: List[str],
        messenger: Messenger,
        ignored_targets: Optional[List[str]] = None,
        cairo_path: Optional[List[Path]] = None,
        no_progress_bar: bool = False,
        exit_first: bool = False,
        slowest_tests_to_report_count: int = 0,
    ) -> TestingSummary:
        include_paths = [
            str(path)
            for path in self._project_cairo_path_builder.build_project_cairo_path_list(
                cairo_path or []
            )
        ] + [str(self._protostar_directory.protostar_cairo1_corelib_path)]

        testing_seed = determine_testing_seed(seed=None)

        compiler_config = CairoCompilerConfig(
            disable_hint_validation=True,
            include_paths=include_paths,
        )
        test_collector = Cairo1TestCollector(compiler_config.include_paths)
        test_collector_result = test_collector.collect(
            targets=targets,
            ignored_targets=ignored_targets,
            default_test_suite_glob=str(self._project_root_path),
        )

        messenger(TestCollectorResultMessage(test_collector_result))

        testing_summary = TestingSummary(
            initial_test_results=test_collector_result.broken_test_suites,  # type: ignore
            testing_seed=testing_seed,
            test_collector_result=test_collector_result,
        )

        if test_collector_result.test_cases_count > 0:
            live_logger = TestingLiveLogger(
                testing_summary=testing_summary,
                no_progress_bar=no_progress_bar,
                exit_first=exit_first,
                slowest_tests_to_report_count=slowest_tests_to_report_count,
                project_root_path=self._project_root_path,
                write=messenger,
            )
            worker = Cairo1TestRunner.worker

            TestScheduler(live_logger=live_logger, worker=worker).run(
                include_paths=include_paths,
                test_collector_result=test_collector_result,
                disable_hint_validation=False,
                profiling=False,
                exit_first=exit_first,
                testing_seed=testing_seed,
                max_steps=None,
                project_root_path=self._project_root_path,
                active_profile_name=self._active_profile_name,
                cwd=self._cwd,
                gas_estimation_enabled=False,
                on_exit_first=lambda: messenger(
                    TestingSummaryResultMessage(
                        test_collector_result=test_collector_result,
                        testing_summary=testing_summary,
                        slowest_tests_to_report_count=slowest_tests_to_report_count,
                    )
                ),
            )

        return testing_summary
