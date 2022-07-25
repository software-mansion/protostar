from protostar.commands.test.cheatcodes.reflect.reflect_cairo_struct import (
    CairoStruct,
    named_cairo_struct,
)
from protostar.commands.test.test_environment_exceptions import CheatcodeException


def test_cairo_struct_equality():
    x = CairoStruct(
        a=111111,
        b=222222,
        c=CairoStruct(
            d=333333,
            e=444444,
            f=555555,
        ),
    )

    y = CairoStruct(
        a=111111,
        b=222222,
        c=CairoStruct(
            d=333333,
            e=444444,
            f=555555,
        ),
    )

    z = CairoStruct(
        a=111111,
        b=222222,
        c=CairoStruct(
            d=333333,
            e=444444,
            f=0xDEADBEEF,
        ),
    )

    assert x == y
    assert x != z


def test_cairo_struct_naming():

    main_type = named_cairo_struct("Foo")
    b_type = named_cairo_struct("Bar")

    x = main_type(a=12, b=b_type(x=13), c=14)
    y = CairoStruct(a=12, b=CairoStruct(x=13), c=14)
    z = CairoStruct(a=12, b=b_type(x=13), c=14)
    w = main_type(a=12, b=CairoStruct(x=13), c=14)

    assert x == y == z == w


def test_cairo_struct_immutability():
    x = CairoStruct(a=0b0110, b=0b1001)

    try:
        x.b = 0b1000101
        assert False
    except CheatcodeException as exc:
        assert "CairoStruct is immutable." in str(exc)


def test_cairo_struct_type_safety():
    try:
        x = CairoStruct(
            a="""
            I love Cairo
            I love Cairo
            I love Cairo
        """
        )
        assert False
    except CheatcodeException as exc:
        assert "is not a valid CairoType" in str(exc)


def test_cairo_struct_no_member():
    x = CairoStruct(a=0xAD0BE_BAD)

    try:
        y = x.b
        assert False
    except CheatcodeException as exc:
        assert "is not a member of this CairoStruct" in str(exc)


def test_cairo_struct_non_keyword_args():
    try:
        x = CairoStruct(
            0xBAD_C0DE,
            a=14,
            b=16,
        )
        assert False
    except CheatcodeException as exc:
        assert "CairoStruct constructor takes only keyword arguments." in str(exc)


def test_cairo_struct_name_not_str():
    try:
        x_type = named_cairo_struct(0xC0FEE)
    except CheatcodeException as exc:
        assert 'Struct typename must be of type "str"' in str(exc)
