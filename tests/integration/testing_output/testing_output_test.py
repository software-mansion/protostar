from pathlib import Path

import pytest

from protostar.commands.test.test_command import TestCommand


@pytest.mark.asyncio
async def test_testing_output(mocker):
    testing_summary = await TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    ).test(targets=[f"{Path(__file__).parent}/testing_output_test.cairo"])

    test_case_output = str(testing_summary.passed[0])
    assert "steps=" in test_case_output
    assert "pedersen_builtin=1" in test_case_output
