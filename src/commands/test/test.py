from pathlib import Path
from re import Pattern
from typing import Optional, List

import pytest

from src.commands.test.runner import TestRunner
from src.commands.test.utils import collect_subdirectories


@pytest.mark.skip
async def test(
    sources_directory: Path,
    omit: Pattern,
    match: Pattern,
    cairo_paths: Optional[List[Path]] = None,
    cairo_paths_recursive: Optional[List[Path]] = None,
):
    cairo_path = [
        *(cairo_paths or []),
        *(
            [
                s
                for path_recursive in cairo_paths_recursive
                for s in collect_subdirectories(path_recursive)
            ]
        ),
    ]

    test_root_dir = Path(sources_directory)
    runner = TestRunner(include_paths=cairo_path)
    await runner.run_tests_in(
        test_root_dir,
        omit_pattern=omit,
        match_pattern=match,
    )
