from pathlib import Path

from src.conftest import BarCommand, FooCommand
from src.core.cli import CLI
from src.core.command import Command
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

    assert "#### `--foo STRING[]=FOO`" in splitted_result


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

    assert "#### `-f` `--foo`" in splitted_result


def test_required_info():
    docs_generator = ReferenceDocsGenerator(
        CLI(
            root_args=[
                Command.Argument(
                    name="foo",
                    short_name="f",
                    description="...",
                    type="bool",
                    is_required=True,
                )
            ]
        )
    )

    result = docs_generator.generate_cli_reference_markdown()
    splitted_result = result.split("\n")

    assert "Required." in splitted_result


def test_saving_markdown_file(tmpdir):
    filepath = Path(tmpdir) / "foo.md"
    ReferenceDocsGenerator.save_to_markdown_file(filepath, "foobar")

    with open(filepath, "r", encoding="utf-8") as file:
        assert file.read() == "foobar"


def test_command_order(foo_command: FooCommand, bar_command: BarCommand):
    docs_generator = ReferenceDocsGenerator(CLI(commands=[foo_command, bar_command]))
    result = docs_generator.generate_cli_reference_markdown()
    splitted_result = result.split("\n")

    foo_command_index = splitted_result.index(f"### `{foo_command.name}`")
    bar_command_index = splitted_result.index(f"### `{bar_command.name}`")

    assert bar_command_index < foo_command_index


def test_args_order_by_is_positional_and_name():
    docs_generator = ReferenceDocsGenerator(
        CLI(
            root_args=[
                Command.Argument(name="foo", description="...", type="str"),
                Command.Argument(name="bar", description="...", type="str"),
                Command.Argument(
                    name="baz", description="...", type="str", is_positional=True
                ),
            ]
        )
    )
    result = docs_generator.generate_cli_reference_markdown()
    splitted_result = result.split("\n")
    baz_index = splitted_result.index("#### `baz STRING`")
    bar_index = splitted_result.index("#### `--bar STRING`")
    foo_index = splitted_result.index("#### `--foo STRING`")
    assert baz_index < bar_index
    assert bar_index < foo_index
