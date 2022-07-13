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
from protostar.utils.log_color_provider import log_color_provider
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
                name="exit-first",
                short_name="x",
                type="bool",
                description="Exit instantly on first broken or failed test",
            ),
            Command.Argument(
                name="stdout-on-success",
                type="bool",
                description="Also print captured stdout for passed test cases.",
            ),
        ]

    async def run(self, args) -> TestingSummary:
        summary = await self.test(
            targets=args.target,
            ignored_targets=args.ignore,
            cairo_path=args.cairo_path,
            disable_hint_validation=args.disable_hint_validation,
            no_progress_bar=args.no_progress_bar,
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
        disable_hint_validation=False,
        no_progress_bar=False,
        exit_first=False,
        stdout_on_success=False,
    ) -> TestingSummary:
        logger = getLogger()

        include_paths = self._build_include_paths(cairo_path or [])

        with ActivityIndicator(log_color_provider.colorize("GRAY", "Collecting tests")):
            test_collector_result = TestCollector(
                StarknetCompiler(
                    disable_hint_validation=True, include_paths=include_paths
                )
            ).collect(
                targets=targets,
                ignored_targets=ignored_targets,
                default_test_suite_glob=str(self._project.project_root),
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

    def _build_include_paths(self, cairo_paths: List[Path]) -> List[str]:
        cairo_paths = self._protostar_directory.add_protostar_cairo_dir(cairo_paths)
        include_paths = [str(pth) for pth in cairo_paths]
        include_paths.extend(self._project.get_include_paths())
        return include_paths
