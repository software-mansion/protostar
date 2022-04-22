from argparse import ArgumentParser
from typing import List, Optional

import pytest

from src.application import AbstractCommand, Application, ArgumentParserFacade


class FooCommand(AbstractCommand):
    @property
    def name(self) -> str:
        return "FOO"

    @property
    def description(self) -> str:
        return "FOO_DESC"

    @property
    def example(self) -> Optional[str]:
        return "$ foo"

    @property
    def arguments(self) -> List[AbstractCommand.Argument]:
        return [
            AbstractCommand.Argument(
                name="foo",
                description="foo_desc",
                example="FOO --foo",
                input_type="bool",
            )
        ]

    async def run(self):
        pass


class BarCommand(AbstractCommand):
    @property
    def name(self) -> str:
        return "BAR"

    @property
    def description(self) -> str:
        return "BAR_DESC"

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self) -> List[AbstractCommand.Argument]:
        return []

    async def run(self):
        pass


@pytest.fixture(name="foo_command")
def foo_command_fixture() -> FooCommand:
    return FooCommand()


@pytest.fixture(name="bar_command")
def bar_command_fixture() -> BarCommand:
    return BarCommand()


def test_generating_markdown_for_commands(
    foo_command: FooCommand, bar_command: FooCommand
):
    app = Application(commands=[foo_command, bar_command], root_args=[])

    result = app.generate_cli_reference_markdown()
    splitted_result = result.split("\n")

    assert f"## `{bar_command.name}`" in splitted_result
    assert bar_command.example is None
    assert f"{bar_command.description}" in splitted_result

    assert f"## `{foo_command.name}`" in splitted_result
    assert f"{foo_command.example}" in splitted_result
    assert f"{foo_command.description}" in splitted_result


def test_generating_markdown_for_command_arguments(foo_command: FooCommand):
    app = Application(commands=[foo_command], root_args=[])

    result = app.generate_cli_reference_markdown()
    splitted_result = result.split("\n")

    assert f"## `{foo_command.name}`" in splitted_result
    assert f"### `{foo_command.arguments[0].name}`" in splitted_result
    assert f"{foo_command.arguments[0].example}" in splitted_result
    assert f"{foo_command.arguments[0].description}" in splitted_result


# TODO: test_root_args
# TODO: test_order


def test_basic_argument_parsing(foo_command: FooCommand):
    app = Application(commands=[foo_command], root_args=[])
    parser = ArgumentParserFacade(ArgumentParser())

    parser = app.setup_parser(parser)
    result = parser.parse(["FOO"])

    assert result.command == foo_command.name
    assert result.foo is False
