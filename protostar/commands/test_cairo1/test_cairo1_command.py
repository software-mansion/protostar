from argparse import Namespace
from pathlib import Path
from typing import List, Optional

from protostar.commands.test import TestCommand

from protostar.cli import ProtostarArgument, ProtostarCommand, MessengerFactory
from protostar.cli.activity_indicator import ActivityIndicator
from protostar.commands.test.messages.testing_summary_message import (
    TestingSummaryResultMessage,
)
from protostar.commands.test.testing_live_logger import TestingLiveLogger
from protostar.compiler import ProjectCairoPathBuilder
from protostar.io.log_color_provider import LogColorProvider
from protostar.protostar_exception import ProtostarException
from protostar.self.cache_io import CacheIO
from protostar.self.protostar_directory import ProtostarDirectory
from protostar.starknet.pass_managers import (
    StarknetPassManagerFactory,
    TestCollectorPassManagerFactory,
)
from protostar.starknet import StarknetCompiler
from protostar.cairo import CairoCompiler, CairoCompilerConfig
from protostar.testing import (
    TestCollector,
    TestingSummary,
    TestRunner,
    TestScheduler,
    determine_testing_seed,
)
from protostar.cairo_testing.cairo_test_runner import CairoTestRunner
from protostar.io.output import Messenger

from  protostar.commands.test import TestCollectorResultMessage
from protostar.commands.test import TestCommandCache
from ...cairo_testing.cairo1_test_collector import Cairo1TestCollector
from ...cairo_testing.cairo1_test_runner_adapter import Cairo1TestRunnerAdapter


class TestCairo1Command(ProtostarCommand):
    def __init__(
        self,
        project_root_path: Path,
        protostar_directory: ProtostarDirectory,
        project_cairo_path_builder: ProjectCairoPathBuilder,
        log_color_provider: LogColorProvider,
        cwd: Path,
        active_profile_name: Optional[str],
        messenger_factory: MessengerFactory,
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
        return "test-cairo1"

    @property
    def description(self) -> str:
        return "Executes cairo1 tests."

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
        test_command = TestCommand(
            project_root_path=self._project_root_path,
            protostar_directory=self._protostar_directory,
            project_cairo_path_builder=self._project_cairo_path_builder,
            log_color_provider=self._log_color_provider,
            cwd=self._cwd,
            active_profile_name=self._active_profile_name,
            messenger_factory=self._messenger_factory,
        )
        summary = await test_command.test(
            targets=cache.obtain_targets(args.target, args.last_failed),
            ignored_targets=args.ignore,
            cairo_path=args.linked_libraries,
            disable_hint_validation=False,
            profiling=False,
            no_progress_bar=args.no_progress_bar,
            safe_collecting=False,
            exit_first=args.exit_first,
            seed=None,
            max_steps=None,
            slowest_tests_to_report_count=args.report_slowest_tests,
            gas_estimation_enabled=False,
            messenger=messenger,
            use_cairo1_test_runner=True,
        )
        cache.write_failed_tests_to_cache(summary)

        summary.assert_all_passed()
        return summary