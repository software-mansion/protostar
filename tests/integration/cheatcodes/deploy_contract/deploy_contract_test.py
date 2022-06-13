from pathlib import Path
from typing import cast

import pytest

from protostar.commands.test.test_command import TestCommand
from tests.integration.conftest import assert_cairo_test_cases
from unittest.mock import MagicMock


@pytest.mark.asyncio
async def test_deploy_contract(mocker):
    protostar_directory_mock = mocker.MagicMock()
    cast(MagicMock, protostar_directory_mock.add_protostar_cairo_dir).return_value = [
        Path() / "tests" / "integration" / "data"
    ]
    testing_summary = await TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=protostar_directory_mock,
    ).test(targets=[f"{Path(__file__).parent}/deploy_contract_test.cairo"])

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_deploy_contract",
            "test_deploy_contract_simplified",
            "test_deploy_contract_with_contructor",
            "test_deploy_contract_with_contructor_steps",
            "test_deploy_contract_pranked",
            "test_deploy_the_same_contract_twice",
            "test_deploy_using_syscall",
            "test_syscall_after_deploy",
            "test_utilizes_cairo_path"
        ],
        expected_failed_test_cases_names=[],
    )
