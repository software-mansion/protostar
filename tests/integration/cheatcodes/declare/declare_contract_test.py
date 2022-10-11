import asyncio
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


@pytest.mark.asyncio
def test_declaring_contract_by_name(create_protostar_project):
    with create_protostar_project() as protostar:
        protostar.create_files(
            {
                "./src/main.cairo": Path(__file__).parent / "basic_contract.cairo",
                "./tests/test_main.cairo": Path(__file__).parent
                / "declaring_contract_by_name_test.cairo",
            }
        )
        protostar.build_sync()
        result = asyncio.run(protostar.test(["./tests"]))

    assert_cairo_test_cases(
        result, expected_passed_test_cases_names=["test_declaring_contract_by_name"]
    )
