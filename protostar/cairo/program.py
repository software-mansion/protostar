from starkware.cairo.lang.compiler.identifier_definition import StructDefinition
from starkware.cairo.lang.compiler.program import Program
from starkware.cairo.lang.compiler.scoped_name import ScopedName


def program_function_has_parameters(function_name: str, program: Program) -> bool:
    function_args = program.identifiers.get(ScopedName(path=(function_name, "Args")))
    args_struct = function_args.identifier_definition
    assert isinstance(
        args_struct, StructDefinition
    ), "Function arguments are not a struct!"
    return bool(args_struct.size)
