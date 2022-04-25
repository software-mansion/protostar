from argparse import ArgumentParser

import pytest

from src.conftest import FooCommand
from src.core.argument_parser_facade import ArgumentParserFacade
from src.core.cli import CLI
from src.core.command import Command


@pytest.mark.asyncio
async def test_command_run_method_was_called(foo_command: FooCommand):
    # MagicMock doesn't work when awaited
    was_called_ref = {"current": False}

    async def on_run(_args) -> None:
        was_called_ref["current"] = True
        return None

    foo_command.run = on_run

    cli = CLI(commands=[foo_command])
    parser = ArgumentParserFacade(ArgumentParser(), cli)

    result = await cli.run(parser.parse([foo_command.name]))

    assert was_called_ref["current"]
    assert result is True


@pytest.mark.asyncio
async def test_run_returns_false_when_no_command_was_called(foo_command: FooCommand):
    cli = CLI(
        commands=[foo_command],
        root_args=[Command.Argument(name="version", type="bool", description="...")],
    )
    parser = ArgumentParserFacade(ArgumentParser(), cli)

    result = await cli.run(parser.parse(["--version"]))

    assert result is False
