import re
from pathlib import Path

import pytest

from src.commands.test import run_test_runner
from src.utils.config.package import Package

current_directory = Path(__file__).parent


@pytest.mark.asyncio
async def test_run_test_runner():
    pkg = Package.current()
    await run_test_runner(
        pkg=pkg,
        tests_root=Path(current_directory, "examples"),
        omit=re.compile(r".*invalid.*"),
        cairo_paths=[
            Path(current_directory, "examples"),
            Path(current_directory, "examples", "broken"),
        ],
    )
