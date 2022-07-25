from protostar.commands.test.cheatcodes.reflect.reflect_cairo_struct import CairoStruct
from protostar.commands.test.test_environment_exceptions import CheatcodeException

# pylint: disable=C0103,W0612


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
