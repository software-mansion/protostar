from pathlib import Path

import pytest

from src.commands.test import TestRunnerWithCheatcodes

CURRENT_DIR = Path(__file__).parent


@pytest.mark.asyncio
async def test_asserts():
    runner = TestRunnerWithCheatcodes()
    await runner.run_tests_in(CURRENT_DIR)
    assert runner.reporter
    assert not runner.reporter.failed_cases
