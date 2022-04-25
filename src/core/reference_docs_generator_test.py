from pathlib import Path

from src.core.cli import CLI
from src.core.command import Command
from src.conftest import FooCommand
from src.core.reference_docs_generator import ReferenceDocsGenerator


def test_generating_markdown_for_commands(
    foo_command: FooCommand, bar_command: FooCommand
):
    docs_generator = ReferenceDocsGenerator(
        CLI(commands=[foo_command, bar_command], root_args=[])
    )

    result = docs_generator.generate_cli_reference_markdown()
    splitted_result = result.split("\n")

    assert f"### `{bar_command.name}`" in splitted_result
    assert bar_command.example is None
    assert f"{bar_command.description}" in splitted_result

    assert f"### `{foo_command.name}`" in splitted_result
    assert f"{foo_command.example}" in splitted_result
    assert f"{foo_command.description}" in splitted_result


def test_generating_markdown_for_command_arguments(foo_command: FooCommand):
    docs_generator = ReferenceDocsGenerator(CLI(commands=[foo_command], root_args=[]))

    result = docs_generator.generate_cli_reference_markdown()
    splitted_result = result.split("\n")

    assert f"### `{foo_command.name}`" in splitted_result
    assert f"#### `--{foo_command.arguments[0].name}`" in splitted_result
    assert f"{foo_command.arguments[0].example}" in splitted_result
    assert f"{foo_command.arguments[0].description}" in splitted_result


def test_generating_default_type_and_array_info():
    docs_generator = ReferenceDocsGenerator(
        CLI(
            root_args=[
                Command.Argument(
                    name="foo",
                    description="...",
                    default="FOO",
                    is_array=True,
                    type="str",
                )
            ]
        )
    )

    result = docs_generator.generate_cli_reference_markdown()
    splitted_result = result.split("\n")

    assert "#### `--foo STR[]=FOO`" in splitted_result


def test_generating_short_name_info():
    docs_generator = ReferenceDocsGenerator(
        CLI(
            root_args=[
                Command.Argument(
                    name="foo",
                    short_name="f",
                    description="...",
                    type="bool",
                )
            ]
        )
    )

    result = docs_generator.generate_cli_reference_markdown()
    splitted_result = result.split("\n")

    assert "#### `--foo` `-f`" in splitted_result


def test_saving_markdown_file(tmpdir):
    filepath = Path(tmpdir) / "foo.md"
    ReferenceDocsGenerator.save_to_markdown_file(filepath, "foobar")

    with open(filepath, "r", encoding="utf-8") as file:
        assert file.read() == "foobar"
