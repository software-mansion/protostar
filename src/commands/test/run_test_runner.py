import asyncio
import multiprocessing
import signal
from logging import getLogger
from multiprocessing import Pool
from pathlib import Path
from re import Pattern
from typing import TYPE_CHECKING, List, Optional, cast

from src.commands.test.reporter import Reporter, ReporterCoordinator
from src.commands.test.runner import TestRunner
from src.commands.test.test_collector import TestCollector
from src.commands.test.utils import TestSubject
from src.utils.starknet_compilation import StarknetCompiler

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
    logger = getLogger()
    cairo_path = cairo_paths or []

    include_paths = [str(pth) for pth in cairo_path]
    if project:
        include_paths.extend(project.get_include_paths())

    test_collector_result = TestCollector(
        StarknetCompiler(disable_hint_validation=True, include_paths=include_paths)
    ).collect(
        target=tests_root,
        match_pattern=match,
        omit_pattern=omit,
    )

    with multiprocessing.Manager() as manager:
        queue = manager.Queue()  # type: ignore
        reporter_coordinator = ReporterCoordinator(
            tests_root,
            cast(List[TestSubject], test_collector_result.test_suites),
            queue,
            logger,
        )
        setups = [
            (
                subject,
                reporter_coordinator.create_reporter(),
                include_paths,
            )
            for subject in test_collector_result.test_suites
        ]

        try:
            with Pool(multiprocessing.cpu_count(), worker_init) as pool:
                result = pool.starmap_async(run_worker, setups)
                reporter_coordinator.live_reporting()
                return result.get()
        except KeyboardInterrupt:
            return []


def worker_init():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def run_worker(
    subject,
    reporter,
    include_paths,
):
    runner = TestRunner(reporter=reporter, include_paths=include_paths)
    asyncio.run(runner.run_test_subject(subject))
    return runner.reporter
