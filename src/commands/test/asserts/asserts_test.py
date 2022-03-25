from os import path
from pathlib import Path

import pytest

from src.commands.test.runner import TestRunner

CURRENT_DIR = Path(__file__).parent


@pytest.mark.asyncio
async def test_asserts():
    runner = TestRunner(
        include_paths=[path.join(CURRENT_DIR, "..", "..", "..", "..", "cairo")]
    )
    await runner.run_tests_in(CURRENT_DIR)
    assert runner.reporter
    assert not runner.reporter.failed_cases
