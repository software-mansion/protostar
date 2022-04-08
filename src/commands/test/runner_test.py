from pathlib import Path
import re
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
        ],
        is_test_fail_enabled=True,
    )
    await runner.run_tests_in(
        test_root_dir,
        match_pattern=re.compile(r".*(nested|failure|broken).*"),
    )


@pytest.mark.asyncio
async def test_failing_test_actually_fail():
    runner = TestRunner()
    await runner.run_tests_in(current_directory / "examples" / "failure")
    assert runner.reporter
    assert len(runner.reporter.failed_cases) == 3
    assert not runner.reporter.passed_cases


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
async def test_revert():
    test_root_dir = Path(current_directory, "examples")
    runner = TestRunner()
    await runner.run_tests_in(test_root_dir, match_pattern=re.compile(r".*(revert).*"))
