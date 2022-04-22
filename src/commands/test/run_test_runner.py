from pathlib import Path
from re import Pattern
from typing import List, Optional, TYPE_CHECKING
from src.commands.test.collector import TestCollector
from src.commands.test.reporter import TestReporter
from src.commands.test.runner import TestRunner


if TYPE_CHECKING:
    from src.utils.config.project import Project

# pylint: disable=too-many-arguments
async def run_test_runner(
    reporter: TestReporter,
    tests_root: Path,
    project: Optional["Project"] = None,
    omit: Optional[Pattern] = None,
    match: Optional[Pattern] = None,
    cairo_paths: Optional[List[Path]] = None,
):
    cairo_path = cairo_paths or []
    include_paths = [str(pth) for pth in cairo_path]

    reporter = reporter if reporter else TestReporter(tests_root)

    test_subjects = TestCollector(
        target=Path(tests_root),
        include_paths=include_paths,
    ).collect(
        match_pattern=match,
        omit_pattern=omit,
    )

    runner = TestRunner(reporter=reporter, project=project, include_paths=include_paths)

    await runner.run_tests_in(test_subjects)
