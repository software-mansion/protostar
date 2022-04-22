import asyncio
from multiprocessing import Pool
import multiprocessing
from pathlib import Path
from re import Pattern
from typing import List, Optional, TYPE_CHECKING
from src.commands.test.collector import TestCollector
from src.commands.test.reporter import ReportCollector, Reporter

from src.commands.test.runner import TestRunner


if TYPE_CHECKING:
    from src.utils.config.project import Project

# pylint: disable=too-many-arguments
async def run_test_runner(
    tests_root: Path,
    project: Optional["Project"] = None,
    omit: Optional[Pattern] = None,
    match: Optional[Pattern] = None,
    cairo_paths: Optional[List[Path]] = None,
) -> List[Reporter]:
    cairo_path = cairo_paths or []

    include_paths = [str(pth) for pth in cairo_path]
    if project:
        include_paths.extend(project.get_include_paths())

    test_subjects = TestCollector(
        target=Path(tests_root),
        include_paths=include_paths,
    ).collect(
        match_pattern=match,
        omit_pattern=omit,
    )

    with multiprocessing.Manager() as manager:
        queue = manager.Queue()  # type: ignore
        reporter = ReportCollector(tests_root, test_subjects, queue)
        setups = [
            (
                subject,
                reporter.get_reporter(subject),
                include_paths,
            )
            for subject in test_subjects
        ]

        with Pool(multiprocessing.cpu_count()) as pool:
            result = pool.starmap_async(run_worker, setups)
            reporter.live_reporting()
            results = result.get()  # TODO add test timeout
            reporter.report_summary(results)

        return results


def run_worker(
    subject,
    reporter,
    include_paths,
):
    runner = TestRunner(reporter=reporter, include_paths=include_paths)
    asyncio.run(runner.run_test_subject(subject))
    return runner.reporter
