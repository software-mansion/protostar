import ast

from .constructs import (
    ClassAttributeConstruct,
    Construct,
    DataclassConstruct,
    FromImportConstruct,
    ModuleConstruct,
)


def unparse(module_construct: ModuleConstruct) -> str:
    return ast.unparse(map_construct_to_python_ast(module_construct))


def map_construct_to_python_ast(construct: Construct) -> ast.AST:
    if isinstance(construct, ModuleConstruct):
        return ast.Module(
            body=[
                [
                    map_construct_to_python_ast(i)
                    for i in [*construct.imports, *construct.children]
                ],
            ],
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
    if isinstance(construct, FromImportConstruct):
        return ast.ImportFrom(
            module=construct.dotted_path,
            names=[ast.alias(name=name) for name in construct.imports],
            level=0,
        )

    assert False, f"Unknown Construct: {construct}"
