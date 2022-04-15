from pathlib import Path

import pytest

from src.commands.test.runner import TestRunner

current_directory = Path(__file__).parent


@pytest.mark.asyncio
async def test_cheatcodes():
    runner = TestRunner()
    await runner.run_tests_in(current_directory / "examples" / "cheats")
    assert runner.reporter
    assert not runner.reporter.failed_cases


@pytest.mark.asyncio
async def test_expect_emit():
    runner = TestRunner()
    await runner.run_tests_in(
        current_directory
        / "examples"
        / "cheats"
        / "expect_events"
        / "test_expect_events.cairo"
    )
    assert runner.reporter
    assert not runner.reporter.failed_cases
