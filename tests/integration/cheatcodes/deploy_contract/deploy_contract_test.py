from pathlib import Path

import pytest

from protostar.commands.test.test_command import TestCommand
from tests.integration.conftest import assert_cairo_test_cases


@pytest.mark.asyncio
async def test_deploy_contract(mocker):
    testing_summary = await TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    ).test(target=Path(__file__).parent / "deploy_contract_test.cairo")

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_proxy_contract",
            "test_missing_logic_contract",
        ],
        expected_failed_test_cases_names=[],
    )
