from typing import List, Optional

import pytest

from src.core.command import AbstractCommand


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
