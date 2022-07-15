from collections import defaultdict, Iterable
from typing import Any, Callable, List, Dict, NamedTuple, Tuple, Type

from protostar.starknet.cheatcode import Cheatcode

from starkware.cairo.lang.vm.vm_consts import is_simple_type, VmConstsReference
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

# from protostar.starknet.types import AddressType


class DumpCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "dump"

    def build(self) -> Callable[..., Any]:
        return self.dump

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

    def _generate_struct_tree(self, struct: VmConstsReference) -> List:
        struct_tree = {}
        stack: List[Tuple[Dict, VmConstsReference]] = [(struct_tree, struct)]

        while len(stack) > 0:
            curr_dict, curr = stack.pop()

            name: str
            member_definition: MemberDefinition
            for name, member_definition in curr._struct_definition.members.items():
                expr_type: CairoType = member_definition.cairo_type
                addr = curr._reference_value + member_definition.offset

                if is_simple_type(expr_type):
                    if isinstance(expr_type, TypeFelt):
                        curr_dict[name] = ("felt", curr.get_or_set_value(name, None))
                    else:
                        assert isinstance(expr_type, TypePointer)
                        depth, ptr_type = self._get_ptr_depth_and_type(expr_type)
                        curr_dict[name] = (
                            f"{ptr_type}" + "*" * depth,
                            str(curr.get_or_set_value(name, None)),
                        )

                elif isinstance(expr_type, TypeStruct):
                    curr_dict[name] = [expr_type.scope.path[1], {}]
                    stack.append(
                        (
                            curr_dict[name][1],
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
                    curr_dict[name] = (f"{ptr_type}" + "*" * depth, "-")

        return [struct._struct_definition.full_name.path[1], struct_tree]

    def _convert_to_named_tuple(self, tree: List) -> NamedTuple:

        stack: List[List] = [tree]
        post_order: List[List] = []
        vis = defaultdict(lambda: False)

        while len(stack) > 0:
            curr = stack.pop()

            if vis[id(curr)]:
                post_order.append(curr)
                continue
            vis[id(curr)] = True

            stack.append(curr)

            if isinstance(curr[1], dict):
                for _, val in curr[1].items():
                    stack.append(val)

        # When we reach each element it contains a single value or namedtuple instead of a dict
        for lst in post_order:
            if not isinstance(lst[1], dict):
                # We can't do anything here either way
                continue

            # Convert all of your children into named tuples
            for name, val in lst[1].items():
                typename = val[0]
                typeval = val[1]

                if not isinstance(val[1], dict):
                    tpl = NamedTuple(
                        typename.replace("*", "_ptr"), [("value", type(typeval))]
                    )
                    lst[1][name] = tpl(typeval)
                else:  # val[1] is a Dict[str, NamedTuple]
                    tpl = NamedTuple(
                        typename, [(key, type(elem)) for key, elem in val[1].items()]
                    )
                    lst[1][name] = tpl(*[elem for elem in val[1].values()])

        tpl = NamedTuple(tree[0], [(key, type(elem)) for key, elem in tree[1].items()])
        return tpl(*[elem for elem in tree[1].values()])

    def dump(self, struct: VmConstsReference) -> Callable[[], None]:

        tree = self._generate_struct_tree(struct)
        # tpl = self._convert_to_named_tuple(tree)
        # print(tpl)

        tpl = self._convert_to_named_tuple(tree)
        print(tpl)
        return lambda: None
