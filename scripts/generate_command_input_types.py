from pathlib import Path

import stringcase

from protostar.argument_parser.argument import Argument
from protostar.argument_parser.command import Command
from protostar.composition_root import build_di_container
from scripts.arg_types_generator.translate_to_python import (
    ClassAttributeConstruct,
    DataclassConstruct,
    FromImportConstruct,
    ModuleConstruct,
    generate_code,
)

TYPES_SOURCE_FOR_GENERATED_FILES_STEM = "_types_source_generated_command_input_types"

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent
    / "protostar"
    / "commands"
    / "_generated_command_input_types.py"
)


def create_module_construct():
    dataclass_constructs = create_dataclass_constructs()
    return ModuleConstruct(
        children=[
            *[
                FromImportConstruct(
                    dotted_path="dataclasses", imports=["dataclass", "field"]
                ),
                FromImportConstruct(dotted_path="typing", imports=["Optional"]),
                FromImportConstruct(
                    dotted_path=f".{TYPES_SOURCE_FOR_GENERATED_FILES_STEM}",
                    imports=["*"],
                ),
            ],
            *dataclass_constructs,
        ],
    )


def create_dataclass_constructs():
    commands = build_di_container(script_root=Path()).protostar_cli.commands
    sorted_commands = sorted(commands, key=lambda cmd: cmd.name)
    return map_command_to_construct(sorted_commands)


def map_command_to_construct(commands: list[Command]):
    return [
        DataclassConstruct(
            name=stringcase.titlecase(command.name).replace(" ", "") + "CommandInput",
            class_attributes=[
                map_argument_to_construct(arg)
                for arg in sort_arguments(command.arguments)
            ],
        )
        for command in commands
    ]


def sort_arguments(arguments: list[Argument]) -> list[Argument]:
    def resolve_order(arg: Argument) -> int:
        if arg.is_required:
            return -1
        if arg.default is not None or arg.type == "bool":
            return 1
        return 0

    # pyright: reportUnknownLambdaType=false
    return sorted(
        arguments,
        key=resolve_order,
    )


def map_argument_to_construct(argument: Argument):
    type_name = argument.type
    default = argument.default
    if type_name == "bool":
        default = False
    else:
        if argument.is_array:
            type_name = f"list[{type_name}]"
        if not argument.is_required and argument.default is None:
            type_name = f"Optional[{type_name}]"

    default = repr(default) if default is not None else None
    if default is not None and argument.is_array:
        default = f"field(default_factory=lambda: {default})"
    return ClassAttributeConstruct(
        name=stringcase.snakecase(argument.name),
        type_name=type_name,
        default=default if default is not None else None,
    )


if __name__ == "__main__":
    module_construct = create_module_construct()
    result = generate_code(module_construct)
    OUTPUT_PATH.write_text(result)
