import asyncio
from multiprocessing import Pool, Process
import multiprocessing
from pathlib import Path
from re import Pattern
from typing import List, Optional, TYPE_CHECKING
from src.commands.test.collector import TestCollector
from src.commands.test.reporter import Reporter, TestReporter

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
):
    cairo_path = cairo_paths or []
    include_paths = [str(pth) for pth in cairo_path]
    test_subjects = TestCollector(
        target=Path(tests_root),
        include_paths=include_paths,
    ).collect(
        match_pattern=match,
        omit_pattern=omit,
    )


    with multiprocessing.Manager() as m:
        queue = m.Queue()
        reporter = TestReporter(tests_root, test_subjects, queue)   
        setups = [
            (
                subject,
                queue,
                project,
                include_paths, 
            )
            for subject in test_subjects
        ]

        with Pool(multiprocessing.cpu_count()) as p:
            result = p.starmap_async(run_worker, setups)
            reporter.live_reporting()
            result.get() # TODO add test timeout
        
        return reporter.failed_cases

def run_worker(    
        subject,
        queue,
        project: "Project",
        include_paths,
    ):
    reporter = Reporter(queue)
    runner = TestRunner(reporter=reporter, project=project, include_paths=include_paths)
    asyncio.run(runner.run_test_subject(subject))
