import pytest

from .protostar_arg_type import map_protostar_type_name_to_parser


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("123", 123),
        ("0xf", int("0xf", 16)),
        ("0xDEADC0DE", int("0xDEADC0DE", 16)),
    ],
)
def test_felt_type(test_input, expected):
    result = map_protostar_type_name_to_parser("felt")(test_input)
    assert result == expected


def test_fee_type():
    parse_fee = map_protostar_type_name_to_parser("fee")
    assert parse_fee("auto") == "auto"
    assert parse_fee("123") == 123
