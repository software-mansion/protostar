from pathlib import Path
from typing import Any, Optional, Pattern

import pytest

from src.conftest import BaseTestCommand, FooCommand
from src.cli.argument_parser_facade import (
    ArgumentDefaultValueProvider,
    ArgumentParserFacade,
)
from src.cli.cli_app import CLIApp
from src.cli.command import Command


def test_bool_argument_parsing(foo_command: FooCommand):
    app = CLIApp(commands=[foo_command])
    parser = ArgumentParserFacade(app)

    result = parser.parse(["FOO"])

    assert result.command == foo_command.name
    assert result.foo is False or result.foo is None


def test_directory_argument():
    app = CLIApp(
        root_args=[Command.Argument(name="dir", description="...", type="directory")]
    )
    parser = ArgumentParserFacade(app)

    result = parser.parse(["--dir", "src"])

    assert isinstance(result.dir, Path)


def test_regexp_argument():
    app = CLIApp(
        root_args=[Command.Argument(name="match", description="...", type="regexp")]
    )
    parser = ArgumentParserFacade(app)

    result = parser.parse(["--match", ".*"])

    assert isinstance(result.match, Pattern)


def test_path_argument():
    app = CLIApp(root_args=[Command.Argument(name="x", description="...", type="path")])
    parser = ArgumentParserFacade(app)

    result = parser.parse(["--x", "foo"])

    assert isinstance(result.x, Path)


def test_short_name_argument():
    app = CLIApp(
        root_args=[
            Command.Argument(
                name="directory", short_name="d", description="...", type="str"
            )
        ]
    )
    parser = ArgumentParserFacade(app)

    result = parser.parse(["-d", "foo"])

    assert result.directory == "foo"


def test_arrays():
    app = CLIApp(
        root_args=[
            Command.Argument(
                name="target",
                description="...",
                type="str",
                is_array=True,
            )
        ]
    )
    parser = ArgumentParserFacade(app)

    result = parser.parse(["--target", "foo", "bar"])

    assert result.target == ["foo", "bar"]


def test_positional():
    class CommandWithRequiredArg(BaseTestCommand):
        @property
        def arguments(self):
            return [
                Command.Argument(
                    name="target", description="...", is_positional=True, type="str"
                )
            ]

    cmd = CommandWithRequiredArg()
    app = CLIApp(
        commands=[cmd],
    )
    parser = ArgumentParserFacade(app)

    result = parser.parse([cmd.name, "foo"])

    assert result.target == "foo"


def test_default():
    app = CLIApp(
        root_args=[
            Command.Argument(
                name="target", description="...", type="str", default="foo"
            )
        ]
    )
    parser = ArgumentParserFacade(app)

    result = parser.parse([])

    assert result.target == "foo"


def test_required_non_positional_arg():
    app = CLIApp(
        root_args=[
            Command.Argument(
                name="target", description="...", type="str", is_required=True
            )
        ]
    )

    ArgumentParserFacade(app).parse(["--target", "foo"])
    with pytest.raises(SystemExit):
        ArgumentParserFacade(app).parse([])


def test_required_positional_arg():
    class CommandWithRequiredArg(BaseTestCommand):
        @property
        def arguments(self):
            return [
                Command.Argument(
                    name="target",
                    description="...",
                    type="str",
                    is_positional=True,
                    is_required=True,
                )
            ]

    app = CLIApp(commands=[CommandWithRequiredArg()])

    ArgumentParserFacade(app).parse(["FOO", "x"])
    with pytest.raises(SystemExit):
        ArgumentParserFacade(app).parse(["FOO"])


def test_loading_default_values_from_provider(foo_command: FooCommand):
    app = CLIApp(
        root_args=[Command.Argument(name="bar", description="...", type="str")],
        commands=[foo_command],
    )

    class DefaultValuesProvider(ArgumentDefaultValueProvider):
        def get_default_value(
            self, command: Optional[Command], _argument: Command.Argument
        ) -> Optional[Any]:
            if command:
                return "COMMAND_ARG_DEFAULT"
            return "ROOT_ARG_DEFAULT"

    parser = ArgumentParserFacade(app, DefaultValuesProvider())

    result = parser.parse(["FOO"])
    assert result.foo == "COMMAND_ARG_DEFAULT"
    assert result.bar == "ROOT_ARG_DEFAULT"
