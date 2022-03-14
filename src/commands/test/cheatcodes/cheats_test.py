from pathlib import Path

import pytest

from src.commands.test import TestRunnerWithCheatcodes

current_directory = Path(__file__).parent


@pytest.mark.asyncio
async def test_cheatcodes():
    runner = TestRunnerWithCheatcodes()
    await runner.run_tests_in(current_directory)
    assert runner.reporter
    assert not runner.reporter.failed_cases
