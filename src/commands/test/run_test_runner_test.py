import re
from pathlib import Path

import pytest

from src.commands.test import run_test_runner
from src.commands.test.cases import PassedCase
from src.commands.test.reporter import TestReporter
from src.utils.config.project_test import make_mock_project

current_directory = Path(__file__).parent


@pytest.fixture(name="test_root_dir")
def fixture_test_root_dir():
    return Path(current_directory, "examples")


def all_passed(results):
    return all(lambda r: isinstance(r, PassedCase), results)
@pytest.mark.asyncio
async def test_run_test_runner(mocker, test_root_dir):
    contracts = {"main": ["examples/basic.cairo"]}
    mock_project = make_mock_project(mocker, contracts, str(test_root_dir))
    results = await run_test_runner(
        project=mock_project,
        tests_root=test_root_dir,
        omit=re.compile(
            r"(test_basic|test_basic_failure|test_basic_broken|test_invalid_syntax).*"
        ),
        cairo_paths=[],
    )
    assert all_passed(results)


@pytest.mark.asyncio
async def test_run_syntaxtically_valid_tests(reporter, test_root_dir):
    results = await run_test_runner(
        test_root_dir,
        cairo_paths=[
            test_root_dir.resolve(),
            Path(test_root_dir, "broken"),  # Additional broken contract source
        ],
        match=re.compile(r"(test_basic|test_basic_failure|test_basic_broken).*"),
    )
    # assert reporter.collected_count == 4
    # assert len(reporter.failed_cases) == 2
    # assert len(reporter.passed_cases) == 2


@pytest.mark.asyncio
async def test_no_collected_items(reporter, test_root_dir):
    results = await run_test_runner(
        reporter,
        test_root_dir,
        cairo_paths=[
            test_root_dir.resolve(),
            Path(test_root_dir, "broken"),  # Additional broken contract source
        ],
        match=re.compile(r".*empty/no_test_functions.*"),
    )
    assert not reporter.failed_cases
    assert not reporter.passed_cases
    assert not reporter.broken_tests


@pytest.mark.asyncio
async def test_revert(reporter, test_root_dir):
    results = await run_test_runner(
        reporter,
        test_root_dir,
        cairo_paths=[
            test_root_dir.resolve(),
            Path(test_root_dir, "broken"),  # Additional broken contract source
        ],
        match=re.compile(r".*(revert).*"),
    )
    assert not reporter.failed_cases

@pytest.mark.asyncio
async def test_cheats(reporter):
    await run_test_runner(reporter, current_directory / "examples" / "cheats")
    assert not reporter.failed_cases
