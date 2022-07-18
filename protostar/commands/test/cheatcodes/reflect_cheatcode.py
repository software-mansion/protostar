from collections import defaultdict
from typing import Any, Callable, List, Dict, NamedTuple, Tuple, Type, Union
from copy import deepcopy
import dataclasses

from starkware.cairo.lang.vm.vm_consts import is_simple_type, VmConstsReference
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

from protostar.starknet.cheatcode import Cheatcode


class ReflectCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "reflect"

    def build(self) -> Callable[..., Any]:
        return self.reflect

    @dataclasses.dataclass
    class _reflectTreeNode:
        typename: str
        value: Union[Dict, int, str]

        def __repr__(self):
            stack: List[
                Tuple[
                    Union[
                        ReflectCheatcode._reflectTreeNode, RelocatableValue, int, str
                    ],
                    int,
                ]
            ] = [(self, 0)]
            result: list[str] = []
            depth = 0

            while len(stack) > 0:
                curr, depth = stack.pop()

                if not isinstance(curr, ReflectCheatcode._reflectTreeNode):
                    result.append(str(curr) + ("" if isinstance(curr, str) else "\n"))
                else:
                    result.append(f"{curr.typename}(\n")
                    stack.append(("    " * depth + ")\n", 0))

                    assert isinstance(curr.value, dict)
                    for name, child in reversed(list(curr.value.items())):
                        stack.append((child, depth + 1))
                        stack.append(("    " * (depth + 1) + f"{name}=", 0))

            return "".join(result)

    REFLECT_VALUE_TYPE = Union[_reflectTreeNode, RelocatableValue, int]

    # We need to access Cairo's underscore variables
    # pylint: disable=W0212,R0201
    def _generate_struct_tree(
        self, struct: Union[VmConstsReference, RelocatableValue, int]
    ) -> "REFLECT_VALUE_TYPE":
        if not isinstance(struct, VmConstsReference):
            return struct

        struct_tree = {}
        stack: List[Tuple[Dict[str, Any], VmConstsReference]] = [(struct_tree, struct)]

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
                        value = int(curr.get_or_set_value(name, None))  # type: ignore
                        assert isinstance(value, int)
                        curr_dict[name] = value
                    else:
                        assert isinstance(expr_type, TypePointer)
                        value = deepcopy(curr.get_or_set_value(name, None))
                        assert isinstance(value, RelocatableValue)
                        curr_dict[name] = value

                elif isinstance(expr_type, TypeStruct):
                    curr_dict[name] = ReflectCheatcode._reflectTreeNode(
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

                    value = deepcopy(curr._context.memory[addr])  # type: ignore
                    assert isinstance(value, RelocatableValue)
                    curr_dict[name] = value

        assert isinstance(struct._struct_definition, StructDefinition)
        return ReflectCheatcode._reflectTreeNode(
            typename=struct._struct_definition.full_name.path[1], value=struct_tree
        )

    # pylint: disable=R0201
    def _convert_to_named_tuple_or_simple_type(
        self, tree: REFLECT_VALUE_TYPE
    ) -> Union[NamedTuple, RelocatableValue, int]:
        if not isinstance(tree, ReflectCheatcode._reflectTreeNode):
            return tree

        stack: List[ReflectCheatcode.REFLECT_VALUE_TYPE] = [tree]
        post_order: List[ReflectCheatcode.REFLECT_VALUE_TYPE] = []
        vis = defaultdict(lambda: False)

        while len(stack) > 0:
            curr = stack.pop()

            if vis[id(curr)]:
                post_order.append(curr)
                continue
            vis[id(curr)] = True

            stack.append(curr)

            if isinstance(curr, ReflectCheatcode._reflectTreeNode):
                assert isinstance(curr.value, dict)
                for _, node in curr.value.items():
                    stack.append(node)

        # When we reach each element it contains a single value or namedtuple instead of a dict
        for node in post_order:
            if not isinstance(node, ReflectCheatcode._reflectTreeNode):
                # We can't do anything here either way
                continue

            # Convert all of your children into named tuples
            assert isinstance(node.value, dict)
            for name, child in node.value.items():

                if not isinstance(child, ReflectCheatcode._reflectTreeNode):
                    node.value[name] = child
                else:  # child.value is a Dict[str, NamedTuple]
                    assert isinstance(child.value, dict)
                    tpl = _get_pretty_tuple(
                        child.typename,
                        [(key, type(elem)) for key, elem in child.value.items()],
                    )

                    # pylint: disable=E1102
                    node.value[name] = tpl(*child.value.values())

        assert isinstance(tree.value, dict)
        tpl = _get_pretty_tuple(
            tree.typename, [(key, type(elem)) for key, elem in tree.value.items()]
        )

        # pylint: disable=E1102
        return tpl(*tree.value.values())

    def reflect(
        self, struct: VmConstsReference
    ) -> Union[NamedTuple, RelocatableValue, int]:
        tree = self._generate_struct_tree(struct)
        tpl = self._convert_to_named_tuple_or_simple_type(tree)
        return tpl


def _isinstance_namedtuple(obj: Any) -> bool:
    return (
        isinstance(obj, tuple) and hasattr(obj, "_asdict") and hasattr(obj, "_fields")
    )


def _get_pretty_tuple(name: str, tuple_args: List[Tuple[str, Type]]) -> Type:
    def fancy_str(self):
        stack: List[Tuple[Union[Any, RelocatableValue, str, int], int]] = [(self, 0)]
        result: List[str] = []
        depth = 0

        while len(stack) > 0:
            curr, depth = stack.pop()

            if not _isinstance_namedtuple(curr):
                result.append(str(curr) + ("" if isinstance(curr, str) else "\n"))
            else:
                result.append(f"{type(curr).__name__}(\n")
                stack.append(("    " * depth + ")\n", 0))

                for name, child in reversed(list(curr._asdict().items())):  # type: ignore
                    stack.append((child, depth + 1))
                    stack.append(("    " * (depth + 1) + f"{name}=", 0))

        return "".join(result)

    tpl = NamedTuple(name, tuple_args)
    tpl.__str__ = fancy_str

    return tpl


# def _get_ptr_depth_and_type(ptr: TypePointer) -> Tuple[int, str]:
#     depth = 1
#     while isinstance(ptr.pointee, TypePointer):
#         ptr = ptr.pointee
#         depth += 1

#     if isinstance(ptr.pointee, TypeFelt):
#         ptr_type = "felt"
#     else:
#         assert isinstance(ptr.pointee, TypeStruct)
#         ptr_type = ptr.pointee.scope.path[1]

#     return (depth, ptr_type)
