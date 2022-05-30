from pathlib import Path

import pytest

from protostar.commands.test.test_command import TestCommand
from tests.integration.conftest import assert_cairo_test_cases


@pytest.mark.skip
@pytest.mark.asyncio
async def test_testing_hooks(mocker):
    testing_summary = await TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    ).test(target=Path(__file__).parent / "testing_hooks_test.cairo")

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=["test_contract_was_deployed_in_setup_state"],
        expected_failed_test_cases_names=[],
    )
