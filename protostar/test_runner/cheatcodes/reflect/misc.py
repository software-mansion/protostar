from typing import Type, Union

from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.cairo.lang.vm.vm_consts import VmConstsReference

from .cairo_struct import CairoStruct

ReflectInputType = Union[VmConstsReference, RelocatableValue, None, int]
ReflectValueType = Union[CairoStruct, RelocatableValue, int]
ReflectReturnType = Union[CairoStruct, RelocatableValue, None, int]


def to_cairo_naming(input_type: Type):
    if input_type == RelocatableValue:
        return "pointer"
    if input_type == int:
        return "felt"
    if input_type == VmConstsReference:
        return "struct"
    if input_type == type(None):
        return "None"

    assert False, "Not a valid Cairo type."
