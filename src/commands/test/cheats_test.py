from pathlib import Path

import pytest

from src.commands.test.runner import TestRunner

current_directory = Path(__file__).parent


@pytest.mark.asyncio
async def test_cheatcodes():
    runner = TestRunner(is_test_fail_enabled=True)
    await runner.run_tests_in(current_directory / "examples" / "cheats")
    assert runner.reporter
    assert not runner.reporter.failed_cases
