from argparse import ArgumentParser

from src.core.application import Application
from src.core.argument_parser_facade import ArgumentParserFacade
from src.core.conftest import FooCommand

# TODO: test_root_args
# TODO: test_order


def test_basic_argument_parsing(foo_command: FooCommand):
    app = Application(commands=[foo_command], root_args=[])
    parser = ArgumentParserFacade(ArgumentParser(), app)

    result = parser.parse(["FOO"])

    assert result.command == foo_command.name
    assert result.foo is False
