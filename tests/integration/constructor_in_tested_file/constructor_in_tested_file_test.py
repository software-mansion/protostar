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

    testing_summary = await test_command.test(
        targets=[f"{Path(__file__).parent}/basic_contract_test.cairo"],
    )

    assert len(testing_summary.broken) == 1
    assert (
        "constructor expecting arguments"
        in cast(ProtostarException, testing_summary.broken[0].exception).message
    )


@pytest.mark.asyncio
async def test_should_not_break_test_suite(
    mocker: MockerFixture,
):
    test_command = TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    )

    testing_summary = await test_command.test(
        targets=[f"{Path(__file__).parent}/basic_contract_integration_test.cairo"],
    )

    assert len(testing_summary.broken) == 0
