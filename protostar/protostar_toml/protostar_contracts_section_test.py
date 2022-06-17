from pathlib import Path
from typing import Dict

import pytest

from protostar.protostar_toml.conftest import MockProtostarTOMLReaderFixture
from protostar.protostar_toml.protostar_contracts_section import (
    ProtostarContractsSection,
)


@pytest.fixture(name="section_dict")
def section_dict_fixture() -> Dict:
    return {"main": ["src/main.cairo"]}


def test_serialization(
    mock_protostar_toml_reader: MockProtostarTOMLReaderFixture, section_dict: Dict
):
    protostar_toml_reader_mock = mock_protostar_toml_reader(section_dict)

    section = ProtostarContractsSection.load(
        protostar_toml_reader=protostar_toml_reader_mock
    )

    assert section.contract_name_to_paths["main"][0] == Path("./src/main.cairo")
    assert section.to_dict() == section_dict


def test_reading_undefined_section(
    mock_protostar_toml_reader: MockProtostarTOMLReaderFixture,
):
    protostar_toml_reader_mock = mock_protostar_toml_reader(protostar_section_dict=None)

    section = ProtostarContractsSection.load(
        protostar_toml_reader=protostar_toml_reader_mock
    )

    # pylint: disable=use-implicit-booleaness-not-comparison
    assert section.contract_name_to_paths == {}
