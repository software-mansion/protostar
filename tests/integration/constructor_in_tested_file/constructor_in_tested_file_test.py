# pylint: disable=protected-access
from pathlib import Path
from typing import cast

import pytest
from pytest_mock import MockerFixture

from protostar.commands.test.test_command import TestCommand
from protostar.protostar_exception import ProtostarException


@pytest.mark.asyncio
async def test_should_pretty_print_constructor_error(mocker: MockerFixture):

    test_command = TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    )
    test_command._build_include_paths = mocker.MagicMock()
    test_command._build_include_paths.return_value = [str(Path(__file__).parent)]

    testing_summary = await test_command.test(
        targets=[f"{Path(__file__).parent}/basic_contract_test.cairo"],
    )

    assert len(testing_summary.broken) == 1
    assert (
        "constructor expecting arguments"
        in cast(ProtostarException, testing_summary.broken[0].exception).message
    )
