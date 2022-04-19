import re
from pathlib import Path

import pytest

from src.commands.test.runner import TestRunner

current_directory = Path(__file__).parent


@pytest.mark.asyncio
async def test_run_syntaxtically_valid_tests():
    test_root_dir = Path(current_directory, "examples")
    runner = TestRunner(
        include_paths=[
            str(test_root_dir.resolve()),
            str(Path(test_root_dir, "broken")),  # Additional broken contract source
        ]
    )
    await runner.run_tests_in(
        test_root_dir,
        match_pattern=re.compile(r".*(nested|failure|broken).*"),
    )


@pytest.mark.asyncio
async def test_no_collected_items():
    test_root_dir = Path(current_directory, "examples")
    runner = TestRunner(
        include_paths=[
            str(test_root_dir.resolve()),
            str(Path(test_root_dir, "broken")),  # Additional broken contract source
        ]
    )
    await runner.run_tests_in(
        test_root_dir, match_pattern=re.compile(r".*empty/no_test_functions.*")
    )


@pytest.mark.asyncio
async def test_cheatcodes():
    runner = TestRunner()
    await runner.run_tests_in(current_directory / "examples" / "cheats")
    assert runner.reporter
    assert not runner.reporter.failed_cases


@pytest.mark.asyncio
async def test_expect_events():
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
