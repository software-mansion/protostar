from copy import deepcopy
from starkware.cairo.lang.vm.vm_consts import (
    is_simple_type,
    VmConstsReference,
    VmConsts,
)
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.cairo.lang.compiler.ast.cairo_types import (
    TypeStruct,
    TypePointer,
    TypeFelt,
)

from starkware.cairo.lang.compiler.identifier_definition import StructDefinition
from protostar.commands.test.test_environment_exceptions import CheatcodeException

from protostar.commands.test.cheatcodes.reflect.misc import (
    ReflectInputType,
    to_cairo_naming,
    ReflectReturnType,
)

from protostar.commands.test.cheatcodes.reflect.get_from_vm import (
    get_value_from_vm,
)
from protostar.commands.test.cheatcodes.reflect.build_output import (
    generate_value_tree,
)


class Reflector:
    def __init__(self, ids: VmConsts, value: ReflectInputType = None):
        self._ids = ids
        self._value = value

    # We need to access Cairo's underscore variables
    # pylint: disable=W0212
    def __getattr__(self, name: str) -> "Reflector":
        new_value: ReflectInputType
        if not self._value:
            new_value = get_value_from_vm(self._ids, name)
        elif isinstance(self._value, VmConstsReference):

            assert isinstance(self._value._struct_definition, StructDefinition)
            assert isinstance(self._value._reference_value, RelocatableValue)
            members = self._value._struct_definition.members

            if name not in members:
                value_name = self._value._struct_definition.full_name.path[1]
                raise CheatcodeException(
                    "reflect", f'"{name}" is not a member of "{value_name}".'
                )

            member = members[name]
            expr_type = member.cairo_type
            addr = self._value._reference_value + member.offset

            if is_simple_type(expr_type):
                if isinstance(expr_type, TypeFelt):
                    tmp = int(self._value.get_or_set_value(name, None))  # type: ignore
                    assert isinstance(tmp, int)
                    new_value = tmp
                else:
                    assert isinstance(expr_type, TypePointer)
                    tmp = deepcopy(self._value.get_or_set_value(name, None))
                    assert isinstance(tmp, RelocatableValue)
                    new_value = tmp

            elif isinstance(expr_type, TypeStruct):
                new_value = VmConstsReference(
                    context=self._value._context,
                    struct_name=expr_type.scope,
                    reference_value=addr,
                )

            else:
                assert isinstance(expr_type, TypePointer) and isinstance(
                    expr_type.pointee, TypeStruct
                ), "Type must be of the form T*."

                tmp = deepcopy(self._value._context.memory[addr])  # type: ignore
                assert isinstance(tmp, RelocatableValue)
                new_value = tmp
        else:
            raise CheatcodeException(
                "reflect",
                f"Tried to get attribute of a {to_cairo_naming(type(self._value))} ({type(self._value).__name__}).",
            )
        return Reflector(self._ids, new_value)

    def get(self) -> ReflectReturnType:
        if self._value is None:
            raise CheatcodeException("reflect", "Reflector.get() called on no value.")
        return generate_value_tree(self._value)
