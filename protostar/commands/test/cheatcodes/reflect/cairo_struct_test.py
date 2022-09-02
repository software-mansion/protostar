import pytest

from starkware.cairo.lang.vm.relocatable import RelocatableValue

from protostar.commands.test.cheatcodes.reflect.cairo_struct import CairoStruct
from protostar.commands.test.test_environment_exceptions import (
    SimpleBreakingReportedException,
)

# pylint: disable=C0103,W0612


def test_cairo_struct_equality():
    x = CairoStruct(
        a=111111,
        b=222222,
        c=CairoStruct(
            d=333333,
            e=RelocatableValue(4, 4),
            f=555555,
        ),
    )

    y = CairoStruct(
        a=111111,
        b=222222,
        c=CairoStruct(
            d=333333,
            e=RelocatableValue(4, 4),
            f=555555,
        ),
    )

    z = CairoStruct(
        a=111111,
        b=222222,
        c=CairoStruct(
            d=333333,
            e=RelocatableValue(4, 4),
            f=0xDEADBEEF,
        ),
    )

    assert x == y
    assert x != z


def test_cairo_struct_immutability():
    x = CairoStruct(i=0b0110, j=0b1001)

    with pytest.raises(SimpleBreakingReportedException) as exc:
        x.j = 0b1000101
    assert "CairoStruct is immutable." in str(exc.value)


def test_cairo_struct_type_safety():
    with pytest.raises(SimpleBreakingReportedException) as exc:
        x = CairoStruct(
            a="""
            I love Cairo
            I love Cairo
            I love Cairo
        """
        )
    assert "is not a valid CairoType" in str(exc.value)


def test_cairo_struct_no_member():
    x = CairoStruct(a=0xAD0BE_BAD)

    with pytest.raises(SimpleBreakingReportedException) as exc:
        y = x.b
    assert "is not a member of this CairoStruct" in str(exc.value)


def test_cairo_struct_non_keyword_args():
    with pytest.raises(SimpleBreakingReportedException) as exc:
        x = CairoStruct(
            0xBAD_C0DE,
            a=14,
            b=16,
        )
    assert "CairoStruct constructor takes only keyword arguments." in str(exc.value)
