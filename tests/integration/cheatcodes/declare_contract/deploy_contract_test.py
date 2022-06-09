from pathlib import Path

import pytest

from protostar.commands.test.test_command import TestCommand
from tests.integration.conftest import assert_cairo_test_cases


@pytest.mark.asyncio
async def test_deploy_contract(mocker):
    testing_summary = await TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    ).test(targets=[str(Path(__file__).parent / "declare_contract_test.cairo")])

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_deploy_declared_contract",
            "test_deploy_declared_contract_in_proxy"
        ],
        expected_failed_test_cases_names=[],
    )
