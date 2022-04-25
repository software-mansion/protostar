from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Optional, Pattern

from src.core.argument_parser_facade import (
    ArgumentDefaultValueProvider,
    ArgumentParserFacade,
)
from src.core.cli import CLI
from src.core.command import Command
from src.core.conftest import BaseTestCommand, FooCommand

# TODO: test_root_args
# TODO: test_order


def test_bool_argument_parsing(foo_command: FooCommand):
    app = CLI(commands=[foo_command])
    parser = ArgumentParserFacade(ArgumentParser(), app)

    result = parser.parse(["FOO"])

    assert result.command == foo_command.name
    assert result.foo is False or result.foo is None


def test_directory_argument():
    app = CLI(
        root_args=[Command.Argument(name="dir", description="...", type="directory")]
    )
    parser = ArgumentParserFacade(ArgumentParser(), app)

    result = parser.parse(["--dir", "src"])

    assert isinstance(result.dir, Path)


def test_regexp_argument():
    app = CLI(
        root_args=[Command.Argument(name="match", description="...", type="regexp")]
    )
    parser = ArgumentParserFacade(ArgumentParser(), app)

    result = parser.parse(["--match", ".*"])

    assert isinstance(result.match, Pattern)


def test_path_argument():
    app = CLI(root_args=[Command.Argument(name="x", description="...", type="path")])
    parser = ArgumentParserFacade(ArgumentParser(), app)

    result = parser.parse(["--x", "foo"])

    assert isinstance(result.x, Path)


def test_short_name_argument():
    app = CLI(
        root_args=[
            Command.Argument(
                name="directory", short_name="d", description="...", type="str"
            )
        ]
    )
    parser = ArgumentParserFacade(ArgumentParser(), app)

    result = parser.parse(["-d", "foo"])

    assert result.directory == "foo"


def test_arrays():
    app = CLI(
        root_args=[
            Command.Argument(
                name="target",
                description="...",
                type="str",
                is_array=True,
            )
        ]
    )
    parser = ArgumentParserFacade(ArgumentParser(), app)

    result = parser.parse(["--target", "foo", "bar"])

    assert result.target == ["foo", "bar"]


def test_required():
    class CommandWithRequiredArg(BaseTestCommand):
        @property
        def arguments(self):
            return [
                Command.Argument(
                    name="target", description="...", is_required=True, type="str"
                )
            ]

    cmd = CommandWithRequiredArg()
    app = CLI(
        commands=[cmd],
    )
    parser = ArgumentParserFacade(ArgumentParser(), app)

    result = parser.parse([cmd.name, "foo"])

    assert result.target == "foo"


def test_default():
    app = CLI(
        root_args=[
            Command.Argument(
                name="target", description="...", type="str", default="foo"
            )
        ]
    )
    parser = ArgumentParserFacade(ArgumentParser(), app)

    result = parser.parse([])

    assert result.target == "foo"


def test_loading_default_values_from_provider(foo_command: FooCommand):
    app = CLI(
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

    parser = ArgumentParserFacade(ArgumentParser(), app, DefaultValuesProvider())

    result = parser.parse(["FOO"])
    assert result.foo == "COMMAND_ARG_DEFAULT"
    assert result.bar == "ROOT_ARG_DEFAULT"
