from pathlib import Path

import pytest

from src.commands.test import TestRunnerWithCheatcodes

current_directory = Path(__file__).parent


@pytest.mark.asyncio
async def test_asserts():
    runner = TestRunnerWithCheatcodes(
        include_paths=[current_directory / ".." / ".." / ".." / "cairo"]
    )
    await runner.run_tests_in(current_directory / "examples" / "asserts")
    assert runner.reporter
    assert not runner.reporter.failed_cases
