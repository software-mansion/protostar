from typing import List, Tuple
from copy import deepcopy

from starkware.cairo.lang.vm.vm_consts import (
    is_simple_type,
    VmConstsReference,
)
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.cairo.lang.compiler.ast.cairo_types import (
    CairoType,
    TypeStruct,
    TypePointer,
    TypeFelt,
)
from starkware.cairo.lang.compiler.identifier_definition import (
    StructDefinition,
    MemberDefinition,
)

from protostar.commands.test.cheatcodes.reflect.reflect_misc import (
    ReflectInputType,
    ReflectValueType,
)

from protostar.commands.test.cheatcodes.reflect.reflect_cairo_struct import CairoStruct

# pylint: disable=W0212
def generate_value_tree(value: ReflectInputType) -> ReflectValueType:
    assert value is not None
    if not isinstance(value, VmConstsReference):
        return value

    assert isinstance(value._struct_definition, StructDefinition)
    tree = CairoStruct()

    stack: List[Tuple[CairoStruct, VmConstsReference]] = [(tree, value)]

    while len(stack) > 0:
        curr_tree, curr = stack.pop()

        assert isinstance(curr._struct_definition, StructDefinition)
        assert isinstance(curr._reference_value, RelocatableValue)

        name: str
        member_definition: MemberDefinition
        for name, member_definition in curr._struct_definition.members.items():
            expr_type: CairoType = member_definition.cairo_type
            addr = curr._reference_value + member_definition.offset

            if is_simple_type(expr_type):
                if isinstance(expr_type, TypeFelt):
                    tmp = int(curr.get_or_set_value(name, None))  # type: ignore
                    assert isinstance(tmp, int)
                    curr_tree._set(name, tmp)
                else:
                    assert isinstance(expr_type, TypePointer)
                    tmp = deepcopy(curr.get_or_set_value(name, None))
                    assert isinstance(tmp, RelocatableValue)
                    curr_tree._set(name, tmp)

            elif isinstance(expr_type, TypeStruct):
                curr_tree._set(name, CairoStruct())
                stack.append(
                    (
                        curr_tree._ordered_dict[name],  # type: ignore
                        VmConstsReference(
                            context=curr._context,
                            struct_name=expr_type.scope,
                            reference_value=addr,
                        ),
                    )
                )

            else:
                assert isinstance(expr_type, TypePointer) and isinstance(
                    expr_type.pointee, TypeStruct
                ), "Type must be of the form T*."

                tmp = deepcopy(curr._context.memory[addr])  # type: ignore
                assert isinstance(tmp, RelocatableValue)
                curr_tree._set(name, tmp)

    assert isinstance(value._struct_definition, StructDefinition)
    return tree
