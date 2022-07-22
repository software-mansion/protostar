from typing import (
    Any,
    Callable,
    Optional,
)

from starkware.cairo.lang.vm.vm_consts import (
    VmConstsReference,
    VmConsts,
    search_identifier_or_scope,
)
from starkware.cairo.lang.compiler.ast.cairo_types import (
    TypeStruct,
    TypePointer,
)
from starkware.cairo.lang.compiler.scoped_name import ScopedName
from starkware.cairo.lang.compiler.identifier_definition import (
    IdentifierDefinition,
    ReferenceDefinition,
)
from starkware.cairo.lang.compiler.ast.expr import ExprDeref
from starkware.cairo.lang.compiler.identifier_manager import (
    IdentifierScope,
    IdentifierSearchResult,
    MissingIdentifierError,
)
from starkware.cairo.lang.compiler.type_system_visitor import simplify_type_system

from protostar.commands.test.cheatcodes.reflect.reflect_misc import ReflectInputType
from protostar.commands.test.test_environment_exceptions import CheatcodeException


def get_value_from_vm(ids: VmConsts, name: str):
    def handler(
        ids: VmConsts,
        identifier: ReferenceDefinition,
    ) -> ReflectInputType:
        reference = getattr(ids, "_context").flow_tracking_data.resolve_reference(
            reference_manager=getattr(ids, "_context").reference_manager,
            name=identifier.full_name,
        )

        expr = reference.eval(getattr(ids, "_context").flow_tracking_data.ap_tracking)
        expr, expr_type = simplify_type_system(
            expr, identifiers=getattr(ids, "_context").identifiers
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

        val = getattr(ids, "_context").evaluator(expr)

        if not is_object:
            return val

        assert isinstance(expr_type, TypePointer) and isinstance(
            expr_type.pointee, TypeStruct
        ), "Type must be of the form T*."
        return VmConstsReference(
            context=getattr(ids, "_context"),
            struct_name=expr_type.pointee.scope,
            reference_value=val,
        )

    try:
        # Handle attributes representing program scopes and constants.
        result = search_identifier_or_scope(
            identifiers=getattr(ids, "_context").identifiers,
            accessible_scopes=getattr(ids, "_accessible_scopes"),
            name=ScopedName.from_string(name),
        )
    except MissingIdentifierError:
        raise CheatcodeException("reflect", f'Unknown identifier "{name}".') from None

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

    if handler_name not in dir(ids):
        ids.raise_unsupported_error(
            name=getattr(ids, "_path") + name, identifier_type=identifier_type  # type: ignore
        )

    if handler_name == "handle_ReferenceDefinition":
        return handler(ids, value)  # type: ignore

    return getattr(ids, handler_name)(name, value, scope, None)
