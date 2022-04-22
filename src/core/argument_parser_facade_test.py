from argparse import ArgumentParser
from pathlib import Path
from typing import Pattern

from src.core.application import Application
from src.core.argument_parser_facade import ArgumentParserFacade
from src.core.command import Command
from src.core.conftest import BaseTestCommand, FooCommand

# TODO: test_root_args
# TODO: test_order


def test_bool_argument_parsing(foo_command: FooCommand):
    app = Application(commands=[foo_command])
    parser = ArgumentParserFacade(ArgumentParser(), app)

    result = parser.parse(["FOO"])

    assert result.command == foo_command.name
    assert result.foo is False


def test_directory_argument():
    app = Application(
        root_args=[
            Command.Argument(name="dir", description="...", input_type="directory")
        ]
    )
    parser = ArgumentParserFacade(ArgumentParser(), app)

    result = parser.parse(["--dir", "src"])

    assert isinstance(result.dir, Path)


def test_regexp_argument():
    app = Application(
        root_args=[
            Command.Argument(name="match", description="...", input_type="regexp")
        ]
    )
    parser = ArgumentParserFacade(ArgumentParser(), app)

    result = parser.parse(["--match", ".*"])

    assert isinstance(result.match, Pattern)


def test_path_argument():
    app = Application(
        root_args=[Command.Argument(name="x", description="...", input_type="path")]
    )
    parser = ArgumentParserFacade(ArgumentParser(), app)

    result = parser.parse(["--x", "foo"])

    assert isinstance(result.x, Path)


def test_short_name_argument():
    app = Application(
        root_args=[
            Command.Argument(
                name="directory", short_name="d", description="...", input_type="str"
            )
        ]
    )
    parser = ArgumentParserFacade(ArgumentParser(), app)

    result = parser.parse(["-d", "foo"])

    assert result.directory == "foo"


def test_arrays():
    app = Application(
        root_args=[
            Command.Argument(
                name="target",
                description="...",
                input_type="str",
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
                    name="target", description="...", is_required=True, input_type="str"
                )
            ]

    cmd = CommandWithRequiredArg()
    app = Application(
        commands=[cmd],
    )
    parser = ArgumentParserFacade(ArgumentParser(), app)

    result = parser.parse([cmd.name, "foo"])

    assert result.target == "foo"


def test_default():
    app = Application(
        root_args=[
            Command.Argument(
                name="target", description="...", input_type="str", default="foo"
            )
        ]
    )
    parser = ArgumentParserFacade(ArgumentParser(), app)

    result = parser.parse([])

    assert result.target == "foo"
