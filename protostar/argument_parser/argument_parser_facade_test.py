from pathlib import Path
from typing import Any, List, Optional, Pattern

import pytest

from protostar.argument_parser.arg_type import ArgTypeName

from .argument import Argument
from .argument_parser_facade import (
    ArgumentParserFacade,
    MissingRequiredArgumentException,
)
from .cli_app import CLIApp
from .command import Command
from .config_file_argument_resolver import ConfigFileArgumentResolverProtocol
from .conftest import BaseTestCommand, FooCommand


def test_bool_argument_parsing(foo_command: FooCommand):
    app = CLIApp(commands=[foo_command])
    parser = ArgumentParserFacade(app)

    result = parser.parse(["FOO"])

    assert result.command == foo_command.name
    assert result.foo is False or result.foo is None


def test_directory_argument():
    app = CLIApp(root_args=[Argument(name="dir", description="...", type="directory")])
    parser = ArgumentParserFacade(app)

    result = parser.parse(["--dir", "protostar"])

    assert isinstance(result.dir, Path)


def test_regexp_argument():
    app = CLIApp(root_args=[Argument(name="match", description="...", type="regexp")])
    parser = ArgumentParserFacade(app)

    result = parser.parse(["--match", ".*"])

    assert isinstance(result.match, Pattern)


def test_path_argument():
    app = CLIApp(root_args=[Argument(name="x", description="...", type="path")])
    parser = ArgumentParserFacade(app)

    result = parser.parse(["--x", "foo"])

    assert isinstance(result.x, Path)


def test_int_argument():
    app = CLIApp(root_args=[Argument(name="x", description="...", type="int")])
    parser = ArgumentParserFacade(app)

    result = parser.parse(["--x", "123"])

    assert result.x == 123

    with pytest.raises(SystemExit):
        parser.parse(["--x", "foo"])


def test_short_name_argument():
    app = CLIApp(
        root_args=[
            Argument(name="directory", short_name="d", description="...", type="str")
        ]
    )
    parser = ArgumentParserFacade(app)

    result = parser.parse(["-d", "foo"])

    assert result.directory == "foo"


def test_arrays():
    app = CLIApp(
        root_args=[
            Argument(
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
                Argument(
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
            Argument(name="target", description="...", type="str", default="foo")
        ]
    )
    parser = ArgumentParserFacade(app)

    result = parser.parse([])

    assert result.target == "foo"


def test_required_non_positional_arg():
    app = CLIApp(
        root_args=[
            Argument(name="target", description="...", type="str", is_required=True)
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
                Argument(
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
        root_args=[Argument(name="bar", description="...", type="str")],
        commands=[foo_command],
    )

    result = ArgumentParserFacade(
        app, FakeConfigFileArgumentResolver(argument_value="FOOBAR")
    ).parse(["FOO"])

    assert result.foo == "FOOBAR"
    assert result.bar == "FOOBAR"


def test_loading_required_value_from_provider():
    fake_arg = Argument(
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
        def arguments(self) -> List[Argument]:
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


def create_fake_command(args: list[Argument]):
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
        def arguments(self) -> List[Argument]:
            return args

        async def run(self, args: Any):
            return await super().run(args)

    return FakeCommand()


def test_kebab_case_with_positional_arguments():
    app = CLIApp(
        root_args=[],
        commands=[
            create_fake_command(
                [
                    Argument(
                        name="kebab-case",
                        description="...",
                        type="str",
                        is_required=True,
                        is_positional=True,
                    )
                ]
            )
        ],
    )
    parser = ArgumentParserFacade(app)

    args = parser.parse(["fake-cmd", "value"])

    assert args.kebab_case == "value"


@pytest.mark.parametrize(
    "value_in_config_file, result",
    [
        ("21", 21),
        (37, 37),
        (["21", "37"], [21, 37]),
    ],
)
def test_parsing_extra_arguments_source(value_in_config_file: Any, result: Any):
    parser_called = False

    def parse_to_int(arg: str) -> int:
        assert isinstance(arg, str)
        nonlocal parser_called
        parser_called = True
        return int(arg)

    def fake_parser_resolver(_argument_type: ArgTypeName):
        return parse_to_int

    parser = ArgumentParserFacade(
        CLIApp(
            root_args=[
                Argument(
                    name="foo",
                    description="",
                    example="",
                    type="str",
                    is_array=isinstance(value_in_config_file, list),
                )
            ]
        ),
        config_file_argument_value_resolver=FakeConfigFileArgumentResolver(
            argument_value=value_in_config_file
        ),
        parser_resolver=fake_parser_resolver,
    )

    args = parser.parse("")

    assert parser_called
    assert args.foo == result
