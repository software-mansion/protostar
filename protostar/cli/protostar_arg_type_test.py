from pathlib import Path

import pytest

from protostar.compiler import ContractSourceIdentifier
from protostar.compiler.contract_source_identifier import (
    ContractSourceIdentifierFactory,
)
from protostar.configuration_file import FakeConfigurationFile

from .protostar_arg_type import create_map_protostar_type_name_to_parser

map_protostar_type_name_to_parser = create_map_protostar_type_name_to_parser(
    ContractSourceIdentifierFactory(FakeConfigurationFile())
)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("123", 123),
        ("0xf", int("0xf", 16)),
        ("0xDEADC0DE", int("0xDEADC0DE", 16)),
    ],
)
def test_felt_type(test_input: str, expected: int):
    result = map_protostar_type_name_to_parser("felt")(test_input)
    assert result == expected


def test_class_hash_type():
    parse = map_protostar_type_name_to_parser("class_hash")
    assert parse("0xF") == 15
    assert parse("15") == 15


def test_wei_type():
    parse = map_protostar_type_name_to_parser("wei")
    assert parse("1e3") == 1000
    assert parse("1000") == 1000


def test_fee_type():
    parse_fee = map_protostar_type_name_to_parser("fee")
    assert parse_fee("auto") == "auto"
    assert parse_fee("123") == 123


def test_address_arg_type():
    parser = map_protostar_type_name_to_parser("address")
    result = parser("0xdeadbeef123")
    assert isinstance(result, int)
    assert result == 15302363377955


def test_block_explorer_type():
    parser = map_protostar_type_name_to_parser("block_explorer")
    result = parser("starkscan")
    assert result == "starkscan"


def test_fail_on_wrong_block_explorer():
    parser = map_protostar_type_name_to_parser("block_explorer")
    with pytest.raises(ValueError):
        parser("abc")


@pytest.fixture(name="fake_contract_path")
def fake_contract_path_fixture(tmp_path: Path) -> Path:
    contract_path = tmp_path / "main.cairo"
    contract_path.touch()
    return contract_path


def test_contract_source_identifier_parser(fake_contract_path: Path):
    parser = create_map_protostar_type_name_to_parser(
        ContractSourceIdentifierFactory(
            FakeConfigurationFile(
                contract_name_to_source_paths={"main": [fake_contract_path]},
            )
        )
    )("contract_source_identifier")

    result = parser("main")

    return result == ContractSourceIdentifier(name="main", paths=[fake_contract_path])
