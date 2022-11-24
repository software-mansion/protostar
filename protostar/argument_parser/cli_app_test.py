from asyncio import Future

import pytest
from pytest_mock import MockerFixture

from .argument import Argument
from .argument_parser_facade import ArgumentParserFacade
from .cli_app import CLIApp
from .conftest import FooCommand


async def test_command_run_method_was_called(
    foo_command: FooCommand, mocker: MockerFixture
):
    foo_command.run = mocker.MagicMock()
    foo_command.run.return_value = Future()
    foo_command.run.return_value.set_result(None)
    cli = CLIApp(commands=[foo_command])
    parser = ArgumentParserFacade(cli)

    await cli.run(parser.parse([foo_command.name]))

    foo_command.run.assert_called_once()


async def test_fail_when_no_command_was_found(foo_command: FooCommand):
    cli = CLIApp(
        commands=[foo_command],
        root_args=[Argument(name="version", type="bool", description="...")],
    )
    parser = ArgumentParserFacade(cli)

    await cli.run(parser.parse(["FOO"]))

    with pytest.raises(CLIApp.CommandNotFoundError):
        await cli.run(None)
