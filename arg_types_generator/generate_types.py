import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence, Union, cast

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
        dataclasses_to_generate.append(map_command_to_type_to_generate(command))
    return ModuleConstruct(dataclasses_to_generate)


def map_command_to_type_to_generate(command: Command):
    return DataclassConstruct(
        name=command.name,
        class_attributes=[
            ClassAttributeConstruct(
                name="bar",
                type_name="baz",
            )
        ],
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
            decorator_list=[],
            bases=[],
            keywords=[],
            body=[
                [
                    map_construct_to_python_ast(child)
                    for child in construct.class_attributes
                ]
            ],
        )
    if isinstance(construct, ClassAttributeConstruct):
        return ast.AnnAssign(
            target=ast.Name(id=construct.name),
            annotation=ast.Name(id=construct.type_name),
            simple=1,
        )

    assert False


def run_example():
    code = """
    from dataclasses import dataclass
    from . import dataclass

    @dataclass
    class Foo:
        foo: baz

        def bar(self):
            pass
    """

    tree = ast.parse(code)

    cls = cast(ast.ClassDef, tree.body[1])

    for construct in cls.body:
        if isinstance(construct, ast.AnnAssign):
            target_node = construct.target
            if isinstance(target_node, ast.Name):
                print(target_node.id)

            type_node = construct.annotation
            if isinstance(type_node, ast.Name):
                print(type_node.id)


main()
