import pytest

from src.conftest import FooCommand
from src.cli.argument_parser_facade import ArgumentParserFacade
from src.cli.cli_app import CLIApp
from src.cli.command import Command


@pytest.mark.asyncio
async def test_command_run_method_was_called(
    foo_command: FooCommand, create_async_called_checker
):
    (on_run, was_called_ref) = create_async_called_checker()
    foo_command.run = on_run
    cli = CLIApp(commands=[foo_command])
    parser = ArgumentParserFacade(cli)

    result = await cli.run(parser.parse([foo_command.name]))

    assert was_called_ref["current"]
    assert result is True


@pytest.mark.asyncio
async def test_run_returns_false_when_no_command_was_called(foo_command: FooCommand):
    cli = CLIApp(
        commands=[foo_command],
        root_args=[Command.Argument(name="version", type="bool", description="...")],
    )
    parser = ArgumentParserFacade(cli)

    result = await cli.run(parser.parse(["--version"]))

    assert result is False
