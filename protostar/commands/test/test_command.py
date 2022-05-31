from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from protostar.cli.command import Command
from protostar.commands.test.test_collector import TestCollector
from protostar.commands.test.test_runner import TestRunner
from protostar.commands.test.test_scheduler import TestScheduler
from protostar.commands.test.testing_live_logger import TestingLiveLogger
from protostar.commands.test.testing_summary import TestingSummary
from protostar.utils.protostar_directory import ProtostarDirectory
from protostar.utils.starknet_compilation import StarknetCompiler

if TYPE_CHECKING:
    from protostar.utils.config.project import Project


class TestCommand(Command):
    def __init__(
        self, project: "Project", protostar_directory: ProtostarDirectory
    ) -> None:
        super().__init__()
        self._project = project
        self._protostar_directory = protostar_directory

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
                    "A glob or globs to a directory or a test suite. You can target a specific test case for example:\n"
                    "`tests/**/*_main*::*_balance`\n"
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
                    "You can target a specific test case."
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
        ]

    async def run(self, args) -> TestingSummary:
        summary = await self.test(
            target_globs=args.target,
            ignored_globs=args.ignore,
            cairo_path=args.cairo_path,
        )
        summary.assert_all_passed()
        return summary

    async def test(
        self,
        target_globs: List[str],
        ignored_globs: Optional[List[str]] = None,
        cairo_path: Optional[List[Path]] = None,
    ) -> TestingSummary:
        logger = getLogger()

        include_paths = self._build_include_paths(cairo_path or [])

        test_collector_result = TestCollector(
            StarknetCompiler(disable_hint_validation=True, include_paths=include_paths)
        ).collect_from_globs(
            target_globs=target_globs,
            ignored_globs=ignored_globs,
            default_test_suite_glob=str(self._project.project_root.resolve()),
        )

        test_collector_result.log(logger)

        testing_summary = TestingSummary([])
        live_logger = TestingLiveLogger(logger, testing_summary)
        TestScheduler(live_logger, worker=TestRunner.worker).run(
            include_paths=include_paths, test_collector_result=test_collector_result
        )

        return testing_summary

    def _build_include_paths(self, cairo_paths: List[Path]) -> List[str]:
        cairo_paths = self._protostar_directory.add_protostar_cairo_dir(cairo_paths)
        include_paths = [str(pth) for pth in cairo_paths]
        include_paths.extend(self._project.get_include_paths())
        return include_paths
