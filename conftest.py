from pathlib import Path
from typing import Dict, List, Optional, Union

import pytest

from protostar.cli.command import Command


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


FolderOrFileName = str
FileContent = str
FolderStructureComponent = Dict[
    FolderOrFileName, Union["FolderStructureComponent", FileContent]
]


def generate_folder_structure(path: Path, composite_map: FolderStructureComponent):
    for composite_name, composite in composite_map.items():
        if isinstance(composite, str):
            file_content = composite
            file_name = composite_name
            (path / file_name).write_text(file_content)
        else:
            directory_name = composite_name
            directory_path = path / directory_name
            directory_path.mkdir()
            generate_folder_structure(directory_path, composite)
