import re

import pytest
from starkware.cairo.lang.vm.relocatable import RelocatableValue

from .cairo_struct import CairoStruct


def test_cairo_struct_equality():
    struct_x = CairoStruct(
        a=111111,
        b=222222,
        c=CairoStruct(
            d=333333,
            e=RelocatableValue(4, 4),
            f=555555,
        ),
    )

    struct_y = CairoStruct(
        a=111111,
        b=222222,
        c=CairoStruct(
            d=333333,
            e=RelocatableValue(4, 4),
            f=555555,
        ),
    )

    struct_z = CairoStruct(
        a=111111,
        b=222222,
        c=CairoStruct(
            d=333333,
            e=RelocatableValue(4, 4),
            f=0xDEADBEEF,
        ),
    )

    assert struct_x == struct_y
    assert struct_x != struct_z


def test_cairo_struct_immutability():
    struct = CairoStruct(i=0b0110, j=0b1001)

    with pytest.raises(ValueError, match=re.escape("CairoStruct is immutable.")):
        struct.j = 0b1000101


def test_cairo_struct_type_safety():
    with pytest.raises(TypeError, match=re.escape("str is not a valid CairoType")):
        CairoStruct(
            a="""
            I love Cairo
            I love Cairo
            I love Cairo
        """
        )


def test_cairo_struct_no_member():
    struct = CairoStruct(a=0xAD0BE_BAD)

    with pytest.raises(
        KeyError, match=re.escape("'b' is not a member of this CairoStruct")
    ):
        _ = struct.b


def test_cairo_struct_non_keyword_args():
    with pytest.raises(
        TypeError,
        match=re.escape("__init__() takes 1 positional argument but 2 were given"),
    ):
        # pylint: disable-next=too-many-function-args
        CairoStruct(0xBAD_C0DE, a=14, b=16)  # type: ignore
