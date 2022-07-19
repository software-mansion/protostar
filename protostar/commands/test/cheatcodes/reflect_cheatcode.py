from typing import Any, Callable, List, Dict, NamedTuple, Tuple, Type, Union, Optional
from copy import deepcopy
from dataclasses import dataclass

from starkware.cairo.lang.vm.vm_consts import (
    is_simple_type,
    VmConstsReference,
    VmConsts,
    search_identifier_or_scope,
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
from starkware.cairo.lang.compiler.identifier_manager import (
    IdentifierError,
    IdentifierManager,
    IdentifierScope,
    IdentifierSearchResult,
    MissingIdentifierError,
)
from starkware.cairo.lang.compiler.scoped_name import ScopedName
from starkware.cairo.lang.compiler.identifier_definition import (
    ConstDefinition,
    IdentifierDefinition,
    LabelDefinition,
    NamespaceDefinition,
    ReferenceDefinition,
    StructDefinition,
)
from starkware.cairo.lang.compiler.identifier_manager import (
    IdentifierError,
    IdentifierManager,
    IdentifierScope,
    IdentifierSearchResult,
    MissingIdentifierError,
)
from starkware.cairo.lang.compiler.ast.cairo_types import (
    CairoType,
    TypeFelt,
    TypePointer,
    TypeStruct,
)
from starkware.cairo.lang.compiler.ast.expr import ExprCast, ExprDeref, Expression
from starkware.cairo.lang.compiler.constants import SIZE_CONSTANT
from starkware.cairo.lang.compiler.identifier_definition import (
    ConstDefinition,
    IdentifierDefinition,
    LabelDefinition,
    NamespaceDefinition,
    ReferenceDefinition,
    StructDefinition,
)
from starkware.cairo.lang.compiler.identifier_manager import (
    IdentifierError,
    IdentifierManager,
    IdentifierScope,
    IdentifierSearchResult,
    MissingIdentifierError,
)
from starkware.cairo.lang.compiler.identifier_utils import get_struct_definition
from starkware.cairo.lang.compiler.preprocessor.flow import (
    FlowTrackingData,
    ReferenceManager,
)
from starkware.cairo.lang.compiler.references import FlowTrackingError, Reference
from starkware.cairo.lang.compiler.scoped_name import ScopedName
from starkware.cairo.lang.compiler.type_system_visitor import simplify_type_system
from starkware.cairo.lang.vm.relocatable import MaybeRelocatable

from protostar.starknet.cheatcode import Cheatcode


@dataclass
class ReflectTreeNode:
    typename: str
    value: Union[Dict, int, str]
    __reference: Optional[VmConstsReference] = None


ReflectInputType = Union[VmConstsReference, RelocatableValue, int]
ReflectValueType = Union[ReflectTreeNode, RelocatableValue, int]
ReflectReturnType = Union[NamedTuple, RelocatableValue, int]


class Reflector:
    def __init__(self, ids: VmConsts):
        def evil_handler(
            self,
            name: str,
            identifier: ReferenceDefinition,
            scope: ScopedName,
            set_value: Optional[MaybeRelocatable],
        ):
            # In set mode, take the address of the given reference instead.
            reference = self._context.flow_tracking_data.resolve_reference(
                reference_manager=self._context.reference_manager,
                name=identifier.full_name,
            )

            if set_value is None:
                expr = reference.eval(self._context.flow_tracking_data.ap_tracking)
                expr, expr_type = simplify_type_system(
                    expr, identifiers=self._context.identifiers
                )
                if isinstance(expr_type, TypeStruct):
                    # If the reference is of type T, take its address and treat it as T*.
                    assert isinstance(
                        expr, ExprDeref
                    ), f"Expected expression of type '{expr_type.format()}' to have an address."
                    expr = expr.addr
                    expr_type = TypePointer(pointee=expr_type)
                val = self._context.evaluator(expr)

                return val
            else:
                assert str(scope[-1:]) == name, "Expecting scope to end with name."
                value, value_type = simplify_type_system(
                    reference.value, identifiers=self._context.identifiers
                )
                assert isinstance(
                    value, ExprDeref
                ), f"""\
    {scope} (= {value.format()}) does not reference memory and cannot be assigned."""

                value_ref = Reference(
                    pc=reference.pc,
                    value=ExprCast(expr=value.addr, dest_type=value_type),
                    ap_tracking_data=reference.ap_tracking_data,
                )

                addr = self._context.evaluator(
                    value_ref.eval(self._context.flow_tracking_data.ap_tracking)
                )
            self._context.memory[addr] = set_value

        self.ids = ids
        self.ids.__PROTOSTAR_HANDLER = evil_handler

    def __getattr__(self, name: str):
        value = self.get_value(name, None)

        # print(value._struct_definition)

        tree = self._generate_value_tree(value)
        if not isinstance(tree, ReflectTreeNode):
            return tree
        tpl = self._convert_to_named_tuple(tree)
        # print(tpl, end="\n\n\n")
        return tpl

    # We need to access Cairo's underscore variables
    # pylint: disable=W0212,R0201
    def _generate_value_tree(self, value: ReflectInputType) -> ReflectValueType:
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

    # pylint: disable=R0201
    def _convert_to_named_tuple(self, tree: ReflectTreeNode) -> ReflectReturnType:
        pre_order = [
            x for x in traverse_pre_order(tree) if isinstance(x, ReflectTreeNode)
        ]

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

    def get_value(self, name: str) -> ReflectInputType:
        try:
            # Handle attributes representing program scopes and constants.
            result = search_identifier_or_scope(
                identifiers=self.ids._context.identifiers,
                accessible_scopes=self.ids._accessible_scopes,
                name=ScopedName.from_string(name),
            )
        except MissingIdentifierError as exc:
            raise MissingIdentifierError(self.ids._path + exc.fullname) from None

        value: Optional[IdentifierDefinition]
        if isinstance(result, IdentifierSearchResult):
            value = result.identifier_definition
            handler_name = f"handle_{type(value).__name__}"
            scope = result.get_canonical_name()
            identifier_type = value.TYPE
        elif isinstance(result, IdentifierScope):
            value = None
            handler_name = "handle_scope"
            scope = result.fullname
            identifier_type = "scope"
        else:
            raise NotImplementedError(f"Unexpected type {type(result).__name__}.")

        if handler_name not in dir(self.ids):
            self.ids.raise_unsupported_error(
                name=self.ids._path + name, identifier_type=identifier_type
            )

        if handler_name == "handle_ReferenceDefinition":
            handler_name = "__PROTOSTAR_HANDLER"

        return getattr(self.ids, handler_name)(name, value, scope, None)

    def __del__(self):
        del self.ids.__PROTOSTAR_HANDLER


class ReflectCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "reflect"

    def build(self) -> Callable[..., Any]:
        return self.reflect

    # We need to access Cairo's underscore variables
    # pylint: disable=W0212,R0201
    def _generate_value_tree(self, value: ReflectInputType) -> ReflectValueType:
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

    # pylint: disable=R0201
    def _convert_to_named_tuple(self, tree: ReflectTreeNode) -> ReflectReturnType:
        pre_order = [
            x for x in traverse_pre_order(tree) if isinstance(x, ReflectTreeNode)
        ]

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

    def reflect(self, ids: VmConsts):
        return Reflector(ids)

    # def reflect(self, value: ReflectInputType, dupa: bool = False) -> ReflectReturnType:
    #     if dupa:
    #         return PrettyNamedTupleUnsafe

    #     tree = self._generate_value_tree(value)
    #     if not isinstance(tree, ReflectTreeNode):
    #         return tree
    #     tpl = self._convert_to_named_tuple(tree)
    #     return tpl


def isinstance_namedtuple(obj: Any) -> bool:
    return (
        isinstance(obj, tuple) and hasattr(obj, "_asdict") and hasattr(obj, "_fields")
    )


def traverse_pre_order(tree: ReflectTreeNode) -> List[ReflectValueType]:
    stack: List[ReflectValueType] = [tree]
    pre_order: List[ReflectValueType] = []

    while len(stack) > 0:
        curr = stack.pop()
        pre_order.append(curr)
        if isinstance(curr, ReflectTreeNode):
            assert isinstance(curr.value, dict)
            for _, node in curr.value.items():
                stack.append(node)

    return pre_order


def PrettyNamedTupleUnsafe(name: str, tuple_args: Any) -> Type:
    return PrettyNamedTuple(name, tuple_args, False)


def PrettyNamedTuple(name: str, tuple_args: List[Tuple[str, Type]], safe=True) -> Type:
    def new_str(self):
        stack: List[Tuple[Union[Any, RelocatableValue, str, int], int]] = [(self, 0)]
        result: List[str] = []
        depth = 0

        while len(stack) > 0:
            curr, depth = stack.pop()

            if not isinstance_namedtuple(curr):
                result.append(str(curr) + ("" if isinstance(curr, str) else "\n"))
            else:
                result.append(f"{type(curr).__name__}(\n")
                stack.append(("    " * depth + ")\n", 0))

                for name, child in reversed(list(curr._asdict().items())):  # type: ignore
                    stack.append((child, depth + 1))
                    stack.append(("    " * (depth + 1) + f"{name}=", 0))

        return "".join(result)

    # def new_eq(self, other):
    #     if not hasattr(other, "__PROTOSTAR_FLAG"):
    #         return False
    #     if len(self) != len(other):
    #         return False
    #     for x, y in zip(self, other):
    #         print(f"X{type(x)}&Y{type(y)}:", x, "|||", y, end="\n\n")

    #         if isinstance(x, RelocatableValue) and hasattr(y, "__PROTOSTAR_FLAG")#isinstance(y, VmConstsReference):
    #             print("IN1", y._reference_value, x)
    #             if y._reference_value != x:
    #                 return False
    #         elif isinstance(y, RelocatableValue) and hasattr(x, "__PROTOSTAR_FLAG")#isinstance(x, VmConstsReference):
    #             print("IN2", x._reference_value, y)
    #             if x._reference_value != y:
    #                 return False
    #         elif not (x == y):
    #             return False
    #     return True

    if safe:
        tpl = NamedTuple(name, tuple_args)
    else:
        from collections import namedtuple

        tpl = namedtuple(name, tuple_args)
    tpl.__str__ = new_str
    # tpl.__eq__ = new_eq
    tpl.__PROTOSTAR_FLAG = True

    return tpl


def get_ids_value(ids: VmConsts, name: str, value=None):
    ids.get_or_set_value(name, value)


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
