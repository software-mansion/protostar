from asyncio import Future

import pytest
from pytest_mock import MockerFixture

from src.cli.argument_parser_facade import ArgumentParserFacade
from src.cli.cli_app import CLIApp
from src.cli.command import Command
from src.conftest import FooCommand


@pytest.mark.asyncio
async def test_command_run_method_was_called(
    foo_command: FooCommand, mocker: MockerFixture
):
    foo_command.run = mocker.MagicMock()
    foo_command.run.return_value = Future()
    foo_command.run.return_value.set_result(True)
    cli = CLIApp(commands=[foo_command])
    parser = ArgumentParserFacade(cli)

    await cli.run(parser.parse([foo_command.name]))

    foo_command.run.assert_called_once()


@pytest.mark.asyncio
async def test_run_returns_false_when_no_command_was_called(foo_command: FooCommand):
    cli = CLIApp(
        commands=[foo_command],
        root_args=[Command.Argument(name="version", type="bool", description="...")],
    )
    parser = ArgumentParserFacade(cli)

    cmd_result = await cli.run(parser.parse(["FOO"]))
    arg_result = await cli.run(parser.parse(["--version"]))

    assert cmd_result is True
    assert arg_result is False
