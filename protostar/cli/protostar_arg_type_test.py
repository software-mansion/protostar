import pytest

from .protostar_arg_type import FeeArgType, FeltArgType


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("123", 123),
        ("0xf", int("0xf", 16)),
        ("0xDEADC0DE", int("0xDEADC0DE", 16)),
    ],
)
def test_felt_type(test_input, expected):
    result = FeltArgType().parse(test_input)
    assert result == expected


def test_fee_type():
    assert FeeArgType().parse("auto") == "auto"
    assert FeeArgType().parse("123") == 123
