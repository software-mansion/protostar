from pathlib import Path

import pytest

from protostar.commands.test.test_command import TestCommand
from tests.integration.conftest import assert_cairo_test_cases


@pytest.mark.asyncio
async def test_store_cheatcode(mocker):
    testing_summary = await TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    ).test(targets=[f"{Path(__file__).parent}/store_test.cairo"])

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_store_in_deployed_contract",
            "test_store_map_in_deployed_contract",
            "test_store_map_complex_key_in_deployed_contract",
            "test_store_map_struct_key_in_deployed_contract",
            "test_store_map_struct_val_in_deployed_contract",
            "test_map_store_local",
        ],
        expected_failed_test_cases_names=[],
    )
