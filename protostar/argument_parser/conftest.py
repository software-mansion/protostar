from typing import Optional, Any

import pytest

from .argument import Argument
from .command import Command


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

    @property
    def arguments(self):
        return []

    async def run(self, args: Any):
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
    def arguments(self):
        return [
            Argument(
                name="foo",
                description="foo_desc",
                example="FOO --foo",
                type="bool",
            )
        ]

    async def run(self, args: Any):
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
    def arguments(self):
        return []

    async def run(self, args: Any):
        pass


@pytest.fixture(name="foo_command")
def foo_command_fixture() -> FooCommand:
    return FooCommand()


@pytest.fixture(name="bar_command")
def bar_command_fixture() -> BarCommand:
    return BarCommand()


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
        def arguments(self) -> list[Argument]:
            return args

        async def run(self, args: Any):
            return await super().run(args)

    return FakeCommand()
