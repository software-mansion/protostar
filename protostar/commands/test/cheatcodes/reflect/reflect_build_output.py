from typing import (
    Any,
    List,
    Dict,
    Tuple,
)
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
from starkware.cairo.lang.compiler.scoped_name import ScopedName
from starkware.cairo.lang.compiler.identifier_definition import (
    StructDefinition,
    MemberDefinition,
)

from protostar.commands.test.cheatcodes.reflect.reflect_misc import (
    ReflectInputType,
    ReflectValueType,
    ReflectReturnType,
    ReflectTreeNode,
    traverse_pre_order,
    PrettyNamedTuple,
)


# pylint: disable=W0212
def generate_value_tree(value: ReflectInputType) -> ReflectValueType:
    assert value is not None
    if not isinstance(value, VmConstsReference):
        return value

    value_tree = {}
    stack: List[Tuple[Dict[str, Any], VmConstsReference]] = [(value_tree, value)]

    while len(stack) > 0:
        curr_dict, curr = stack.pop()

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
                    curr_dict[name] = tmp
                else:
                    assert isinstance(expr_type, TypePointer)
                    tmp = deepcopy(curr.get_or_set_value(name, None))
                    assert isinstance(tmp, RelocatableValue)
                    curr_dict[name] = tmp

            elif isinstance(expr_type, TypeStruct):
                curr_dict[name] = ReflectTreeNode(
                    typename=expr_type.scope.path[1], value={}
                )
                stack.append(
                    (
                        curr_dict[name].value,
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
                curr_dict[name] = tmp

    assert isinstance(value._struct_definition, StructDefinition)
    return ReflectTreeNode(
        typename=value._struct_definition.full_name.path[1], value=value_tree
    )


def convert_to_named_tuple(tree: ReflectTreeNode) -> ReflectReturnType:
    pre_order = [x for x in traverse_pre_order(tree) if isinstance(x, ReflectTreeNode)]

    # When we reach each element it contains a single value or namedtuple instead of a dict
    for node in reversed(pre_order):

        # Convert all of your children into named tuples
        assert isinstance(node.value, dict)
        for name, child in node.value.items():
            if not isinstance(child, ReflectTreeNode):
                node.value[name] = child
            else:  # child.value is a Dict[str, NamedTuple]
                assert isinstance(child.value, dict)
                tpl = PrettyNamedTuple(
                    child.typename,
                    [(key, type(elem)) for key, elem in child.value.items()],
                )

                # pylint: disable=E1102
                node.value[name] = tpl(*child.value.values())

    assert isinstance(tree.value, dict)
    tpl = PrettyNamedTuple(
        tree.typename, [(key, type(elem)) for key, elem in tree.value.items()]
    )

    # pylint: disable=E1102
    return tpl(*tree.value.values())
