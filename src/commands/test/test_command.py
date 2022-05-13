from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Pattern

from src.cli.command import Command
from src.commands.test.test_collector import TestCollector
from src.commands.test.test_runner import TestRunner
from src.commands.test.test_scheduler import TestScheduler
from src.commands.test.testing_live_logger import TestingLiveLogger
from src.commands.test.testing_summary import TestingSummary
from src.utils.protostar_directory import ProtostarDirectory
from src.utils.starknet_compilation import StarknetCompiler

if TYPE_CHECKING:
    from src.utils.config.project import Project


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
                    "A path can point to:\n"
                    "- the directory with test files\n"
                    "    - `tests`\n"
                    "- the specific test file\n"
                    "    - `tests/test_main.cairo`\n"
                    "- the specific test case\n"
                    "    - `tests/test_main.cairo::test_example`\n"
                ),
                type="path",
                is_positional=True,
                default="tests",
            ),
            Command.Argument(
                name="omit",
                short_name="o",
                description="A filepath regexp that omits the test file if it matches the pattern.",
                type="regexp",
            ),
            Command.Argument(
                name="match",
                short_name="m",
                description="A filepath regexp that omits the test file if it does not match the pattern.",
                type="regexp",
            ),
            Command.Argument(
                name="cairo-path",
                is_array=True,
                description="Additional directories to look for sources.",
                type="directory",
            ),
        ]

    async def run(self, args) -> TestingSummary:
        return await self.test(
            target=args.target,
            match=args.match,
            omit=args.omit,
            cairo_path=args.cairo_path,
        )

    async def test(
        self,
        target: Path,
        match: Optional[Pattern] = None,
        omit: Optional[Pattern] = None,
        cairo_path: Optional[List[Path]] = None,
    ) -> TestingSummary:
        logger = getLogger()

        include_paths = self._build_include_paths(cairo_path or [])

        test_collector_result = TestCollector(
            StarknetCompiler(disable_hint_validation=True, include_paths=include_paths)
        ).collect(
            target=target,
            match_pattern=match,
            omit_pattern=omit,
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
