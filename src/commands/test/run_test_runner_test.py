import re
from pathlib import Path

import pytest

from src.commands.test import run_test_runner
from src.commands.test.reporter import TestReporter
from src.utils.config.project_test import make_mock_project

current_directory = Path(__file__).parent


@pytest.fixture(name="test_root_dir")
def fixture_test_root_dir():
    return Path(current_directory, "examples")


@pytest.fixture(name="reporter")
def fixture_reporter(test_root_dir):
    return TestReporter(test_root_dir)


@pytest.mark.asyncio
async def test_run_test_runner(mocker, test_root_dir, reporter):
    contracts = {"main": ["examples/basic.cairo"]}
    mock_project = make_mock_project(mocker, contracts, str(test_root_dir))
    await run_test_runner(
        reporter=reporter,
        project=mock_project,
        tests_root=test_root_dir,
        omit=re.compile(r".*invalid.*"),
        cairo_paths=[],
    )
    assert not reporter.failed_cases


@pytest.mark.asyncio
async def test_run_syntaxtically_valid_tests(reporter, test_root_dir):
    await run_test_runner(
        reporter,
        test_root_dir,
        cairo_paths=[
            test_root_dir.resolve(),
            Path(test_root_dir, "broken"),  # Additional broken contract source
        ],
        match=re.compile(r".*(nested|failure|broken).*"),
    )
    assert not reporter.failed_cases


@pytest.mark.asyncio
async def test_no_collected_items(reporter, test_root_dir):
    await run_test_runner(
        reporter,
        test_root_dir,
        cairo_paths=[
            test_root_dir.resolve(),
            Path(test_root_dir, "broken"),  # Additional broken contract source
        ],
        match=re.compile(r".*empty/no_test_functions.*"),
    )
    assert not reporter.failed_cases


@pytest.mark.asyncio
async def test_revert(reporter, test_root_dir):
    await run_test_runner(
        reporter,
        test_root_dir,
        cairo_paths=[
            test_root_dir.resolve(),
            Path(test_root_dir, "broken"),  # Additional broken contract source
        ],
        match=re.compile(r".*(revert).*"),
    )
    assert not reporter.failed_cases
