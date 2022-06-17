# pylint: disable=protected-access
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from protostar.commands.test.test_command import TestCommand


@pytest.fixture(name="pretty_printed_error_message_substring")
def pretty_printed_error_message_substring_fixture() -> str:
    return "constructor expecting arguments"


@pytest.mark.asyncio
async def test_should_pretty_print_constructor_error(
    mocker: MockerFixture, pretty_printed_error_message_substring: str
):
    test_command = TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    )

    testing_summary = await test_command.test(
        targets=[f"{Path(__file__).parent}/basic_contract_test.cairo"],
    )

    assert len(testing_summary.broken) == 1
    assert pretty_printed_error_message_substring in str(
        testing_summary.broken[0].exception
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


@pytest.mark.asyncio
async def test_not_pretty_printing_the_constructor_error(
    mocker: MockerFixture, pretty_printed_error_message_substring: str
):
    test_command = TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    )

    testing_summary = await test_command.test(
        targets=[f"{Path(__file__).parent}/error_from_deploy_syscall_test.cairo"],
    )

    assert len(testing_summary.failed) == 1
    assert pretty_printed_error_message_substring not in str(
        testing_summary.failed[0].exception
    )
