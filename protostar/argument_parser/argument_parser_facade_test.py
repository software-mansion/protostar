from pathlib import Path
from typing import Any, List, Optional, Pattern

import pytest

from conftest import BaseTestCommand, FooCommand

from .argument_parser_facade import (
    ArgumentParserFacade,
    MissingRequiredArgumentException,
)
from .cli_app import CLIApp
from .command import Command
from .config_file_argument_resolver import ConfigFileArgumentResolverProtocol


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

    result = parser.parse(["--dir", "protostar"])

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


def test_int_argument():
    app = CLIApp(root_args=[Command.Argument(name="x", description="...", type="int")])
    parser = ArgumentParserFacade(app)

    result = parser.parse(["--x", "123"])

    assert result.x == 123

    with pytest.raises(SystemExit):
        parser.parse(["--x", "foo"])


def test_wei_argument():
    app = CLIApp(root_args=[Command.Argument(name="x", description="...", type="wei")])
    parser = ArgumentParserFacade(app)

    result = parser.parse(["--x", "123"])

    assert result.x == 123

    with pytest.raises(SystemExit):
        parser.parse(["--x", "foo"])


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
    with pytest.raises(MissingRequiredArgumentException):
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
    with pytest.raises(MissingRequiredArgumentException):
        ArgumentParserFacade(app).parse(["FOO"])


class FakeConfigFileArgumentResolver(ConfigFileArgumentResolverProtocol):
    def __init__(self, argument_value: Optional[Any]) -> None:
        super().__init__()
        self._canned_response = argument_value

    def resolve_argument(
        self, command_name: Optional[str], argument_name: str
    ) -> Optional[Any]:
        return self._canned_response


def test_loading_default_values_from_provider(foo_command: FooCommand):
    app = CLIApp(
        root_args=[Command.Argument(name="bar", description="...", type="str")],
        commands=[foo_command],
    )

    result = ArgumentParserFacade(
        app, FakeConfigFileArgumentResolver(argument_value="FOOBAR")
    ).parse(["FOO"])

    assert result.foo == "FOOBAR"
    assert result.bar == "FOOBAR"


def test_loading_required_value_from_provider():
    fake_arg = Command.Argument(
        name="fake-arg", description="...", type="str", is_required=True
    )

    class FakeCommand(Command):
        @property
        def name(self) -> str:
            return "fake-cmd"

        @property
        def description(self) -> str:
            return "..."

        @property
        def example(self) -> Optional[str]:
            return None

        @property
        def arguments(self) -> List[Command.Argument]:
            return [fake_arg]

        async def run(self, args: Any):
            return await super().run(args)

    fake_command = FakeCommand()
    app = CLIApp(
        root_args=[],
        commands=[fake_command],
    )

    fake_value = "FAKE_VALUE"

    parser = ArgumentParserFacade(
        app, FakeConfigFileArgumentResolver(argument_value=fake_value)
    )

    result = parser.parse(["fake-cmd"])

    assert result.fake_arg == fake_value
