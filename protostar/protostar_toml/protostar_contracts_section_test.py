from pathlib import Path
from typing import Dict

import pytest
from pytest_mock import MockerFixture

from protostar.protostar_toml._conftest import mock_protostar_toml_reader
from protostar.protostar_toml.protostar_contracts_section import (
    ProtostarContractsSection,
)


@pytest.fixture(name="section_dict")
def section_dict_fixture() -> Dict:
    return {"main": ["src/main.cairo"]}


def test_serialization(mocker: MockerFixture, section_dict: Dict):
    protostar_toml_reader_mock = mock_protostar_toml_reader(mocker)(section_dict)

    section = ProtostarContractsSection.from_protostar_toml_reader(
        protostar_toml_reader=protostar_toml_reader_mock
    )

    assert section.contract_name_to_paths["main"][0] == Path("./src/main.cairo")
    assert section.to_dict() == section_dict


def test_reading_undefined_section(mocker: MockerFixture):
    protostar_toml_reader_mock = mock_protostar_toml_reader(mocker)(
        protostar_section_dict=None
    )

    section = ProtostarContractsSection.from_protostar_toml_reader(
        protostar_toml_reader=protostar_toml_reader_mock
    )

    # pylint: disable=use-implicit-booleaness-not-comparison
    assert section.contract_name_to_paths == {}
