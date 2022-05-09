from dataclasses import dataclass, field
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Pattern

from src.cli.command import Command
from src.commands.test.reporter import ReporterCoordinator
from src.commands.test.test_collector import TestCollector
from src.utils.protostar_directory import ProtostarDirectory

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
                description="A filename regexp, which omits the test file if it matches the pattern.",
                type="regexp",
            ),
            Command.Argument(
                name="match",
                short_name="m",
                description="A filename regexp, which omits the test file if it does not match the pattern.",
                type="regexp",
            ),
            Command.Argument(
                name="cairo-path",
                is_array=True,
                description="Additional directories to look for sources.",
                type="directory",
            ),
        ]

    @dataclass
    class Args:
        target: Path
        match: Optional[Pattern] = None
        omit: Optional[Pattern] = None
        cairo_path: List[Path] = field(default_factory=list)

    async def run(self, args: "TestCommand.Args") -> None:

        cairo_paths: List[Path] = args.cairo_path or []
        cairo_paths = self._protostar_directory.add_protostar_cairo_dir(cairo_paths)
        include_paths = [str(pth) for pth in cairo_paths]
        include_paths.extend(self._project.get_include_paths())

        logger = getLogger()

        collection_result = TestCollector(
            target=args.target,
            include_paths=include_paths,
        ).collect(
            match_pattern=args.match,
            omit_pattern=args.omit,
        )
        collection_result.log(logger)

        reporter_coordinator = ReporterCoordinator(
            args.target, collection_result.test_subjects, logger
        )
        reporter_coordinator.run(
            include_paths=include_paths, test_subjects=collection_result.test_subjects
        )
