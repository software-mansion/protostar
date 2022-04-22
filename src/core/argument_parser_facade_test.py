from argparse import ArgumentParser
from pathlib import Path
from typing import Pattern

from src.core.application import Application
from src.core.argument_parser_facade import ArgumentParserFacade
from src.core.command import Command
from src.core.conftest import FooCommand

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


# def test_regexp_argument():
#     app = Application(
#         root_args=[
#             Command.Argument(name="match", description="...", input_type="regexp")
#         ]
#     )
#     parser = ArgumentParserFacade(ArgumentParser(), app)

#     result = parser.parse(["--mach", ".*"])

#     assert isinstance(result.dir, Pattern)
