from collections import defaultdict, Iterable
from struct import Struct
from typing import Any, Callable, List, Dict, NamedTuple, Tuple, Type, Union

from protostar.starknet.cheatcode import Cheatcode

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

import json
import dataclasses

# from protostar.starknet.types import AddressType


class DumpCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "dump"

    def build(self) -> Callable[..., Any]:
        return self.dump

    @dataclasses.dataclass
    class _dumpTreeNode:
        typename: str
        value: Union[Dict, int, str]

        def __repr__(self):
            stack: List[Tuple[Union[DumpCheatcode._dumpTreeNode, str], int]] = [
                (self, 0)
            ]
            result: list[str] = []
            depth = 0

            while len(stack) > 0:
                curr, depth = stack.pop()

                if isinstance(curr, str):
                    result.append(curr)
                elif not isinstance(curr.value, dict):
                    result.append(f"{curr.typename}(value={curr.value})\n")
                else:
                    result.append(f"{curr.typename}(\n")
                    stack.append(("    " * depth + ")\n", 0))

                    for name, child in curr.value.items():
                        stack.append((child, depth + 1))
                        stack.append(("    " * (depth + 1) + f"{name}=", 0))

            return "".join(result)

    def _get_ptr_depth_and_type(self, ptr: TypePointer) -> Tuple[int, str]:
        depth = 1
        while isinstance(ptr.pointee, TypePointer):
            ptr = ptr.pointee
            depth += 1

        if isinstance(ptr.pointee, TypeFelt):
            ptr_type = "felt"
        else:
            assert isinstance(ptr.pointee, TypeStruct)
            ptr_type = ptr.pointee.scope.path[1]

        return (depth, ptr_type)

    def _generate_struct_tree(self, struct: VmConstsReference) -> _dumpTreeNode:
        if not isinstance(struct, VmConstsReference):
            print(f"Typ to: {type(struct)}")
            return DumpCheatcode._dumpTreeNode("Wolo", "Lolo")

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
                        value = int(curr.get_or_set_value(name, None))
                        assert isinstance(value, int)
                        curr_dict[name] = DumpCheatcode._dumpTreeNode(
                            typename="felt",
                            value=value,
                        )
                    else:
                        assert isinstance(expr_type, TypePointer)
                        depth, ptr_type = self._get_ptr_depth_and_type(expr_type)
                        curr_dict[name] = DumpCheatcode._dumpTreeNode(
                            typename=f"{ptr_type}" + "*" * depth,
                            value=str(curr.get_or_set_value(name, None)),
                        )

                elif isinstance(expr_type, TypeStruct):
                    curr_dict[name] = DumpCheatcode._dumpTreeNode(
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

                    depth, ptr_type = self._get_ptr_depth_and_type(expr_type)
                    curr_dict[name] = DumpCheatcode._dumpTreeNode(
                        typename=f"{ptr_type}" + "*" * depth, value="-"
                    )

        return DumpCheatcode._dumpTreeNode(
            typename=struct._struct_definition.full_name.path[1], value=struct_tree
        )

    def _convert_to_named_tuple(self, tree: _dumpTreeNode) -> NamedTuple:
        if not isinstance(tree.value, dict):
            tpl = NamedTuple(
                tree.typename.replace("*", "_ptr"), [("value", type(tree.value))]
            )
            return tpl(tree.value)

        stack: List[DumpCheatcode._dumpTreeNode] = [tree]
        post_order: List[DumpCheatcode._dumpTreeNode] = []
        vis = defaultdict(lambda: False)

        while len(stack) > 0:
            curr = stack.pop()

            if vis[id(curr)]:
                post_order.append(curr)
                continue
            vis[id(curr)] = True

            stack.append(curr)

            if isinstance(curr.value, dict):
                for _, node in curr.value.items():
                    stack.append(node)

        # When we reach each element it contains a single value or namedtuple instead of a dict
        for node in post_order:
            if not isinstance(node.value, dict):
                # We can't do anything here either way
                continue

            # Convert all of your children into named tuples
            for name, child in node.value.items():
                typename = child.typename
                typeval = child.value

                if not isinstance(child.value, dict):
                    tpl = NamedTuple(
                        typename.replace("*", "_ptr"), [("value", type(typeval))]
                    )
                    node.value[name] = tpl(typeval)
                else:  # child.value is a Dict[str, NamedTuple]
                    tpl = NamedTuple(
                        typename,
                        [(key, type(elem)) for key, elem in child.value.items()],  # type: ignore
                    )
                    node.value[name] = tpl(*child.value.values())

        tpl = NamedTuple(
            tree.typename, [(key, type(elem)) for key, elem in tree.value.items()]  # type: ignore
        )
        return tpl(*tree.value.values())

    def dump(self, struct: VmConstsReference) -> Callable[[], None]:

        tree = self._generate_struct_tree(struct)
        # tpl = self._convert_to_named_tuple(tree)
        # print(tpl)

        print(tree)
        print("\n\n\n")

        tpl = self._convert_to_named_tuple(tree)
        print(tpl)
        return lambda: None
