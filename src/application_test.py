from typing import Optional

import pytest

from src.application import AbstractCommand, Application


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

    async def run(self):
        pass


@pytest.fixture(name="foo_command")
def foo_command_fixture() -> FooCommand:
    return FooCommand([])


@pytest.fixture(name="bar_command")
def bar_command_fixture() -> BarCommand:
    return BarCommand([])


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
