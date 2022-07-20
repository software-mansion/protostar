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
from starkware.cairo.lang.compiler.scoped_name import ScopedName
from starkware.cairo.lang.compiler.identifier_definition import (
    IdentifierDefinition,
    ReferenceDefinition,
    StructDefinition,
    MemberDefinition,
)
from starkware.cairo.lang.compiler.ast.expr import ExprDeref
from starkware.cairo.lang.compiler.identifier_manager import (
    IdentifierScope,
    IdentifierSearchResult,
    MissingIdentifierError,
)
from starkware.cairo.lang.compiler.type_system_visitor import simplify_type_system

from protostar.starknet.cheatcode import Cheatcode


@dataclass
class ReflectTreeNode:
    typename: str
    value: Union[Dict, int, str]


ReflectInputType = Union[VmConstsReference, RelocatableValue, int]
ReflectValueType = Union[ReflectTreeNode, RelocatableValue, int]
ReflectReturnType = Union[NamedTuple, RelocatableValue, int]


class Reflector:
    def __init__(self, ids: VmConsts):
        self.ids = ids

    def __getattr__(self, name: str):
        value = self._get_value(name)
        tree = self._generate_value_tree(value)
        if not isinstance(tree, ReflectTreeNode):
            return tree
        tpl = self._convert_to_named_tuple(tree)
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

    def _get_value(self, name: str) -> ReflectInputType:
        ids_get: Callable[[str], Any] = lambda name: object.__getattribute__(
            self.ids, name
        )

        try:
            # Handle attributes representing program scopes and constants.
            result = search_identifier_or_scope(
                identifiers=ids_get("_context").identifiers,
                accessible_scopes=ids_get("_accessible_scopes"),
                name=ScopedName.from_string(name),
            )
        except MissingIdentifierError as exc:
            raise MissingIdentifierError(ids_get("_path") + exc.fullname) from None  # type: ignore

        value: Optional[IdentifierDefinition]
        if isinstance(result, IdentifierSearchResult):
            value = result.identifier_definition
            handler_name = f"handle_{type(value).__name__}"
            scope = result.get_canonical_name()
            identifier_type = value.TYPE
        elif isinstance(result, IdentifierScope):  # type: ignore
            value = None
            handler_name = "handle_scope"
            scope = result.fullname
            identifier_type = "scope"
        else:
            raise NotImplementedError(f"Unexpected type {type(result).__name__}.")

        if handler_name not in dir(self.ids):
            self.ids.raise_unsupported_error(
                name=ids_get("_path") + name, identifier_type=identifier_type  # type: ignore
            )

        if handler_name == "handle_ReferenceDefinition":
            return self._handler(value)  # type: ignore

        return getattr(self.ids, handler_name)(name, value, scope, None)

    def _handler(
        self,
        identifier: ReferenceDefinition,
    ) -> ReflectInputType:

        ids_get: Callable[[str], Any] = lambda name: object.__getattribute__(
            self.ids, name
        )

        reference = ids_get("_context").flow_tracking_data.resolve_reference(
            reference_manager=ids_get("_context").reference_manager,
            name=identifier.full_name,
        )

        expr = reference.eval(ids_get("_context").flow_tracking_data.ap_tracking)
        expr, expr_type = simplify_type_system(
            expr, identifiers=ids_get("_context").identifiers
        )

        is_object = False
        if isinstance(expr_type, TypeStruct):
            # If the reference is of type T, take its address and treat it as T*.
            assert isinstance(
                expr, ExprDeref
            ), f"Expected expression of type '{expr_type.format()}' to have an address."
            expr = expr.addr
            expr_type = TypePointer(pointee=expr_type)

            is_object = True

        val = ids_get("_context").evaluator(expr)

        if not is_object:
            return val

        assert isinstance(expr_type, TypePointer) and isinstance(
            expr_type.pointee, TypeStruct
        ), "Type must be of the form T*."
        return VmConstsReference(
            context=ids_get("_context"),
            struct_name=expr_type.pointee.scope,
            reference_value=val,
        )


class ReflectCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "reflect"

    def build(self) -> Callable[..., Any]:
        return self.reflect

    # pylint: disable=R0201
    def reflect(self, ids: VmConsts):
        return Reflector(ids)


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


# pylint: disable=C0103
def PrettyNamedTuple(name: str, tuple_args: List[Tuple[str, Type]]) -> Type:
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

    tpl = NamedTuple(name, tuple_args)
    tpl.__str__ = new_str
    return tpl
