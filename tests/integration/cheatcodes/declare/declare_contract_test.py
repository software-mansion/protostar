from pathlib import Path

import pytest

from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases,
)


@pytest.mark.asyncio
async def test_declare_contract(run_cairo_test_runner: RunCairoTestRunnerFixture):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "declare_contract_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_deploy_declared_contract",
            "test_deploy_declared_contract_in_proxy",
            "test_deploy_declared_contract_deploy_zero_flag",
        ],
        expected_failed_test_cases_names=[],
    )
