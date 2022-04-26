from typing import TYPE_CHECKING, List, Optional

from src.commands.test import run_test_runner
from src.commands.test.reporter import TestReporter
from src.core.command import Command
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

    async def run(self, args):
        await run_test_runner(
            TestReporter(args.target),
            args.target,
            project=self._project,
            omit=args.omit,
            match=args.match,
            cairo_paths=self._protostar_directory.inject_protostar_cairo_dir(
                args.cairo_path
            ),
        )
