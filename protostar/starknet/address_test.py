import pytest

from protostar.protostar_exception import ProtostarException

from .address import Address


def test_human_representation():
    assert (
        Address.from_valid_input("0xAbCdEf").as_str()
        == "0x0000000000000000000000000000000000000000000000000000000000abcdef"
    )
    assert (
        f'{Address.from_valid_input("0xAbCdEf")}'
        == "0x0000000000000000000000000000000000000000000000000000000000abcdef"
    )


def test_numeric_representation():
    assert Address.from_valid_input("0xF").as_int() == 15


def test_handling_invalid_input():
    with pytest.raises(ProtostarException):
        Address.from_valid_input("-1")
