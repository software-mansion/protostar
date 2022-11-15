import pytest

from protostar.protostar_exception import ProtostarException

from .address import Address


def test_equality():
    address = Address.from_user_input("0xF")
    assert address == 15
    assert address == "0xf"
    assert address == "15"
    assert address == Address.from_user_input("0xF")


def test_human_representation():
    assert (
        f'{Address.from_user_input("0xAbCdEf")}'
        == "0x0000000000000000000000000000000000000000000000000000000000abcdef"
    )


def test_numeric_representation():
    assert int(Address.from_user_input("0xF")) == 15


def test_handling_negative_values():
    with pytest.raises(ProtostarException):
        Address.from_user_input("-1")


def test_handling_invalid_input():
    with pytest.raises(ProtostarException):
        Address.from_user_input("XYZ")
