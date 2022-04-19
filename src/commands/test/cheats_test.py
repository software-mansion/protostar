from pathlib import Path

import pytest
from src.commands.test.reporter import TestReporter
from src.commands.test.run_test_runner import run_test_runner

current_directory = Path(__file__).parent


@pytest.mark.asyncio
async def test_cheatcodes():
    reporter = TestReporter(current_directory / "examples" / "cheats")
    await run_test_runner(reporter, current_directory / "examples" / "cheats")
    assert not reporter.failed_cases
