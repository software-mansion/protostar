from pathlib import Path

import pytest

from protostar.commands.test.test_command import TestCommand
from tests.integration.conftest import assert_cairo_test_cases


@pytest.fixture(name="target")
def target_fixture() -> str:
    return f"{Path(__file__).parent}/deploy_contract_test.cairo"


@pytest.mark.asyncio
async def test_deploy_contract(mocker, target: str):
    testing_summary = await TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    ).test(targets=[target], ignored_targets=[f"{target}::test_data_transformation"])

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_proxy_contract",
            "test_missing_logic_contract",
        ],
        expected_failed_test_cases_names=[],
    )


@pytest.mark.asyncio
async def test_data_transformation(mocker, target):
    testing_summary = await TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    ).test(targets=[f"{target}::test_data_transformation"])

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_data_transformation",
        ],
        expected_failed_test_cases_names=[],
    )
