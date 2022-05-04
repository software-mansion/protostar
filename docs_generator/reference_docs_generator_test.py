from pathlib import Path

from conftest import BarCommand, FooCommand
from docs_generator import ReferenceDocsGenerator
from src.cli.cli_app import CLIApp
from src.cli.command import Command


def test_generating_markdown_for_commands(
    foo_command: FooCommand, bar_command: FooCommand
):
    docs_generator = ReferenceDocsGenerator(
        CLIApp(commands=[foo_command, bar_command], root_args=[])
    )

    result = docs_generator.generate_cli_reference_markdown()

    assert bar_command.name in result
    assert bar_command.example is None
    assert bar_command.description in result

    assert foo_command.name in result
    assert foo_command.example is not None and foo_command.example in result
    assert foo_command.description in result


def test_generating_markdown_for_command_arguments(foo_command: FooCommand):
    docs_generator = ReferenceDocsGenerator(
        CLIApp(commands=[foo_command], root_args=[])
    )

    result = docs_generator.generate_cli_reference_markdown()

    assert foo_command.name in result
    assert foo_command.arguments[0].name in result
    assert foo_command.arguments[0].example or "" in result
    assert foo_command.arguments[0].description in result


def test_generating_default_type_and_array_info():
    docs_generator = ReferenceDocsGenerator(
        CLIApp(
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
        CLIApp(
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

    assert "-f" in result
    assert "--foo" in result


def test_required_info():
    docs_generator = ReferenceDocsGenerator(
        CLIApp(
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

    assert "Required." in result


def test_saving_markdown_file(tmpdir):
    filepath = Path(tmpdir) / "foo.md"
    ReferenceDocsGenerator.save_to_markdown_file(filepath, "foobar")

    with open(filepath, "r", encoding="utf-8") as file:
        assert file.read() == "foobar"


def test_command_order(foo_command: FooCommand, bar_command: BarCommand):
    docs_generator = ReferenceDocsGenerator(CLIApp(commands=[foo_command, bar_command]))
    result = docs_generator.generate_cli_reference_markdown()

    foo_command_index = result.index(foo_command.name)
    bar_command_index = result.index(bar_command.name)

    assert bar_command_index < foo_command_index


def test_args_order_by_is_positional_and_name():
    docs_generator = ReferenceDocsGenerator(
        CLIApp(
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

    baz_index = result.index("baz")
    bar_index = result.index("--bar")
    foo_index = result.index("--foo")
    assert baz_index < bar_index
    assert bar_index < foo_index
