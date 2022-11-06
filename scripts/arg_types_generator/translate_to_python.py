import ast

import black

from .constructs import (
    ClassAttributeConstruct,
    Construct,
    DataclassConstruct,
    FromImportConstruct,
    ModuleConstruct,
)


def generate_code(module_construct: ModuleConstruct) -> str:
    python_code = ast.unparse(map_construct_to_python_ast(module_construct))
    return black.format_str(python_code, mode=black.FileMode())


def map_construct_to_python_ast(construct: Construct) -> ast.AST:
    if isinstance(construct, ModuleConstruct):
        return ast.Module(
            body=[
                [map_construct_to_python_ast(child) for child in construct.children],
            ],
            type_ignores=[],
        )
    if isinstance(construct, DataclassConstruct):
        return ast.ClassDef(
            name=construct.name,
            decorator_list=[ast.Name(id="dataclass")],
            bases=[ast.Name(id="SimpleNamespace")],
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
