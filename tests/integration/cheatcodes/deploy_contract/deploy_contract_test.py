from pathlib import Path

import pytest

from protostar.commands.test.test_command import TestCommand
from tests.integration.conftest import assert_cairo_test_cases


@pytest.mark.asyncio
async def test_deploy_contract(mocker):
    testing_summary = await TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    ).test(targets=[f"{Path(__file__).parent}/deploy_contract_test.cairo"])

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_deploy_contract",
            "test_deploy_contract_simplified",
            "test_deploy_contract_with_contructor",
            "test_deploy_contract_with_contructor_steps",
            "test_deploy_contract_pranked",
            "test_deploy_the_same_contract_twice"
        ],
        expected_failed_test_cases_names=[],
    )
