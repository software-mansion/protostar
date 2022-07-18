from pathlib import Path

import pytest

from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_testing_hooks(run_cairo_test_runner: RunCairoTestRunnerFixture):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "testing_hooks_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_contract_was_deployed_in_setup",
        ],
        expected_failed_test_cases_names=[],
    )


@pytest.mark.asyncio
async def test_invalid_setup(run_cairo_test_runner: RunCairoTestRunnerFixture):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "invalid_setup_test.cairo"
    )

    assert len(testing_summary.broken) == 1
