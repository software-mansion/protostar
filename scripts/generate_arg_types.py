from pathlib import Path

import stringcase

from protostar.argument_parser.argument import Argument
from protostar.argument_parser.command import Command
from protostar.composition_root import build_di_container
from scripts.arg_types_generator.generate_types import (
    ClassAttributeConstruct,
    DataclassConstruct,
    FromImportConstruct,
    ModuleConstruct,
    unparse,
)


def load_module_construct():
    commands = build_di_container(script_root=Path()).protostar_cli.commands
    return ModuleConstruct(
        imports=[
            FromImportConstruct(dotted_path="dataclasses", imports=["dataclass"]),
            FromImportConstruct(dotted_path=".input_types", imports=["*"]),
        ],
        children=map_command_to_construct(commands),
    )


def map_command_to_construct(commands: list[Command]):
    return [
        DataclassConstruct(
            name=stringcase.titlecase(command.name).replace(" ", "") + "CommandArgs",
            class_attributes=[
                map_argument_to_construct(arg) for arg in command.arguments
            ],
        )
        for command in commands
    ]


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
    return ClassAttributeConstruct(
        name=stringcase.snakecase(argument.name),
        type_name=type_name,
        default=repr(default),
    )


module_construct = load_module_construct()
result = unparse(module_construct)

print(result)
