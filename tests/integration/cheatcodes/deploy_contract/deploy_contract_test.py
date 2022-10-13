import asyncio
from pathlib import Path

import pytest

from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases,
)


@pytest.mark.asyncio
async def test_deploy_contract(run_cairo_test_runner: RunCairoTestRunnerFixture):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "deploy_contract_test.cairo",
        cairo_path=[Path() / "tests" / "integration" / "data"],
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_deploy_contract",
            "test_deploy_contract_simplified",
            "test_deploy_contract_with_constructor",
            "test_deploy_contract_with_constructor_steps",
            "test_deploy_contract_pranked",
            "test_deploy_the_same_contract_twice",
            "test_deploy_using_syscall",
            "test_syscall_after_deploy",
            "test_utilizes_cairo_path",
            "test_data_transformation",
            "test_passing_constructor_data_as_list",
            "test_deploy_using_syscall_non_zero_flag",
            "test_constructor_no_args_executed",
            "test_emitting_events_from_user_contract_constructor_and_from_current_contract",
        ],
        expected_failed_test_cases_names=[],
    )


@pytest.mark.asyncio
def test_deploying_contract_by_name(create_protostar_project):
    with create_protostar_project() as protostar:
        protostar.create_files(
            {
                "./src/main.cairo": Path(__file__).parent / "basic_contract.cairo",
                "./tests/test_main.cairo": Path(__file__).parent
                / "deploying_contract_by_name_test.cairo",
            }
        )
        result = asyncio.run(protostar.test(["./tests"]))

    assert_cairo_test_cases(
        result, expected_passed_test_cases_names=["test_deploy_contract_by_name"]
    )
