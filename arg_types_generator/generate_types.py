import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence, Union, cast

import stringcase

from protostar.argument_parser.argument import Argument
from protostar.argument_parser.command import Command
from protostar.composition_root import build_di_container


class Construct:
    pass


DottedPath = str
Identifier = str


@dataclass
class FromImportConstruct(Construct):
    dotted_path: DottedPath
    imports: Sequence[Identifier]


@dataclass
class ClassAttributeConstruct(Construct):
    name: str
    type_name: str
    default: Optional[str] = None


@dataclass
class DataclassConstruct(Construct):
    name: str
    class_attributes: Sequence[ClassAttributeConstruct]


@dataclass
class ModuleConstruct(Construct):
    children: Sequence[Union[FromImportConstruct, DataclassConstruct]]


def main():
    module_construct = load_module_construct()
    python_ast = map_construct_to_python_ast(module_construct)
    result = ast.unparse(python_ast)
    print(result)


def load_module_construct():
    commands = build_di_container(script_root=Path()).protostar_cli.commands
    dataclasses_to_generate: list[DataclassConstruct] = []
    for command in commands:
        dataclasses_to_generate.append(map_command_to_construct(command))
    return ModuleConstruct(dataclasses_to_generate)


def map_command_to_construct(command: Command):
    return DataclassConstruct(
        name=stringcase.titlecase(command.name).replace(" ", "") + "CommandArgs",
        class_attributes=[map_argument_to_construct(arg) for arg in command.arguments],
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

    return ClassAttributeConstruct(
        name=stringcase.snakecase(argument.name),
        type_name=type_name,
        default=repr(default),
    )


def map_construct_to_python_ast(construct: Construct) -> ast.AST:
    if isinstance(construct, ModuleConstruct):
        return ast.Module(
            body=[[map_construct_to_python_ast(child) for child in construct.children]],
            type_ignores=[],
        )
    if isinstance(construct, DataclassConstruct):
        return ast.ClassDef(
            name=construct.name,
            decorator_list=[ast.Name(id="dataclass")],
            bases=[],
            keywords=[],
            body=[
                [
                    map_construct_to_python_ast(child)
                    for child in construct.class_attributes
                ]
                if len(construct.class_attributes) > 0
                else ast.Pass()
            ],
        )
    if isinstance(construct, ClassAttributeConstruct):

        return ast.AnnAssign(
            target=ast.Name(id=construct.name),
            annotation=ast.Name(id=construct.type_name),
            value=ast.Name(construct.default) if construct.default else None,
            simple=1,
        )

    assert False


def run_example():
    code = """
from dataclasses import dataclass

@dataclass
class Foo:
    foo: baz

    def bar(self):
        pass
    """

    tree = ast.parse(code)

    cls = cast(ast.ClassDef, tree.body[1])
    print(cls.decorator_list)
    for construct in cls.body:
        print(construct)
        # if isinstance(construct, ast.AnnAssign):
        #     target_node = construct.target
        #     if isinstance(target_node, ast.Name):
        #         print(target_node.id)

        #     type_node = construct.annotation
        #     if isinstance(type_node, ast.Name):
        #         print(type_node.id)


# run_example()
main()
