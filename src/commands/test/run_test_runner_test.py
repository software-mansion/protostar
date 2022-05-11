import re
from pathlib import Path

import pytest

from src.commands.test import run_test_runner
from src.commands.test.reporter import TestingResult
from src.utils.config.project_test import make_mock_project

current_directory = Path(__file__).parent


@pytest.fixture(name="test_root_dir")
def fixture_test_root_dir():
    return Path(current_directory, "examples")


@pytest.mark.asyncio
async def test_run_test_runner(mocker, test_root_dir):
    contracts = {"main": ["examples/basic.cairo"]}
    mock_project = make_mock_project(mocker, contracts, str(test_root_dir))
    reporters = await run_test_runner(
        project=mock_project,
        tests_root=test_root_dir,
        omit=re.compile(
            r"(test_basic|test_basic_failure|test_basic_broken|test_invalid_syntax).*"
        ),
        cairo_paths=[],
    )

    testing_result = TestingResult.from_reporters(reporters)
    assert len(testing_result.passed) == 23
    assert len(testing_result.failed) == 0
    assert len(testing_result.broken) == 0


@pytest.mark.asyncio
async def test_run_syntaxtically_valid_tests(test_root_dir):
    reporters = await run_test_runner(
        test_root_dir,
        cairo_paths=[
            test_root_dir.resolve(),
            Path(test_root_dir, "broken"),  # Additional broken contract source
        ],
        match=re.compile(r"(test_basic|test_basic_failure|test_basic_broken).*"),
    )
    testing_result = TestingResult.from_reporters(reporters)
    assert len(testing_result.test_files) == 3
    assert len(testing_result.failed) == 2
    assert len(testing_result.passed) == 2


@pytest.mark.asyncio
async def test_no_collected_items(test_root_dir):
    results = await run_test_runner(
        test_root_dir,
        cairo_paths=[
            test_root_dir.resolve(),
            Path(test_root_dir, "broken"),  # Additional broken contract source
        ],
        match=re.compile(r".*empty/no_test_functions.*"),
    )
    assert not results


@pytest.mark.asyncio
async def test_revert(test_root_dir):
    reporters = await run_test_runner(
        test_root_dir,
        cairo_paths=[
            test_root_dir.resolve(),
            Path(test_root_dir, "broken"),  # Additional broken contract source
        ],
        match=re.compile(r".*(revert).*"),
    )
    testing_result = TestingResult.from_reporters(reporters)
    assert len(testing_result.failed) == 0


async def test_cheats():
    reporters = await run_test_runner(current_directory / "examples" / "cheats")

    testing_result = TestingResult.from_reporters(reporters)
    assert len(testing_result.failed) == 0


async def test_prank():
    reporters = await run_test_runner(current_directory / "examples" / "cheats"/ "test_prank.cairo")

    testing_result = TestingResult.from_reporters(reporters)
    assert len(testing_result.failed) == 0
