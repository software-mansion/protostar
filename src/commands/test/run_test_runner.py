from pathlib import Path
from re import Pattern
from typing import List, Optional
from src.commands.test.runner import TestRunner
from src.utils.config.project import Project
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.utils.config.project import Project


async def run_test_runner(
    tests_root: Path,
    project: Optional["Project"] = None,
    omit: Optional[Pattern] = None,
    match: Optional[Pattern] = None,
    cairo_paths: Optional[List[Path]] = None,
):
    cairo_path = cairo_paths or []

    test_root_dir = Path(tests_root)
    runner = TestRunner(project=project, include_paths=[str(pth) for pth in cairo_path])
    await runner.run_tests_in(
        test_root_dir,
        omit_pattern=omit,
        match_pattern=match,
    )
