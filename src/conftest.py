from typing import List, Optional

import pytest

from src.core.command import Command


class BaseTestCommand(Command):
    @property
    def name(self) -> str:
        return "FOO"

    @property
    def description(self) -> str:
        return "FOO_DESC"

    @property
    def example(self) -> Optional[str]:
        return "$ foo"

    async def run(self, args):
        pass


class FooCommand(Command):
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
    def arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="foo",
                description="foo_desc",
                example="FOO --foo",
                type="bool",
            )
        ]

    async def run(self, args):
        pass


class BarCommand(Command):
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
    def arguments(self) -> List[Command.Argument]:
        return []

    async def run(self, args):
        pass


@pytest.fixture(name="foo_command")
def foo_command_fixture() -> FooCommand:
    return FooCommand()


@pytest.fixture(name="bar_command")
def bar_command_fixture() -> BarCommand:
    return BarCommand()


# MagicMock doesn't work when awaited
@pytest.fixture(name="create_async_called_checker")
def fixture_create_async_called_checker():
    def create_async_called_checker():
        was_called_ref = {"current": False}

        async def on_run(_args) -> None:
            was_called_ref["current"] = True
            return None

        return (on_run, was_called_ref)

    return create_async_called_checker
